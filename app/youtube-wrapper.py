#!/usr/bin/python3
"""GTK/WebKit YouTube window and local server lifecycle."""
from http.server import ThreadingHTTPServer
from ui_language import ui
import json
import math
import re
import secrets
import sys
import threading
from urllib.parse import urlsplit
from youtube_server import make_handler
from window_geometry import GeometryTracker
from window_pointer import PointerWatch
import local_library
import desktop_features

ALLOWED_EXTERNAL_HOSTS = frozenset({
    'www.youtube.com',
    'www.orbit.zone',
    'console.cloud.google.com',
})

def is_allowed_external_uri(uri):
    """Limit the local app action to approved external destinations."""
    try:
        parsed = urlsplit(uri)
        if (parsed.scheme != 'https' or parsed.hostname not in ALLOWED_EXTERNAL_HOSTS
                or parsed.username is not None or parsed.password is not None
                or parsed.port not in (None, 443) or parsed.fragment):
            return False
        if parsed.hostname == 'www.youtube.com':
            return (parsed.path == '/' and not parsed.query) or (
                parsed.path == '/watch' and bool(re.fullmatch(r'v=[A-Za-z0-9_-]{11}', parsed.query)))
        if parsed.hostname == 'www.orbit.zone':
            return parsed.path == '/' and not parsed.query
        return parsed.path == '/apis/credentials' and not parsed.query
    except (AttributeError, TypeError, ValueError):
        return False

def target_window_height(state, workarea_height):
    """Return a compact, monitor-bounded height for a page layout state."""
    # Keep enough room for four search results even before the dropdown opens.
    preferred = {'idle': 520, 'settings': 320, 'panel': 520, 'player': 700}
    if state not in preferred:
        raise ValueError('Estado de janela inválido.')
    workarea_height=max(1,int(workarea_height))
    available = max(96, workarea_height - 64)
    return min(preferred[state], available, workarea_height)

def user_resized_from_target(current_height, target_height, programmatic=False):
    """Detect deliberate height changes without mistaking our resize for one."""
    return target_height is not None and not programmatic and abs(current_height-target_height)>8

