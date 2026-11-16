"""Scope guard: the running dovetail cannot enter the finishing selection."""
import unittest
from body_fillets import SPEC


class FilletScopeTest(unittest.TestCase):
    def test_one_mm_and_rail_exclusion(self):
        self.assertEqual(SPEC['radiusMm'], 1)
        for edge in SPEC['edges']:
            if edge['maximum'][1] > 188:
                self.assertAlmostEqual(edge['minimum'][1], edge['maximum'][1], places=5)
                self.assertAlmostEqual(edge['minimum'][1], 261.023, delta=.02)
