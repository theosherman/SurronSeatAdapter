"""Approved preview is an independent acceptance fixture for native manufacture."""
import json
from pathlib import Path
import unittest
from build123d import Edge, Wire, Face, Solid, Compound, ShapeList, Plane
from adapter import build_master, tool
from coordinates import ADAPTER_TRANSLATION_MM, source_to_model

class SuspensionOutlineTests(unittest.TestCase):
    def test_native_blank_matches_approved_outline(self):
        lines = json.loads((Path(__file__).parent/'fixtures/accepted-dimensions.json').read_text())['bottomOutlineLines']
        def wire(ids):
            return Wire([Edge.make_line((*lines[str(i)][0], 0), (*lines[str(i)][1], 0)) for i in ids])
        outline = Face(wire([i for i in range(1,19) if str(i) in lines]), [wire(range(19,23))])
        outline = outline.translate(tuple(-v for v in ADAPTER_TRANSLATION_MM))
        expected = Solid.extrude(outline.translate((0,0,-50)), (0,0,200))
        half = build_master(stop='M01')
        actual = half.fuse(half.mirror(Plane.YZ))
        self.assertLess(actual.cut(expected).volume, .001)
        self.assertLess(expected.cut(actual).volume, .001)
        clipped = expected.intersect(tool(12,120,source_to_model([1,0,0])))
        clipped = Compound(clipped) if isinstance(clipped, ShapeList) else clipped
        clipped = clipped.intersect(tool(14,490,source_to_model([0,1,0])))
        clipped = Compound(clipped) if isinstance(clipped, ShapeList) else clipped
        expected_base = clipped.fuse(clipped.mirror(Plane.YZ))
        base = build_master(stop='M05')
        self.assertTrue(base.is_valid)
        self.assertEqual(len(base.solids()), 1)
        self.assertLess(base.cut(expected_base).volume, .001)
        self.assertLess(expected_base.cut(base).volume, .001)

if __name__ == '__main__':
    unittest.main()
