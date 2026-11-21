"""Checkpoint and geometry checks for the editable latch."""
import unittest


class LatchTests(unittest.TestCase):
    def test_latch_sidewalls_align_with_rear_adapter(self):
        from build123d import GeomType
        from latch import build_latch

        body = build_latch()
        for sign in (-1, 1):
            sides = [face for face in body.faces()
                     if face.geom_type == GeomType.PLANE
                     and abs(face.normal_at().X - sign) < 1e-7
                     and abs(face.center().X - sign * 55) < 1e-7]
            self.assertEqual(len(sides), 1)
            bounds = sides[0].bounding_box()
            self.assertAlmostEqual(bounds.min.Y, body.bounding_box().min.Y, places=6)
            self.assertAlmostEqual(bounds.max.Y, body.bounding_box().max.Y, places=6)

    def test_checkpoints_and_model_bounds(self):
        from latch import build_latch
        body, stages = build_latch(with_stages=True)
        expected = [161420.2604, 322840.5208, 260778.5622, 254688.0538, 252902.3949]
        self.assertEqual(len(stages), len(expected))
        for stage, volume in zip(stages, expected):
            self.assertAlmostEqual(stage['volumeMm3'], volume, delta=0.01)
            self.assertTrue(stage['valid'])
            self.assertEqual(stage['solids'], 1)
        bounds = body.bounding_box()
        for actual, wanted in zip(tuple(bounds.min), (-55.0,147.800566681,-45.662921353)):
            self.assertAlmostEqual(actual, wanted, delta=0.001)
        for actual, wanted in zip(tuple(bounds.max), (55.0,219.997761302,47.321249211)):
            self.assertAlmostEqual(actual, wanted, delta=0.001)
        from build123d import GeomType
        self.assertTrue(any(f.geom_type == GeomType.CYLINDER for f in body.faces()))

    def test_clearance_removes_material_and_rejects_negative(self):
        from latch import build_latch
        nominal = build_latch()
        zero = build_latch(clearance=0)
        larger = build_latch(clearance=0.3)
        self.assertAlmostEqual(zero.volume, 254688.0538, delta=0.01)
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
