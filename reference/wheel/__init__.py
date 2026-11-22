"""Checked-in Sherman P references in the adapter's millimeter frame."""
from pathlib import Path

WHEEL_REFERENCE = Path(__file__).resolve().parent
SEAT_LOWERING_MM = 18.0  # Relative to the printed 8 mm deeper-seating revision.
SEATING_DEPTH_MM = 8.0 + SEAT_LOWERING_MM
