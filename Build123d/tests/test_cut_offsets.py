"""Check the manufacturing cutters against independently measured source planes."""
import unittest
from math import hypot
from adapter import tool
from build123d import GeomType, Vector

class CutOffsetTests(unittest.TestCase):
    def test_front_triangle_faces_are_one_mm_outward_on_both_sides(self):
        cutter=tool(86,1000,(0,0,1),symmetric=True)
        length=hypot(31,29.84830397955)
        for side in (-1,1):
            normal=Vector(-side*29.84830397955/length,-31/length,0)
            old=Vector(-side*49,-193.15953208748562,0)
            faces=[f for f in cutter.faces() if f.geom_type==GeomType.PLANE
                   and abs(f.normal_at().dot(normal))>.999999]
            self.assertEqual(len(faces),1)
            self.assertAlmostEqual((faces[0].center()-old).dot(normal),1,places=6)
        self.assertTrue(cutter.is_valid)
        self.assertEqual(len(cutter.solids()),2)
