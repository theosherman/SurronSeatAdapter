"""Acceptance checks for the approved real rear-wall move and cavity reduction."""
import unittest
from build123d import GeomType,Vector
from adapter import build_master

class RearCavityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=build_master(imprint=False)
        cls.original=build_master(imprint=False,rear_wall_move=0,rear_wall_extra=0)
        from latch import build_latch
        cls.source_latch=build_latch(rear_wall_move=0)
        cls.latch=build_latch(adapter_body=cls.body)

    def test_cavity_rear_plane_is_twenty_mm_inward(self):
        # Saved original cavity plane: now 10 mm movement + 10 mm addition in Y.
        p=Vector(0,133.1140784829675,11.036531871516697)
        n=Vector(0,-.8949343616021163,-.44619781310962575)
        matches=[f for f in self.body.faces() if f.area>1500
                 and f.normal_at().dot(n)>1-1e-7
                 and abs((f.center()-p).dot(n))<.001]
        self.assertTrue(matches,'Cavity rear boundary did not move inward 20 mm')

    def test_latch_facing_wall_is_ten_mm_inward(self):
        p=Vector(0,155.41714823915711,1.578677917809248)
        n=Vector(0,.8597932986247546,.5106422266518543)
        self.assertTrue(any(f.geom_type==GeomType.PLANE and f.area>2000
                            and f.normal_at().dot(n)>1-1e-7
                            and abs((f.center()-p).dot(n))<.001
                            for f in self.body.faces()),'Outer wall did not move inward 10 mm')

    def test_front_and_upper_seat_structure_stay_fixed(self):
        from build123d import Solid,Plane
        from rear_cavity import combined
        for region in [Solid.make_box(400,600,300,Plane((-200,-500,-100))),
                       Solid.make_box(400,1000,200,Plane((-200,-500,60.001)))]:
            old=combined(self.original.intersect(region));new=combined(self.body.intersect(region))
            self.assertLess(combined(old.cut(new)).volume+combined(new.cut(old)).volume,.001)

    def test_latch_contact_face_and_hook_stay_fixed(self):
        from build123d import Plane,Keep
        from rear_cavity import combined
        contact=max((f for f in self.source_latch.faces() if f.geom_type==GeomType.PLANE
                     and f.normal_at().Y>.8 and f.normal_at().Z>.4),key=lambda f:f.area)
        p,n=contact.center(),contact.normal_at()
        faces=[f for f in self.latch.faces() if f.geom_type==GeomType.PLANE
               and f.normal_at().dot(n)>1-1e-8 and abs((f.center()-p).dot(n))<1e-6]
        self.assertAlmostEqual(sum(f.area for f in faces),contact.area,delta=.001)
        hook=combined(self.source_latch.split(Plane((0,0,0),z_dir=(0,0,1)),Keep.BOTTOM))
        self.assertLess(combined(hook.cut(self.latch)).volume,.001)
        hook_zone=Plane((0,0,-25),z_dir=(0,0,1))
        old_hook=combined(self.source_latch.split(hook_zone,Keep.BOTTOM))
        new_hook=combined(self.latch.split(hook_zone,Keep.BOTTOM))
        self.assertLess(combined(old_hook.cut(new_hook)).volume+combined(new_hook.cut(old_hook)).volume,.001)
        self.assertGreater(self.latch.volume,self.source_latch.volume+10000)

    def test_extended_latch_is_separate_and_has_planar_running_clearance(self):
        from rear_cavity import combined
        self.assertTrue(self.body.is_valid and self.latch.is_valid)
        self.assertEqual(len(self.latch.solids()),1)
        self.assertLess(combined(self.body.intersect(self.latch)).volume,.001)
        # Clearance is defined on mating-plane interiors; source cylindrical
        # and spline junctions have exact contacts and are not global offsets.
        for point in [(0,168.7767,40.9574),(12.2614,153.7798,36.7995),
                      (-12.2614,153.7798,36.7995)]:
            self.assertGreaterEqual(self.latch.distance_to(Vector(point)),.199,point)
        p=Vector(0,155.41714823915711,1.578677917809248)
        n=Vector(0,.8597932986247546,.5106422266518543)
        # The mating face normal points toward the adapter, opposite its outward normal.
        faces=[f for f in self.latch.faces() if f.geom_type==GeomType.PLANE
               and f.normal_at().dot(-n)>1-1e-7
               and abs((f.center()-p).dot(n)-.2)<1e-5]
        self.assertTrue(faces,'New latch mating plane must retain 0.2 mm clearance')

    def test_rear_screwdriver_paths_remain_open_below_the_ceilings(self):
        from adapter import SKETCHES
        from coordinates import ADAPTER_TRANSLATION_MM
        bolt=SKETCHES['BoltHolesSketch'] # Already in model coordinates.
        origin=Vector(bolt['originMm'])+Vector(ADAPTER_TRANSLATION_MM)
        x,y,n=map(Vector,(bolt['xAxis'],bolt['yAxis'],bolt['normal']))
        for u in (-14.5,14.5):
            cap=origin+x*u+y*193.9428441873774-n*3
            for depth in (1,10,18,19,20,21,22,23,25,35,50):
                for dx in (-6,0,6):
                    p=cap-n*depth+Vector(dx,0,0)
                    self.assertFalse(self.body.is_inside(p),(u,depth,dx,tuple(p)))

    def test_invalid_dimensions_fail_before_native_operations(self):
        from rear_cavity import revise_rear_wall
        for move,extra in [(-1,10),(10,-1),(float('nan'),10),(10,float('inf'))]:
            with self.assertRaises(ValueError):revise_rear_wall(self.original,move,extra)

if __name__=='__main__':unittest.main()

