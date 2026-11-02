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
errors=[];done=[]
def check():
 app=Gio.Application.get_default();window=app.get_windows()[0];view=window.get_child();manager=view.get_user_content_manager();manager.register_script_message_handler('mazetest')
 assert not window.get_decorated(),'native title bar must remain disabled'
 def received(_manager,result):
  data=json.loads(result.get_js_value().to_string())
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
 const bar=document.getElementById('window-bar');check(bar.getBoundingClientRect().height===34,'internal title bar');check(bar.querySelectorAll('button').length===3,'three window controls');check(document.querySelectorAll('.window-resize-edge').length===8,'all native resize grips');for(const [x,y,edge] of [[1,innerHeight/2,'w'],[innerWidth-1,innerHeight/2,'e'],[innerWidth/2,1,'n'],[innerWidth/2,innerHeight-1,'s'],[1,1,'nw'],[innerWidth-1,1,'ne'],[1,innerHeight-1,'sw'],[innerWidth-1,innerHeight-1,'se']])check(document.elementFromPoint(x,y).dataset.windowEdge===edge,'edge hit target '+edge);
 await sendWindowCommand('maximize');await wait(700);check(window.orbitzWindowLocked,'maximized');check(getComputedStyle(document.querySelector('.window-resize-edge')).display==='none','resize disabled when maximized');check(document.getElementById('window-maximize').dataset.maximized==='true','restore icon');check(document.getElementById('window-maximize').getAttribute('aria-label')==='Restaurar','restore label');await sendWindowCommand('maximize');await wait(900);check(!window.orbitzWindowLocked,'restored');check(document.getElementById('window-maximize').dataset.maximized==='false','maximize icon restored');check(getComputedStyle(document.querySelector('#window-maximize svg')).width==='12px','compact vector icon');
 window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({ok:true}));
 }catch(error){window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({error:String(error)}))}})()''',None,None,None)
 return False
if os.environ.get('HOME_TEST_NARROW'):
 GLib.timeout_add(500,lambda:(Gio.Application.get_default().get_windows()[0].resize(420,640),False)[1])
GLib.timeout_add(3000,check)
GLib.timeout_add(15000,lambda:(errors.append('timeout'),Gio.Application.get_default().quit(),False)[-1])
source=(root/'app/youtube-wrapper.py').read_text().replace("application_id='io.orbitz.YouTubeDesktop'","application_id='io.orbitz.YouTubeDesktop.MazeTest'")
exec(compile(source,str(root/'app/youtube-wrapper.py'),'exec'),{'__name__':'__main__'})
assert done and not errors,errors
print('OK: custom title bar, maximize/restore with native decorations disabled.')