def main():
    import gi
    gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
    from gi.repository import Gtk,WebKit2,Gio,Gdk,GLib
    app=Gtk.Application(application_id='io.orbitz.YouTubeDesktop',flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
    windows={}
    window_serial=0
    def activate(app):
        if windows:next(reversed(windows.values())).present();return
        create_window(app)
    def create_window(app):
        nonlocal window_serial
        instance=window_serial;window_serial+=1
        holder={}
        token=secrets.token_urlsafe(24)
        server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(token));server.cache={};server.daemon_threads=True
        threading.Thread(target=server.serve_forever,daemon=True).start()
        window=ui.widget(Gtk.ApplicationWindow,application=app,title=ui.msg('youtube.window_title'))
        window.set_decorated(False)
        visual=window.get_screen().get_rgba_visual()
        if visual:window.set_visual(visual)
        window.set_app_paintable(True)
        window.set_name('orbitz-player-window')
        transparent_css=Gtk.CssProvider();transparent_css.load_from_data(b'#orbitz-player-window { background-color: transparent; }')
        window.get_style_context().add_provider(transparent_css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        display=Gdk.Display.get_default()
        monitor=display.get_monitor_at_point(*display.get_default_seat().get_pointer().get_position()[1:]) or display.get_primary_monitor()
        area=monitor.get_workarea() if monitor else Gdk.Rectangle(x=0,y=0,width=1280,height=900)
        window.set_size_request(min(420,area.width),min(280,area.height))
        initial_height=target_window_height('idle',area.height)
        initial_width=min(1100,max(1,area.width-48))
        geometry=GeometryTracker(window,Gtk,Gdk,GLib,[display.get_monitor(i).get_workarea() for i in range(display.get_n_monitors())])
        if not geometry.prepare():
            window.set_position(Gtk.WindowPosition.CENTER)
            window.set_default_size(initial_width,initial_height)
        window.set_resizable(True)
        shortcut_state={'media_keys':set()}
        resize_state={'enabled':not bool(geometry.saved),'target':initial_height,'programmatic':False,'page':'idle','source':0}
        def window_size_locked():
            native=window.get_window()
            return bool(native and native.get_state() & (Gdk.WindowState.FULLSCREEN|Gdk.WindowState.MAXIMIZED))
        def workarea_height():
            try:
                screen=window.get_screen();index=screen.get_monitor_at_window(window.get_window())
                return screen.get_monitor_workarea(index).height
            except (AttributeError,TypeError,ValueError):
                return area.height
        def clear_programmatic(expected):
            if resize_state['target']==expected:resize_state['programmatic']=False
            return False
        def apply_page_size():
            resize_state['source']=0
            if not resize_state['enabled'] or window_size_locked():return False
            width,current=window.get_size();target=target_window_height(resize_state['page'],workarea_height())
            if user_resized_from_target(current,resize_state['target'],resize_state['programmatic']):
                resize_state['enabled']=False
                return False
            if abs(current-target)<=2:
                resize_state['target']=target
                return False
            resize_state['target']=target;resize_state['programmatic']=True
            window.resize(width,target)
            GLib.timeout_add(900,clear_programmatic,target)
            return False
        def request_page_size(state):
            if state not in ('idle','settings','panel','player'):return
            resize_state['page']=state
            if resize_state['source']:GLib.source_remove(resize_state['source'])
            resize_state['source']=GLib.timeout_add(90,apply_page_size)
        def configure_size(_window,event):
            if window_size_locked():return False
            if resize_state['programmatic']:
                if abs(event.height-resize_state['target'])<=3:resize_state['programmatic']=False
            elif resize_state['enabled'] and (user_resized_from_target(event.height,resize_state['target']) or event.width!=initial_width):
                resize_state['enabled']=False
            return False
        window.connect('configure-event',configure_size)
        def window_state_changed(_window,event):
            view.run_javascript('window.orbitzWindowLocked='+str(bool(event.new_window_state & (Gdk.WindowState.FULLSCREEN|Gdk.WindowState.MAXIMIZED))).lower()+';',None,None,None)
            view.run_javascript('window.orbitzWindowMaximized='+str(bool(event.new_window_state & Gdk.WindowState.MAXIMIZED)).lower()+';window.orbitzSyncWindowButtons?.();',None,None,None)
            if not event.new_window_state & (Gdk.WindowState.FULLSCREEN|Gdk.WindowState.MAXIMIZED):
                request_page_size(resize_state['page'])
            return False
        window.connect('window-state-event',window_state_changed)
        view=WebKit2.WebView()
        view.set_background_color(Gdk.RGBA(red=0,green=0,blue=0,alpha=0))
        settings=view.get_settings()
        settings.set_property('enable-developer-extras',False)
        # WebKit disables the Fullscreen API by default; YouTube's iframe
        # button otherwise cannot emit enter-fullscreen for this GTK window.
        settings.set_property('enable-fullscreen',True)
        settings.set_media_playback_requires_user_gesture(False)
        def dispatch_to_gtk(callback,value,timeout=5):
            completed=threading.Event();outcome=[]
            def run():
                try:outcome.append((True,callback(value)))
                except Exception as error:outcome.append((False,error))
                completed.set();return False
            source=GLib.idle_add(run)
            if not completed.wait(timeout):
                GLib.source_remove(source)
                raise RuntimeError('Ação da interface expirou.')
            succeeded,result=outcome[0]
            if not succeeded:raise RuntimeError('Não foi possível concluir a ação da interface.') from result
            return result
        def set_window_state(data):
            state=data.get('state')
            if state not in ('idle','settings','panel','player'):raise ValueError('Estado de janela inválido.')
            def apply(_):
                if 'content_bounds' in data:chrome_watch.set_content_bounds(data['content_bounds'])
                request_page_size(state)
            dispatch_to_gtk(apply,None)
        def fit_player(data):
            edge=data.get('edge');names={'nw':'NORTH_WEST','n':'NORTH','ne':'NORTH_EAST','w':'WEST','e':'EAST','sw':'SOUTH_WEST','s':'SOUTH','se':'SOUTH_EAST'}
            if not isinstance(edge,str) or edge not in names:raise ValueError('Alça inválida.')
            values=[data.get(k) for k in ('x','y','viewport_width','viewport_height')]
            if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=32768 for v in values):raise ValueError('Coordenadas inválidas.')
            x,y,vw,vh=values
            if not vw or not vh or x>vw or y>vh:raise ValueError('Coordenadas inválidas.')
            def begin(_):
                if window_size_locked():return {'applied':False}
                resize_state['enabled']=False
                width,height=window.get_size();ox,oy=window.get_window().get_root_coords(0,0)
                window.begin_resize_drag(getattr(Gdk.WindowEdge,names[edge]),1,round(ox+x*width/vw),round(oy+y*height/vh),Gdk.CURRENT_TIME)
                return {'applied':True}
            return dispatch_to_gtk(begin,None)
        def window_action(data):
            action=data.get('command')
            if action not in ('minimize','maximize','close','move'):raise ValueError('Comando inválido.')
            if action=='move':
                values=[data.get(k) for k in ('x','y','viewport_width','viewport_height')]
                if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=32768 for v in values):raise ValueError('Coordenadas inválidas.')
                x,y,vw,vh=values
                if not vw or not vh or x>vw or y>vh:raise ValueError('Coordenadas inválidas.')
            def apply(_):
                if action=='minimize':window.iconify()
                elif action=='maximize':
                    native=window.get_window()
                    if native.get_state() & Gdk.WindowState.MAXIMIZED:window.unmaximize()
                    elif not native.get_state() & Gdk.WindowState.FULLSCREEN:window.maximize()
                elif action=='close':GLib.timeout_add(50,lambda:(window.close(),False)[1])
                elif not window_size_locked():
                    width,height=window.get_size();ox,oy=window.get_window().get_root_coords(0,0)
                    window.begin_move_drag(1,round(ox+x*width/vw),round(oy+y*height/vh),Gdk.CURRENT_TIME)
                return {'ok':True}
            return dispatch_to_gtk(apply,None)
        def open_external(data):
            uri=data.get('uri')
            if not isinstance(uri,str) or not is_allowed_external_uri(uri):raise ValueError('Link externo inválido.')
            def launch(value):Gio.AppInfo.launch_default_for_uri(value,None)
            dispatch_to_gtk(launch,uri)
        def copy_youtube_link(data):
            uri=data.get('uri')
            if not isinstance(uri,str) or not re.fullmatch(r'https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}',uri):
                raise ValueError('Link de vídeo inválido.')
            def copy(value):
                clipboard=Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                clipboard.set_text(value,-1);clipboard.store()
            dispatch_to_gtk(copy,uri)
        def set_always_above(data):
            enabled=data.get('enabled')
            if type(enabled) is not bool:raise ValueError('Estado inválido.')
            dispatch_to_gtk(window.set_keep_above,enabled)
            local_library.action({'op':'preferences','values':{'always_above':enabled}})
        chrome_watch=PointerWatch(window,view,GLib,Gdk,callback="orbitzChromePointer",interval=100)
        from media_controls import MediaControls
        media=MediaControls(window,view,instance=instance)
        def media_update(data):return dispatch_to_gtk(media.update,data)
        def transfer_library(data):return dispatch_to_gtk(lambda value:desktop_features.transfer(window,Gtk,value),data,timeout=None)
        def get_diagnostics(_data):return dispatch_to_gtk(lambda _:desktop_features.diagnostics(Gtk,WebKit2),None)
        def save_last_playback(*_):
            if media.state['id']:
                saved=local_library.action({})['resume']
                if saved and saved['id']!=media.state['id']:return False
                import time
                value=media.state
                position=value['position']+((time.monotonic()-media.updated)*value.get('rate',1.0) if value['status']=='Playing' else 0)
                try:local_library.action({'op':'progress','video':{'id':value['id'],'title':value['title']},'position':min(position,value['duration']) if value['duration'] else position,'duration':value['duration'],'live':value.get('live',False),'restart':value.get('restart',False)})
                except (OSError,ValueError):pass
            return False
        window.connect('delete-event',save_last_playback)
        server.ui_actions={'window-action':window_action,'fit-player':fit_player,'new-window':lambda _data:dispatch_to_gtk(lambda _:create_window(app),None),'media-state':media_update,'library-transfer':transfer_library,'diagnostics':get_diagnostics,'always-above':set_always_above,'window-state':set_window_state,'open-external':open_external,'copy-link':copy_youtube_link}
        def policy(view,decision,kind):
            if kind==WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:
                # Never treat a popup requested inside the cross-origin player
                # as an external-app launch (the native fullscreen control is
                # handled by WebKit's fullscreen API). Outer UI links use the
                # token-protected local action endpoint instead.
                decision.ignore();return True
            return False
        view.connect('decide-policy',policy)
        def language_changed(*_):
            payload={'locale':ui.get_locale(),'catalog':ui._load()['pt-BR']|ui._load().get(ui.get_locale(),{})}
            view.run_javascript('window.orbitzSetLanguage && window.orbitzSetLanguage('+json.dumps(payload,ensure_ascii=True)+');',None,None,None)
        holder['language_callback']=language_changed
        unwatch_language=ui.watch(language_changed)
        def page_loaded(_view,event):
            if event==WebKit2.LoadEvent.STARTED:
                save_last_playback()
                media.update(dict(id='',title='',position=0,duration=0,status='Stopped',volume=1.0,next=False,rate=1.0))
                chrome_watch.reset()
            if event==WebKit2.LoadEvent.FINISHED:
                language_changed()
                chrome_watch.configure({'enabled':True,'sequence':0})
                view.run_javascript('window.orbitzWindowLocked='+str(window_size_locked()).lower()+';window.orbitzWindowMaximized='+str(bool(window.get_window() and window.get_window().get_state() & Gdk.WindowState.MAXIMIZED)).lower()+';window.orbitzSyncWindowButtons?.();',None,None,None)
        view.connect('load-changed',page_loaded)

        # Do not connect enter/leave-fullscreen: WebKit's default handlers
        # must own the iframe's fullscreen request and its toplevel changes.
        def key_press(_window,event):
            # Handle this before WebKit dispatches to a focused cross-origin iframe.
            modifiers=event.state & Gtk.accelerator_get_default_mod_mask()
            if Gdk.keyval_to_lower(event.keyval)==Gdk.KEY_t and modifiers==Gdk.ModifierType.CONTROL_MASK:
                pressed=shortcut_state['media_keys']
                if Gdk.KEY_t not in pressed:
                    pressed.add(Gdk.KEY_t);view.run_javascript('window.orbitzFitPlayer && window.orbitzFitPlayer();',None,None,None)
                return True
            shortcuts={Gdk.KEY_space:('playpause',None),Gdk.KEY_m:('mute',None)}
            if modifiers==Gdk.ModifierType.CONTROL_MASK and Gdk.keyval_to_lower(event.keyval) in shortcuts:
                key=Gdk.keyval_to_lower(event.keyval)
                pressed=shortcut_state['media_keys']
                if key not in pressed:
                    pressed.add(key);command,value=shortcuts[key];media.command(command,value)
                return True
            if modifiers==(Gdk.ModifierType.CONTROL_MASK|Gdk.ModifierType.MOD1_MASK):
                if event.keyval in (Gdk.KEY_Left,Gdk.KEY_Right):
                    media.command('seek',-10 if event.keyval==Gdk.KEY_Left else 10);return True
                if Gdk.keyval_to_lower(event.keyval)==Gdk.KEY_n:
                    pressed=shortcut_state['media_keys']
                    if Gdk.KEY_n not in pressed:pressed.add(Gdk.KEY_n);media.command('next')
                    return True
            if event.keyval==Gdk.KEY_F11:
                state=window.get_window().get_state()
                if state & Gdk.WindowState.FULLSCREEN:
                    window.unfullscreen();request_page_size(resize_state['page'])
                else:window.fullscreen()
                return True
            if event.keyval==Gdk.KEY_Escape and resize_state['page']!='idle' and window.get_window().get_state() & Gdk.WindowState.FULLSCREEN:
                view.run_javascript('if(document.fullscreenElement)document.exitFullscreen();',None,None,None)
                window.unfullscreen();request_page_size(resize_state['page'])
                return False
            return False
        def reset_shortcut(*_):
            shortcut_state['media_keys'].clear()
            return False
        def key_release(_window,event):
            shortcut_state['media_keys'].discard(Gdk.keyval_to_lower(event.keyval))
            if Gdk.keyval_to_lower(event.keyval) in (Gdk.KEY_Control_L,Gdk.KEY_Control_R):reset_shortcut()
            return False
        window.connect('key-press-event',key_press)
        window.connect('key-release-event',key_release)
        window.connect('focus-out-event',reset_shortcut)
        def terminated(_view,reason):
            window.unfullscreen()
            dialog=ui.widget(Gtk.MessageDialog,transient_for=window,modal=True,message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK_CANCEL,text=ui.msg('youtube.player_interrupted'))
            ui.call(dialog,'format_secondary_text',ui.msg('youtube.reopen_player'))
            if dialog.run()==Gtk.ResponseType.OK:view.reload()
            dialog.destroy()
        view.connect('web-process-terminated',terminated)
        window.add(view);view.load_uri(f'http://127.0.0.1:{server.server_port}/{token}/')
        window.connect('destroy',lambda *_:(unwatch_language(),server.shutdown(),holder.clear(),windows.pop(instance,None)))
        holder['window']=window;windows[instance]=window;window.show_all()
    def startup(app):
        action=Gio.SimpleAction.new('new-window',None)
        action.connect('activate',lambda *_:create_window(app));app.add_action(action)
        app.set_accels_for_action('app.new-window',['<Primary>n'])
    app.add_main_option('new-window',0,GLib.OptionFlags.NONE,GLib.OptionArg.NONE,'Open a new window',None)
    def command_line(app,command):
        if command.get_options_dict().contains('new-window'):create_window(app)
        else:activate(app)
        return 0
    app.connect('command-line',command_line)
    app.connect('startup',startup)
    app.connect('activate',activate);app.run(sys.argv)

if __name__=='__main__':main()
