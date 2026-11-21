"""Acceptance checks for the approved raised screen and tangent ramp."""
import json
from pathlib import Path
import unittest

from build123d import GeomType, Vector

from adapter import build_master


class ScreenSurroundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = build_master(imprint=False)
        cls.reference = json.loads(
            (Path(__file__).parent / 'fixtures/accepted-dimensions.json').read_text()
        )['screen']

    def test_raised_rails_retain_slope_and_keep_the_screen_open(self):
        rear_y, rear_z = self.reference['startYZmm']
        _, ny, nz = self.reference['bottomPlaneNormal']
        for y in (-106, -115, -130, -145, -160, -173, -181, -188):
            wall_z = rear_z + 7 - ny / nz * (y - rear_y)
            for x in (-44, 44):
                self.assertTrue(self.body.is_inside((x, y, wall_z - .2)), (x, y))
                self.assertFalse(self.body.is_inside((x, y, wall_z + .2)), (x, y))
                self.assertFalse(self.body.is_inside((42 * x / abs(x), y, wall_z - .2)))
            self.assertFalse(self.body.is_inside((0, y, wall_z)))

    def test_rear_screen_wall_returns_to_body_top_ahead_of_bolt_seats(self):
        normal = Vector(0, -.26418906967883117, .964470909598733)
        top = next(f for f in self.body.faces() if f.geom_type == GeomType.PLANE
                   and f.normal_at().dot(normal) > .999999
                   and f.bounding_box().max.Y > -75 and f.bounding_box().min.Y < -86)
        point = top.center()
        join_y = -87
        join_z = point.Z - normal.Y / normal.Z * (join_y - point.Y)
        rear_y, rear_z = self.reference['startYZmm']
        for y in (-101, -98, -92, -88):
            z = rear_z + 7 + (join_z - rear_z - 7) * (y - rear_y) / (join_y - rear_y)
            self.assertTrue(self.body.is_inside((0, y, z - .2)))
            self.assertFalse(self.body.is_inside((0, y, z + .2)))

    def test_front_ramp_is_one_plane(self):
        ramps = [f for f in self.body.faces() if f.geom_type == GeomType.PLANE
                 and .84 < f.normal_at().Y < .86 and .52 < f.normal_at().Z < .54
                 and f.bounding_box().min.Y < -197 and f.bounding_box().max.Y > -178
                 and f.area > 2000]
        self.assertEqual(len(ramps), 1)
