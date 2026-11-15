"""Acceptance checks against the exact rear-face planes in the approved preview."""
import json
from pathlib import Path
import unittest
from build123d import Vector,GeomType
from adapter import build_master

class PrintPlaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=build_master(imprint=False)
        cls.reference=json.loads((Path(__file__).resolve().parents[1]/
            'exports/concepts/print-plane-trim-report.json').read_text())

    def test_all_geometry_inside_each_original_printing_plane(self):
        for plane in self.reference['planes']:
            point,normal=Vector(plane['pointMm']),Vector(plane['outwardNormal'])
            maximum=max((v.center()-point).dot(normal) for v in self.body.vertices())
            self.assertLessEqual(maximum,1e-6)

    def test_front_contact_patches_share_exact_rear_planes(self):
        for plane in self.reference['planes']:
            point,normal=Vector(plane['pointMm']),Vector(plane['outwardNormal'])
            matches=[f for f in self.body.faces() if f.geom_type==GeomType.PLANE
                     and f.normal_at().dot(normal)>.999999
                     and abs((f.center()-point).dot(normal))<1e-6
                     and f.bounding_box().min.Y<-200]
            self.assertTrue(matches,'Missing front contact patch on original printing plane')

if __name__=='__main__':unittest.main()
