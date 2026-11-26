"""Regression checks for the split adapter's butterfly recesses."""
import unittest
from pathlib import Path

from build123d import GeomType, Keep, Vector, import_step

from split_adapter import build_split, connector_tools, split_plane


class SplitAdapterTests(unittest.TestCase):
    def test_top_recess_is_perpendicular_to_its_opening(self):
        seam = split_plane()
        tool = dict(connector_tools(seam))['top']
        floor, mouth = sorted(
            (face for face in tool.faces() if len(face.edges()) == 6),
            key=lambda face: face.center().Z,
        )
        sweep = floor.center() - mouth.center()
        self.assertAlmostEqual(sweep.length, 12.8, places=6)
        self.assertAlmostEqual(sweep.cross(mouth.normal_at()).length, 0.0, places=6)

    def test_each_half_has_only_the_top_and_two_equal_cavity_recesses(self):
        master = import_step(Path(__file__).resolve().parents[1] / 'exports/adapter-body.step')
        seam = split_plane()
        self.assertAlmostEqual(seam.origin.Y, 37.0)
        self.assertAlmostEqual(abs(seam.z_dir.Y), 1.0)
        uncut = sorted(master.split(seam, keep=Keep.BOTH), key=lambda part: part.center().Y)
        tools = dict(connector_tools(seam))
        for name, tool in tools.items():
            if name.startswith('cavity-'):
                engaged_volume = sum(s.volume for s in master.intersect(tool).solids())
                self.assertAlmostEqual(engaged_volume, tool.volume, delta=0.01, msg=name)

        for bare, (name, finished) in zip(uncut, build_split(master), strict=True):
            with self.subTest(half=name):
                rounded = dict(connector_tools(seam, rim_radius=1.0))
                nominal_volume = sum(sum(s.volume for s in bare.intersect(tool).solids())
                                     for tool in tools.values())
                rounded_volume = sum(sum(s.volume for s in bare.intersect(tool).solids())
                                     for tool in rounded.values())
                self.assertGreater(rounded_volume, nominal_volume)
                self.assertAlmostEqual(bare.volume - finished.volume, rounded_volume, delta=0.05)
                removed = bare.cut(finished)
                self.assertEqual(len(removed if isinstance(removed, list) else removed.solids()), 3)

    def test_recess_rounds_match_side_corners_and_leave_sharp_floors(self):
        plane = split_plane()
        nominal = dict(connector_tools(plane))
        rounded = dict(connector_tools(plane, rim_radius=1.0))
        outward = {'top': Vector(0, 0, 1), 'cavity-negative-x': Vector(1, 0, 0),
                   'cavity-positive-x': Vector(-1, 0, 0)}
        for name, original in nominal.items():
            with self.subTest(recess=name):
                tool = rounded[name]
                mouth = max(original.faces(), key=lambda face: face.normal_at().dot(outward[name]))
                normal = mouth.normal_at()
                caps = [face for face in tool.faces()
                        if face.geom_type == GeomType.PLANE and abs(face.normal_at().dot(normal)) > 0.999]
                opening, floor = sorted(caps, key=lambda face: face.center().dot(normal), reverse=True)
                self.assertAlmostEqual((opening.center() - floor.center()).dot(normal),
                                       12.8 if name == "top" else 6.8, places=5)
                self.assertGreater(opening.area, floor.area)
                blends = [face for face in tool.faces() if face.geom_type == GeomType.CYLINDER]
                # Six side corners and six mouth edges. The floor remains sharp.
                self.assertEqual(len(blends), 12)
                for blend in blends:
                    self.assertAlmostEqual(blend.radius, 1.0, places=5)
