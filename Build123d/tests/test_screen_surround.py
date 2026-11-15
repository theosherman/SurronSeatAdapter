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
        cls.reference=json.loads((Path(__file__).resolve().parents[1]/
            'exports/concepts/parallel-screen-report.json').read_text())

    def test_reinforced_sides_and_open_screen(self):
        for x in (-50,50):
            self.assertTrue(self.body.is_inside(Vector(x,-135,40)))
        self.assertFalse(self.body.is_inside(Vector(0,-135,40)))

    def test_new_top_is_parallel_to_underside_at_approved_height(self):
        y0,z0=self.reference['startYZmm']
        nx,ny,nz=self.reference['bottomPlaneNormal']
        slope=-ny/nz
        faces=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
               and -170<f.center().Y<-110 and f.area>100
               and f.normal_at().dot(Vector(-nx,-ny,-nz))>.999999
               and abs(f.center().Z-(z0+slope*(f.center().Y-y0)))<1e-6]
        self.assertTrue(faces)

    def test_continuous_front_ramp_without_added_upright(self):
        ramps=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
               and .81<f.normal_at().Y<.83 and .57<f.normal_at().Z<.58
               and f.bounding_box().min.Y<-192 and f.bounding_box().max.Y>-168
               and f.area>3000]
        self.assertEqual(len(ramps),1)
        uprights=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
                  and f.normal_at().Y>.999 and -181<f.center().Y<-175 and f.area>1]
        self.assertFalse(uprights)

if __name__=='__main__':unittest.main()
