"""Verify body-only fit scaling cannot move or scale either handle."""
import unittest
from build123d import Solid
from prepare_sherman_p import prepare_parts


class ScanPreparationTests(unittest.TestCase):
    def test_only_middle_scales_and_handles_remain_fixed(self):
        scan = Solid.make_box(20, 500, 40).translate((-10, -250, -20))
        parts = prepare_parts(scan)
        front, body, rear = [parts[k] for k in ('front-handle', 'body-original', 'rear-handle')]
        self.assertAlmostEqual(front.bounding_box().max.Y, -191, places=6)
        self.assertAlmostEqual(rear.bounding_box().min.Y, 170, places=6)
        self.assertAlmostEqual(sum(p.volume for p in (front, body, rear)), scan.volume, places=5)
        self.assertAlmostEqual(front.bounding_box().min.Y, -250, places=6)
        self.assertAlmostEqual(rear.bounding_box().max.Y, 250, places=6)
        scaled = parts['body-scaled']
        self.assertAlmostEqual(scaled.volume, body.volume * 1.003**3, places=5)
        self.assertAlmostEqual(scaled.bounding_box().min.Y, -191*1.003, places=6)
        self.assertAlmostEqual(scaled.bounding_box().max.Y, 170*1.003, places=6)
        merged = parts['merged']
        self.assertTrue(merged.is_valid)
        self.assertEqual(len(merged.solids()), 1)
        self.assertAlmostEqual(merged.bounding_box().min.Y, -250, places=6)
        self.assertAlmostEqual(merged.bounding_box().max.Y, 250, places=6)
        for handle in (front, rear):
            self.assertLess(abs(handle.cut(merged).volume), 1e-6)
        self.assertGreater(sum(p.volume for p in front.intersect(scaled)), 0)
        self.assertGreater(sum(p.volume for p in rear.intersect(scaled)), 0)
