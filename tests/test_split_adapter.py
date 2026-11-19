"""Regression checks for the split adapter's cavity butterfly keys."""
import unittest
from pathlib import Path

from build123d import Keep, Plane, import_step

from split_adapter import RECIPE, build_split, placed_point, source_to_model


class SplitAdapterTests(unittest.TestCase):
    def test_each_half_has_only_the_top_and_two_equal_cavity_recesses(self):
        master = import_step(Path(__file__).resolve().parents[1] / 'exports/adapter-body.step')
        datum = RECIPE['child']['splitPlane']
        seam = Plane(placed_point(datum['originMm']), z_dir=source_to_model(datum['normal']))
        uncut = sorted(master.split(seam, keep=Keep.BOTH), key=lambda part: part.center().Y)

        for bare, (name, finished) in zip(uncut, build_split(master), strict=True):
            with self.subTest(half=name):
                removed = bare.cut(finished)
                recesses = removed if isinstance(removed, list) else removed.solids()
                volumes = sorted(recess.volume for recess in recesses)
                self.assertEqual(len(volumes), 3, volumes)
                # Each cavity profile is 150 mm² and is cut 8 mm deep, half on either side.
                self.assertAlmostEqual(volumes[0], 600.0, places=3)
                self.assertAlmostEqual(volumes[1], 600.0, places=3)
                self.assertAlmostEqual(volumes[2], 6647.521, places=3)
