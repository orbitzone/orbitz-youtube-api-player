"""Window bounds and lifecycle tests with synthetic preferences only."""
from pathlib import Path
import sys,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'app'))
import window_geometry as geometry

VALUE=dict(version=1,x=100,y=80,width=602,height=366,maximized=False)

class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        override=patch.object(geometry,'GEOMETRY_FILE',Path(self.directory.name)/'window.json');override.start();self.addCleanup(override.stop)

    def tracker(self,saved=None):
        if saved:geometry.save_geometry(saved)
        window=Mock();window.get_window.return_value.get_state.return_value=0
        window.get_window.return_value.get_frame_extents.return_value=SimpleNamespace(x=100,y=80,width=602,height=366)
        window.get_size.return_value=(600,332)
        callbacks={};counter=[0]
        def timeout(_ms,fn):counter[0]+=1;callbacks[counter[0]]=fn;return counter[0]
        glib=SimpleNamespace(timeout_add=timeout,source_remove=lambda source:callbacks.pop(source,None))
        gtk=SimpleNamespace(WindowPosition=SimpleNamespace(NONE=0))
        gdk=SimpleNamespace(Gravity=SimpleNamespace(NORTH_WEST=1),WindowState=SimpleNamespace(FULLSCREEN=1,MAXIMIZED=2))
        return geometry.GeometryTracker(window,gtk,gdk,glib,[]),window,callbacks

    def test_private_atomic_roundtrip_and_corrupt_input(self):
        self.assertIsNone(geometry.read_geometry());geometry.save_geometry(VALUE);self.assertEqual(geometry.read_geometry(),VALUE)
        self.assertEqual(geometry.GEOMETRY_FILE.stat().st_mode&0o777,0o600)
        for text in ('[]','null','bad json','{"version":1}'):
            geometry.GEOMETRY_FILE.write_text(text);self.assertIsNone(geometry.read_geometry())
        self.assertEqual(list(Path(self.directory.name).glob('*.tmp')),[])

    def test_invalid_geometry_never_overwrites_a_preference(self):
        geometry.save_geometry(VALUE)
        for changed in ({'version':True},{'width':0},{'height':32769},{'x':True},{'maximized':1},{'y':-1000001}):
            with self.subTest(changed=changed),self.assertRaises(ValueError):geometry.save_geometry({**VALUE,**changed})
        self.assertEqual(geometry.read_geometry(),VALUE)

    def test_symlink_is_not_followed_and_failed_replace_preserves_existing_value(self):
        other=Path(self.directory.name)/'key.json';other.write_text('synthetic key stays intact')
        geometry.GEOMETRY_FILE.symlink_to(other);self.assertIsNone(geometry.read_geometry())
        geometry.save_geometry(VALUE);self.assertEqual(other.read_text(),'synthetic key stays intact')
        with patch.object(geometry.os,'replace',side_effect=OSError('synthetic failure')):
            with self.assertRaises(OSError):geometry.save_geometry({**VALUE,'x':200})
        self.assertEqual(geometry.read_geometry(),VALUE)

    def test_negative_monitor_coordinates_are_exact_and_offscreen_recovery_is_bounded(self):
        areas=[SimpleNamespace(x=0,y=0,width=1000,height=800),SimpleNamespace(x=-1280,y=0,width=1280,height=1024)]
        left={**VALUE,'x':-1000};self.assertEqual(geometry.visible_geometry(left,areas),left)
        outside={**VALUE,'x':8000,'y':9000,'width':1400,'height':1200}
        self.assertEqual(geometry.visible_geometry(outside,areas),{**outside,'x':0,'y':0,'width':1000,'height':800})

    def test_restore_measures_decorations_and_keeps_exact_external_bounds(self):
        tracker,window,_=self.tracker({**VALUE,'x':240,'y':170})
        self.assertTrue(tracker.prepare());window.set_position.assert_called_once_with(0);window.move.assert_called_with(240,170)
        self.assertTrue(tracker.restore());window.resize.assert_called_once_with(600,332)
        window.get_window.return_value.get_frame_extents.return_value=SimpleNamespace(x=240,y=170,width=602,height=366)
        self.assertFalse(tracker.restore());self.assertFalse(tracker.restoring)
        self.assertEqual(tracker.last,{**VALUE,'x':240,'y':170})

    def test_move_and_resize_are_debounced_but_close_flushes_latest_immediately(self):
        tracker,window,callbacks=self.tracker()
        self.assertFalse(tracker.prepare())
        tracker.configured();tracker.configured();self.assertEqual(len(callbacks),1)
        window.get_window.return_value.get_frame_extents.return_value=SimpleNamespace(x=333,y=222,width=700,height=400)
        self.assertFalse(tracker.close_requested());self.assertEqual(callbacks,{})
        self.assertEqual(geometry.read_geometry(),{**VALUE,'x':333,'y':222,'width':700,'height':400})

    def test_duplicate_notifications_do_not_restart_deadline_or_schedule_saved_bounds(self):
        tracker,window,callbacks=self.tracker()
        tracker.configured();source=tracker.save_source
        for _ in range(1000):tracker.configured()
        self.assertEqual(tracker.save_source,source);self.assertEqual(len(callbacks),1)
        tracker.flush();self.assertEqual(callbacks,{})
        for _ in range(1000):tracker.configured()
        self.assertEqual(callbacks,{})
        window.get_window.return_value.get_frame_extents.return_value=SimpleNamespace(x=200,y=80,width=602,height=366)
        tracker.configured();self.assertEqual(len(callbacks),1)
        tracker.close_requested();self.assertEqual(geometry.read_geometry()['x'],200)

    def test_maximized_and_temporary_fullscreen_do_not_replace_normal_bounds(self):
        tracker,window,_=self.tracker();tracker.configured()
        window.get_window.return_value.get_state.return_value=2
        window.get_window.return_value.get_frame_extents.return_value=SimpleNamespace(x=0,y=0,width=1920,height=1080)
        tracker.configured();tracker.flush();self.assertEqual(geometry.read_geometry(),{**VALUE,'maximized':True})
        window.get_window.return_value.get_state.return_value=1;tracker.flush()
        self.assertEqual(geometry.read_geometry(),{**VALUE,'maximized':True})
        second,other,_=self.tracker({**VALUE,'maximized':True});self.assertFalse(second.restore());other.maximize.assert_called_once()

    def test_destroy_saves_cached_bounds_and_removes_pending_sources(self):
        tracker,window,callbacks=self.tracker();tracker.configured()
        tracker.destroyed();self.assertEqual(callbacks,{});self.assertFalse(tracker.alive)
        self.assertEqual(geometry.read_geometry(),VALUE)

    def test_restore_does_not_overwrite_saved_state_with_startup_configure_events(self):
        tracker,window,callbacks=self.tracker({**VALUE,'x':500})
        tracker.configured();tracker.flush();self.assertEqual(callbacks,{})
        self.assertEqual(geometry.read_geometry(),{**VALUE,'x':500})
        source=(ROOT/'app/youtube-wrapper.py').read_text()
        self.assertIn("'enabled':not bool(geometry.saved)",source)

if __name__=='__main__':unittest.main()
