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
 const soundButton=document.getElementById('game-sound');check(soundButton,'sound button');soundButton.click();check(soundButton.getAttribute('aria-pressed')==='true','sound enabled');soundButton.click();check(soundButton.getAttribute('aria-pressed')==='false','sound disabled');
 const slider=document.getElementById('game-volume');slider.value='35';slider.dispatchEvent(new Event('input'));check(slider.getAttribute('aria-valuetext')==='35%','volume adjusts');soundButton.click();check(slider.value==='0','mute to zero');soundButton.click();check(slider.value==='35','restore previous volume');
 const brand=document.getElementById('runner-brand'),br=brand.getBoundingClientRect(),sr=slider.getBoundingClientRect();check(br.top>sr.bottom,'link remains in footer');check(sr.height>sr.width,'vertical volume');check(Math.abs(br.right-document.getElementById('runner').getBoundingClientRect().right)<18,'link at right edge');check(getComputedStyle(brand).fontFamily.includes('Orbitron'),'Orbitron font');check(getComputedStyle(soundButton).borderTopWidth==='0px','border removed');
 slider.focus();check(getComputedStyle(slider).outlineStyle==='none','no volume focus border');slider.setPointerCapture=()=>{};slider.dispatchEvent(new PointerEvent('pointerdown',{pointerId:17,button:0,bubbles:true}));document.dispatchEvent(new PointerEvent('pointerup',{pointerId:17,bubbles:true}));check(document.activeElement===document.getElementById('runner-canvas'),'volume returns focus to runner');
 document.body.focus();press('Escape');check(window.orbitzGamePaused(),'runner pauses');
 document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',repeat:true,bubbles:true}));check(window.orbitzGamePaused(),'repeat does not resume');press('Escape');check(!window.orbitzGamePaused(),'runner resumes');
 press('ArrowUp',true);check(window.orbitzGameMode==='maze','switch to maze');
 check(!document.getElementById('maze-canvas').hidden,'maze canvas visible');check(!soundButton.hidden,'sound button available in maze');press('Escape');check(window.orbitzGamePaused(),'maze pauses');check(!document.getElementById('game-pause').hidden,'pause overlay');press('Escape');check(!window.orbitzGamePaused(),'maze resumes');press('ArrowLeft');
 press('ArrowDown',true);check(window.orbitzGameMode==='runner','switch back');
 const input=document.getElementById('query');input.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowUp',shiftKey:true,bubbles:true}));check(window.orbitzGameMode==='runner','ignore text fields');
 press('ArrowUp',true);check(window.orbitzGameMode==='maze','return to maze');
 const ctx=document.getElementById('maze-canvas').getContext('2d'),original=ctx.drawImage.bind(ctx);let frames=0;
 ctx.drawImage=(...args)=>{frames++;return original(...args)};press('ArrowLeft');
 setTimeout(()=>{try{
  check(frames>=5,'continuous rendering between tiles');check(frames<30,'bounded rendering');
  press('ArrowDown',true);
  setTimeout(()=>{const stopped=frames;setTimeout(()=>{try{
   check(frames===stopped,'hidden maze stops drawing');press('ArrowUp',true);
   window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({ok:true,frames}));
  }catch(error){window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({error:String(error)}))}},100)},50);
 }catch(error){window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({error:String(error)}))}},250);
 }catch(error){window.webkit.messageHandlers.mazetest.postMessage(JSON.stringify({error:String(error)}))}})()''',None,None,None)
 return False
GLib.timeout_add(3000,check)
GLib.timeout_add(15000,lambda:(errors.append('timeout'),Gio.Application.get_default().quit(),False)[-1])
source=(root/'app/youtube-wrapper.py').read_text().replace("application_id='io.orbitz.YouTubeDesktop'","application_id='io.orbitz.YouTubeDesktop.MazeTest'")
exec(compile(source,str(root/'app/youtube-wrapper.py'),'exec'),{'__name__':'__main__'})
assert done and not errors,errors
print('OK: real WebKit maze switching, start, runner return and editable-field exclusion.')
