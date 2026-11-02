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
 def received(_manager,result):
  data=json.loads(result.get_js_value().to_string())
  if 'evidence' in data:
   print(json.dumps(data['evidence'],ensure_ascii=False),flush=True)
   evidence_dir=os.environ.get('GAME_RESIZE_EVIDENCE')
   if evidence_dir and data['evidence']['requested']==[500,320]:
    destination=Path(evidence_dir)/(data['evidence']['game']+'.png')
    def capture(view,result,*_):
     try:view.get_snapshot_finish(result).write_to_png(str(destination))
     except Exception as error:errors.append(str(error))
    view.get_snapshot(WebKit2.SnapshotRegion.VISIBLE,WebKit2.SnapshotOptions.NONE,None,capture,None)
   return
  if 'resize' in data:
   window.resize(*data['resize']);return
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
 const panel=document.getElementById('runner');
 for(const game of ['runner','maze','invaders','asteroids','breaker','lander']){
  document.querySelector('.game-card[data-game="'+game+'"]').click();
  window.orbitzToggleControls();await wait(1050);
  check(document.body.classList.contains('controls-hidden'),game+' hidden');
  window.orbitzFitPlayer();
  for(const size of [[620,380],[800,540],[500,320]]){
   window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({resize:size}));await wait(300);
   const r=panel.getBoundingClientRect(),o=document.getElementById('player-resize-overlay').getBoundingClientRect();
   check(r.height>200&&Math.abs(r.height-innerHeight)<3,game+' fills resized hidden window: '+r.height+'/'+innerHeight);
   check(Math.abs(o.height-r.height)<2&&Math.abs(o.width-r.width)<2,game+' overlay follows content');
   const c=document.getElementById(game==='runner'?'runner-canvas':game+'-canvas');
   check(c.width>100&&c.height>100,game+' canvas remains sized');
   const pixels=c.getContext('2d').getImageData(0,0,c.width,c.height).data;check(pixels.some((v,i)=>i%4===3&&v>0),game+' canvas remains drawn');
   check(window.orbitzResizeActive()&&window.orbitzGamePaused(),game+' resize remains paused');window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({evidence:{game,requested:size,viewport:[innerWidth,innerHeight],content:[r.width,r.height],canvas:[c.width,c.height],hidden:document.body.classList.contains('controls-hidden'),overlay:window.orbitzResizeActive(),paused:window.orbitzGamePaused(),drawn:true}}));await wait(250);
  }
  window.orbitzFitPlayer();window.orbitzToggleControls();await wait(1050);
  check(panel.getBoundingClientRect().height>100,game+' visible after restoring controls');
  document.getElementById('home-logo').click();
 }
 window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({ok:true}));
 }catch(error){window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({error:String(error)}))}})()''',None,None,None)
 return False
if os.environ.get('HOME_TEST_NARROW'):
 GLib.timeout_add(500,lambda:(Gio.Application.get_default().get_windows()[0].resize(420,640),False)[1])
GLib.timeout_add(3000,check)
GLib.timeout_add(45000,lambda:(errors.append('timeout'),Gio.Application.get_default().quit(),False)[-1])
source=(root/'app/youtube-wrapper.py').read_text().replace("application_id='io.orbitz.YouTubeDesktop'","application_id='io.orbitz.YouTubeDesktop.MazeTest'")
exec(compile(source,str(root/'app/youtube-wrapper.py'),'exec'),{'__name__':'__main__'})
assert done and not errors,errors
print('OK: all six games remain drawn and fill the hidden window through three actual native resizes.')
