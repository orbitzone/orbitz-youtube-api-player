"""Observe the native pointer, including cross-origin WebKit iframe areas."""
import json


class PointerWatch:
    def __init__(self, window, view, GLib, Gdk):
        self.window, self.view, self.GLib, self.Gdk = window, view, GLib, Gdk
        self.source = 0
        self.sequence = -1
        self.last_sample = None
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
        if self.source:
            self.GLib.source_remove(self.source)
            self.source = 0
        if enabled:
            self.source = self.GLib.timeout_add(80, self.sample)
            self.sample()

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
        sample = (self.sequence, inside, x, y)
        if sample == self.last_sample:
            return True
        self.last_sample = sample
        payload = json.dumps(dict(sequence=self.sequence, inside=inside, x=x, y=y))
        self.view.run_javascript('window.orbitzAutoPointer && window.orbitzAutoPointer('+payload+');', None, None, None)
        return True

    def reset(self):
        if self.source:
            self.GLib.source_remove(self.source)
            self.source = 0
        self.sequence = -1
        self.last_sample = None

    def destroyed(self, *_):
        self.alive = False
        if self.source:
            self.GLib.source_remove(self.source)
            self.source = 0
