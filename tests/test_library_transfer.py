from pathlib import Path
import json
import sys,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import desktop_features,local_library


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        override=patch.object(local_library,'DATABASE',Path(self.folder.name)/'library.sqlite3');override.start();self.addCleanup(override.stop)
        self.dialog=Mock();self.dialog.run.return_value=1
        self.file=Path(self.folder.name)/'bookmarks.json';self.dialog.get_filename.return_value=str(self.file)
        self.gtk=SimpleNamespace(FileChooserNative=SimpleNamespace(new=Mock(return_value=self.dialog)),FileChooserAction=SimpleNamespace(OPEN=0,SAVE=1),ResponseType=SimpleNamespace(ACCEPT=1),FileFilter=Mock)

    def test_export_import_merge_and_cancel(self):
        item=dict(id='abcdefghijk',title='Synthetic')
        local_library.action(dict(op='save',kind='favorites',video=item))
        self.assertTrue(desktop_features.transfer(None,self.gtk,dict(mode='export'))['exported'])
        value=json.loads(self.file.read_text());self.assertEqual(set(value),{'version','favorites','later'})
        local_library.action(dict(op='remove',kind='favorites',video=item))
        result=desktop_features.transfer(None,self.gtk,dict(mode='import'));self.assertEqual(result['favorites'],[item])
        self.dialog.run.return_value=0;self.assertEqual(desktop_features.transfer(None,self.gtk,dict(mode='import')),{'cancelled':True})

    def test_file_only_portal_export_falls_back_to_the_selected_file(self):
        with patch.object(desktop_features.tempfile,'mkstemp',side_effect=PermissionError('synthetic portal')):
            result=desktop_features.transfer(None,self.gtk,dict(mode='export'))
        self.assertTrue(result['exported']);self.assertEqual(json.loads(self.file.read_text())['version'],1)

    def test_invalid_and_oversized_files_do_not_modify_database(self):
        for content in ('not JSON','[]','{"version":1,"favorites":[{"id":"bad"}]}',' '*4194305):
            self.file.write_text(content)
            with self.assertRaises(ValueError):desktop_features.transfer(None,self.gtk,dict(mode='import'))
            self.assertEqual(local_library.action({})['favorites'],[])
        self.dialog.destroy.assert_called()
