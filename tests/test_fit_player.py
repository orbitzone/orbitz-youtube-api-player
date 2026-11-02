import ast
import json
import math
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import youtube_api

class FitPlayerTests(unittest.TestCase):
    def test_native_drag_keeps_hidden_mode_and_validates_coordinates(self):
        source=ast.parse((Path(__file__).resolve().parents[1]/'app/youtube-wrapper.py').read_text())
        fit=next(n for n in ast.walk(source) if isinstance(n,ast.FunctionDef) and n.name=='fit_player')
        bounds=SimpleNamespace(x=0,y=0,width=1280,height=720)
        native=Mock();native.get_frame_extents.return_value=SimpleNamespace(width=1000,height=830)
        window=Mock();window.get_window.return_value=native;window.get_size.return_value=(1000,800);window.get_position.return_value=(600,400)
        display=Mock();display.get_monitor_at_window.return_value.get_workarea.return_value=bounds
        ns=dict(window=window,display=display,area=bounds,math=math,chrome={'hidden':False,'transition':False},resize_state={},window_size_locked=lambda:False,dispatch_to_gtk=lambda fn,value:fn(value))
        exec(compile(ast.Module(body=[fit],type_ignores=[]),'fit','exec'),ns)
        ns['chrome']['hidden']=True
        ns['chrome']['geometry']={'size':(1000,890),'root':(10,10)}
        native.get_root_coords.return_value=(50,60)
        ns['Gdk']=SimpleNamespace(WindowEdge=SimpleNamespace(SOUTH_EAST=7),CURRENT_TIME=0)
        data={'edge':'se','x':990,'y':790,'viewport_width':1000,'viewport_height':800}
        self.assertTrue(ns['fit_player'](data)['applied'])
        window.begin_resize_drag.assert_called_once_with(7,1,1040,850,0)
        window.resize.assert_not_called();window.set_decorated.assert_not_called()
        self.assertTrue(ns['chrome']['hidden'])
        ns['window_size_locked']=lambda:True;window.begin_resize_drag.reset_mock()
        self.assertFalse(ns['fit_player'](data)['applied']);window.begin_resize_drag.assert_not_called()
        with self.assertRaises(ValueError):ns['fit_player']({**data,'x':float('nan')})
        with self.assertRaises(ValueError):ns['fit_player']({**data,'edge':'invalid'})
