"""Close-time resume rules with isolated SQLite and synthetic MPRIS state."""
import ast
from pathlib import Path
import sys,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'app'))
import local_library


class NativeResumeTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        override=patch.object(local_library,'DATABASE',Path(self.folder.name)/'library.sqlite3');override.start();self.addCleanup(override.stop)
        tree=ast.parse((ROOT/'app/youtube-wrapper.py').read_text());main=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='main');activate=next(node for node in main.body if isinstance(node,ast.FunctionDef) and node.name=='create_window')
        self.function=next(node for node in activate.body if isinstance(node,ast.FunctionDef) and node.name=='save_last_playback')

    def close(self,**changes):
        state=dict(id='abcdefghijk',title='Synthetic',position=42,duration=300,status='Paused',rate=1.0,live=False,restart=False);state.update(changes)
        scope=dict(local_library=local_library,media=SimpleNamespace(state=state,updated=100))
        exec(compile(ast.Module(body=[self.function],type_ignores=[]),'native_resume','exec'),scope)
        with patch('time.monotonic',return_value=110):scope['save_last_playback']()
        return local_library.action({})['resume']

    def test_paused_playing_finished_stopped_and_live_are_never_discarded(self):
        for changes,expected in (({},42),({'status':'Playing'},52),({'status':'Stopped','position':0,'restart':True},0),({'status':'Stopped','position':300,'restart':True},0),({'status':'Playing','position':900000,'duration':1_700_000_000,'live':True},0)):
            with self.subTest(changes=changes):
                saved=self.close(**changes);self.assertEqual(saved['id'],'abcdefghijk');self.assertEqual(saved['position'],expected)

    def test_new_selection_before_player_ready_is_not_overwritten_by_old_track(self):
        local_library.action({'op':'remember','video':{'id':'123456789_-','title':'New selected'}})
        saved=self.close(status='Playing');self.assertEqual(saved['id'],'123456789_-');self.assertEqual(saved['position'],0)

    def test_reopening_and_closing_without_playback_retains_the_offer(self):
        local_library.action({'op':'remember','video':{'id':'abcdefghijk','title':'Radio'},'live':True})
        saved=self.close(id='');self.assertEqual(saved['id'],'abcdefghijk');self.assertEqual(saved['position'],0)
