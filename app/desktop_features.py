"""User-triggered file transfer and diagnostics; no continuous monitoring."""
import json
import os
from pathlib import Path
import platform
import tempfile
import local_library
from app_version import VERSION


def transfer(window,Gtk,data):
    mode=data.get('mode')
    if mode not in ('import','export'):raise ValueError('Invalid transfer mode')
    from ui_language import ui
    dialog=Gtk.FileChooserNative.new(ui.tr('youtube.'+mode+'_library'),window,Gtk.FileChooserAction.OPEN if mode=='import' else Gtk.FileChooserAction.SAVE,ui.tr('youtube.choose_file'),ui.tr('youtube.cancel'))
    file_filter=Gtk.FileFilter();file_filter.set_name('JSON');file_filter.add_pattern('*.json');dialog.add_filter(file_filter)
    if mode=='export':dialog.set_current_name('youtube-library.json');dialog.set_do_overwrite_confirmation(True)
    try:
        if dialog.run()!=Gtk.ResponseType.ACCEPT:return {'cancelled':True}
        filename=dialog.get_filename()
        if not filename:return {'cancelled':True}
        path=Path(filename)
        if mode=='import':
            with path.open('rb') as stream:raw=stream.read(4194305)
            if len(raw)>4194304:raise ValueError('File too large')
            return local_library.import_library(json.loads(raw))
        payload=json.dumps(local_library.export_library(),ensure_ascii=False,indent=2)
        try:fd,temporary=tempfile.mkstemp(prefix='.youtube-export-',dir=path.parent)
        except PermissionError:
            # Document portals may authorize only the selected filename, not
            # temporary siblings. The chooser has already confirmed overwrite.
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'w') as stream:
                stream.write(payload);stream.flush();os.fsync(stream.fileno())
            return {'exported':True}
        try:
            with os.fdopen(fd,'w') as stream:
                stream.write(payload)
                stream.flush();os.fsync(stream.fileno())
            os.replace(temporary,path)
        finally:
            if os.path.exists(temporary):os.unlink(temporary)
        return {'exported':True}
    finally:dialog.destroy()


def diagnostics(Gtk,WebKit2):
    import gi
    gi.require_version('Gst','1.0')
    from gi.repository import Gst,GLib
    Gst.init(None)
    return dict(application='YouTube API Player - By Orbitz',version=VERSION,python=platform.python_version(),gtk='.'.join(map(str,(Gtk.get_major_version(),Gtk.get_minor_version(),Gtk.get_micro_version()))),webkit='.'.join(map(str,(WebKit2.get_major_version(),WebKit2.get_minor_version(),WebKit2.get_micro_version()))),glib='.'.join(map(str,(GLib.MAJOR_VERSION,GLib.MINOR_VERSION,GLib.MICRO_VERSION))),gpu_access=any(os.access(path,os.R_OK|os.W_OK) for path in Path('/dev/dri').glob('renderD*')),hardware_decoders={name:bool(Gst.ElementFactory.find(name)) for name in ('vah264dec','vah265dec','vavp9dec','vaav1dec')},mpris='org.mpris.MediaPlayer2.orbitz_youtube_wrapper',note='Decoder availability does not identify the codec used by the current video.')
