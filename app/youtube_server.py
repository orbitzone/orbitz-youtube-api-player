"""Token-protected loopback HTTP boundary for the YouTube window."""
from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
import time
from youtube_api import MissingAPIKey,save_key,search,video_details,video_likes
from recommendation_engine import recommend as recommendations
from runner_score import read_best_score,save_best_score
from ui_language import ui
import local_library
import sqlite3

BASE = Path(__file__).resolve().parent

def make_handler(token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def reply(self,status,body,kind='application/json'):
            raw=body if isinstance(body,bytes) else json.dumps(body,ensure_ascii=False).encode()
            self.send_response(status);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.send_header('Referrer-Policy','strict-origin-when-cross-origin');self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if self.path=='/'+token+'/fonts/Orbitron.ttf':
                self.reply(200,(BASE/'fonts'/'Orbitron.ttf').read_bytes(),'font/ttf');return
            if self.path in tuple('/'+token+'/audio/'+name for name in ('phaseJump1.ogg','laser1.ogg','laser5.ogg','spaceTrash1.ogg','lowDown.ogg')):
                self.reply(200,(BASE/'audio'/self.path.rsplit('/',1)[1]).read_bytes(),'audio/ogg');return
            if self.path in ('/'+token+'/features.js','/'+token+'/maze.js','/'+token+'/game_audio.js','/'+token+'/game_synth.js','/'+token+'/game_controls.js','/'+token+'/invaders.js','/'+token+'/asteroids.js','/'+token+'/games_home.js','/'+token+'/extra_games.js'):self.reply(200,(BASE/self.path.rsplit('/',1)[1]).read_bytes(),'text/javascript');return
            if self.path!='/'+token+'/':self.reply(404,{});return
            self.reply(200,(BASE/'index.html').read_bytes(),'text/html')
        def do_POST(self):
            action=self.path.removeprefix('/'+token+'/')
            origin='http://127.0.0.1:'+str(self.server.server_port)
            if not self.path.startswith('/'+token+'/') or self.headers.get('Origin')!=origin:
                self.reply(403,{'error':'Origem inválida.'});return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=4096:raise ValueError('Requisição inválida.')
                data=json.loads(self.rfile.read(length))
                if not isinstance(data,dict):raise ValueError('Requisição inválida.')
                if action=='local-state':self.reply(200,local_library.action(data))
                elif action in ('breaker-score','lander-score','maze-score'):
                    game=action.removesuffix('-score')
                    best=save_best_score(data['score'],game) if 'score' in data else read_best_score(game)
                    self.reply(200,{'best':best})
                elif action=='asteroids-score':
                    best=save_best_score(data['score'],'asteroids') if 'score' in data else read_best_score('asteroids')
                    self.reply(200,{'best':best})
                elif action=='invaders-score':
                    best=save_best_score(data['score'],'invaders') if 'score' in data else read_best_score('invaders')
                    self.reply(200,{'best':best})
                elif action=='runner-score':
                    best=save_best_score(data['score']) if 'score' in data else read_best_score()
                    self.reply(200,{'best':best})
                elif action=='key':
                    save_key(data.get('key'));self.server.cache.clear();self.reply(200,{'saved':True})
                elif action=='language':
                    locale=data.get('locale')
                    if locale not in ('pt-BR','en-US'):raise ValueError('Idioma inválido.')
                    applied_locale=ui.set_locale(locale);self.reply(200,{'saved':True,'locale':applied_locale})
                elif action in ('new-window','window-state','open-external','copy-link','always-above','auto-controls','library-transfer','diagnostics','media-state'):
                    callback=getattr(self.server,'ui_actions',{}).get(action)
                    if callback is None:raise ValueError('Ação indisponível.')
                    if action in ('always-above','auto-controls') and type(data.get('enabled')) is not bool:raise ValueError('Estado inválido.')
                    result=callback(data)
                    self.reply(200,result if isinstance(result,dict) else {'ok':True})
                elif action=='video-likes':
                    self.reply(200,{'likes':video_likes(data.get('ids'))})
                elif action=='video-details':
                    self.reply(200,video_details(data.get('id')))
                elif action=='recommendations':
                    self.reply(200,recommendations(data.get('mode','videos'),ui.get_locale()))
                elif action=='search':
                    query=data.get('query')
                    mode=data.get('mode','videos')
                    if not isinstance(query,str) or not 0<len(query.strip())<=300 or any(ord(char)<32 for char in query):raise ValueError('Busca inválida.')
                    if not isinstance(mode,str) or mode not in ('videos','shorts','live','podcasts'):raise ValueError('Filtro de busca inválido.')
                    query=query.strip()
                    history_revision=local_library.recommendation_profile()['revision']
                    identity=(query,mode)
                    cache=self.server.cache.get(identity)
                    if not cache or time.time()-cache[0]>300:
                        cache=(time.time(),search(query,mode))
                        # Bound the in-memory cache while keeping distinct results
                        # for each query/mode pair and the recommendations entry.
                        self.server.cache={k:v for k,v in self.server.cache.items()
                            if k is None or (isinstance(k,tuple) and len(k)==2 and time.time()-v[0]<=300)}
                        if len(self.server.cache)>=40:
                            self.server.cache={k:v for k,v in self.server.cache.items() if k is None}
                        self.server.cache[identity]=cache
                    local_library.record_search(query,mode,history_revision)
                    self.reply(200,{'items':cache[1]})
                else:self.reply(404,{})
            except (ValueError,TypeError,OSError,RuntimeError,sqlite3.Error):
                import sys
                error=sys.exc_info()[1]
                self.reply(400,{'error':str(error)[:250],'code':'key_required' if isinstance(error,MissingAPIKey) else 'request_failed'})
    return Handler
