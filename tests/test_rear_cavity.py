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

    def test_lower_toe_is_removed_without_cutting_upper_seat_support(self):
        self.assertFalse(self.body.is_inside((0,180,-25)))
        for x in (-15,0,15):
            self.assertTrue(self.body.is_inside((x,255,100)),x)

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

    def test_untrimmed_angled_rear_wall_retains_five_mm_of_material(self):
        from trunk_cavity import REAR_WALL_POINT_MM,REAR_WALL_NORMAL
        point,normal=Vector(REAR_WALL_POINT_MM),Vector(REAR_WALL_NORMAL)
        for x in (-25,0,25):
            for z in (0,20):
                y=point.Y-(z-point.Z)*normal.Z/normal.Y
                outer=Vector(x,y,z)
                for depth in (.1,2.5,4.9):
                    self.assertTrue(self.body.is_inside(outer-normal*depth),(x,z,depth))

    def test_original_interface_changes_only_by_approved_cavity_and_side_cuts(self):
        datum=Plane((0,164.41714823915711,1.578677917809248),
                    z_dir=(0,.8597932986247546,.5106422266518543))
        actual=combined(self.body.split(datum,Keep.TOP))
        # The approved printing-plane offset adds a 1 mm outer strip. Compare
        # the old interface only inside its original envelope; independent
        # printing-plane tests check the new boundary and contact patches.
        import json
        planes=json.loads((Path(__file__).parent/'fixtures/accepted-dimensions.json').read_text())['printingPlanes']
        for plane in planes:
            actual=combined(actual.split(Plane(plane['pointMm'],
                z_dir=plane['outwardNormal']),Keep.BOTTOM))
        expected=import_step(Path(__file__).parent/'fixtures/original-rear-interface.step')
        from trunk_cavity import rear_cavity_tool,rear_side_tools,trim_lower_rear_tip
        cavity=rear_cavity_tool(SKETCHES['BodyCutSketch']).translate(ADAPTER_TRANSLATION_MM)
        expected=combined(expected.cut(cavity,*rear_side_tools()))
        # Independently preserve the entire upper interface, including dovetail.
        # Do not apply the production trim to this expected region.
        upper=Plane((0,0,-17.98689437242),z_dir=(0,0,1))
        actual_upper=combined(actual.split(upper,Keep.TOP))
        expected_upper=combined(expected.split(upper,Keep.TOP))
        self.assertLess(combined(actual_upper.cut(expected_upper)).volume,.001)
        self.assertLess(combined(expected_upper.cut(actual_upper)).volume,.001)
        expected=combined(trim_lower_rear_tip(expected))
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
