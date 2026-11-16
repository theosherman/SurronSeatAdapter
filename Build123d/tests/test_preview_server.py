"""Preview selection and confinement, without CAD dependencies."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('preview_server', Path(__file__).resolve().parents[1]/'preview_server.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PreviewTests(unittest.TestCase):
    def test_nested_image_appears_and_updates(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            self.assertIsNone(module.latest_preview(root))
            image=root/'cavity'/'preview.png'; image.parent.mkdir(); image.write_bytes(b'first')
            first=module.latest_preview(root)
            self.assertEqual(first['path'],'cavity/preview.png')
            image.write_bytes(b'changed image')
            self.assertNotEqual(first['version'],module.latest_preview(root)['version'])

    def test_outside_symlinks_and_traversal_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'tmp'; root.mkdir()
            outside=root.parent/'private.png'; outside.write_bytes(b'private')
            (root/'link.png').symlink_to(outside)
            self.assertIsNone(module.latest_preview(root))
            for name in ['../private.png','link.png','/etc/passwd']:
                with self.assertRaises(ValueError): module.preview_file(root,name)

if __name__=='__main__': unittest.main()
