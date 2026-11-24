"""Shape acceptance: long open cavity, rear side relief, original latch interface."""
import unittest
from pathlib import Path
from build123d import Vector,Plane,Keep,Compound,ShapeList,Solid,import_step
from adapter import build_master,SKETCHES,tool
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
        for v in (-50,0,35):
            self.assertFalse(self.body.is_inside(origin+y*v-n*30),v)
            self.assertTrue(self.body.is_inside(origin+y*v-n*18),v)
        # The new underside reaches above the old cavity roof near the front.
        self.assertTrue(self.body.is_inside(origin+y*80-n*5))
        self.assertFalse(self.body.is_inside(origin+y*80-n*10))

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

    def test_rear_seat_raised_area_and_notch_floors(self):
        slope = .27456857573275 / .9615675208845652
        for x, y, rise in ((0,191.47,0), (0,191.49,5), (0,223.12,5),
                           (0,223.14,0), (0,235,0)):
            height = 88.39413736888 + (y - 188.48114962565) * slope + rise
            self.assertTrue(self.body.is_inside((x,y,height-.005)), (x,y))
            self.assertFalse(self.body.is_inside((x,y,height+.005)), (x,y))
        for x in (-20,20):
            for y in (223.14,235):
                height = 90.82434901374 + (y - 226.1286209686) * slope + 3
                self.assertTrue(self.body.is_inside((x,y,height-.005)), (x,y))
                self.assertFalse(self.body.is_inside((x,y,height+.005)), (x,y))

    def test_angled_latch_wall_is_ten_mm_thick_inward(self):
        from trunk_cavity import REAR_WALL_POINT_MM,REAR_WALL_NORMAL
        point,normal=Vector(REAR_WALL_POINT_MM),Vector(REAR_WALL_NORMAL)
        for x in (-25,0,25):
            for z in (5,20):
                y=point.Y-(z-point.Z)*normal.Z/normal.Y
                outer=Vector(x,y,z)
                for depth in (.1,4.9,9.9):
                    self.assertTrue(self.body.is_inside(outer-normal*depth),(x,z,depth))
                self.assertFalse(self.body.is_inside(outer-normal*10.1),(x,z))

    def test_original_interface_changes_only_by_approved_cuts(self):
        datum=Plane((0,164.41714823915711,1.578677917809248),
                    z_dir=(0,.8597932986247546,.5106422266518543))
        actual=combined(self.body.split(datum,Keep.TOP))
        # The approved printing-plane offset adds an outer strip. Compare
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
        tag_sketch = SKETCHES['AirtagCutSketch']
        tag_normal = Vector(tag_sketch['normal'])
        tag = tool(126, 8.5, direction=-tag_normal).translate(
            Vector(ADAPTER_TRANSLATION_MM) + 90 * Vector(tag_sketch['yAxis']))
        expected=combined(expected.cut(cavity,tag,*rear_side_tools()))
        # The fixture predates the stepped roof and frontward notch extensions.
        # Exclude their envelope while keeping the lower latch and rail in scope.
        roof_change = Solid.make_box(120, 54, 30, Plane((-60,191.48,88)))
        actual = combined(actual.cut(roof_change))
        expected = combined(expected.cut(roof_change))
        old_center = Vector(tag_sketch['originMm']) + Vector(ADAPTER_TRANSLATION_MM)
        old_center += 26.8363533686 * Vector(tag_sketch['yAxis'])
        new_center = old_center + 90 * Vector(tag_sketch['yAxis'])
        self.assertTrue(self.body.is_inside(old_center - 4 * tag_normal))
        self.assertFalse(self.body.is_inside(new_center - 4 * tag_normal))
        self.assertTrue(self.body.is_inside(new_center - 9 * tag_normal))
        # Independently apply the measured original bottom plane plus 18 mm.
        # Its rear intersection is below the latch root and dovetail.
        upper=Plane((0,0,10.06786030784744), z_dir=(0,.1184039683059526,.9929655081066024))
        actual_upper=combined(actual.split(upper,Keep.TOP))
        expected_upper=combined(expected.split(upper,Keep.TOP))
        self.assertLess(combined(actual_upper.cut(expected_upper)).volume,.001)
        self.assertLess(combined(expected_upper.cut(actual_upper)).volume,.001)
        expected=combined(trim_lower_rear_tip(expected).split(upper, Keep.TOP))
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
