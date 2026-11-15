"""Physical acceptance checks for the approved raised, thickened front."""
import unittest
from build123d import GeomType, Plane, Keep, Vector
from adapter import build_master

class RaisedFrontTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=build_master(imprint=False)
        from unittest.mock import patch
        with patch('front_clip.redesign_front',side_effect=lambda body:body), \
             patch('screen_surround.reinforce_screen',side_effect=lambda body:body):
            cls.baseline=build_master(imprint=False)

    def test_handle_axis_and_unchanged_bore(self):
        arcs=[e for e in self.body.edges() if e.geom_type==GeomType.CIRCLE
              and abs(e.radius-15.1)<1e-6 and e.arc_center.Y<-200]
        self.assertTrue(arcs)
        for e in arcs:
            self.assertAlmostEqual(e.arc_center.Y,-220.3743032668,places=6)
            self.assertAlmostEqual(e.arc_center.Z,32.8742416819,places=6)

    def test_front_dovetail_removed(self):
        self.assertFalse(self.body.is_inside(Vector(0,-201.98,63.0)))
        dovetail_faces=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
                        and f.center().Y<-190 and f.area>100
                        and abs(f.normal_at().Y-0.800745)<0.002
                        and f.normal_at().Z<-.59]
        self.assertFalse(dovetail_faces)

    def test_bridge_has_added_thickness_above_retained_bottom(self):
        self.assertTrue(self.body.is_inside(Vector(0,-190,48)))
        self.assertTrue(self.body.is_inside(Vector(0,-190,17)))
        self.assertFalse(self.body.is_inside(Vector(0,-190,10)))

    def test_screen_front_ramp_continues(self):
        faces=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
               and f.area>100 and f.bounding_box().min.Y<-190 and abs(f.normal_at().Z)>.5
               and abs(abs(f.normal_at().Y)-0.819152)<1e-4]
        self.assertTrue(faces,'No continued 55 degree screen ramp')

    def test_rear_screen_and_underbody_preserved(self):
        plane=Plane((0,-101.585,0),z_dir=(0,1,0))
        retained=self.body.split(plane,Keep.TOP)
        original=self.baseline.split(plane,Keep.TOP)
        self.assertAlmostEqual(retained.volume,original.volume,delta=.001)
        self.assertLess(retained.cut(original).volume,.001)
        self.assertLess(original.cut(retained).volume,.001)
        # Original underside immediately in front of the screen stays fixed.
        for y in (-180,-185,-190,-192):
            for x in (-40,0,40):
                for z in (10,14,16,18):
                    point=Vector(x,y,z)
                    self.assertEqual(self.body.is_inside(point),self.baseline.is_inside(point))

    def test_single_valid_native_solid(self):
        self.assertTrue(self.body.is_valid)
        self.assertEqual(len(self.body.solids()),1)

if __name__=='__main__':unittest.main()
