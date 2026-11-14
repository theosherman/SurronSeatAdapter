"""Front/rear correction must exist in inputs and the first manufacturing step."""
import json
from pathlib import Path
import unittest
from adapter import profiles, build_master, SKETCHES

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT/'cad-rebuild/recipe.json').read_text())

class OrientationTests(unittest.TestCase):
    def test_initial_profile_is_in_corrected_coordinates(self):
        source = next(p for p in SOURCE['selectedProfiles'] if p['sourceTimelineIndex']==9)['profiles'][0]
        center = profiles(9)[0].center()
        self.assertAlmostEqual(center.X, -source['centroidMm'][0], places=6)
        self.assertAlmostEqual(center.Y, -source['centroidMm'][1], places=6)

    def test_sketch_frames_keep_up_and_reverse_forward(self):
        source = next(s for s in SOURCE['sketches'] if s['name']=='BoltHolesSketch')
        for key in ('originMm','xAxis','yAxis','normal'):
            self.assertEqual(SKETCHES['BoltHolesSketch'][key],[-source[key][0],-source[key][1],source[key][2]])

    def test_first_extrusion_already_faces_correct_way(self):
        box = build_master(stop='M01').bounding_box()
        self.assertAlmostEqual(box.min.Y,-193.15953208748562,places=5)
        self.assertAlmostEqual(box.max.Y,290,places=5)
        self.assertAlmostEqual(box.min.Z,-50,places=5)
        self.assertAlmostEqual(box.max.Z,150,places=5)

if __name__=='__main__': unittest.main()
