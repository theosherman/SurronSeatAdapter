"""Scope guard: the running dovetail cannot enter the finishing selection."""
import unittest
from body_fillets import SPEC, require_mirrored_selection


class FilletScopeTest(unittest.TestCase):
    def test_one_mm_and_rail_exclusion(self):
        self.assertEqual(SPEC['radiusMm'], 1)
        for edge in SPEC['edges']:
            if edge['maximum'][1] > 188:
                self.assertAlmostEqual(edge['minimum'][1], edge['maximum'][1], places=5)
                self.assertAlmostEqual(edge['minimum'][1], 261.023, delta=.02)

    def test_dovetail_terminal_base_stays_sharp(self):
        # The two shoulders and central foot at the latch entry must not bulge.
        roots = [edge for edge in SPEC['edges']
                 if abs(edge['minimum'][1]-261.01919499428)<.001
                 and abs(edge['maximum'][1]-261.01919499428)<.001
                 and abs(edge['minimum'][2]-edge['maximum'][2])<.001
                 and edge['maximum'][2]<100]
        self.assertEqual(roots, [], 'Latch-entry base edges must stay unfilleted')

    def test_every_selected_edge_has_its_mirror(self):
        for edge in SPEC['edges']:
            reflected_min = [-edge['maximum'][0], *edge['minimum'][1:]]
            reflected_max = [-edge['minimum'][0], *edge['maximum'][1:]]
            mirrors = [other for other in SPEC['edges']
                       if abs(other['length']-edge['length']) < .001
                       and all(abs(a-b)<.001 for a,b in zip(other['minimum'],reflected_min))
                       and all(abs(a-b)<.001 for a,b in zip(other['maximum'],reflected_max))]
            self.assertEqual(len(mirrors), 1, edge)

    def test_runtime_rejects_one_sided_fillets(self):
        edge = dict(length=10, minimum=[1,0,0], maximum=[1,10,0])
        with self.assertRaisesRegex(ValueError, 'no mirrored partner'):
            require_mirrored_selection([edge])
