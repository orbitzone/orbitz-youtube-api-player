"""Persist native window bounds independently of the API key and game record."""
import json
import logging
import os
from pathlib import Path
import tempfile

GEOMETRY_FILE=Path(os.environ.get('XDG_CONFIG_HOME',Path.home()/'.config'))/'orbitz-youtube-wrapper'/'window.json'


def valid_geometry(value):
    return (isinstance(value,dict) and type(value.get('version')) is int and value['version']==1 and
        all(type(value.get(key)) is int and -1_000_000<=value[key]<=1_000_000 for key in ('x','y')) and
        all(type(value.get(key)) is int and 1<=value[key]<=32768 for key in ('width','height')) and
        type(value.get('maximized')) is bool)


def read_geometry():
    try:
        fd=os.open(GEOMETRY_FILE,os.O_RDONLY|os.O_NOFOLLOW)
        with os.fdopen(fd) as stream:value=json.loads(stream.read(4096))
        return value if valid_geometry(value) else None
    except (OSError,ValueError,TypeError):return None


def save_geometry(value):
    if not valid_geometry(value):raise ValueError('Invalid window geometry')
    GEOMETRY_FILE.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,temporary=tempfile.mkstemp(prefix='.window-',suffix='.tmp',dir=GEOMETRY_FILE.parent)
    try:
        with os.fdopen(fd,'w') as stream:
            os.fchmod(stream.fileno(),0o600);json.dump(value,stream)
            stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,GEOMETRY_FILE)
    finally:
        try:os.unlink(temporary)
        except FileNotFoundError:pass


def visible_geometry(value,areas):
    """Recover unusable bounds and keep the full window on a reachable monitor."""
    if not areas:return dict(value)
    area=next((a for a in areas if value['x']<a.x+a.width and value['x']+value['width']>a.x and value['y']<a.y+a.height and value['y']+value['height']>a.y),areas[0])
    width=min(area.width,max(min(420,area.width),value['width']))
    height=min(area.height,max(min(280,area.height),value['height']))
    return {**value,'x':max(area.x,min(value['x'],area.x+area.width-width)),
        'y':max(area.y,min(value['y'],area.y+area.height-height)),'width':width,'height':height}


class GeometryTracker:
    def __init__(self,window,Gtk,Gdk,GLib,areas):
        self.window=window;self.Gtk=Gtk;self.Gdk=Gdk;self.GLib=GLib
        saved=read_geometry();self.saved=visible_geometry(saved,areas) if saved else None
        self.last=self.saved;self.written=saved;self.restoring=bool(self.saved)
        self.alive=True;self.save_source=0;self.restore_source=0;self.attempts=0
        window.connect('configure-event',self.configured)
        window.connect('window-state-event',self.configured)
        window.connect('map-event',self.mapped)
        window.connect('delete-event',self.close_requested)
        window.connect('destroy',self.destroyed)

    def prepare(self):
        if not self.saved:return False
        value=self.saved
        self.window.set_position(self.Gtk.WindowPosition.NONE)
        self.window.set_gravity(self.Gdk.Gravity.NORTH_WEST)
        self.window.set_default_size(value['width'],value['height'])
        self.window.move(value['x'],value['y'])
        return True

    def mapped(self,*_):
        if self.restoring and not self.restore_source:self.restore_source=self.GLib.timeout_add(80,self.restore)
        return False

    def restore(self):
        if not self.alive:self.restore_source=0;return False
        native=self.window.get_window()
        if native is None:return True
        target=self.saved;frame=native.get_frame_extents();width,height=self.window.get_size()
        self.attempts+=1
        exact=(frame.x,frame.y,frame.width,frame.height)==(target['x'],target['y'],target['width'],target['height'])
        if exact or self.attempts>=8:
            self.restoring=False;self.restore_source=0
            if target['maximized']:self.window.maximize()
            self.configured();return False
        # Persisted bounds include the WM title bar/borders. Measure current
        # extents instead of assuming a theme-dependent decoration height.
        border_width=max(0,frame.width-width);border_height=max(0,frame.height-height)
        self.window.resize(max(1,target['width']-border_width),max(1,target['height']-border_height))
        self.window.move(target['x'],target['y'])
        return True

    def snapshot(self):
        native=self.window.get_window()
        if not native:return None
        state=native.get_state()
        if state & self.Gdk.WindowState.FULLSCREEN:return self.last
        if state & self.Gdk.WindowState.MAXIMIZED:
            return {**self.last,'maximized':True} if self.last else None
        frame=native.get_frame_extents()
        value=dict(version=1,x=frame.x,y=frame.y,width=frame.width,height=frame.height,maximized=False)
        return value if valid_geometry(value) and frame.width>=96 and frame.height>=96 else None

    def configured(self,*_):
        if not self.alive or self.restoring:return False
        value=self.snapshot()
        if value is None:return False
        changed=value!=self.last
        self.last=value
        # Duplicate configure/state notifications must not restart the debounce
        # or wake a flush when these exact bounds are already persisted.
        if not changed and (self.save_source or value==self.written):return False
        if self.save_source:self.GLib.source_remove(self.save_source)
        self.save_source=self.GLib.timeout_add(250,self.flush)
        return False

    def flush(self):
        if self.save_source:self.GLib.source_remove(self.save_source);self.save_source=0
        if self.alive and not self.restoring:
            value=self.snapshot()
            if value:self.last=value
        if self.last and self.last!=self.written:
            try:save_geometry(self.last);self.written=dict(self.last)
            except OSError:logging.warning('Could not persist YouTube window position and size')
        return False

    def close_requested(self,*_):
        self.flush();return False

    def destroyed(self,*_):
        self.alive=False;self.flush()
        if self.restore_source:self.GLib.source_remove(self.restore_source);self.restore_source=0
