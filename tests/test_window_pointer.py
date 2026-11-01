"""Native pointer observer lifecycle and coordinate contracts; no real desktop data."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from window_pointer import PointerWatch


class PointerTests(unittest.TestCase):
    def setup_watch(self):
        window,view,glib=Mock(),Mock(),Mock()
        glib.timeout_add.return_value=17
        window.get_mapped.return_value=True
        window.get_window.return_value.get_state.return_value=0
        window.get_window.return_value.get_root_coords.return_value=(100,200)
        window.get_size.return_value=(700,500)
        window.get_display.return_value.get_default_seat.return_value.get_pointer.return_value.get_position.return_value=(None,450,400)
        return PointerWatch(window,view,glib,SimpleNamespace(WindowState=SimpleNamespace(ICONIFIED=1)))

    def payload(self,watch):
        script=watch.view.run_javascript.call_args.args[0]
        return json.loads(script.split('orbitzAutoPointer(',1)[1].split(');',1)[0])

    def test_native_coordinates_include_the_iframe_and_scale_to_viewport(self):
        watch=self.setup_watch();watch.configure({'enabled':True,'sequence':1})
        self.assertEqual(self.payload(watch),dict(sequence=1,inside=True,x=.5,y=.4))
        pointer=watch.window.get_display.return_value.get_default_seat.return_value.get_pointer.return_value
        pointer.get_position.return_value=(None,50,400);watch.sample()
        self.assertFalse(self.payload(watch)['inside'])
        watch.window.get_window.return_value.get_state.return_value=1;watch.sample()
        self.assertFalse(self.payload(watch)['inside'])

    def test_reconfiguration_removes_timer_and_rejects_obsolete_sequences(self):
        watch=self.setup_watch();watch.configure({'enabled':True,'sequence':2})
        watch.configure({'enabled':False,'sequence':1});self.assertEqual(watch.source,17)
        watch.configure({'enabled':False,'sequence':3});self.assertEqual(watch.source,0)
        watch.GLib.source_remove.assert_called_once_with(17)
        for enabled,sequence in ((1,4),(True,True),(False,-1),(False,2**53)):
            with self.assertRaises(ValueError):watch.configure(dict(enabled=enabled,sequence=sequence))

    def test_stationary_pointer_does_not_wake_webkit_and_outside_movement_is_coalesced(self):
        watch=self.setup_watch();watch.configure({'enabled':True,'sequence':1})
        watch.view.run_javascript.reset_mock()
        for _ in range(100):watch.sample()
        watch.view.run_javascript.assert_not_called()
        pointer=watch.window.get_display.return_value.get_default_seat.return_value.get_pointer.return_value
        pointer.get_position.return_value=(None,50,400);watch.sample()
        watch.view.run_javascript.assert_called_once()
        pointer.get_position.return_value=(None,20,20);watch.sample()
        watch.view.run_javascript.assert_called_once()
        pointer.get_position.return_value=(None,450,400);watch.sample()
        self.assertEqual(watch.view.run_javascript.call_count,2)
        watch.configure({'enabled':True,'sequence':2})
        self.assertEqual(self.payload(watch)['sequence'],2)

    def test_reload_and_destruction_cleanup_observer(self):
        watch=self.setup_watch();watch.configure({'enabled':True,'sequence':4});watch.reset()
        self.assertEqual(watch.sequence,-1);self.assertEqual(watch.source,0)
        watch.configure({'enabled':True,'sequence':1});self.assertEqual(watch.source,17)
        watch.destroyed();self.assertEqual(watch.source,0);self.assertFalse(watch.sample())
        watch.configure({'enabled':True,'sequence':2});self.assertEqual(watch.source,0)
