"""Check the printable keys against the shared recess geometry."""
import unittest

from butterfly_keys import build_keys, lay_flat
from split_adapter import connector_tools, split_plane


class ButterflyKeyTests(unittest.TestCase):
    def test_each_recess_has_a_key_with_clearance_on_every_face(self):
        recesses = dict(connector_tools(split_plane()))
        keys = dict(build_keys())
        self.assertEqual(set(keys), {'top', 'cavity-negative-x', 'cavity-positive-x'})
        for name, key in keys.items():
            with self.subTest(key=name):
                recess = recesses[name]
                self.assertTrue(key.is_valid)
                self.assertEqual(len(key.solids()), 1)
                overlap = key.intersect(recess)
                self.assertAlmostEqual(sum(solid.volume for solid in overlap.solids()), key.volume, places=5)
                for face in recess.faces():
                    self.assertAlmostEqual(key.distance_to(face), 0.4, places=5)
                bounds = lay_flat(key).bounding_box()
                self.assertAlmostEqual(bounds.min.Z, 0.0, places=5)
                self.assertAlmostEqual(bounds.size.Z, 7.2, places=5)
