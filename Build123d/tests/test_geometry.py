"""Acceptance checks against saved source dimensions, not implementation details."""
import unittest
from adapter import profiles, build_master
from coordinates import source_to_model, ADAPTER_TRANSLATION_MM

class GeometryTests(unittest.TestCase):
    def test_selected_profile_areas(self):
        for index in (9, 12, 14, 18, 75, 76, 77, 79, 84, 86, 89, 91, 97, 121, 124, 126):
            for face, source in profiles(index, with_source=True):
                self.assertAlmostEqual(face.area, source['areaMm2'], delta=0.01, msg=str(index))

    def test_front_clip_center_matches_approved_handle_y(self):
        from build123d import GeomType
        body = build_master(imprint=False)
        arcs = [e for e in body.edges() if e.geom_type == GeomType.CIRCLE
                and abs(e.radius-15.1)<1e-6]
        self.assertTrue(arcs)
        for edge in arcs:
            self.assertAlmostEqual(edge.arc_center.Y, -220.37430326680117, places=6)
            self.assertAlmostEqual(edge.arc_center.Z, 32.87424168191536, places=6)

    def test_completed_master_and_mounting_material(self):
        body = build_master()
        self.assertEqual(len(body.solids()), 1)
        self.assertTrue(body.is_valid)
        # Independent accepted tool/checkpoint regression: handles must not cut the adapter.
        from build123d import import_step
        from pathlib import Path
        exports = Path(__file__).resolve().parents[1] / 'exports'
        pre = import_step(exports/'adapter-body-pre-imprint.step')
        tool = import_step(exports/'sherman-p-prepared/body-scaled.step')
        expected = pre.cut(tool)
        self.assertAlmostEqual(body.volume, expected.volume, delta=0.1)
        # Front clip material formerly removed by the full scan's fixed handle.
        self.assertTrue(body.solids()[0].is_inside((-40, -237.42678716846677, 33.05263206373636)))
        # Trunk side walls must survive the subsequent wheel-scan subtraction.
        for y in (45,50,55,60):
            for side in (-1,1):
                self.assertTrue(body.is_inside((side*20,y,30)),(side,y))
            self.assertTrue(body.is_inside((0,y,30)),y)
        for side in (-1,1):
            self.assertTrue(body.is_inside((side*30,33,45)))
            self.assertTrue(body.is_inside((side*25,40,45)))
        import json
        from pathlib import Path
        saved = json.loads((Path(__file__).resolve().parents[2] / 'SolidCraft/logs/mounting-ceiling-validation.json').read_text())
        for check in saved['checks']:
            point = tuple(v+d for v,d in zip(source_to_model(check['pointMm']), ADAPTER_TRANSLATION_MM))
            self.assertEqual(body.solids()[0].is_inside(point), check['expectedMaterial'], check['name'])

if __name__ == '__main__':
    unittest.main()
