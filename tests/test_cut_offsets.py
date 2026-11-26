"""Check the manufacturing cutters against independently measured source planes."""
import unittest
from adapter import tool
from build123d import GeomType, Vector, Vertex

class CutOffsetTests(unittest.TestCase):
    def test_front_diagonals_meet_clip_sides_at_cut_end(self):
        cutter = tool(86, 1000, (0, 0, 1), symmetric=True)
        for side in (-1, 1):
            diagonal = next(f for f in cutter.faces()
                            if f.geom_type == GeomType.PLANE
                            and .5 < abs(f.normal_at().X) < .9
                            and abs(f.normal_at().Y) > .5
                            and side * f.center().X > 0)
            clip_corner = Vertex(side * 49, -193.15953208748562, 0)
            self.assertLess(diagonal.distance_to(clip_corner), 1e-6)
        self.assertTrue(cutter.is_valid)
        self.assertEqual(len(cutter.solids()), 2)

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

    def test_seat_relief_keeps_lower_opening_and_extends_at_the_top(self):
        from adapter import seat_edge_relief, tool
        from build123d import Plane
        from coordinates import ADAPTER_TRANSLATION_MM

        original = tool(97, 240, symmetric=True).translate(ADAPTER_TRANSLATION_MM)
        relief = seat_edge_relief()
        flank = Plane((62.8589058205, -84.9726967486, 0),
                      z_dir=(0.654991476223, 0.755636265722, 0))
        lower_before, = original.intersect(flank).faces()
        lower_after, = relief.intersect(flank).faces()
        self.assertAlmostEqual(lower_before.area, lower_after.area, delta=.002)
        self.assertAlmostEqual(sum(f.area for f in lower_before.intersect(lower_after).faces()), lower_before.area, delta=.002)
        near_seat = (58, -113, 52)
        self.assertFalse(original.is_inside(near_seat))
        self.assertTrue(relief.is_inside(near_seat))
