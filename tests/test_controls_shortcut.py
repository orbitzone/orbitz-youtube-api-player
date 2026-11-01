import ast
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'app'))
import youtube_server as server
import test_frontend_modules as boundary_fixture
spec=importlib.util.spec_from_file_location('controls_native',ROOT/'app/youtube-wrapper.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)

RECT={'left':0,'top':62,'width':700,'height':590,'viewport_width':700,'viewport_height':700}

class ControlsTests(unittest.TestCase):
    request=boundary_fixture.YouTubeBoundaryTests.request

    def test_old_automatic_preference_endpoint_is_disabled(self):
        self.assertEqual(self.request('controls-preference',{'enabled':True})[0][0],404)
        source=(ROOT/'app/youtube-wrapper.py').read_text()
        for old in ('enter-notify-event','leave-notify-event','watch_titlebar','send_pointer','pointer_source'):
            self.assertNotIn(old,source)

    def test_native_controls_payload_accepts_game_and_video_but_not_modal_or_coerced_flags(self):
        self.assertIsNone(native.controls_request({'state':'player'}))
        self.assertEqual(native.controls_request({'state':'player','hide_controls':True,'controls_sequence':1,'player_rect':RECT}),(True,1,RECT))
        self.assertEqual(native.controls_request({'state':'idle','hide_controls':True,'controls_sequence':2,'player_rect':RECT}),(True,2,RECT))
        for data in ({'state':'settings','hide_controls':True,'controls_sequence':1},{'state':'player','hide_controls':'true','controls_sequence':1},{'state':'player','hide_controls':True,'controls_sequence':True},{'state':'player','hide_controls':True,'controls_sequence':-1}):
            with self.assertRaises(ValueError):native.controls_request(data)

    def callbacks(self):
        tree=ast.parse((ROOT/'app/youtube-wrapper.py').read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');activate=next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name=='create_window')
        names={'set_window_state','end_controls_transition','key_press','key_release','reset_shortcut'};functions=[n for n in activate.body if isinstance(n,ast.FunctionDef) and n.name in names]
        window=Mock();window.get_allocated_width.return_value=700;window.get_allocated_height.return_value=450
        window.get_window.return_value.get_state.return_value=0
        window.get_window.return_value.get_root_coords.return_value=(20,50)
        window.get_size.return_value=(700,700);window.get_position.return_value=(20,20)
        ns=dict(media=Mock(),window=window,view=Mock(),Gtk=SimpleNamespace(accelerator_get_default_mod_mask=lambda:29),Gdk=SimpleNamespace(Gravity=SimpleNamespace(STATIC=10),keyval_to_lower=lambda key:104 if key==72 else key,KEY_space=32,KEY_Right=65363,KEY_Left=65361,KEY_m=109,KEY_n=110,KEY_h=104,KEY_Control_L=65507,KEY_Control_R=65508,KEY_F11=65480,KEY_Escape=65307,ModifierType=SimpleNamespace(CONTROL_MASK=4,MOD1_MASK=8),WindowState=SimpleNamespace(FULLSCREEN=1)),controls_request=native.controls_request,player_window_rect=native.player_window_rect,window_size_locked=lambda:False,
            chrome={'hidden':False,'sequence':-1,'shortcut_down':False,'geometry':None,'transition':False},resize_state={'programmatic':False,'target':700,'page':'player','source':0},GLib=SimpleNamespace(timeout_add=Mock(return_value=17),source_remove=Mock()),clear_programmatic=Mock(),request_page_size=Mock(),dispatch_to_gtk=lambda fn,value:fn(value))
        exec(compile(ast.Module(body=functions,type_ignores=[]),'youtube-wrapper.py','exec'),ns);return ns

    def test_native_decoration_toggle_rejects_out_of_order_changes(self):
        ns=self.callbacks();call=ns['set_window_state']
        call({'state':'player','hide_controls':True,'controls_sequence':2,'player_rect':RECT});ns['window'].set_decorated.assert_called_once_with(False)
        ns['window'].resize.assert_called_once_with(700,590);ns['window'].move.assert_called_once_with(20,112)
        call({'state':'player','hide_controls':False,'controls_sequence':1});ns['window'].set_decorated.assert_called_once()
        call({'state':'player','hide_controls':False,'controls_sequence':3});self.assertEqual(ns['window'].set_decorated.call_args.args,(True,))
        self.assertTrue(ns['resize_state']['programmatic'])
        self.assertEqual(ns['window'].resize.call_args.args,(700,700));self.assertEqual(ns['window'].move.call_args.args,(20,20))
        ns['request_page_size'].assert_not_called();self.assertTrue(ns['chrome']['transition'])
        ns['end_controls_transition'](3);self.assertFalse(ns['chrome']['transition'])

    def test_anchor_corrects_actual_client_origin_after_decoration_changes(self):
        ns=self.callbacks()
        ns['set_window_state']({'state':'player','hide_controls':True,'controls_sequence':2,'player_rect':RECT})
        anchor=next(call.args[1] for call in ns['GLib'].timeout_add.call_args_list if call.args[0]==16)
        window=ns['window'];window.get_window.return_value.get_root_coords.return_value=(20,90)
        window.get_position.return_value=(20,60)
        self.assertTrue(anchor());window.move.assert_called_with(20,112)
        ns['chrome']['sequence']=3
        self.assertFalse(anchor())

    def test_above_action_validates_boolean_and_dispatches_to_gtk(self):
        for enabled in (None,1,'true',[]):
            self.assertEqual(self.request('always-above',{'enabled':enabled})[0][0],400)
        tree=ast.parse((ROOT/'app/youtube-wrapper.py').read_text())
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        activate=next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name=='create_window')
        fn=next(n for n in activate.body if isinstance(n,ast.FunctionDef) and n.name=='set_always_above')
        window=Mock();dispatch=Mock();ns={'window':window,'dispatch_to_gtk':dispatch,'local_library':Mock()}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'above','exec'),ns)
        for enabled in (True,False):
            ns['set_always_above']({'enabled':enabled});dispatch.assert_called_with(window.set_keep_above,enabled)
        with self.assertRaises(ValueError):ns['set_always_above']({'enabled':1})

    def test_player_geometry_scales_css_pixels_without_changing_video_proportions(self):
        self.assertEqual(native.player_window_rect(700,700,RECT),(700,590,0,62))
        self.assertEqual(native.player_window_rect(1400,1400,RECT),(1400,1180,0,124))
        for width,height in ((524,340),(980,650)):
            rect=dict(left=0,top=62,width=width,height=height-110,viewport_width=width,viewport_height=height)
            self.assertEqual(native.player_window_rect(width,height,rect),(width,height-110,0,62))

    def test_invalid_video_geometry_is_rejected_before_resizing(self):
        for change in ({'width':10**1000},{'height':float('nan')},{'height':0},{'width':-1},{'top':-1},{'left':-1},{'height':float('inf')},{'width':True},{'viewport_width':0},{'height':800}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                native.controls_request({'state':'player','hide_controls':True,'controls_sequence':1,'player_rect':{**RECT,**change}})
        with self.assertRaises(ValueError):native.controls_request({'state':'player','hide_controls':True,'controls_sequence':1})

    def test_ctrl_h_is_captured_natively_even_when_the_player_has_focus(self):
        ns=self.callbacks();event=SimpleNamespace(keyval=104,state=4)
        self.assertTrue(ns['key_press'](None,event))
        self.assertIn('orbitzToggleControls',ns['view'].run_javascript.call_args.args[0])
        ns['key_press'](None,event);self.assertEqual(ns['view'].run_javascript.call_count,1)
        ns['key_release'](None,event);ns['key_press'](None,event)
        self.assertEqual(ns['view'].run_javascript.call_count,2)
        ns['reset_shortcut']();ns['key_press'](None,event)
        self.assertEqual(ns['view'].run_javascript.call_count,3)

    def test_other_modifiers_are_ignored_but_caps_lock_is_supported(self):
        ns=self.callbacks()
        for state in (0,1,5,12,20):self.assertFalse(ns['key_press'](None,SimpleNamespace(keyval=104,state=state)))
        ns['view'].run_javascript.assert_not_called()
        self.assertTrue(ns['key_press'](None,SimpleNamespace(keyval=72,state=6)))
        ns['key_release'](None,SimpleNamespace(keyval=65507))
        self.assertFalse(ns['chrome']['shortcut_down'])

    def test_media_shortcuts_reach_native_controller_and_text_navigation_stays_available(self):
        ns=self.callbacks();press=ns['key_press'];event=lambda key,state:SimpleNamespace(keyval=key,state=state)
        self.assertTrue(press(None,event(32,4)));ns['media'].command.assert_called_with('playpause',None)
        count=ns['media'].command.call_count;press(None,event(32,4));self.assertEqual(ns['media'].command.call_count,count,'holding play/pause does not toggle repeatedly')
        ns['key_release'](None,event(32,4));press(None,event(32,4));self.assertEqual(ns['media'].command.call_count,count+1)
        self.assertTrue(press(None,event(109,4)));ns['media'].command.assert_called_with('mute',None)
        self.assertTrue(press(None,event(65363,12)));ns['media'].command.assert_called_with('seek',10)
        self.assertTrue(press(None,event(65361,12)));ns['media'].command.assert_called_with('seek',-10)
        self.assertTrue(press(None,event(110,12)));ns['media'].command.assert_called_with('next')
        self.assertFalse(press(None,event(65363,4)),'Ctrl+Right remains available for text editing')

    def test_fullscreen_shortcuts_remain_available(self):
        ns=self.callbacks()
        self.assertTrue(ns['key_press'](None,SimpleNamespace(keyval=65480,state=0)))
        ns['window'].fullscreen.assert_called_once()
        ns['window'].get_window.return_value.get_state.return_value=1
        ns['resize_state']['page']='player'
        self.assertFalse(ns['key_press'](None,SimpleNamespace(keyval=65307,state=0)))
        ns['window'].unfullscreen.assert_called_once()
        self.assertIn('exitFullscreen',ns['view'].run_javascript.call_args.args[0])

if __name__=='__main__':unittest.main()
