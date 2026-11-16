"""Approved single long cavity: no old roof ledge or drafted middle breakthrough."""
import unittest
from build123d import Vector
from adapter import SKETCHES

class RearSketchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from trunk_cavity import rear_cavity_profile,rear_cavity_tool
        cls.sketch=SKETCHES['BodyCutSketch']
        cls.profile=rear_cavity_profile(cls.sketch)
        cls.tool=rear_cavity_tool(cls.sketch)

    def test_profile_is_one_simple_sixteen_segment_outline(self):
        self.assertTrue(self.profile.is_valid and self.tool.is_valid)
        self.assertEqual(len(self.profile.outer_wire().edges()),16)
        self.assertEqual(len(self.profile.inner_wires()),0)

    def test_long_neck_is_cut_with_straight_walls(self):
        origin,x,y,n=map(Vector,(self.sketch[k] for k in ('originMm','xAxis','yAxis','normal')))
        for v in (-50,0,80):
            for depth in (19,35,60):
                self.assertTrue(self.tool.is_inside(origin+y*v-n*depth),(v,depth))
                self.assertFalse(self.tool.is_inside(origin+x*13+y*v-n*depth),(v,depth))

    def test_single_roof_level_replaces_old_higher_recess(self):
        origin,y,n=map(Vector,(self.sketch[k] for k in ('originMm','yAxis','normal')))
        for v in (-120,-110,-20,50):
            self.assertFalse(self.tool.is_inside(origin+y*v-n*18))
            self.assertTrue(self.tool.is_inside(origin+y*v-n*19))

if __name__=='__main__':unittest.main()
