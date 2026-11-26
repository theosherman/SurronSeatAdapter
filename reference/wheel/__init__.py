"""Checked-in Sherman P references in the adapter's millimeter frame."""
from pathlib import Path

WHEEL_REFERENCE = Path(__file__).resolve().parent
SEAT_LOWERING_MM = 20.0  # Relative to the printed 8 mm deeper-seating revision.
SEATING_DEPTH_MM = 8.0 + SEAT_LOWERING_MM
PREPARED_SEATING_DEPTH_MM = 26.0
WHEEL_RISE_MM = SEATING_DEPTH_MM - PREPARED_SEATING_DEPTH_MM


def load_wheel_cutter():
    from build123d import import_brep

    return import_brep(WHEEL_REFERENCE / 'body-scaled.brep').translate((0, 0, WHEEL_RISE_MM))
