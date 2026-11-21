"""Physical acceptance checks for the approved raised, thickened front."""
import unittest
from build123d import GeomType, Plane, Keep, Vector, Solid
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
            self.assertAlmostEqual(e.arc_center.Z,58.8742416819,places=6)

    def test_front_dovetail_removed(self):
        self.assertFalse(self.body.is_inside(Vector(0,-201.98,78.0)))
        dovetail_faces=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
                        and f.center().Y<-190 and f.area>100
                        and abs(f.normal_at().Y-0.800745)<0.002
                        and f.normal_at().Z<-.59]
        self.assertFalse(dovetail_faces)

    def test_extended_screen_gusset_keeps_full_clip_bore_open(self):
        bore = Solid.make_cylinder(15.1, 100,
            Plane((-50,-220.37430326680117,58.87424168191536), z_dir=(1,0,0)))
        overlap = self.body.intersect(bore)
        self.assertLess(sum(s.volume for s in overlap) if isinstance(overlap,list) else (0 if overlap is None else overlap.volume), 1e-5)

    def test_bridge_has_added_thickness_above_retained_bottom(self):
        self.assertFalse(self.body.is_inside(Vector(0,-190,63)))
        self.assertTrue(self.body.is_inside(Vector(0,-200,63)))
        self.assertTrue(self.body.is_inside(Vector(0,-190,35)))
        self.assertFalse(self.body.is_inside(Vector(0,-190,32)))

    def test_screen_ramp_is_tangent_to_the_outer_clip(self):
        section = self.body.intersect(Plane.YZ)
        start = Vector(0,-171.5863192559,30.5282901425)
        contact = Vector(0,-198.0430732835,72.8381651900)
        ramp = next(e for e in section.edges() if e.geom_type == GeomType.LINE
                    and min(((e @ t)-start).length for t in (0,1)) < 1e-5
                    and min(((e @ t)-contact).length for t in (0,1)) < 1e-5)
        arc = next(e for e in section.edges() if e.geom_type == GeomType.CIRCLE
                   and min(((e @ t)-contact).length for t in (0,1)) < 1e-5)
        self.assertAlmostEqual(arc.radius, 26.3377104606, places=6)
        self.assertAlmostEqual(((ramp @ 1) - (ramp @ 0)).dot(contact-arc.arc_center), 0, places=6)

    def test_rear_screen_and_underbody_preserved(self):
        plane=Plane((0,-86.999,0),z_dir=(0,1,0))
        retained=self.body.split(plane,Keep.TOP)
        original=self.baseline.split(plane,Keep.TOP)
        self.assertAlmostEqual(retained.volume,original.volume,delta=.001)
        self.assertLess(retained.cut(original).volume,.001)
        self.assertLess(original.cut(retained).volume,.001)
        # The native bottom plane rises by 18 mm with its slope preserved.
        for y in (-180, -185, -190, -192):
            z = -0.11924278067999218 * y - 7.9321396921525595 + 18
            self.assertFalse(self.body.is_inside((0, y, z - .1)))
            self.assertTrue(self.body.is_inside((0, y, z + .1)))

    def test_single_valid_native_solid(self):
        self.assertTrue(self.body.is_valid)
        self.assertEqual(len(self.body.solids()),1)

if __name__=='__main__':unittest.main()
