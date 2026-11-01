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
  if data.get('error'):errors.append(data['error'])
  else:done.append(True)
  def snapshot(view,result,*_):
   try:view.get_snapshot_finish(result).write_to_png(os.environ.get('MAZE_SNAPSHOT','/tmp/youtube-maze-preview.png'))
   except Exception as error:print('Snapshot:',error)
   app.quit()
  view.get_snapshot(WebKit2.SnapshotRegion.VISIBLE,WebKit2.SnapshotOptions.NONE,None,snapshot,None)
 manager.connect('script-message-received::mazetest',received)
 view.run_javascript('''(()=>{try{
 const check=(v,m)=>{if(!v)throw Error(m)};
 const home=document.getElementById('games-home'),cards=[...home.querySelectorAll('.game-card')];
 check(window.orbitzGamesHome&&!home.hidden,'starts on home');check(cards.length===6,'four cards');
 check(home.querySelectorAll('canvas[data-static-preview]').length===6,'real game miniature canvases');check(!home.querySelector('svg,video,audio,animate,animateTransform'),'no separate illustrations or active media');for(const card of cards){const c=card.querySelector('canvas');check(c.width>=740&&c.height>=140,'miniature resolution');const pixels=c.getContext('2d').getImageData(0,0,c.width,c.height).data;check(pixels.some((value,i)=>i%4===3&&value>0),'scene drawn');}
 for(const card of cards){const title=card.querySelector('strong'),cr=card.getBoundingClientRect(),tr=title.getBoundingClientRect(),cv=card.querySelector('canvas').getBoundingClientRect();check(!card.querySelector('small'),'no play label');check(Math.abs((cr.left+cr.right-tr.left-tr.right)/2)<1,'title centered horizontally');check(Math.abs((cr.top+cr.bottom-tr.top-tr.bottom)/2)<1,'title centered vertically');check(getComputedStyle(title).fontFamily.includes('Orbitron'),'Orbitron title');check(Math.abs(cv.width-(cr.width-2))<1&&Math.abs(cv.height-(cr.height-2))<1,'scene fills card')}
 const columns=getComputedStyle(home.querySelector('.games-home-grid')).gridTemplateColumns.split(' ').length;check(columns===(innerWidth<=480?1:innerWidth>=1200?3:2),'responsive columns');
 const resume=document.getElementById('feature-resume');check(resume.querySelector('.feature-resume-thumb'),'resume thumbnail');check(document.getElementById('keep-watching-title').textContent==='Keep Watching','section title');check(resume.querySelectorAll('button').length===1,'no dismiss button');check(resume.querySelector('button').textContent==='Continue assistindo','consistent continue label');check(home.contains(resume),'resume belongs to home layout');check(resume.getBoundingClientRect().bottom<=cards[0].getBoundingClientRect().top,'resume does not overlap cards');
 check(resume.querySelector('.feature-resume-thumb').src.includes('abcdefghijk'),'thumbnail matches last video');
 document.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowUp',shiftKey:true,bubbles:true}));check(window.orbitzGamesHome,'home ignores gameplay switching');
 for(const card of cards){card.click();check(!window.orbitzGamesHome,'card opens game');check(window.orbitzGameMode===card.dataset.game,'correct game');for(const canvas of home.querySelectorAll('canvas'))canvas.width=canvas.width;document.getElementById('games-home-back').click();check(window.orbitzGamesHome,'returns home');for(const canvas of home.querySelectorAll('canvas')){const pixels=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;check(pixels.some((value,i)=>i%4===3&&value>0),'previews redrawn after return with unchanged dimensions')}}
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
print('OK: static 2x2 home cards, game selection/return and resume thumbnail.')
