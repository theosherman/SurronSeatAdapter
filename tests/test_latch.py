"""Checkpoint and geometry checks for the editable latch."""
import unittest


class LatchTests(unittest.TestCase):
    def test_latch_taper_tracks_the_raised_tongue(self):
        from math import atan2, degrees
        from build123d import GeomType, Vector
        from latch import build_latch
        from trunk_cavity import REAR_WALL_NORMAL, REAR_WALL_POINT_MM

        wall_normal = Vector(REAR_WALL_NORMAL)
        wall_point = Vector(REAR_WALL_POINT_MM) + wall_normal * 0.2 + Vector(0, 0, 18)
        body = build_latch()
        for sign in (-1, 1):
            sides = [face for face in body.faces()
                     if face.geom_type == GeomType.PLANE
                     and sign * face.normal_at().X > 0.9
                     and face.normal_at().Y > 0.1]
            self.assertEqual(len(sides), 1)
            normal = sides[0].normal_at()
            self.assertAlmostEqual(degrees(atan2(normal.Y, abs(normal.X))), 16.763375, places=5)
            self.assertAlmostEqual(normal.Z / normal.Y, wall_normal.Z / wall_normal.Y, places=6)
            seam = Vector(sign * 55, wall_point.Y, wall_point.Z)
            self.assertAlmostEqual((sides[0].center() - seam).dot(normal), 0, places=6)

    def test_checkpoints_and_model_bounds(self):
        from latch import build_latch
        body, stages = build_latch(with_stages=True)
        expected = [181526.5471, 363053.0942, 269573.7206, 261672.9306, 259953.2879]
        self.assertEqual(len(stages), len(expected))
        for stage, volume in zip(stages, expected):
            self.assertAlmostEqual(stage['volumeMm3'], volume, delta=0.01)
            self.assertTrue(stage['valid'])
            self.assertEqual(stage['solids'], 1)
        bounds = body.bounding_box()
        for actual, wanted in zip(tuple(bounds.min), (-55.0,147.800566681,-28.832840525)):
            self.assertAlmostEqual(actual, wanted, delta=0.001)
        for actual, wanted in zip(tuple(bounds.max), (55.0,219.997761302,52.014847916)):
            self.assertAlmostEqual(actual, wanted, delta=0.001)
        from build123d import GeomType
        self.assertTrue(any(f.geom_type == GeomType.CYLINDER for f in body.faces()))

    def test_raised_edge_and_tongue_planes(self):
        from build123d import GeomType, Vector
        from latch import build_latch

        body = build_latch()
        corner = Vector(0, 219.997761301043, -11.76219965661)
        edge, = [edge for edge in body.edges() if (edge.center() - corner).length < 1e-6]
        self.assertAlmostEqual(edge.length, 88.472226, places=5)

        planes = body.faces().filter_by(GeomType.PLANE)
        for normal in (Vector(0, .85979329862475, .51064222665185),
                       Vector(0, .88401823052998, -.46745242334450)):
            inner = [face for face in planes
                     if face.normal_at().dot(-normal) > 1-1e-7
                     and abs((corner-face.center()).dot(normal) - 14.393670) < 1e-5]
            self.assertEqual(len(inner), 1)

        # The shelf keeps its slope and moves 3 mm along its outward normal.
        shelf_normal = Vector(0, .154, -1).normalized()
        shelf, = [face for face in planes if face.normal_at().dot(shelf_normal) > .99999]
        original_shelf = Vector(0, 171.563092565, -8.769549215)
        self.assertAlmostEqual((shelf.center() - original_shelf).dot(shelf_normal),
                               3.0, places=5)

    def test_clearance_removes_material_and_rejects_negative(self):
        from latch import build_latch
        nominal = build_latch()
        zero = build_latch(clearance=0)
        larger = build_latch(clearance=0.3)
        self.assertAlmostEqual(zero.volume, 261672.9306, delta=0.01)
        self.assertLess(larger.volume, nominal.volume)
        self.assertAlmostEqual(nominal.cut(zero).volume, 0, delta=0.001)
        with self.assertRaises(ValueError):
            build_latch(clearance=-0.1)

    def test_three_mating_faces_move_inward_by_clearance(self):
        from latch import build_latch, FEATURES
        from coordinates import source_to_model, ADAPTER_TRANSLATION_MM
        from build123d import GeomType, Vector
        body = build_latch(clearance=0.2)
        for selector in FEATURES[106]['inputFaces']:
            normal = Vector(source_to_model(selector['geometry']['normal']))
            if selector['isParamReversed']:
                normal = -normal
            origin = Vector(source_to_model(selector['geometry']['origin'])) + Vector(ADAPTER_TRANSLATION_MM)
            shifted = [f for f in body.faces() if f.geom_type == GeomType.PLANE
                       and f.normal_at().dot(normal)>1-1e-7
                       and abs((f.center()-origin).dot(normal)+0.2)<1e-6]
            self.assertTrue(shifted, selector['point'])

    def test_dovetail_uses_shared_master_profile(self):
        from copy import deepcopy
        import adapter
        from latch import build_latch
        selected = next(p for p in adapter.RECIPE['selectedProfiles'] if p['sourceTimelineIndex']==18)
        saved = deepcopy(selected['profiles'])
        baseline = build_latch()
        try:
            # Symmetric width increase in the actual master profile data must
            # propagate into the latch's cut, without changing its outer frame.
            for profile in selected['profiles']:
                for loop in profile['loops']:
                    for curve in loop['curves']:
                        for key in ('startMm','endMm'):
                            if key in curve:
                                curve[key][0] *= 1.02
            widened = build_latch()
            self.assertLess(widened.volume, baseline.volume-100)
        finally:
            selected['profiles'] = saved
        self.assertAlmostEqual(build_latch().volume, baseline.volume, delta=0.001)
