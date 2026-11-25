"""Check the printable keys against the shared recess geometry."""
import unittest

from build123d import Plane

from butterfly_keys import build_keys, lay_flat
from split_adapter import RECESS_RIM_RADIUS_MM, connector_tools, split_plane


class ButterflyKeyTests(unittest.TestCase):
    def test_two_printable_keys_fit_all_three_recesses(self):
        seam = split_plane()
        recesses = dict(connector_tools(seam, rim_radius=RECESS_RIM_RADIUS_MM))
        keys = dict(build_keys())
        self.assertEqual(set(keys), {'top', 'cavity'})
        cavity = keys['cavity']
        cap = next(face for face in recesses['cavity-negative-x'].faces() if len(face.edges()) > 4)
        # Two reflections make a rigid rotation, so the print fits the other wall too.
        axis = cap.normal_at().cross(seam.z_dir)
        opposite = cavity.mirror(Plane(cavity.center(), z_dir=axis)).mirror(Plane.YZ)
        placements = {
            'top': keys['top'],
            'cavity-negative-x': cavity,
            'cavity-positive-x': opposite,
        }
        for name, key in placements.items():
            with self.subTest(key=name):
                recess = recesses[name]
                self.assertTrue(key.is_valid)
                self.assertEqual(len(key.solids()), 1)
                overlap = key.intersect(recess)
                overlap_volume = sum(solid.volume for solid in overlap.solids())
                self.assertAlmostEqual(overlap_volume, key.volume, places=5)
                self.assertAlmostEqual(overlap_volume, recess.volume, places=5)
                bounds = lay_flat(key).bounding_box()
                self.assertAlmostEqual(bounds.min.Z, 0.0, places=5)
                self.assertAlmostEqual(bounds.size.Z, 12.8 if name == "top" else 6.8, places=5)
