"""Native shape checks for the rear-only controlling octagonal sketch."""
import unittest

class RearSketchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from adapter import SKETCHES
        from trunk_cavity import rear_cavity_profile,rear_cavity_tool
        cls.profile=rear_cavity_profile(SKETCHES['BodyCutSketch'])
        cls.tool=rear_cavity_tool(SKETCHES['BodyCutSketch'])

    def test_profile_is_one_simple_octagon(self):
        self.assertTrue(self.profile.is_valid and self.tool.is_valid)
        self.assertEqual(len(self.profile.outer_wire().edges()),8)
        self.assertEqual(len(self.profile.inner_wires()),0)

    def test_draft_stays_out_of_narrow_middle_at_all_body_heights(self):
        from build123d import Solid,Plane
        middle=Solid.make_box(200,175,140,Plane((-100,-100,-30)))
        overlap=self.tool.intersect(middle)
        volume=0 if overlap is None else sum(s.volume for s in overlap.solids())
        self.assertLess(volume,.001)

    def test_rear_pocket_is_open_without_cutting_the_thicker_rear_wall(self):
        for x in (-15,0,15):
            self.assertTrue(self.tool.is_inside((x,110,25)),x)
            for z in (0,15,30):
                self.assertFalse(self.tool.is_inside((x,150-.594*z,z)),(x,z))

if __name__=='__main__':unittest.main()
