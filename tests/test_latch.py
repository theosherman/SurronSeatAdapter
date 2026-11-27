"""Checkpoint and geometry checks for the editable latch."""
import unittest


class LatchTests(unittest.TestCase):
    def test_latch_has_one_taper_per_side_at_original_end_widths(self):
        from build123d import GeomType, Vector
        from latch import build_latch
        from trunk_cavity import REAR_WALL_NORMAL

        wall_normal = Vector(REAR_WALL_NORMAL)
        front = Vector(0, 147.526479575834, 31.702071992565) + wall_normal * 0.2
        rear = Vector(0, 219.997761301043, -11.76219965661)
        body = build_latch()
        for sign in (-1, 1):
            sides = [face for face in body.faces()
                     if face.geom_type == GeomType.PLANE
                     and sign * face.normal_at().X > 0.9]
            self.assertEqual(len(sides), 1)
            normal = sides[0].normal_at()
            self.assertAlmostEqual(normal.Z / normal.Y, wall_normal.Z / wall_normal.Y, places=6)
            for datum, width in ((front, 110.0), (rear, 88.47222616882672)):
                edge = datum + Vector(sign * width / 2, 0, 0)
                self.assertAlmostEqual((sides[0].center() - edge).dot(normal), 0, places=6)

    def test_checkpoints_and_model_bounds(self):
        from latch import build_latch
        body, stages = build_latch(with_stages=True)
        expected = [190086.8796, 380173.7593, 276646.8459, 268706.6657, 267191.1742]
        self.assertEqual(len(stages), len(expected))
        for stage, volume in zip(stages, expected):
            self.assertAlmostEqual(stage['volumeMm3'], volume, delta=0.01)
            self.assertTrue(stage['valid'])
            self.assertEqual(stage['solids'], 1)
        bounds = body.bounding_box()
        for actual, wanted in zip(tuple(bounds.min), (-54.694612192,147.800566681,-31.651350849)):
            self.assertAlmostEqual(actual, wanted, delta=0.001)
        for actual, wanted in zip(tuple(bounds.max), (54.694612192,218.033855901,52.116976362)):
            self.assertAlmostEqual(actual, wanted, delta=0.001)

    def test_raised_edge_and_tongue_planes(self):
        from build123d import GeomType, Vector
        from coordinates import ADAPTER_TRANSLATION_MM
        from OCP.BRepAdaptor import BRepAdaptor_Surface
        from latch import build_latch, latch_side_profile

        body = build_latch()
        corner = Vector(0, 219.997761301043, -11.76219965661)
        cylinders = [(face, BRepAdaptor_Surface(face.wrapped).Cylinder().Radius())
                     for face in body.faces().filter_by(GeomType.CYLINDER)]
        tongue_fillet, = [face for face, radius in cylinders if abs(radius - 15) < 1e-6]
        self.assertEqual(sum(abs(radius - 1) < 1e-6 for _, radius in cylinders), 13)
        self.assertEqual(sum(abs(radius - 4.5) < 1e-6 for _, radius in cylinders), 1)
        self.assertLess((tongue_fillet.center() - corner).length, 3)

        # The finishing fillets blend away the short inner tip face.
        sketch_corner = corner - Vector(ADAPTER_TRANSLATION_MM)
        profile_lines = latch_side_profile().edges().filter_by(GeomType.LINE)
        for normal in (Vector(0, .85979329862475, .51064222665185),
                       Vector(0, .88401823052998, -.46745242334450)):
            for offset in (0.2, 0.2 - 25.0):
                matching = [edge for edge in profile_lines
                            if all(abs((Vector(vertex) - sketch_corner).dot(normal) - offset) < 1e-5
                                   for vertex in edge.vertices())]
                self.assertEqual(len(matching), 1)

        # The shelf rises 8 mm in Z from its previous 3 mm normal offset.
        planes = body.faces().filter_by(GeomType.PLANE)
        shelf_normal = Vector(0, .154, -1).normalized()
        shelf, = [face for face in planes if face.normal_at().dot(shelf_normal) > .99999]
        original_shelf = Vector(0, 171.563092565, -8.769549215)
        self.assertAlmostEqual((shelf.center() - original_shelf).dot(shelf_normal),
                               3.0 + 8.0 * shelf_normal.Z, places=5)

    def test_clearance_removes_material_and_rejects_negative(self):
        from latch import build_latch
        nominal = build_latch()
        zero, stages = build_latch(clearance=0, with_stages=True)
        larger = build_latch(clearance=0.3)
        self.assertAlmostEqual(stages[-1]['volumeMm3'], 268706.6657, delta=0.01)
        self.assertLess(zero.volume, stages[-1]['volumeMm3'])
        self.assertLess(larger.volume, nominal.volume)
        self.assertAlmostEqual(nominal.cut(zero).volume, 0, delta=0.001)
        with self.assertRaises(ValueError):
            build_latch(clearance=-0.1)

    def test_three_mating_faces_move_inward_by_clearance(self):
        from latch import build_latch, FEATURES
        from coordinates import source_to_model, ADAPTER_TRANSLATION_MM
        from build123d import GeomType, Vector
        body = build_latch(clearance=0.2)
        for selector in FEATURES[106]['inputFaces']:
            normal = Vector(source_to_model(selector['geometry']['normal']))
            if selector['isParamReversed']:
                normal = -normal
            origin = Vector(source_to_model(selector['geometry']['origin'])) + Vector(ADAPTER_TRANSLATION_MM)
            shifted = [f for f in body.faces() if f.geom_type == GeomType.PLANE
                       and f.normal_at().dot(normal)>1-1e-7
                       and abs((f.center()-origin).dot(normal)+0.2)<1e-6]
            self.assertTrue(shifted, selector['point'])

    def test_dovetail_uses_shared_master_profile(self):
        from copy import deepcopy
        import adapter
        from latch import build_latch
        selected = next(p for p in adapter.RECIPE['selectedProfiles'] if p['sourceTimelineIndex']==18)
        saved = deepcopy(selected['profiles'])
        baseline = build_latch()
        try:
            # Symmetric width increase in the actual master profile data must
            # propagate into the latch's cut, without changing its outer frame.
            for profile in selected['profiles']:
                for loop in profile['loops']:
                    for curve in loop['curves']:
                        for key in ('startMm','endMm'):
                            if key in curve:
                                curve[key][0] *= 1.02
            widened = build_latch()
            self.assertLess(widened.volume, baseline.volume-100)
        finally:
            selected['profiles'] = saved
        self.assertAlmostEqual(build_latch().volume, baseline.volume, delta=0.001)
