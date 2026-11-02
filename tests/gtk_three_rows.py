"""Real game switching smoke with temporary profile and synthetic provider."""
import os
from pathlib import Path
import sys,tempfile,json
root=Path(__file__).resolve().parents[1]
profile=tempfile.TemporaryDirectory(prefix='youtube-maze-test-')
os.environ['XDG_CONFIG_HOME']=profile.name;os.environ['XDG_CACHE_HOME']=profile.name;os.environ['GSETTINGS_BACKEND']='memory'
sys.path.insert(0,str(root/'app'))
import youtube_server
youtube_server.recommendations=lambda *args:{'items':[],'basis':'popular','terms':[]}
import local_library
local_library.action({'op':'remember','video':{'id':'abcdefghijk','title':'Último vídeo de teste','channel':'Canal de teste'},'position':25,'duration':100})
import media_controls
media_controls.NAME+='.MazeTest'
import gi
gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,GLib,Gio,WebKit2
errors=[];done=[];body_frames=[];settled_frames={}
def check():
 app=Gio.Application.get_default();window=app.get_windows()[0];view=window.get_child();manager=view.get_user_content_manager();manager.register_script_message_handler('mazetest')
 # Disable physical pointer sampling so synthetic enter/leave is deterministic.
 def received(_manager,result):
  data=json.loads(result.get_js_value().to_string())
  if 'settled' in data:
   def settled_snapshot(view,result,*_):
    try:
     surface=view.get_snapshot_finish(result);surface.flush();raw=surface.get_data();stride=surface.get_stride();top=round(data['top']);bottom=round(data['bottom'])
     pixels=bytes(raw[:top*stride])+bytes(raw[bottom*stride:surface.get_height()*stride])
     samples=settled_frames.setdefault(data['settled'],[])
     if samples:assert pixels==samples[0],'chrome pixels changed after '+data['settled']+' transition finished'
     samples.append(pixels)
    except Exception as error:errors.append(str(error))
   view.get_snapshot(WebKit2.SnapshotRegion.VISIBLE,WebKit2.SnapshotOptions.NONE,None,settled_snapshot,None)
   return
  if 'frame' in data:
   def frame_snapshot(view,result,*_):
    try:
     surface=view.get_snapshot_finish(result);surface.flush();raw=surface.get_data();stride=surface.get_stride();top=round(data['frame']['top']);height=min(64,round(data['frame']['height']))
     pixels=bytes(raw[top*stride:(top+height)*stride])
     if body_frames:assert pixels==body_frames[0],'body pixels changed during chrome transition'
     body_frames.append(pixels)
    except Exception as error:errors.append(str(error))
   view.get_snapshot(WebKit2.SnapshotRegion.VISIBLE,WebKit2.SnapshotOptions.NONE,None,frame_snapshot,None)
   return
  if data.get('alpha'):
   def alpha_snapshot(view,result,*_):
    try:
     surface=view.get_snapshot_finish(result);surface.flush();pixels=surface.get_data();x=surface.get_width()//2
     assert pixels[2*surface.get_stride()+x*4+3]==0,'hidden header pixels must be transparent'
    except Exception as error:errors.append(str(error))
   view.get_snapshot(WebKit2.SnapshotRegion.VISIBLE,WebKit2.SnapshotOptions.NONE,None,alpha_snapshot,None)
   return
  if data.get('error'):errors.append(data['error'])
  else:done.append(True)
  def snapshot(view,result,*_):
   try:view.get_snapshot_finish(result).write_to_png(os.environ.get('MAZE_SNAPSHOT','/tmp/youtube-maze-preview.png'))
   except Exception as error:print('Snapshot:',error)
   app.quit()
  view.get_snapshot(WebKit2.SnapshotRegion.VISIBLE,WebKit2.SnapshotOptions.NONE,None,snapshot,None)
 manager.connect('script-message-received::mazetest',received)
 view.run_javascript('''(async()=>{try{
 const check=(v,m)=>{if(!v)throw Error(m)},wait=ms=>new Promise(r=>setTimeout(r,ms));
 const header=document.getElementById('app-header'),body=document.getElementById('app-body'),footer=document.querySelector('footer'),panel=document.getElementById('runner');
 document.activeElement.blur();for(const image of body.querySelectorAll('img'))image.style.visibility='hidden';await wait(100);const rect=body.getBoundingClientRect();const settled=async stage=>{for(let i=0;i<8;i++){window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({settled:stage,top:rect.top,bottom:rect.bottom}));await wait(35)}};const capture=()=>window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({frame:{top:rect.top,height:rect.height}}));capture();await wait(200);
 for(const node of [header,body,footer])check(Math.abs(node.getBoundingClientRect().width-innerWidth)<1,'full width rows');check(panel.getBoundingClientRect().left===0,'no side gap');
 check(getComputedStyle(header).transitionDuration==='0s'&&getComputedStyle(footer).transitionDuration==='0s','no CSS transition endpoint layer changes');
 window.orbitzChromePointer({inside:true,x:.5,y:0.01});await wait(550);check(!document.body.classList.contains('chrome-retracted'),'header space preserves revealed state');window.orbitzChromePointer({inside:true,x:.5,y:.99});await wait(80);check(!document.body.classList.contains('chrome-retracted'),'footer space preserves revealed state');window.orbitzChromePointer({inside:false,x:0,y:0});await wait(550);check(document.body.classList.contains('chrome-retracted'),'only leaving full application retracts');check(new DOMMatrix(getComputedStyle(footer).transform).m42<0,'footer is hidden above its row and reveals downward');check(getComputedStyle(document.body).backgroundColor==='rgba(0, 0, 0, 0)','transparent root');window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({alpha:true}));await wait(200);
 check(body.getBoundingClientRect().top===rect.top&&body.getBoundingClientRect().height===rect.height,'no content shift');await settled('hidden');window.orbitzChromePointer({inside:true,x:.5,y:0.01});await wait(80);check(document.body.classList.contains('chrome-retracted'),'entering header alone does not reveal');
 window.orbitzChromePointer({inside:true,x:.5,y:(rect.top+rect.height/2)/innerHeight});let lastY=-Infinity;for(let i=0;i<7;i++){await wait(70);capture();const y=new DOMMatrix(getComputedStyle(footer).transform).m42;check(y>=lastY-.1,'footer moves monotonically down: '+lastY+' -> '+y+' state='+document.body.className);lastY=y;check(getComputedStyle(document.getElementById('header-clip')).overflow==='hidden'&&getComputedStyle(document.getElementById('footer-clip')).overflow==='hidden','permanent animation masks');check(document.elementFromPoint(innerWidth/2,rect.top+10).closest('#app-body'),'body always above animation');check(body.getBoundingClientRect().top===rect.top,'stable body during animation')}await wait(100);check(!document.body.classList.contains('chrome-retracted'),'show over body');await settled('shown');
 window.orbitzChromePointer({inside:false,x:0,y:0});await wait(80);window.orbitzChromePointer({inside:true,x:.5,y:(rect.top+rect.height/2)/innerHeight});await wait(550);check(!document.body.classList.contains('chrome-retracted'),'rapid reversal settles shown');
 check(body.getBoundingClientRect().top===rect.top,'body still stable');window.orbitzChromePointer({inside:true,x:.5,y:(rect.top+rect.height/2)/innerHeight,idle:true});await wait(550);check(document.body.classList.contains('chrome-retracted'),'idle mouse retracts inside body');window.orbitzChromePointer({inside:true,x:.5,y:(rect.top+rect.height/2)/innerHeight,idle:false});await wait(550);check(!document.body.classList.contains('chrome-retracted'),'mouse movement reveals after idle');for(const id of ['settings-menu','discovery','config']){const panel=document.getElementById(id);panel.hidden=false;window.orbitzChromePointer({inside:false,x:0,y:0});await wait(550);check(document.body.classList.contains('chrome-retracted'),'window exit retracts even with '+id+' open');panel.hidden=true;window.orbitzChromePointer({inside:true,x:.5,y:(rect.top+rect.height/2)/innerHeight});await wait(550)}
 window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({ok:true}));
 }catch(error){window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({error:String(error)}))}})()''',None,None,None)
 return False
if os.environ.get('HOME_TEST_NARROW'):
 GLib.timeout_add(500,lambda:(Gio.Application.get_default().get_windows()[0].resize(420,640),False)[1])
GLib.timeout_add(3000,check)
GLib.timeout_add(22000,lambda:(errors.append('timeout'),Gio.Application.get_default().quit(),False)[-1])
source=(root/'app/youtube-wrapper.py').read_text().replace("application_id='io.orbitz.YouTubeDesktop'","application_id='io.orbitz.YouTubeDesktop.MazeTest'")
source=source.replace("chrome_watch.configure({'enabled':True,'sequence':0})","chrome_watch.reset()")
exec(compile(source,str(root/'app/youtube-wrapper.py'),'exec'),{'__name__':'__main__'})
assert done and not errors,errors
assert len(body_frames)>=8,'must verify body pixels throughout transition'
assert all(len(settled_frames.get(k,[]))==8 for k in ('hidden','shown')),'verify post-transition frames'
print('OK: full-width three-row layout, synchronized 0.5s transitions, pointer reversal and stable body.')
