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
  if data.get('error'):errors.append(data['error'])
  else:done.append(True)
  def snapshot(view,result,*_):
   try:view.get_snapshot_finish(result).write_to_png(os.environ.get('MAZE_SNAPSHOT','/tmp/youtube-maze-preview.png'))
   except Exception as error:print('Snapshot:',error)
   app.quit()
  view.get_snapshot(WebKit2.SnapshotRegion.VISIBLE,WebKit2.SnapshotOptions.NONE,None,snapshot,None)
 manager.connect('script-message-received::mazetest',received)
 view.run_javascript('''(()=>{try{
 window.orbitzOpenGame('runner');
 const check=(v,m)=>{if(!v)throw Error(m)};
 const press=(key,shift=false)=>document.dispatchEvent(new KeyboardEvent('keydown',{key,shiftKey:shift,bubbles:true}));
 const release=key=>document.dispatchEvent(new KeyboardEvent('keyup',{key,bubbles:true}));
 const report=error=>window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify(error?{error:String(error)}:{ok:true}));
 window.orbitzOpenGame('breaker');
 check(window.orbitzGameMode==='breaker','third game in cycle');const canvas=document.getElementById('breaker-canvas');check(!canvas.hidden,'breaker visible');
 const ctx=canvas.getContext('2d'),original=ctx.setTransform.bind(ctx);let frames=0;ctx.setTransform=(...args)=>{frames++;return original(...args)};
 press(' ');press('ArrowRight');
 setTimeout(()=>{try{
  release('ArrowRight');release(' ');check(frames>=4,'continuous rendering');press('Escape');check(window.orbitzGamePaused(),'breaker pause');
  setTimeout(()=>{const frozen=frames;setTimeout(()=>{try{
   check(frames===frozen,'no draws while paused');press('Escape');check(!window.orbitzGamePaused(),'resume');
   const slider=document.getElementById('game-volume');slider.focus();slider.setPointerCapture=()=>{};slider.dispatchEvent(new PointerEvent('pointerdown',{pointerId:21,button:0,bubbles:true}));document.dispatchEvent(new PointerEvent('pointerup',{pointerId:21,bubbles:true}));check(document.activeElement===canvas,'volume restores breaker focus');
   for(let i=0;i<6&&window.orbitzGameMode!=='runner';i++)press('ArrowUp',true);check(window.orbitzGameMode==='runner','cycle wraps to runner');
   setTimeout(()=>{const hiddenFrames=frames;setTimeout(()=>{try{
    check(frames===hiddenFrames,'hidden breaker stop drawing');for(let i=0;i<6&&window.orbitzGameMode!=='breaker';i++)press('ArrowDown',true);check(window.orbitzGameMode==='breaker','reverse cycle restores breaker');report();
   }catch(error){report(error)}},100)},50);
  }catch(error){report(error)}},100)},50);
 }catch(error){report(error)}},250);
 }catch(error){window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({error:String(error)}))}})()''',None,None,None)
 return False
GLib.timeout_add(3000,check)
GLib.timeout_add(15000,lambda:(errors.append('timeout'),Gio.Application.get_default().quit(),False)[-1])
source=(root/'app/youtube-wrapper.py').read_text().replace("application_id='io.orbitz.YouTubeDesktop'","application_id='io.orbitz.YouTubeDesktop.MazeTest'")
exec(compile(source,str(root/'app/youtube-wrapper.py'),'exec'),{'__name__':'__main__'})
assert done and not errors,errors
print('OK: fourth-game cycle, firing/movement, pause/resume, volume focus and hidden rendering.')
