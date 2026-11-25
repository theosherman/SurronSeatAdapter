"""Scope guard: the running dovetail cannot enter the finishing selection."""
import unittest
from body_fillets import SPEC, require_mirrored_selection


class FilletScopeTest(unittest.TestCase):
    def test_one_mm_and_rail_exclusion(self):
        self.assertEqual(SPEC['radiusMm'], 1)
        for edge in SPEC['edges']:
            lo, hi = edge['minimum'], edge['maximum']
            # The rail and its lead-ins occupy the lower center of the rear.
            # The seat support is above it, and the side reliefs are outboard.
            if hi[1] > 188 and lo[0] < 23.001 and hi[0] > -23.001 and lo[2] < 90:
                self.assertAlmostEqual(lo[1], hi[1], places=5)
                self.assertAlmostEqual(lo[1], 261.023, delta=.02)

    def test_body_junction_of_dovetail_stays_sharp(self):
        # Five connected edges form the shoulders and trapezoid where the rail
        # grows out of the rear body wall, not its far end at Y=261 mm.
        root = [edge for edge in SPEC['edges']
                if 147 < edge['minimum'][1] < 152
                and 147 < edge['maximum'][1] < 152
                and 24 < edge['minimum'][2] < 32
                and 24 < edge['maximum'][2] < 32]
        self.assertEqual(root, [], 'Highlighted body/rail junction must stay sharp')

    def test_dovetail_junction_side_returns_stay_sharp(self):
        # The highlighted U-shaped return on each side of the root.
        returns = [edge for edge in SPEC['edges']
                   if 147 < edge['minimum'][1] and edge['maximum'][1] < 179
                   and 24 < edge['minimum'][2] and edge['maximum'][2] < 50
                   and max(abs(edge['minimum'][0]),abs(edge['maximum'][0])) < 15]
        self.assertEqual(returns, [], 'Both mirrored root-side returns must stay sharp')

    def test_every_selected_edge_has_its_mirror(self):
        for edge in SPEC['edges']:
            reflected_min = [-edge['maximum'][0], *edge['minimum'][1:]]
            reflected_max = [-edge['minimum'][0], *edge['maximum'][1:]]
            mirrors = [other for other in SPEC['edges']
                       if abs(other['length']-edge['length']) < .001
                       and all(abs(a-b)<.001 for a,b in zip(other['minimum'],reflected_min))
                       and all(abs(a-b)<.001 for a,b in zip(other['maximum'],reflected_max))]
            self.assertEqual(len(mirrors), 1, edge)

    def test_runtime_rejects_different_mirrored_radii(self):
        left = dict(length=10, minimum=[-1,0,0], maximum=[-1,10,0], radiusMm=5)
        right = dict(length=10, minimum=[1,0,0], maximum=[1,10,0])
        with self.assertRaisesRegex(ValueError, 'no mirrored partner'):
            require_mirrored_selection([left, right])

    def test_runtime_rejects_one_sided_fillets(self):
        edge = dict(length=10, minimum=[1,0,0], maximum=[1,10,0])
        with self.assertRaisesRegex(ValueError, 'no mirrored partner'):
            require_mirrored_selection([edge])
