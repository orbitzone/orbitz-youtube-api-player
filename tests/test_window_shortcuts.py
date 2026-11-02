import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
ROOT=Path(__file__).resolve().parents[1]
class WindowShortcutTests(unittest.TestCase):
    def callbacks(self):
        tree=ast.parse((ROOT/'app/youtube-wrapper.py').read_text())
        functions=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name in ('key_press','key_release','reset_shortcut')]
        ns=dict(media=Mock(),window=Mock(),view=Mock(),Gtk=SimpleNamespace(accelerator_get_default_mod_mask=lambda:29),Gdk=SimpleNamespace(keyval_to_lower=lambda k:k,KEY_space=32,KEY_Right=65363,KEY_Left=65361,KEY_m=109,KEY_n=110,KEY_t=116,KEY_Control_L=65507,KEY_Control_R=65508,KEY_F11=65480,KEY_Escape=65307,ModifierType=SimpleNamespace(CONTROL_MASK=4,MOD1_MASK=8),WindowState=SimpleNamespace(FULLSCREEN=1)),shortcut_state={'media_keys':set()},resize_state={'page':'player'},request_page_size=Mock())
        ns['window'].get_window.return_value.get_state.return_value=0
        exec(compile(ast.Module(body=functions,type_ignores=[]),'native','exec'),ns)
        return ns
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


    def test_unassigned_control_shortcut_is_not_intercepted(self):
        ns=self.callbacks()
        self.assertFalse(ns['key_press'](None,SimpleNamespace(keyval=104,state=4)))
        ns['view'].run_javascript.assert_not_called()
