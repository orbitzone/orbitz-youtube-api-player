"""Regression: launch the desktop action, including its --new-window argument."""
import os
from pathlib import Path
import sys,tempfile
root=Path(__file__).resolve().parents[1]
profile=tempfile.TemporaryDirectory(prefix='youtube-desktop-action-')
os.environ['XDG_CONFIG_HOME']=profile.name;os.environ['XDG_CACHE_HOME']=profile.name;os.environ['GSETTINGS_BACKEND']='memory'
sys.path.insert(0,str(root/'app'))
import youtube_server
youtube_server.recommendations=lambda *args:{'items':[],'basis':'popular','terms':[]}
import media_controls
media_controls.NAME+='.DesktopActionTest'
import gi
gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,GLib,Gio
source=(root/'app/youtube-wrapper.py').read_text().replace("application_id='io.orbitz.YouTubeDesktop'","application_id='io.orbitz.YouTubeDesktop.DesktopActionTest'")
launcher=Path(profile.name)/'launcher.py'
launcher.write_text('import sys\nsys.path.insert(0,'+repr(str(root/'app'))+')\nexec(compile('+repr(source)+','+repr(str(root/'app/youtube-wrapper.py'))+",'exec'),{'__name__':'__main__'})\n")
desktop=Path(profile.name)/'test.desktop'
desktop.write_text('[Desktop Entry]\nType=Application\nName=Test\nExec=/usr/bin/python3 '+str(launcher)+'\nActions=new-window;\n[Desktop Action new-window]\nName=New Window\nExec=/usr/bin/python3 '+str(launcher)+' --new-window\n')
import window_geometry
window_geometry.save_geometry(dict(version=1,x=11,y=1120,width=1069,height=1,maximized=False))
errors=[];done=[]
def launch():
    app=Gio.Application.get_default()
    assert len(app.get_windows())==1
    Gio.DesktopAppInfo.new_from_filename(str(desktop)).launch_action('new-window',None)
    GLib.timeout_add(2000,verify)
    return False
def verify():
    app=Gio.Application.get_default()
    for window in app.get_windows():
        width,height=window.get_size()
        if width<420 or height<280:errors.append('Window restored with unusable dimensions')
    if len(app.get_windows())!=2:errors.append('Desktop action did not create the second window')
    else:done.append(True)
    for window in list(app.get_windows()):window.close()
    return False
GLib.timeout_add(1500,launch)
GLib.timeout_add(12000,lambda:(errors.append('timeout'),Gio.Application.get_default().quit(),False)[-1])
exec(compile(source,str(root/'app/youtube-wrapper.py'),'exec'),{'__name__':'__main__'})
assert done and not errors,errors
print('OK: desktop action launches --new-window into the existing application and creates a second window.')
