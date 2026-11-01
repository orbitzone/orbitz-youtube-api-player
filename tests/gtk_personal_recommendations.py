"""All-category recommendation UI + real HTTP/SQLite; isolated and offline."""
import json,os,secrets,sys,tempfile,threading
from pathlib import Path
from http.server import ThreadingHTTPServer
root=Path(__file__).resolve().parents[1];profile=tempfile.TemporaryDirectory(prefix='youtube-recommendations-smoke-')
os.environ['XDG_CONFIG_HOME']=profile.name;os.environ['XDG_CACHE_HOME']=profile.name;os.environ['GSETTINGS_BACKEND']='memory'
sys.path.insert(0,str(root/'app'))
import youtube_api,local_library,youtube_server
local_library.action(dict(op='recommendation-settings',values=dict(interests=['astronomia','música anos 90'],use_recent=True)))
local_library.record_search('lofi','videos',local_library.recommendation_profile()['revision'])
calls=[]
def search(query=None,mode='videos',locale=None):
    calls.append((query,mode));return [dict(id=f'{i:011d}',title=f'{mode} synthetic {i}',channel='Synthetic',thumbnail='') for i in range(20)]
youtube_api.search=search;youtube_server.search=search
token=secrets.token_urlsafe(24);server=ThreadingHTTPServer(('127.0.0.1',0),youtube_server.make_handler(token));server.cache={};server.daemon_threads=True
server.ui_actions={'window-state':lambda data:None,'always-above':lambda data:None,'auto-controls':lambda data:None,'media-state':lambda data:None}
threading.Thread(target=server.serve_forever,daemon=True).start()
import gi
gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,GLib,WebKit2
manager=WebKit2.UserContentManager();manager.register_script_message_handler('recommendationscheck');view=WebKit2.WebView(user_content_manager=manager)
window=Gtk.Window(title='Recomendações — teste temporário');window.set_default_size(900,600);window.add(view);errors=[];completed=[]
catalog=json.loads((root/'i18n/pt-BR.json').read_text())
script='''(async()=>{
 const assert=(v,m)=>{if(!v)throw Error(m)};
 const wait=()=>new Promise(resolve=>setTimeout(resolve,100));
 const until=async(fn)=>{for(let i=0;i<50;i++){if(fn())return;await wait()}throw Error('Timed out')};
 window.orbitzSetLanguage({locale:'pt-BR',catalog:CATALOG});
 openDiscovery();await until(()=>$('feature-interests').value.includes('astronomia'));
 for(const mode of ['videos','shorts','live','podcasts']){
  setTab(mode);await until(()=>$('results').querySelector('strong')?.textContent.startsWith(mode+' synthetic'));
  assert($('results').querySelectorAll('.feature-result-row').length===20,'twenty suggestions '+mode);
  assert($('status').textContent.includes('para você'),'personalization explanation '+mode);
 }
 $('query').value='jazz piano';await searchCurrentTab();$('query').value='';await loadRecommendations();
 assert($('status').textContent.includes('jazz piano'),'successful recent search affects suggestions');
 openSettings();$('feature-interests').value='culinária, ciência';$('feature-use-recent').checked=false;await featureSaveRecommendations.onclick();
 await loadRecommendations();assert(!$('status').textContent.includes('jazz piano'),'recent opt out');
 await featureClearSearches.onclick();closeSettings();
 const state=await api('local-state',{});assert(state.recommendation_preferences.interests.includes('ciência'),'preferences persisted');
 window.webkit.messageHandlers.recommendationscheck.postMessage(JSON.stringify({ok:true,categories:4,items:20}));
})().catch(error=>window.webkit.messageHandlers.recommendationscheck.postMessage(JSON.stringify({error:String(error),stack:error.stack})));'''.replace('CATALOG',json.dumps(catalog))
def receive(_manager,result):
 value=json.loads(result.get_js_value().to_string());print(json.dumps(value),flush=True)
 if 'error' in value:errors.append(value)
 else:completed.append(True)
 Gtk.main_quit()
manager.connect('script-message-received::recommendationscheck',receive)
view.connect('load-changed',lambda _view,event:view.run_javascript(script,None,None,None) if event==WebKit2.LoadEvent.FINISHED else None)
view.load_uri(f'http://127.0.0.1:{server.server_port}/{token}/');window.show_all();GLib.timeout_add_seconds(20,lambda:Gtk.main_quit() or False);Gtk.main();window.destroy();server.shutdown();server.server_close()
assert not local_library.recommendation_profile()['recent'];profile.cleanup()
if errors or not completed:raise SystemExit('Recommendation UI FAILED '+str(errors))
print('GTK personalized recommendations PASS: all tabs, interests, recent search, opt out, clear history')
