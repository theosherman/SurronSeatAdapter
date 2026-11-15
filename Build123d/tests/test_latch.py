"""Historical source latch checks; the rear revision is tested independently."""
import unittest


class LatchTests(unittest.TestCase):
    def test_source_checkpoints_and_model_bounds(self):
        from latch import build_latch
        body, stages = build_latch(with_stages=True,rear_wall_move=0)
        expected = [161420.2604, 322840.5208, 238753.4027, 232662.8943, 230819.7862464548]
        self.assertEqual(len(stages), len(expected))
        for stage, volume in zip(stages, expected):
            self.assertAlmostEqual(stage['volumeMm3'], volume, delta=0.01)
            self.assertTrue(stage['valid'])
            self.assertEqual(stage['solids'], 1)
        bounds = body.bounding_box()
        for actual, wanted in zip(tuple(bounds.min), (-60.865103223,147.800566681,-45.662921353)):
            self.assertAlmostEqual(actual, wanted, delta=0.001)
        for actual, wanted in zip(tuple(bounds.max), (60.865103223,219.997761302,47.321249211)):
            self.assertAlmostEqual(actual, wanted, delta=0.001)
        from build123d import GeomType
        self.assertTrue(any(f.geom_type == GeomType.CYLINDER for f in body.faces()))

    def test_clearance_removes_material_and_rejects_negative(self):
        from latch import build_latch
        nominal = build_latch(rear_wall_move=0)
        zero = build_latch(rear_wall_move=0,clearance=0)
        larger = build_latch(rear_wall_move=0,clearance=0.3)
        self.assertAlmostEqual(zero.volume, 232662.89426460396, delta=0.01)
        self.assertLess(larger.volume, nominal.volume)
        self.assertAlmostEqual(nominal.cut(zero).volume, 0, delta=0.001)
        with self.assertRaises(ValueError):
            build_latch(rear_wall_move=0,clearance=-0.1)

    def test_three_mating_faces_move_inward_by_clearance(self):
        from latch import build_latch, FEATURES
        from coordinates import source_to_model, ADAPTER_TRANSLATION_MM
        from build123d import GeomType, Vector
        body = build_latch(rear_wall_move=0,clearance=0.2)
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
        baseline = build_latch(rear_wall_move=0)
        try:
            # Symmetric width increase in the actual master profile data must
            # propagate into the latch's cut, without changing its outer frame.
            for profile in selected['profiles']:
                for loop in profile['loops']:
                    for curve in loop['curves']:
                        for key in ('startMm','endMm'):
                            if key in curve:
                                curve[key][0] *= 1.02
            widened = build_latch(rear_wall_move=0)
            self.assertLess(widened.volume, baseline.volume-100)
        finally:
            selected['profiles'] = saved
        self.assertAlmostEqual(build_latch(rear_wall_move=0).volume, baseline.volume, delta=0.001)
