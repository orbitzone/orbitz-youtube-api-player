"""Real GTK multiwindow lifecycle with isolated data and synthetic recommendations."""
import os
from pathlib import Path
import sys
import tempfile
root=Path(__file__).resolve().parents[1]
profile=tempfile.TemporaryDirectory(prefix='youtube-multiwindow-')
os.environ['XDG_CONFIG_HOME']=profile.name
os.environ['XDG_CACHE_HOME']=profile.name
os.environ['GSETTINGS_BACKEND']='memory'
sys.path.insert(0,str(root/'app'))
import youtube_server
youtube_server.recommendations=lambda *args:{'items':[],'basis':'popular','terms':[]}
import media_controls
media_controls.NAME+='.MultiwindowTest'
import gi
gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,GLib,Gio
errors=[]
finished=[]

def check():
    app=Gio.Application.get_default()
    try:
        assert len(app.get_windows())==1
        first=app.get_windows()[0]
        app.activate_action('new-window',None)
        assert len(app.get_windows())==2
        second=next(w for w in app.get_windows() if w is not first)
        assert first.get_child() is not second.get_child()
        assert first.get_child().get_uri()!=second.get_child().get_uri()
        first.close()
        GLib.timeout_add(500,check_remaining)
    except Exception as error:
        import traceback;traceback.print_exc();errors.append(repr(error));app.quit()
    return False
def check_remaining():
    app=Gio.Application.get_default()
    try:
        assert len(app.get_windows())==1
        app.activate_action('new-window',None)
        assert len(app.get_windows())==2
        finished.append(True)
        for window in list(app.get_windows()):window.close()
    except Exception as error:
        errors.append(repr(error));app.quit()
    return False
GLib.timeout_add(2500,check)
source=(root/'app/youtube-wrapper.py').read_text().replace("application_id='io.orbitz.YouTubeDesktop'","application_id='io.orbitz.YouTubeDesktop.MultiwindowTest'")
exec(compile(source,str(root/'app/youtube-wrapper.py'),'exec'),{'__name__':'__main__'})
assert finished and not errors,errors
print('OK: independent windows, per-window media registration, close and reopen lifecycle.')
