"""Regression checks for the split adapter's cavity butterfly keys."""
import unittest
from pathlib import Path

from build123d import import_step

from split_adapter import build_split


class SplitAdapterTests(unittest.TestCase):
    def test_exterior_recesses_do_not_break_into_cavity_butterflies(self):
        master = import_step(Path(__file__).resolve().parents[1] / 'exports/adapter-body.step')
        rear = dict(build_split(master))['rear']
        for side in (-1, 1):
            with self.subTest(side=side):
                # The exterior tool used to remove this point beside the lower wing.
                self.assertTrue(rear.is_inside((side * 47.0804, 105.5344, 7.884)))
