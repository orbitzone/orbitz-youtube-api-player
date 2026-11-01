"""Official public statistics: batches, unavailable counts, cache and validation."""
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import youtube_api as api

class LikesTests(unittest.TestCase):
    def setUp(self):
        api._LIKES_CACHE.clear()

    def test_batch_cache_zero_and_unavailable(self):
        ids=['abcdefghijk','123456789_-','ABCDEFGHIJK']
        payload={'items':[{'id':ids[0],'statistics':{'likeCount':'0'}},{'id':ids[1],'statistics':{}}]}
        with patch.object(api,'read_key',return_value='synthetic'),patch.object(api.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(payload).encode())) as request:
            result=api.video_likes(ids)
            self.assertEqual(result,{ids[0]:'0',ids[1]:None,ids[2]:None})
            self.assertEqual(api.video_likes(ids),result)
            self.assertEqual(request.call_count,1)
            self.assertIn('part=statistics',request.call_args.args[0])
        api._LIKES_CACHE[ids[0]]=(0,'10')
        with patch.object(api,'read_key',return_value='synthetic'),patch.object(api.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(payload).encode())) as request:
            api.video_likes([ids[0]])
            self.assertEqual(request.call_count,1)

    def test_invalid_ids_do_not_access_network(self):
        with patch.object(api.urllib.request,'urlopen') as request:
            for value in (None,[],['bad'],['abcdefghijk']*51):
                with self.assertRaises(ValueError):api.video_likes(value)
            request.assert_not_called()
