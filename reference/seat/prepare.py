"""Save the stud-corrected seat mesh in the adapter frame."""
from argparse import ArgumentParser
from pathlib import Path
from struct import unpack_from

import numpy as np

SEAT_DIR = Path(__file__).resolve().parent
SOURCE = SEAT_DIR / 'LunaSurronSeat_Studs_5p3x15.stl'
OUTPUT = SEAT_DIR / 'surron-seat.stl'

# Stud bases in scan coordinates, matched to the rear and front hole mouths
# on the placed adapter. Each pair is ordered by increasing model X.
SEAT_STUD_BASES = np.array([
    [24.70667, 15.33698, 475.16435],
    [14.98497, 42.77187, 469.04293],
    [266.48427, 98.95719, 505.11411],
    [250.87502, 141.84964, 494.85075],
])
ADAPTER_HOLE_MOUTHS = np.array([
    [-14.5, 178.99538, 81.07012],
    [14.5, 178.99538, 81.07012],
    [-23, -76.74852, 44.00181],
    [23, -76.74852, 44.00181],
])

def place_seat(vertices):
    """Fit the four stud bases with a proper rotation and translation."""
    source_center = SEAT_STUD_BASES.mean(axis=0)
    target_center = ADAPTER_HOLE_MOUTHS.mean(axis=0)
    covariance = (SEAT_STUD_BASES - source_center).T @ (ADAPTER_HOLE_MOUTHS - target_center)
    left, _, right = np.linalg.svd(covariance)
    left[:, -1] *= np.linalg.det(left @ right)
    return (vertices - source_center) @ (left @ right) + target_center


def main():
    ArgumentParser(description=__doc__).parse_args()
    data = bytearray(SOURCE.read_bytes())
    count, = unpack_from('<I', data, 80)
    if not count or len(data) != 84 + count * 50:
        raise ValueError(f'{SOURCE} is not a binary STL')

    facets = np.ndarray((count, 4, 3), dtype='<f4', buffer=data, offset=84, strides=(50, 12, 4))
    vertices = place_seat(facets[:, 1:])
    sides = vertices[:, 1:] - vertices[:, :1]
    normals = np.cross(sides[:, 0], sides[:, 1])
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    facets[:, 0] = np.divide(normals, lengths, out=np.zeros_like(normals), where=lengths > 0)
    facets[:, 1:] = vertices
    OUTPUT.write_bytes(data)
    print(OUTPUT)


if __name__ == '__main__':
    main()
