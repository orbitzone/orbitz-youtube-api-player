"""Personalized recommendations: isolated profile/cache, synthetic provider, no network."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys,tempfile,time,unittest
from unittest.mock import patch,MagicMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import local_library as library
import recommendation_engine as engine
import youtube_api


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        override=patch.object(library,'DATABASE',Path(self.folder.name)/'library.sqlite3');override.start();self.addCleanup(override.stop)
        cache=patch.dict(engine.os.environ,{'XDG_CACHE_HOME':self.folder.name});cache.start();self.addCleanup(cache.stop)
        self.items=[dict(id=f'{index:011d}',title=f'Synthetic {index}',channel='Test',thumbnail='') for index in range(20)]

    def record(self,query,mode):library.record_search(query,mode,library.recommendation_profile()['revision'])

    def test_each_category_gets_twenty_generic_results_without_profile(self):
        with patch.object(youtube_api,'search',return_value=self.items) as search:
            for mode in engine.MODES:
                result=engine.recommend(mode)
                self.assertEqual(result['mode'],mode);self.assertEqual(result['basis'],'popular');self.assertEqual(len(result['items']),20)
                search.assert_called_with(None,mode,locale='pt-BR')
            self.assertEqual(search.call_count,4)

    def test_explicit_interests_and_category_recent_searches_are_combined(self):
        library.action(dict(op='recommendation-settings',values=dict(interests=['Jazz'],use_recent=True)))
        self.record('astronomia','videos');self.record('história brasileira','podcasts')
        plan=engine.plan('podcasts');self.assertIn('Jazz',plan['terms']);self.assertIn('história brasileira',plan['terms']);self.assertIn('astronomia',plan['terms'])
        self.assertIn(' | ',plan['query']);self.assertEqual(plan['basis'],'personalized')
        with patch.object(youtube_api,'search',return_value=self.items) as search:
            engine.recommend('podcasts');search.assert_called_once_with(plan['query'],'podcasts',locale='pt-BR')

    def test_dedup_bound_expiry_and_revision_protect_clear_from_inflight_search(self):
        for index in range(40):self.record('topic '+str(index),'videos')
        self.record('TOPIC 39','videos');profile=library.recommendation_profile();self.assertEqual(len(profile['recent']),30);self.assertEqual(profile['recent'][0]['query'],'TOPIC 39')
        revision=profile['revision'];library.action({'op':'clear-searches'});library.record_search('late result','videos',revision);self.assertEqual(library.recommendation_profile()['recent'],[])
        self.record('expires','shorts')
        with patch.object(library.time,'time',return_value=time.time()+31*86400):self.assertEqual(library.recommendation_profile()['recent'],[])
        self.assertEqual(library.recommendation_profile()['recent'],[])

    def test_recent_opt_out_and_clear_keep_interests_and_favorites(self):
        self.record('old topic','videos');library.action(dict(op='save',kind='favorites',video=dict(id='abcdefghijk',title='Kept')))
        library.action(dict(op='recommendation-settings',values=dict(interests=['cooking'],use_recent=False)))
        self.record('not recorded','live');self.assertEqual(len(library.recommendation_profile()['recent']),1)
        self.assertEqual(engine.plan('videos')['terms'],['cooking'])
        library.action({'op':'clear-searches'});result=library.action({});self.assertEqual(len(result['favorites']),1);self.assertEqual(result['recommendation_preferences']['interests'],['cooking'])
        self.assertEqual(set(library.export_library()),{'version','favorites','later'})

    def test_existing_favorites_seed_suggestions_before_any_new_search(self):
        library.action(dict(op='save',kind='favorites',video=dict(id='abcdefghijk',title='Radio 90s Hits | 24/7 live stream')))
        self.assertEqual(engine.plan('shorts')['terms'],['Radio 90s Hits'])
        library.action(dict(op='recommendation-settings',values=dict(interests=['science'],use_recent=False)))
        self.assertEqual(engine.plan('shorts')['terms'],['science'])

    def test_invalid_preferences_modes_and_urls(self):
        for values in (dict(interests=['a']*11,use_recent=True),dict(interests=[''],use_recent=True),dict(interests=['a'],use_recent=1)):
            with self.assertRaises(ValueError):library.action(dict(op='recommendation-settings',values=values))
        for mode in ('comments',[],None):
            with self.assertRaises(ValueError):engine.recommend(mode)
        self.record('https://example.invalid/private','videos');self.assertEqual(library.recommendation_profile()['recent'],[])

    def test_cache_is_profile_specific_category_specific_private_and_coalesced(self):
        with patch.object(youtube_api,'search',return_value=self.items) as search:
            with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(lambda _:engine.recommend('shorts'),range(4)))
            self.assertTrue(all(len(result['items'])==20 for result in results));self.assertEqual(search.call_count,1)
            self.record('new topic','shorts');engine.recommend('shorts');self.assertEqual(search.call_count,2)
            engine.recommend('live');self.assertEqual(search.call_count,3)
        cache=Path(self.folder.name)/'orbitz-youtube-wrapper'/'recommendations-shorts.json'
        self.assertEqual(cache.stat().st_mode&0o777,0o600)
        self.assertNotIn('new topic',cache.read_text())
        self.assertEqual(len(list(cache.parent.glob('recommendations-*.json'))),2)

    def test_empty_results_are_cached_and_live_cache_expires(self):
        with patch.object(youtube_api,'search',return_value=[]) as search:
            self.assertEqual(engine.recommend('live')['items'],[]);engine.recommend('live');self.assertEqual(search.call_count,1)
            path=Path(self.folder.name)/'orbitz-youtube-wrapper'/'recommendations-live.json';cached=json.loads(path.read_text());cached['time']-=301;path.write_text(json.dumps(cached))
            engine.recommend('live');self.assertEqual(search.call_count,2)

    def test_generic_filters_and_podcast_or_terms_remain_correct(self):
        response=MagicMock();response.read.return_value=b'{"items":[]}';response.__enter__.return_value=response
        from urllib.parse import urlsplit,parse_qs
        with patch.object(youtube_api,'read_key',return_value='synthetic-key'),patch.object(youtube_api.urllib.request,'urlopen',return_value=response) as request:
            youtube_api.search(None,'shorts');self.assertEqual(parse_qs(urlsplit(request.call_args.args[0]).query)['videoDuration'],['short'])
            youtube_api.search(None,'live');params=parse_qs(urlsplit(request.call_args.args[0]).query);self.assertEqual(params['eventType'],['live']);self.assertNotIn('publishedAfter',params)
            youtube_api.search('jazz | science','podcasts');self.assertEqual(parse_qs(urlsplit(request.call_args.args[0]).query)['q'],['podcast jazz | podcast science'])
