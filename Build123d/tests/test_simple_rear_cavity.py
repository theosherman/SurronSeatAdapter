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

    def test_cavity_retains_fourteen_mm_inside_mirrored_lower_cut(self):
        from coordinates import ADAPTER_TRANSLATION_MM
        # Independent accepted placed-model datum; catches wrong sign or spacing.
        point=Vector(0,177.270005683283,-17.98689437242)
        normal=Vector(0,.8597932986247546,-.5106422266518543)
        tool=self.tool.translate(ADAPTER_TRANSLATION_MM)
        maximum=max((v.center()-point).dot(normal) for v in tool.vertices())
        self.assertLessEqual(maximum,-14+1e-6)

    def test_cutter_retains_five_mm_normal_to_original_angled_rear_face(self):
        from pathlib import Path
        from build123d import import_step,GeomType
        from coordinates import ADAPTER_TRANSLATION_MM
        original=import_step(Path(__file__).parent/'fixtures/original-rear-interface.step')
        normal=Vector(0,.8597932986247546,.5106422266518543)
        face=next(f for f in original.faces() if f.geom_type==GeomType.PLANE
                  and f.normal_at().dot(normal)>.999999 and f.area>8000)
        tool=self.tool.translate(ADAPTER_TRANSLATION_MM)
        # Every cutter vertex must remain at least 5 mm inside the actual
        # original exterior face, measured perpendicular to the angled wall.
        maximum=max((v.center()-face.center()).dot(normal) for v in tool.vertices())
        self.assertLessEqual(maximum,-5+1e-6)

if __name__=='__main__':unittest.main()
