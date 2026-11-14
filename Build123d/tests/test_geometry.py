"""Acceptance checks against saved source dimensions, not implementation details."""
import unittest
from adapter import profiles, build_master
from coordinates import source_to_model

class GeometryTests(unittest.TestCase):
    def test_selected_profile_areas(self):
        for index in (9, 12, 14, 18, 75, 76, 77, 79, 84, 86, 89, 91, 97, 121, 124, 126):
            for face, source in profiles(index, with_source=True):
                self.assertAlmostEqual(face.area, source['areaMm2'], delta=0.01, msg=str(index))

    def test_base_matches_fusion(self):
        body = build_master(stop='M05')
        self.assertEqual(len(body.solids()), 1)
        self.assertTrue(body.is_valid)
        self.assertAlmostEqual(body.volume, 2096156.9173983494, delta=0.01)

    def test_completed_master_and_mounting_material(self):
        body = build_master()
        self.assertEqual(len(body.solids()), 1)
        self.assertTrue(body.is_valid)
        self.assertAlmostEqual(body.volume, 1507476.065203498, delta=5)
        import json
        from pathlib import Path
        saved = json.loads((Path(__file__).resolve().parents[2] / 'SolidCraft/logs/mounting-ceiling-validation.json').read_text())
        for check in saved['checks']:
            self.assertEqual(body.solids()[0].is_inside(source_to_model(check['pointMm'])), check['expectedMaterial'], check['name'])

if __name__ == '__main__':
    unittest.main()
