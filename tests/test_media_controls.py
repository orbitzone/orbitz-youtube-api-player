import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
try:
    import media_controls as media
except ImportError:
    media=None


@unittest.skipIf(media is None,'Gio bindings not installed')
class MediaTests(unittest.TestCase):
    def player(self):
        player=object.__new__(media.MediaControls)
        player.view=Mock();player.window=Mock();player.connection=Mock()
        player.state=dict(id='',title='',position=0,duration=0,status='Stopped',volume=1.0,next=False)
        player.updated=0
        return player

    def track(self,player,identity='abcdefghi_-'):
        value=dict(id=identity,title='Synthetic <title>',position=12,duration=100,status='Playing',volume=.5,next=True)
        player.update(value);return value

    def test_properties_metadata_and_position_are_event_driven(self):
        player=self.player()
        with patch.object(media.time,'monotonic',return_value=10):self.track(player)
        with patch.object(media.time,'monotonic',return_value=15):
            props=player.properties(media.PLAYER);self.assertEqual(props['Position'].unpack(),17_000_000)
            self.assertEqual(props['PlaybackStatus'].unpack(),'Playing')
            self.assertEqual(props['Metadata'].unpack()['xesam:title'],'Synthetic <title>')
        self.assertTrue(player.properties(media.ROOT)['CanRaise'].unpack())
        player.connection.emit_signal.assert_called_once()
        value=self.track(player);value['status']='Paused';player.update(value)
        with patch.object(media.time,'monotonic',return_value=10**6):self.assertEqual(player.properties(media.PLAYER)['Position'].unpack(),12_000_000)

    def test_track_paths_are_valid_and_collision_free(self):
        player=self.player();self.track(player,'abcdefghi_-');first=player.properties(media.PLAYER)['Metadata'].unpack()['mpris:trackid']
        self.track(player,'abcdefghi__');second=player.properties(media.PLAYER)['Metadata'].unpack()['mpris:trackid']
        self.assertNotEqual(first,second);self.assertNotIn('-',first)
        media.GLib.Variant('o',first)

    def test_commands_and_stale_or_invalid_seek(self):
        player=self.player();self.track(player);invocation=Mock()
        player.call(None,None,None,media.PLAYER,'PlayPause',media.GLib.Variant('()',()),invocation)
        self.assertIn('"playpause"',player.view.run_javascript.call_args.args[0])
        player.view.reset_mock()
        player.call(None,None,None,media.PLAYER,'SetPosition',media.GLib.Variant('(ox)',('/stale',50_000_000)),invocation)
        player.view.run_javascript.assert_not_called()
        track=player.properties(media.PLAYER)['Metadata'].unpack()['mpris:trackid']
        for position in (-1,101_000_000):
            player.call(None,None,None,media.PLAYER,'SetPosition',media.GLib.Variant('(ox)',(track,position)),invocation)
        player.view.run_javascript.assert_not_called()
        player.call(None,None,None,media.PLAYER,'SetPosition',media.GLib.Variant('(ox)',(track,50_000_000)),invocation)
        self.assertIn('50.0',player.view.run_javascript.call_args.args[0])

    def test_state_validation_and_volume(self):
        player=self.player();value=self.track(player)
        for change in ({'position':float('nan')},{'volume':2},{'duration':True},{'id':'invalid'},{'title':[]},{'status':'invalid'}):
            with self.assertRaises(ValueError):player.update({**value,**change})
        self.assertTrue(player.set(None,None,None,None,'Volume',media.GLib.Variant('d',.8)))
        self.assertIn('0.8',player.view.run_javascript.call_args.args[0])
