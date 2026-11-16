"""Shape acceptance: long open cavity, rear side relief, original latch interface."""
import unittest
from pathlib import Path
from build123d import Vector,Plane,Keep,Compound,ShapeList,import_step
from adapter import build_master,SKETCHES
from coordinates import ADAPTER_TRANSLATION_MM


def combined(shape):
    if shape is None:return Compound([])
    return Compound(shape) if isinstance(shape,(list,ShapeList)) else shape

class RearCavityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.body=build_master(imprint=False)

    def test_long_middle_cavity_is_open_below_its_roof(self):
        origin=Vector(SKETCHES['BodyCutSketch']['originMm'])+Vector(ADAPTER_TRANSLATION_MM)
        y,n=map(Vector,(SKETCHES['BodyCutSketch']['yAxis'],SKETCHES['BodyCutSketch']['normal']))
        for v in (-50,0,80):
            self.assertFalse(self.body.is_inside(origin+y*v-n*30),v)
            self.assertTrue(self.body.is_inside(origin+y*v-n*18),v)

    def test_approved_side_cuts_remove_both_corners(self):
        from trunk_cavity import rear_side_tools
        for tool in rear_side_tools():
            self.assertLess(combined(self.body.intersect(tool)).volume,.001)
        for x in (-60,60):
            self.assertFalse(self.body.is_inside((x,150,50)),x)

    def test_cavity_is_empty_without_blocks_or_secondary_features(self):
        from trunk_cavity import rear_cavity_tool
        tool=rear_cavity_tool(SKETCHES['BodyCutSketch']).translate(ADAPTER_TRANSLATION_MM)
        self.assertLess(combined(self.body.intersect(tool)).volume,.001)
        for x in (-15,0,15):
            self.assertFalse(self.body.is_inside((x,110,25)),x)

    def test_rear_bridge_remains_material(self):
        for x in (-15,0,15):
            self.assertTrue(self.body.is_inside((x,235,90)),x)

    def test_original_interface_changes_only_by_approved_cavity_and_side_cuts(self):
        datum=Plane((0,164.41714823915711,1.578677917809248),
                    z_dir=(0,.8597932986247546,.5106422266518543))
        actual=combined(self.body.split(datum,Keep.TOP))
        expected=import_step(Path(__file__).parent/'fixtures/original-rear-interface.step')
        from trunk_cavity import rear_cavity_tool,rear_side_tools
        cavity=rear_cavity_tool(SKETCHES['BodyCutSketch']).translate(ADAPTER_TRANSLATION_MM)
        expected=combined(expected.cut(cavity,*rear_side_tools()))
        self.assertLess(combined(actual.cut(expected)).volume,.001)
        self.assertLess(combined(expected.cut(actual)).volume,.001)

    def test_rear_screwdriver_paths_remain_open(self):
        bolt=SKETCHES['BoltHolesSketch']
        origin=Vector(bolt['originMm'])+Vector(ADAPTER_TRANSLATION_MM)
        x,y,n=map(Vector,(bolt['xAxis'],bolt['yAxis'],bolt['normal']))
        for u in (-14.5,14.5):
            cap=origin+x*u+y*193.9428441873774-n*3
            for depth in (1,10,18,19,20,21,22,23,25,35,50):
                for dx in (-6,0,6):
                    self.assertFalse(self.body.is_inside(cap-n*depth+Vector(dx,0,0)),(u,depth,dx))

if __name__=='__main__':unittest.main()
