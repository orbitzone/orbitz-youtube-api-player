"""Actual session-bus MPRIS smoke with a temporary name and synthetic metadata."""
from pathlib import Path
import subprocess,sys,threading
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
import media_controls as media
media.NAME+='.Test'
class View:
    def __init__(self):self.commands=[]
    def run_javascript(self,script,*_):self.commands.append(script)
window=Gtk.Window(title='Teste temporário de mídia');view=View();player=media.MediaControls(window,view)
player.update(dict(id='abcdefghijk',title='Synthetic MPRIS',position=42,duration=300,status='Playing',volume=.7,next=True))
errors=[];finished=[]
def run():
 try:
  base=['gdbus','call','--session','--dest',media.NAME,'--object-path',media.PATH,'--method']
  result=subprocess.check_output(base+['org.freedesktop.DBus.Properties.GetAll',media.PLAYER],text=True,timeout=5)
  assert 'Synthetic MPRIS' in result and 'Playing' in result,result
  subprocess.check_output(base+[media.PLAYER+'.PlayPause'],timeout=5)
  track='/io/orbitz/track/'+'abcdefghijk'.encode().hex()
  subprocess.check_output(base+[media.PLAYER+'.SetPosition',track,'60000000'],timeout=5)
  assert any('playpause' in command for command in view.commands),view.commands
  assert any('position' in command and '60.0' in command for command in view.commands),view.commands
  print('MPRIS real D-Bus PASS: discovery, properties, PlayPause, SetPosition',flush=True)
  finished.append(True)
 except Exception as error:errors.append(str(error))
 GLib.idle_add(lambda:Gtk.main_quit() or False)
def start():threading.Thread(target=run,daemon=True).start();return False
window.show_all();GLib.timeout_add(500,start);GLib.timeout_add_seconds(10,lambda:Gtk.main_quit() or False);Gtk.main();window.destroy()
if errors or not finished:raise SystemExit('MPRIS FAILED '+str(errors))
