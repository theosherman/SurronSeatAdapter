import struct
import tempfile
import unittest
from pathlib import Path
from scripts.validate_mesh import inspect_stl


class MeshValidationTest(unittest.TestCase):
    def check_mesh(self, faces):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'tetra.stl'
            raw = bytearray(80)+struct.pack('<I',len(faces))
            for face in faces:
                raw += struct.pack('<12fH',0,0,0,*[c for p in face for c in p],0)
            path.write_bytes(raw)
            return inspect_stl(path)

    def test_closed_and_open_tetrahedron(self):
        a,b,c,d=(0,0,0),(1,0,0),(0,1,0),(0,0,1)
        faces=[(a,c,b),(a,b,d),(a,d,c),(b,c,d)]
        closed=self.check_mesh(faces)
        self.assertTrue(closed['valid'])
        self.assertEqual(closed['solids'],1)
        self.assertAlmostEqual(closed['volumeMm3'],1/6)
        self.assertFalse(self.check_mesh(faces[:-1])['valid'])
        self.assertFalse(self.check_mesh([faces[0][::-1],*faces[1:]])['valid'])
