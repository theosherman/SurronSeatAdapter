"""Check the manufacturing cutters against independently measured source planes."""
import unittest
from math import hypot
from adapter import tool
from build123d import GeomType, Vector

class CutOffsetTests(unittest.TestCase):
    def test_front_triangle_faces_are_three_mm_outward_on_both_sides(self):
        cutter=tool(86,1000,(0,0,1),symmetric=True)
        length=hypot(31,29.84830397955)
        for side in (-1,1):
            normal=Vector(-side*29.84830397955/length,-31/length,0)
            old=Vector(-side*49,-193.15953208748562,0)
            faces=[f for f in cutter.faces() if f.geom_type==GeomType.PLANE
                   and abs(f.normal_at().dot(normal))>.999999]
            self.assertEqual(len(faces),1)
            self.assertAlmostEqual((faces[0].center()-old).dot(normal),3,places=6)
        self.assertTrue(cutter.is_valid)
        self.assertEqual(len(cutter.solids()),2)

    def test_rear_notches_extend_outward_at_original_depth(self):
        from adapter_profiles import SKETCHES

        sketch = SKETCHES['RearSeatNotchSketch']
        origin, u, v, normal = map(Vector, (
            sketch['originMm'], sketch['xAxis'], sketch['yAxis'], sketch['normal']))
        cutter = tool(89, 8, direction=-normal)
        self.assertTrue(cutter.is_valid)
        self.assertEqual(len(cutter.solids()), 2)
        for side in (-1, 1):
            center = origin + v * 254.7089693376844
            self.assertFalse(cutter.is_inside(center - normal * 4))
            for width in (14, 35, 50, 90):
                point = center + u * (side * width)
                self.assertTrue(cutter.is_inside(point - normal * 4))
                self.assertFalse(cutter.is_inside(point - normal * 8.1))
