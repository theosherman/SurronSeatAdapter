"""Write offline interactive previews alongside binary STL exports."""
from argparse import ArgumentParser
from base64 import b64encode
from gzip import compress
from html import escape
from pathlib import Path
from struct import pack

import numpy as np

TRIANGLE = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])
TEMPLATE = Path(__file__).with_name('stl_preview.html')


def write_preview(stl):
    raw = stl.read_bytes()
    triangles = int.from_bytes(raw[80:84], 'little')
    if not triangles or len(raw) != 84 + TRIANGLE.itemsize * triangles:
        raise ValueError(f'{stl} is not a nonempty binary STL')
    coordinates = np.frombuffer(raw, dtype=TRIANGLE, offset=84)['vertices'].reshape(-1, 3)
    vertices, indices = np.unique(coordinates, axis=0, return_inverse=True)
    low, high = vertices.min(axis=0), vertices.max(axis=0)
    vertices = vertices - (low + high) / 2
    radius = np.linalg.norm(vertices, axis=1).max()
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError(f'{stl} has invalid bounds')
    packed = pack('<I', len(vertices)) + (vertices / radius).astype('<f4').tobytes()
    packed += indices.astype('<u4').tobytes()
    payload = b64encode(compress(packed, compresslevel=6, mtime=0)).decode('ascii')
    output = stl.with_suffix('.preview.html')
    output.write_text(TEMPLATE.read_text().replace('__MESH__', payload).replace('__PART__', escape(stl.name)),
                      encoding='utf-8')
    return output


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('stls', nargs='*', type=Path)
    args = parser.parse_args()
    stls = args.stls or sorted(Path('exports').glob('*.stl'))
    if not stls:
        parser.error('No STL files found in exports/')
    for stl in stls:
        print(write_preview(stl))


if __name__ == '__main__':
    main()
