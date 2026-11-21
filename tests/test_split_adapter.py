"""Regression checks for the split adapter's cavity butterfly keys."""
import unittest
from pathlib import Path

from build123d import GeomType, Keep, Plane, Vector, import_step

from split_adapter import RECIPE, build_split, connector_tools, placed_point, source_to_model, split_plane


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
                # The rim adds volume to each 750 mm³ cavity pocket and the top pocket.
                self.assertGreater(volumes[0], 750.0)
                # The raised, asymmetric wheel imprint clips the front rims
                # slightly differently while the recess tools remain mirrored.
                self.assertAlmostEqual(volumes[0], volumes[1], delta=0.02)
                self.assertGreater(volumes[2], 8309.401)

    def test_recess_rounds_are_confined_to_the_mouth(self):
        plane = split_plane()
        nominal = dict(connector_tools(plane))
        rounded = dict(connector_tools(plane, rim_radius=1.0))
        outward = {'top': Vector(0, 0, 1), 'cavity-negative-x': Vector(1, 0, 0),
                   'cavity-positive-x': Vector(-1, 0, 0)}
        for name, original in nominal.items():
            with self.subTest(recess=name):
                tool = rounded[name]
                caps = [face for face in original.faces() if len(face.edges()) > 4]
                self.assertAlmostEqual(caps[0].distance_to(caps[1]), 10.0, places=5)
                mouth = max(caps, key=lambda face: face.normal_at().dot(outward[name]))
                extra = tool.cut(original)
                self.assertAlmostEqual(original.cut(tool).volume, 0.0, places=5)
                self.assertGreater(extra.volume, 0.0)
                self.assertLess(max((mouth.center() - v.center()).dot(mouth.normal_at())
                                    for v in extra.vertices()), 2.0)
                blends = [face for face in tool.faces() if face.geom_type == GeomType.CYLINDER]
                self.assertEqual(len(blends), 6)
                for blend in blends:
                    self.assertAlmostEqual(blend.radius, 1.0, places=5)
