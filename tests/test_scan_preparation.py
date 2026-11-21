"""Verify approved whole-scan movement precedes world-Y slicing and body scale."""
import unittest
from build123d import Solid, Axis, Plane, Keep
from prepare_sherman_p import prepare_parts


class ScanPreparationTests(unittest.TestCase):
    def test_alignment_precedes_slices_and_only_middle_scales(self):
        scan = Solid.make_box(20, 500, 40).translate((-10, -250, -20))
        # Independent reference: rigid motion of the complete scan, before clipping.
        reference = scan.rotate(Axis.X, -3.4932161177016057).translate((0, 0, 11.464786838041892))
        parts = prepare_parts(scan)
        front, body, rear = [parts[k] for k in ('front-handle', 'body-original', 'rear-handle')]
        regions = [front, body, rear]
        self.assertAlmostEqual(min(p.bounding_box().min.Z for p in regions), reference.bounding_box().min.Z, places=6)
        self.assertAlmostEqual(max(p.bounding_box().max.Z for p in regions), reference.bounding_box().max.Z, places=6)
        self.assertAlmostEqual(front.bounding_box().max.Y, -191, places=6)
        self.assertAlmostEqual(rear.bounding_box().min.Y, 170, places=6)
        self.assertAlmostEqual(sum(p.volume for p in regions), scan.volume, places=5)
        for handle, y, side in [(front, -191, Keep.BOTTOM), (rear, 170, Keep.TOP)]:
            expected = reference.split(Plane(origin=(0, y, 0), z_dir=(0, 1, 0)), keep=side)
            self.assertLess(abs(handle.cut(expected).volume), 1e-6)
            self.assertLess(abs(expected.cut(handle).volume), 1e-6)
        scaled = parts['body-scaled']
        self.assertAlmostEqual(scaled.volume, body.volume * 1.003**3, places=5)
        self.assertAlmostEqual(scaled.bounding_box().min.Y, -191*1.003, places=6)
        self.assertAlmostEqual(scaled.bounding_box().max.Y, 170*1.003, places=6)
        expected_scaled = body.translate((0, 0, -8)).scale(1.003, about=(0,0,0)).translate((0, 0, 8))
        self.assertLess(abs(scaled.cut(expected_scaled).volume), 1e-6)
        self.assertLess(abs(expected_scaled.cut(scaled).volume), 1e-6)
        merged = parts['merged']
        self.assertTrue(merged.is_valid)
        self.assertEqual(len(merged.solids()), 1)
        for handle in (front, rear):
            self.assertLess(abs(handle.cut(merged).volume), 1e-6)

    def test_attached_line_meets_lower_outer_bottom(self):
        from build123d import Edge
        from prepare_sherman_p import align_scan
        # Approved drawn line in YZ: z=-0.0577784327454574*y-11.047808379470325.
        line = Edge.make_line((0, -100, -5.269965104924585), (0, 100, -16.825651654016065))
        aligned = align_scan(line)
        for v in aligned.vertices():
            self.assertAlmostEqual(v.Z, -0.11924278067999218*v.Y+0.357237157925979, places=8)

    def test_disconnected_slice_fragments_are_preserved(self):
        # A connected scan may have several disconnected solids on one side of a cut.
        left = Solid.make_box(5, 500, 20).translate((-15, -250, -10))
        right = Solid.make_box(5, 500, 20).translate((10, -250, -10))
        bridge = Solid.make_box(30, 20, 20).translate((-15, -10, -10))
        scan = left.fuse(right, bridge)
        parts = prepare_parts(scan)
        self.assertEqual(len(parts['front-handle'].solids()), 2)
        self.assertEqual(len(parts['rear-handle'].solids()), 2)
        self.assertAlmostEqual(sum(parts[k].volume for k in ('front-handle', 'body-original', 'rear-handle')), scan.volume, places=5)
        self.assertTrue(parts['merged'].is_valid)
        self.assertEqual(len(parts['merged'].solids()), 1)

    def test_screen_reconnection_preserves_scan_points_and_triangle_count(self):
        import struct
        from pathlib import Path
        from coordinates import source_to_model
        from scan_patch import repair_screen_patch
        raw = bytearray((Path(__file__).resolve().parents[1]/'reference/fusion/Sherman_P_Scan_Aligned_To_Adapter_mm.stl').read_bytes())
        for i in range(16000):
            for j in range(4):
                at = 84+i*50+j*12
                struct.pack_into('<3f',raw,at,*source_to_model(struct.unpack_from('<3f',raw,at)))
        repaired = repair_screen_patch(raw)
        def vertices(data):
            return {struct.unpack_from('<3f',data,84+i*50+j*12) for i in range(16000) for j in (1,2,3)}
        self.assertEqual(len(repaired), len(raw))
        self.assertEqual(vertices(repaired), vertices(raw))
        self.assertEqual(len(vertices(repaired)), 7988)
        self.assertNotEqual(repaired, raw)
        with self.assertRaises(ValueError):
            repair_screen_patch(b'not the approved scan')
