"""Temporary real GTK close/reopen smoke, with a disposable geometry file."""
from pathlib import Path
import sys,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Gdk,GLib
import window_geometry as geometry
folder=tempfile.TemporaryDirectory();geometry.GEOMETRY_FILE=Path(folder.name)/'window.json'
display=Gdk.Display.get_default();areas=[display.get_monitor(i).get_workarea() for i in range(display.get_n_monitors())]
windows=[];results={};errors=[]
def build():
 window=Gtk.Window(title='Teste de restauração — temporário');window.add(Gtk.Label(label='Teste sintético de posição e tamanho'))
 tracker=geometry.GeometryTracker(window,Gtk,Gdk,GLib,areas)
 if not tracker.prepare():window.set_default_size(540,300)
 window.show_all();windows.append(window)
 return window,tracker
first,tracker=build()
def move_first():
 first.resize(602,334);first.move(areas[0].x+120,areas[0].y+90)
 GLib.timeout_add(400,close_first);return False
def close_first():
 frame=first.get_window().get_frame_extents()
 results['before']=(frame.x,frame.y,frame.width,frame.height)
 tracker.close_requested();first.destroy()
 second,other=build()
 def check():
  frame=second.get_window().get_frame_extents();results['after']=(frame.x,frame.y,frame.width,frame.height)
  print('Synthetic close/reopen geometry:',results,flush=True)
  if results['before']!=results['after']:errors.append('geometry differs')
  second.destroy();Gtk.main_quit();return False
 GLib.timeout_add(1000,check);return False
GLib.timeout_add(200,move_first);GLib.timeout_add_seconds(8,lambda:Gtk.main_quit() or False)
Gtk.main()
for window in windows:window.destroy()
folder.cleanup()
if errors or set(results)!={'before','after'}:raise SystemExit(str(errors)+str(results))
print('GTK close/reopen geometry PASS: identical x, y, outer width and outer height')
