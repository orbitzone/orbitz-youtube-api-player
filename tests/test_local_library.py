"""Transactional local storage tests; every test uses a disposable profile."""
import json
from pathlib import Path
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import local_library as library

VIDEO=dict(id='abcdefghijk',title='Synthetic <video>')
SECOND=dict(id='123456789_-',title='Second')


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        change=patch.object(library,'DATABASE',Path(self.directory.name)/'library.sqlite3');change.start();self.addCleanup(change.stop)

    def test_resume_metadata_preserves_position_and_rejects_stale_video(self):
        library.action(dict(op='remember',video=VIDEO,position=42,duration=100,live=False))
        result=library.action(dict(op='resume-metadata',video={**VIDEO,'channel':'Canal & teste'}))
        self.assertEqual(result['resume']['channel'],'Canal & teste')
        self.assertEqual(result['resume']['position'],42)
        library.action(dict(op='remember',video=SECOND,position=0,duration=100))
        result=library.action(dict(op='resume-metadata',video={**VIDEO,'channel':'Canal antigo'}))
        self.assertEqual(result['resume']['id'],SECOND['id'])
        self.assertNotIn('channel',result['resume'])
        with self.assertRaises(ValueError):
            library.action(dict(op='resume-metadata',video={**VIDEO,'channel':'x'*201}))

    def test_game_sound_preference_persists_and_requires_boolean(self):
        self.assertFalse(library.action({})['preferences']['game_sound'])
        library.action(dict(op='preferences',values={'game_sound':True}))
        self.assertTrue(library.action({})['preferences']['game_sound'])
        with self.assertRaises(ValueError):library.action(dict(op='preferences',values={'game_sound':1}))

    def test_game_volume_boundaries_and_type(self):
        for volume in (0,35,100):
            library.action(dict(op='preferences',values={'game_volume':volume}))
            self.assertEqual(library.action({})['preferences']['game_volume'],volume)
        for volume in (-1,101,True,25.5,'50'):
            with self.assertRaises(ValueError):library.action(dict(op='preferences',values={'game_volume':volume}))

    def test_preferences_roundtrip_and_private_file(self):
        result=library.action({});self.assertEqual(result['preferences'],library.DEFAULTS)
        result=library.action(dict(op='preferences',values=dict(always_above=True,auto_controls=True,hide_delay=3000,show_delay=800)))
        self.assertEqual(result['preferences']['hide_delay'],3000)
        self.assertEqual(library.DATABASE.stat().st_mode&0o777,0o600)
        for value in ({'auto_controls':1},{'hide_delay':99},{'show_delay':True},{'unknown':False}):
            with self.assertRaises(ValueError):library.action(dict(op='preferences',values=value))
        self.assertTrue(library.action({})['preferences']['auto_controls'])

    def test_bookmarks_export_excludes_secrets_preferences_resume_queue(self):
        for kind in ('favorites','later'):library.action(dict(op='save',kind=kind,video=VIDEO))
        library.action(dict(op='save',kind='favorites',video=VIDEO))
        result=library.export_library();self.assertEqual(set(result),{'version','favorites','later'});self.assertEqual(len(result['favorites']),1)
        library.action(dict(op='remove',kind='favorites',video=VIDEO));self.assertEqual(library.action({})['favorites'],[])
        self.assertEqual(library.import_library(result)['favorites'],[VIDEO])
        with self.assertRaises(ValueError):library.import_library(dict(version=True))

    def test_invalid_import_is_atomic_and_never_replaces_existing_library(self):
        library.action(dict(op='save',kind='favorites',video=VIDEO))
        with self.assertRaises(ValueError):library.import_library(dict(version=1,favorites=[SECOND],later=[{'id':'invalid'}]))
        self.assertEqual(library.action({})['favorites'],[VIDEO])
        with self.assertRaises(ValueError):library.import_library(dict(version=1,favorites=[SECOND]*1001))

    def test_queue_reorder_remove_and_next_are_transactional(self):
        library.action(dict(op='queue-add',video=VIDEO));result=library.action(dict(op='queue-add',video=SECOND))
        qid=result['queue'][1]['qid'];library.action(dict(op='queue-up',qid=qid))
        result=library.action(dict(op='queue-next'));self.assertEqual(result['next'],SECOND);self.assertEqual(len(result['queue']),1)
        library.action(dict(op='queue-remove',qid=result['queue'][0]['qid']));self.assertEqual(library.action({})['queue'],[])
        self.assertNotIn('next',library.action(dict(op='queue-next')))

    def test_parallel_appends_and_consumers_never_lose_or_duplicate_queue_items(self):
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda _:library.action(dict(op='queue-add',video=VIDEO)),range(20)))
        self.assertEqual(len(library.action({})['queue']),20)
        with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(lambda _:library.action(dict(op='queue-next')),range(25)))
        self.assertEqual(sum('next' in result for result in results),20);self.assertEqual(library.action({})['queue'],[])

    def test_resume_always_keeps_the_video_and_validates_position(self):
        library.action(dict(op='progress',video=VIDEO,position=35,duration=100));self.assertEqual(library.action({})['resume']['position'],35)
        for position in (True,float('nan'),float('inf'),-1,library.MAX_MEDIA_SECONDS+1):
            with self.assertRaises(ValueError):library.action(dict(op='progress',video=VIDEO,position=position,duration=100))
        library.action(dict(op='progress',video=VIDEO,position=95,duration=100));self.assertEqual(library.action({})['resume']['position'],95)
        library.action(dict(op='progress',video=VIDEO,position=25,duration=0));library.action(dict(op='clear-resume'));self.assertIsNone(library.action({})['resume'])

    def test_remember_before_playback_short_paused_stopped_and_finished_video(self):
        library.action(dict(op='remember',video=VIDEO));self.assertEqual(library.action({})['resume']['id'],VIDEO['id'])
        self.assertEqual(library.action({})['resume']['position'],0)
        for position in (0,2,35,99):
            library.action(dict(op='progress',video=VIDEO,position=position,duration=100))
            self.assertEqual(library.action({})['resume']['position'],position)
        for payload in (dict(position=100,duration=100),dict(position=42,duration=100,restart=True)):
            library.action(dict(op='progress',video=VIDEO,**payload))
            self.assertEqual(library.action({})['resume']['id'],VIDEO['id'])
            self.assertEqual(library.action({})['resume']['position'],0)

    def test_live_radio_and_unknown_duration_remain_available_from_start(self):
        for payload in (dict(position=42,duration=0),dict(position=42,duration=1_700_000_000),dict(position=42,duration=300,live=True)):
            library.action(dict(op='progress',video=VIDEO,**payload))
            saved=library.action({})['resume'];self.assertEqual(saved['id'],VIDEO['id']);self.assertEqual(saved['position'],0)
        for payload in (dict(live=1),dict(restart='yes')):
            with self.assertRaises(ValueError):library.action(dict(op='progress',video=VIDEO,position=0,duration=0,**payload))

    def test_database_symlink_is_not_followed(self):
        target=Path(self.directory.name)/'secret';target.write_text('unchanged')
        library.DATABASE.symlink_to(target)
        with self.assertRaises(OSError):library.action({})
        self.assertEqual(target.read_text(),'unchanged')
