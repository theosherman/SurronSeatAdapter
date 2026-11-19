"""Check the printable keys against the shared recess geometry."""
import unittest

from build123d import GeomType, Plane

from butterfly_keys import build_keys, lay_flat
from split_adapter import connector_tools, split_plane


class ButterflyKeyTests(unittest.TestCase):
    def test_two_printable_keys_fit_all_three_recesses(self):
        seam = split_plane()
        recesses = dict(connector_tools(seam))
        keys = dict(build_keys())
        self.assertEqual(set(keys), {'top', 'cavity'})
        cavity = keys['cavity']
        cap = max(cavity.faces(), key=lambda face: face.area)
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
                self.assertAlmostEqual(sum(solid.volume for solid in overlap.solids()), key.volume, places=5)
                for face in recess.faces():
                    self.assertGreaterEqual(key.distance_to(face), 0.39999)
                blends = [face for face in key.faces() if face.geom_type == GeomType.CYLINDER]
                # The two tangent joins in the top profile share their blend surfaces.
                self.assertEqual(len(blends), 22 if name == 'top' else 18)
                for blend in blends:
                    self.assertAlmostEqual(blend.radius, 1.0, places=5)
                bounds = lay_flat(key).bounding_box()
                self.assertAlmostEqual(bounds.min.Z, 0.0, places=5)
                self.assertAlmostEqual(bounds.size.Z, 7.2, places=5)
