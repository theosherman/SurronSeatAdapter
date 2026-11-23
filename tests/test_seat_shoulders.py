"""Seat-support tabs continue back to the neck on their existing shoulder plane."""
import unittest
from build123d import Vector,GeomType
from adapter import build_master

class SeatShoulderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=build_master(imprint=False)

    def test_both_rear_shoulders_have_continuous_material_to_body(self):
        for side in (-1,1):
            for x,y in ((30,43),(25,50),(23,51)):
                for z in (43,47,52):
                    self.assertTrue(self.body.is_inside(Vector(side*x,y,z)),(side,x,y,z))

    def test_inner_shoulder_underside_rises_with_the_30_degree_draft(self):
        for side in (-1,1):
            self.assertFalse(self.body.is_inside(Vector(side*30,43,37)))

    def test_hook_contact_edge_remains_in_place(self):
        for side in (-1,1):
            self.assertTrue(self.body.is_inside(Vector(side*50.5,20,48)))
            self.assertFalse(self.body.is_inside(Vector(side*52,20,48)))

    def test_original_rear_shoulder_plane_reaches_the_neck(self):
        faces=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
               and abs(f.normal_at().Y-.8322153953472133)<1e-7
               and 48<f.center().Y<72]
        self.assertEqual(len(faces),2)
        for face in faces:
            box=face.bounding_box()
            self.assertGreater(box.max.X-box.min.X, 19)

if __name__=='__main__': unittest.main()
