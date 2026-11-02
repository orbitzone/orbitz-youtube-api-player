"""Full app lifecycle smoke in a disposable profile and a separate application ID."""
import os
from pathlib import Path
import sys,tempfile,json
root=Path(__file__).resolve().parents[1]
profile=tempfile.TemporaryDirectory(prefix='youtube-desktop-smoke-')
os.environ['XDG_CONFIG_HOME']=profile.name;os.environ['XDG_CACHE_HOME']=profile.name;os.environ['GSETTINGS_BACKEND']='memory'
sys.path.insert(0,str(root/'app'))
import youtube_server
# No provider request, personal key or personal database.
youtube_server.recommendations=lambda *args:{'items':[],'basis':'popular','terms':[]}
import local_library
local_library.action({'op':'preferences','values':{'always_above':True}})
import media_controls
media_controls.NAME+='.Test'
import gi
gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,GLib
errors=[];completed=[]
def check():
 windows=[window for window in Gtk.Window.list_toplevels() if window.get_title()=='YouTube API Player - By Orbitz']
 if not windows:return True
 window=windows[0];view=window.get_child();manager=view.get_user_content_manager();manager.register_script_message_handler('desktopcheck')
 def receive(_manager,result):
  data=json.loads(result.get_js_value().to_string());print(json.dumps(data),flush=True)
  if 'error' in data:errors.append(data)
  else:completed.append(True)
  window.close()
 manager.connect('script-message-received::desktopcheck',receive)
 view.run_javascript('''(async()=>{
 const assert=(v,m)=>{if(!v)throw Error(m)};
 assert(alwaysAbove,'persistent toggles restored in native app');
 assert(autoHideDelay===3000&&autoShowDelay===800,'persistent delays');
 const d=await api('diagnostics',{});assert(d.webkit&&typeof d.gpu_access==='boolean','native diagnostics');
 await api('media-state',{id:'abcdefghijk',title:'Synthetic native',position:42,duration:300,status:'Paused',volume:.7,next:false});
 window.webkit.messageHandlers.desktopcheck.postMessage(JSON.stringify({ok:true,webkit:d.webkit,gpu:d.gpu_access}));
 })().catch(error=>window.webkit.messageHandlers.desktopcheck.postMessage(JSON.stringify({error:String(error)})));''',None,None,None)
 return False
GLib.timeout_add_seconds(3,check)
def timeout():
 errors.append('Timed out')
 for window in Gtk.Window.list_toplevels():window.destroy()
 return False
source=(root/'app/youtube-wrapper.py').read_text().replace("application_id='io.orbitz.YouTubeDesktop'","application_id='io.orbitz.YouTubeDesktop.Test'")
GLib.timeout_add_seconds(12,timeout)
exec(compile(source,'desktop-smoke','exec'),{'__name__':'__main__'})
if completed:
 saved=local_library.action({});assert saved['resume']['position']==42;assert saved['preferences']['always_above']
profile.cleanup()
if errors or not completed:raise SystemExit('Desktop smoke failed '+str(errors))
print('Full GTK desktop PASS: restored native preferences, diagnostics, media state and close-time resume')
