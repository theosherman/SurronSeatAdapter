"""Acceptance checks against the exact rear-face planes in the approved preview."""
import json
from pathlib import Path
import unittest
from build123d import Vector,GeomType,import_step
from adapter import build_master

class PrintPlaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=build_master(imprint=False)
        cls.reference=json.loads((Path(__file__).parent/'fixtures/accepted-dimensions.json').read_text())

    def test_all_geometry_inside_each_offset_printing_plane(self):
        for plane in self.reference['printingPlanes']:
            normal=Vector(plane['outwardNormal'])
            point=Vector(plane['pointMm']) + self.reference['printingPlaneOutwardOffsetMm'] * normal
            maximum=max((v.center()-point).dot(normal) for v in self.body.vertices())
            self.assertLessEqual(maximum,1e-6)
            self.assertAlmostEqual(maximum,0,places=6)

    def test_front_contact_patches_share_offset_rear_planes(self):
        for plane in self.reference['printingPlanes']:
            normal=Vector(plane['outwardNormal'])
            point=Vector(plane['pointMm']) + self.reference['printingPlaneOutwardOffsetMm'] * normal
            matches=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
                     and f.normal_at().dot(normal)>.999999
                     and abs((f.center()-point).dot(normal))<1e-6
                     and f.bounding_box().min.Y<-200]
            self.assertTrue(matches,'Missing front contact patch on offset printing plane')

    def test_finished_screen_wall_retains_two_mm_at_wheel_imprint(self):
        model = import_step(Path(__file__).parents[1] / 'exports/adapter-body.step')
        # Outermost prepared wheel points in the left and right screen-wall bands.
        points = (
            (-69.8299331665, -171.3075714111, 33.8662738800),
            (69.1511306763, -172.8207855225, 34.4286346436),
        )
        for point, plane in zip(points, self.reference['printingPlanes'], strict=True):
            normal = Vector(plane['outwardNormal'])
            for depth in (.01, .5, 1, 1.5, 2):
                self.assertTrue(model.is_inside(Vector(point) + depth * normal),
                                (point, depth))

if __name__=='__main__':unittest.main()
