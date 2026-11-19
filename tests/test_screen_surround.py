"""Acceptance checks from the approved parallel-side/continuous-ramp prototype."""
import unittest
import json
from pathlib import Path
from build123d import Vector,GeomType
from adapter import build_master

class ScreenSurroundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=build_master(imprint=False)
        cls.reference=json.loads((Path(__file__).parent/'fixtures/accepted-dimensions.json').read_text())['screen']

    def test_reinforced_sides_and_open_screen(self):
        for x in (-50,50):
            self.assertTrue(self.body.is_inside(Vector(x,-135,32)))
        self.assertFalse(self.body.is_inside(Vector(0,-135,32)))
        for x in (-50,50):
            self.assertFalse(self.body.is_inside(Vector(x,-135,36)))

    def test_new_top_is_parallel_to_underside_at_approved_height(self):
        y0,z0=self.reference['startYZmm']
        z0 -= 8.0
        nx,ny,nz=self.reference['bottomPlaneNormal']
        slope=-ny/nz
        faces=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
               and -170<f.center().Y<-110 and f.area>100
               and f.normal_at().dot(Vector(-nx,-ny,-nz))>.999999
               and abs(f.center().Z-(z0+slope*(f.center().Y-y0)))<1e-6]
        self.assertTrue(faces)

    def test_existing_body_top_continues_down_onto_both_screen_walls(self):
        # Original body top from the saved manufacturing geometry, not a new angle.
        normal=Vector(0,-0.26418906967888117,0.964470909598733)
        # The exact plane is recovered from the retained central body top.
        top=next(f for f in self.body.faces() if f.geom_type==GeomType.PLANE
                 and f.area>2000 and f.normal_at().dot(normal)>.999999
                 and -100<f.center().Y<-60)
        datum=top.center()
        for side in (-1,1):
            for y in (-103,-110,-118):
                z=datum.Z-normal.Y/normal.Z*(y-datum.Y)
                self.assertTrue(self.body.is_inside(Vector(side*50,y,z-.1)),(side,y,z))
                self.assertFalse(self.body.is_inside(Vector(side*50,y,z+.1)),(side,y,z))
            # Continuation must be part of the original coplanar top, with no seam.
            faces=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
                   and f.normal_at().dot(normal)>.999999
                   and f.bounding_box().min.Y<-120
                   and f.bounding_box().max.Y>-90]
            self.assertTrue(faces)
        self.assertFalse(self.body.is_inside(Vector(0,-110,32)))

    def test_raised_ribbon_at_rounded_cutout_is_removed(self):
        # User's green circle: the prior 3.418 mm² extrusion ribbon was here.
        for side in (-1,1):
            self.assertFalse(self.body.is_inside(Vector(side*55.84,-103.407,38)))

    def test_continuous_front_ramp_without_added_upright(self):
        ramps=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
               and .84<f.normal_at().Y<.86 and .52<f.normal_at().Z<.54
               and f.bounding_box().min.Y<-197 and f.bounding_box().max.Y>-178
               and f.area>3000]
        self.assertEqual(len(ramps),1)
        uprights=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
                  and f.normal_at().Y>.999 and -204<f.center().Y<-180 and f.area>1
                  and abs(f.center().X)>43 and f.center().Z>35]
        self.assertFalse(uprights)

    def test_screen_side_walls_reach_the_front_ramp(self):
        rear_y, rear_z = self.reference['startYZmm']
        _, normal_y, normal_z = self.reference['bottomPlaneNormal']
        for y in (-173, -177, -181, -188):
            wall_z = rear_z - 8.0 - normal_y / normal_z * (y - rear_y)
            for side in (-1, 1):
                with self.subTest(y=y, side=side):
                    self.assertTrue(self.body.is_inside(Vector(side * 43.5, y, wall_z - .2)))
                    self.assertFalse(self.body.is_inside(Vector(side * 43.5, y, wall_z + .2)))
                    self.assertFalse(self.body.is_inside(Vector(side * 42.5, y, wall_z - .2)))

if __name__=='__main__':unittest.main()
