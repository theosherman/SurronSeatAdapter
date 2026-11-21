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

    def test_raised_grip_preserved_outside_redesigned_connection(self):
        old = import_step(Path(__file__).parent/'fixtures/front-before-suspension.step').translate((0,0,23))
        # Raising the clip requires the existing fixed printing planes to trim
        # its outer sides. Compare both grips inside those same half-spaces.
        from build123d import GeomType
        for face in self.body.faces():
            normal=face.normal_at()
            if (face.geom_type==GeomType.PLANE and face.area>5000
                and face.center().Y>0 and abs(normal.X)>.85
                and .4<normal.Z<.5 and abs(normal.Y)<1e-8):
                old=old.split(Plane(face.center(),z_dir=normal),Keep.BOTTOM)
        # The tangent trim begins around Y=-217.21. The jaw forward of
        # Y=-218 retains its original geometry, translated exactly 23 mm.
        plane=Plane((0,-218,0),z_dir=(0,1,0))
        old_grip=old.split(plane,Keep.BOTTOM)
        new_grip=self.body.split(plane,Keep.BOTTOM)
        old_grip=Compound(old_grip) if isinstance(old_grip,list) else old_grip
        new_grip=Compound(new_grip) if isinstance(new_grip,list) else new_grip
        self.assertLess(old_grip.cut(new_grip).volume,.001)
        self.assertLess(new_grip.cut(old_grip).volume,.001)

    def test_trunk_has_both_side_walls_and_open_middle(self):
        for y in (45,50,55,60):
            for z in (5,10,20,30):
                for side in (-1,1):
                    self.assertTrue(self.body.is_inside(Vector(side*20,y,z)),(side,y,z))
                self.assertFalse(self.body.is_inside(Vector(0,y,z)),(y,z))
        # Follow the extended rear diagonal too; rear diagonal and roof stay intact.
        lines=json.loads((Path(__file__).parent/'fixtures/accepted-dimensions.json').read_text())['bottomOutlineLines']
        a,b=lines['13']
        for y in (70,80,90):
            edge_x=a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
            for z in (0,10,20):
                for side in (-1,1):
                    self.assertTrue(self.body.is_inside(Vector(side*(edge_x-2),y,z)),(side,y,z))
        self.assertTrue(self.body.is_inside(Vector(0,50,44)))

if __name__ == '__main__':
    unittest.main()
