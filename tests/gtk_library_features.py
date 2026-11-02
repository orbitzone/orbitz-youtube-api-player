"""Real WebKit DOM + authenticated HTTP + disposable SQLite; no YouTube/network/key."""
import json
import os
from pathlib import Path
import secrets
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer

root=Path(__file__).resolve().parents[1]
profile=tempfile.TemporaryDirectory(prefix='youtube-features-smoke-')
os.environ['XDG_CONFIG_HOME']=profile.name
os.environ['XDG_CACHE_HOME']=profile.name
os.environ['GSETTINGS_BACKEND']='memory'
sys.path.insert(0,str(root/'app'))
import youtube_server as backend
backend.recommendations=lambda *args:{'items':[],'basis':'popular','terms':[]}
import local_library
local_library.action({'op':'preferences','values':{'always_above':True}})
local_library.action({'op':'progress','video':{'id':'abcdefghijk','title':'Synthetic resume'},'position':42,'duration':300})
import gi
gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,GLib,WebKit2,Gdk
token=secrets.token_urlsafe(24);server=ThreadingHTTPServer(('127.0.0.1',0),backend.make_handler(token));server.cache={};server.daemon_threads=True
server.ui_actions={'window-state':lambda data:None,'always-above':lambda data:None,'media-state':lambda data:None,'diagnostics':lambda data:{'synthetic':True}}
threading.Thread(target=server.serve_forever,daemon=True).start()
manager=WebKit2.UserContentManager();manager.register_script_message_handler('check')
view=WebKit2.WebView(user_content_manager=manager);window=Gtk.Window(title='Biblioteca — teste temporário');window.set_default_size(int(os.environ.get('ORBITZ_TEST_WIDTH','980')),int(os.environ.get('ORBITZ_TEST_HEIGHT','650')));window.add(view)
errors=[];finished=[]
catalog=json.loads((root/'i18n/pt-BR.json').read_text())
script='''(async()=>{
 const assert=(condition,message)=>{if(!condition)throw Error(message)};
 const wait=()=>new Promise(resolve=>setTimeout(resolve,100));
 featureThumb=item=>{const placeholder=document.createElement('div');placeholder.className='feature-thumb';placeholder.style.background='linear-gradient(135deg,#324660,#172535)';return placeholder};
 window.orbitzSetLanguage({locale:'pt-BR',catalog:CATALOG});
 for(let i=0;i<30&&(!featureState.resume||!alwaysAbove);i++)await wait();
 assert(!$('feature-resume').hidden,'resume offer on startup');
 featureDismissResume();assert($('feature-resume').hidden,'not now hides only this opening');assert((await api('local-state',{})).resume,'not now never deletes previous video');featureResumeDismissed=false;featureRender();assert(!$('feature-resume').hidden,'next opening can offer same video again');assert(alwaysAbove,'saved preferences restored');
 playerReady=true;let position=42;
 youtubePlayer={getVideoData:()=>({video_id:selected,title:'Synthetic player'}),getCurrentTime:()=>position,getDuration:()=>300,getVolume:()=>70,isMuted:()=>false,getPlayerState:()=>2,playVideo(){},pauseVideo(){},seekTo(value){position=value}};
 play=(id,title)=>{window.orbitzBeforeVideo();selected=id;window.orbitzOnVideo(id,title);$('screen').hidden=false;$('runner').hidden=true;};
 featurePlay(featureState.resume,42);assert(window.orbitzVideoStart(selected)===42,'resume position consumed once');assert(window.orbitzVideoStart(selected)===0,'resume cannot leak');
 $('query').focus();featureOpen();featurePlay({id:'abcdefghijk',title:'Selected from library'});assert($('discovery').hidden,'playback does not restore search focus or reopen discovery');
 featureOpen();await featureSave('favorites');await featureSave('later');
 assert(featureState.favorites.length===1&&featureState.later.length===1,'both bookmark lists');
 await featureQueue({id:'123456789_-',title:'Next synthetic'});assert(featureState.queue.length===1,'queue append');
 const current=selected;assert(current==='abcdefghijk','queue does not interrupt playback');
 featureView='queue';featureRender();assert(document.querySelectorAll('.feature-row').length===1,'queue row rendered');
 await featureNext();assert(selected==='123456789_-','next consumes queue');assert(featureState.queue.length===0,'queue persisted');
 window.orbitzMediaCommand('seek',10);assert(position===52,'seek command');
 renderResults([{id:'abcdefghijk',title:'Queued from search',channel:'Synthetic',thumbnail:''}]);$('results').querySelector('.feature-result-queue').click();await wait();await featureChain;assert(featureState.queue.length===1&&selected==='123456789_-','search queue button does not interrupt');
 featureOpen('diagnostics');await wait();assert($('feature-diagnostics').textContent.includes('synthetic'),'diagnostics on demand');
 featureOpen('shortcuts');assert($('feature-list').textContent.includes('Ctrl+'),'shortcut help');
 featureClose();
 window.orbitzSetLanguage({locale:'en-US',catalog:ENGLISH});assert(featureHeader.getAttribute('aria-label')==='Library','live language bindings');
 featurePlay(featureState.favorites[0]);await featureChain;featureOpen('favorites');
 const star=$('feature-current-actions').querySelector('button');assert(star.getAttribute('aria-pressed')==='true','current favorite visibly marked');star.focus();star.click();await wait();await featureChain;assert(document.activeElement===$('feature-current-actions').querySelector('button'),'focus retained after favorite mutation');assert(featureState.favorites.length===0,'star removes favorite');
 $('feature-current-actions').querySelector('button').click();await wait();await featureChain;assert(featureState.favorites.length===1,'star saves favorite without extra buttons');
 const action=$('feature-list').querySelector('.feature-icon-button:last-child');action.click();await wait();
 assert(!featurePopup.hidden,'row actions open as dropdown');assert(featurePopup.querySelectorAll('button').length===2,'compact row menu exposes queue/remove');
 featurePopup.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true,cancelable:true}));assert(document.activeElement===featurePopup.querySelectorAll('button')[1],'menu arrow navigation');
 featurePopup.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));assert(featurePopup.hidden&&!featurePanel.hidden,'Escape closes dropdown before panel');
 $('feature-transfer').querySelector('button').click();await wait();assert(featurePopup.querySelectorAll('button').length===2,'Manage groups import/export');featureCloseMenu();
 assert($('feature-current-actions').querySelectorAll('button').length===2,'only two compact current-video actions');
 assert($('feature-transfer').querySelectorAll('button').length===1,'import/export grouped into Manage');
 const dialog=featurePanel.querySelector('.modal-card').getBoundingClientRect();assert(dialog.top>=0&&dialog.bottom<=innerHeight&&dialog.left>=0&&dialog.right<=innerWidth,'dialog contained');assert($('settings').getBoundingClientRect().right<=innerWidth,'header fits');
 await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
 window.webkit.messageHandlers.check.postMessage(JSON.stringify({ok:true,viewport:[innerWidth,innerHeight],bookmarks:featureState.favorites.length}));
})().catch(error=>window.webkit.messageHandlers.check.postMessage(JSON.stringify({error:String(error),stack:error.stack})));'''.replace('CATALOG',json.dumps(catalog)).replace('ENGLISH',json.dumps(json.loads((root/'i18n/en-US.json').read_text())))
def receive(_manager,result):
 data=json.loads(result.get_js_value().to_string());print(json.dumps(data),flush=True)
 if 'error' in data:errors.append(data)
 else:
  finished.append(True)
  def capture():
   pixbuf=Gdk.pixbuf_get_from_window(window.get_window(),0,0,*window.get_size())
   pixbuf.savev(os.environ.get('ORBITZ_TEST_OUTPUT','/tmp/youtube-library-smoke.png'),'png',[],[])
   Gtk.main_quit();return False
  GLib.timeout_add(500,capture)
 if errors:Gtk.main_quit()
manager.connect('script-message-received::check',receive)
view.connect('load-changed',lambda _v,event:view.run_javascript(script,None,None,None) if event==WebKit2.LoadEvent.FINISHED else None)
view.load_uri(f'http://127.0.0.1:{server.server_port}/{token}/');window.show_all();GLib.timeout_add_seconds(15,lambda:Gtk.main_quit() or False);Gtk.main();window.destroy();server.shutdown();server.server_close();profile.cleanup()
if errors or not finished:raise SystemExit('Features smoke failed: '+str(errors))
print('GTK library features PASS')
