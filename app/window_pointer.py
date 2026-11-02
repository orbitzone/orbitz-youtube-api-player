"""Observe the native pointer, including cross-origin WebKit iframe areas."""
import json
import time


class PointerWatch:
    def __init__(self, window, view, GLib, Gdk, callback="orbitzChromePointer", interval=100):
        self.window, self.view, self.GLib, self.Gdk = window, view, GLib, Gdk
        self.callback,self.interval=callback,interval
        self.source = 0
        self.sequence = -1
        self.last_sample = None
        self.content_bounds = None
        self.last_position=None;self.last_motion=time.monotonic()
        self.alive = True
        window.connect('destroy', self.destroyed)

    def configure(self, data):
        enabled, sequence = data.get('enabled'), data.get('sequence')
        if type(enabled) is not bool or type(sequence) is not int or not 0 <= sequence <= 2**53-1:
            raise ValueError('Estado automático inválido.')
        if not self.alive or sequence <= self.sequence:
            return
        self.sequence = sequence
        self.last_sample = None
        self.last_position=None;self.last_motion=time.monotonic()
        if self.source:
            self.GLib.source_remove(self.source)
            self.source = 0
        if enabled:
            self.source = self.GLib.timeout_add(self.interval, self.sample)
            self.sample()

    def set_content_bounds(self, bounds):
        if not isinstance(bounds,dict) or set(bounds)!={'left','top','right','bottom'}:
            raise ValueError('Área de conteúdo inválida.')
        values=[bounds[k] for k in ('left','top','right','bottom')]
        if any(type(v) not in (int,float) or not 0<=v<=1 for v in values) or bounds['left']>=bounds['right'] or bounds['top']>=bounds['bottom']:
            raise ValueError('Área de conteúdo inválida.')
        if bounds!=self.content_bounds:
            self.content_bounds=dict(bounds);self.last_sample=None

    def sample(self):
        if not self.alive:
            return False
        inside, x, y = False, 0, 0
        native = self.window.get_window()
        if native and self.window.get_mapped() and not native.get_state() & self.Gdk.WindowState.ICONIFIED:
            pointer = self.window.get_display().get_default_seat().get_pointer()
            _, px, py = pointer.get_position()
            ox, oy = native.get_root_coords(0, 0)
            width, height = self.window.get_size()
            x, y = (px-ox)/max(1,width), (py-oy)/max(1,height)
            inside = 0 <= x < 1 and 0 <= y < 1
        if not inside:
            x, y = 0, 0
        now=time.monotonic()
        position=(inside,x,y)
        if position!=self.last_position:
            self.last_motion=now;self.last_position=position
        idle=inside and now-self.last_motion>=5
        if self.content_bounds:
            r=self.content_bounds
            over_body=inside and r['left']<=x<r['right'] and r['top']<=y<r['bottom']
            sample=(self.sequence,inside,over_body,idle)
        else:sample = (self.sequence, inside, x, y,idle)
        if sample == self.last_sample:
            return True
        self.last_sample = sample
        payload = json.dumps(dict(sequence=self.sequence, inside=inside, x=x, y=y,idle=idle))
        self.view.run_javascript('window.'+self.callback+' && window.'+self.callback+'('+payload+');', None, None, None)
        return True

    def reset(self):
        if self.source:
            self.GLib.source_remove(self.source)
            self.source = 0
        self.sequence = -1
        self.last_sample = None
        self.content_bounds = None
        self.last_position=None;self.last_motion=time.monotonic()

    def destroyed(self, *_):
        self.alive = False
        if self.source:
            self.GLib.source_remove(self.source)
            self.source = 0
