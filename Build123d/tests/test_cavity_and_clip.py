"""Regression checks for the outline revision's broken trunk and hanging jaw."""
from pathlib import Path
import json
import unittest
from build123d import import_step, Plane, Keep, Vector, Compound
from adapter import build_master

class CavityAndClipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = build_master(imprint=False)

    def test_enlarged_opening_does_not_add_material_under_old_clip(self):
        old = import_step(Path(__file__).parent/'fixtures/front-before-suspension.step')
        new = self.body.split(Plane((0,-192.96,0),z_dir=(0,1,0)),Keep.BOTTOM)
        excess = new.cut(old)
        self.assertLess(excess.volume, .001)
        # The complete grip in front of its rear tangent is unchanged.
        plane=Plane((0,-205.275,0),z_dir=(0,1,0))
        old_grip=old.split(plane,Keep.BOTTOM)
        new_grip=new.split(plane,Keep.BOTTOM)
        old_grip=Compound(old_grip) if isinstance(old_grip,list) else old_grip
        new_grip=Compound(new_grip) if isinstance(new_grip,list) else new_grip
        self.assertLess(old_grip.cut(new_grip).volume,.001)

    def test_trunk_has_both_side_walls_and_remains_hollow(self):
        for y in (45,50,55,60):
            for z in (0,10,20,30):
                for side in (-1,1):
                    self.assertTrue(self.body.is_inside(Vector(side*20,y,z)),(side,y,z))
                self.assertFalse(self.body.is_inside(Vector(0,y,z)),(y,z))
        # Follow the extended rear diagonal too; center void and roof stay intact.
        lines=json.loads((Path(__file__).resolve().parents[1]/
            'exports/bottom-outline-proposed-lines.json').read_text())
        a,b=lines['13']
        for y in (70,80,90):
            edge_x=a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
            for z in (0,10,20):
                for side in (-1,1):
                    self.assertTrue(self.body.is_inside(Vector(side*(edge_x-2),y,z)),(side,y,z))
        self.assertTrue(self.body.is_inside(Vector(0,50,44)))

if __name__ == '__main__':
    unittest.main()
