"""Category isolation and empty personalized fallback; synthetic provider only."""
import io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import youtube_api as api
import recommendation_engine as engine
class CategoryTests(unittest.TestCase):
    def test_broadcasts_and_podcast_evidence_are_filtered(self):
        def item(i,title,broadcast):return {'id':{'videoId':f'{i:011d}'},'snippet':{'title':title,'channelTitle':'Canal','liveBroadcastContent':broadcast}}
        entries=[item(1,'Podcast ciência','none'),item(2,'Podcast LIVE','live'),item(3,'Podcast amanhã','upcoming'),item(4,'Notícias','none'),item(5,'Cortes podcast','none')]
        for mode,expected in [('live',[2]),('podcasts',[1]),('videos',[1,4,5]),('shorts',[1,4,5])]:
            with patch.object(api,'read_key',return_value='synthetic'),patch.object(api.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps({'items':entries}).encode())):
                result=api.search('ciência',mode)
            self.assertEqual([item['id'] for item in result],[f'{i:011d}' for i in expected])
    def test_fallback_keeps_category_and_cache_metadata(self):
        selected=dict(key='synthetic',query='rare topic',basis='personalized',terms=['rare topic'])
        with tempfile.TemporaryDirectory() as folder,patch.dict(engine.os.environ,{'XDG_CACHE_HOME':folder}),patch.object(engine,'plan',return_value=selected),patch.object(api,'search',side_effect=[[],[{'id':'abcdefghijk'}]]) as search:
            result=engine.recommend('live');self.assertEqual(result['basis'],'popular');self.assertEqual(result['terms'],[])
            self.assertEqual(search.call_args_list[1].args,(None,'live'))
            again=engine.recommend('live');self.assertEqual(again,result);self.assertEqual(search.call_count,2)
