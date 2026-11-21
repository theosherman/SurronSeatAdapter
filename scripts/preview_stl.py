"""Write one offline interactive preview for a set of binary STL exports."""
from argparse import ArgumentParser
from base64 import b64encode
from gzip import compress
from html import escape
from pathlib import Path
from struct import pack

import numpy as np

TRIANGLE = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])
TEMPLATE = Path(__file__).with_name('stl_preview.html')
PARTS = {
    'adapter-body-split-front': ('Split front', '#5ea5e7'),
    'adapter-body-split-rear': ('Split rear', '#efa55b'),
    'butterfly-key-top': ('Top key', '#65cf92'),
    'butterfly-key-cavity': ('Cavity key', '#65cf92'),
    'latch': ('Latch', '#c0a5eb'),
    'adapter-body': ('Full adapter', '#4abdc7'),
    'merged': ('EUC', '#788698'),
    'surron-seat': ('Surron Seat', '#a69680'),
}
SPLIT_PARTS = {'adapter-body-split-front', 'adapter-body-split-rear',
               'butterfly-key-top', 'butterfly-key-cavity'}
REFERENCES = {'merged', 'surron-seat'}


def read_mesh(stl):
    step = stl.with_suffix('.step')
    if stl.stem in ('butterfly-key-top', 'butterfly-key-cavity') and step.is_file():
        # The printable key meshes are laid flat. The STEPs preserve the seated pose.
        from build123d import import_step

        vertices, triangles = import_step(step).tessellate(.005, .05)
        return np.asarray([tuple(vertex) for vertex in vertices]), np.asarray(triangles)

    raw = stl.read_bytes()
    triangles = int.from_bytes(raw[80:84], 'little')
    if not triangles or len(raw) != 84 + TRIANGLE.itemsize * triangles:
        raise ValueError(f'{stl} is not a nonempty binary STL')
    coordinates = np.frombuffer(raw, dtype=TRIANGLE, offset=84)['vertices'].reshape(-1, 3)
    return np.unique(coordinates, axis=0, return_inverse=True)


def write_preview(stls, output):
    stls = [stl for stl in stls if stl.stem != 'adapter-body-pre-imprint']
    if not stls:
        raise ValueError('No previewable STL files')
    meshes = [read_mesh(stl) for stl in stls]
    if any(not vertices.size or not np.isfinite(vertices).all() for vertices, _ in meshes):
        raise ValueError('Preview meshes must have finite vertices')
    low = np.min([vertices.min(axis=0) for vertices, _ in meshes], axis=0)
    high = np.max([vertices.max(axis=0) for vertices, _ in meshes], axis=0)
    center = (low + high) / 2
    radius = max(np.linalg.norm(vertices - center, axis=1).max() for vertices, _ in meshes)
    if radius <= 0:
        raise ValueError('Preview meshes have invalid bounds')

    controls = []
    payloads = []
    for index, (stl, (vertices, indices)) in enumerate(zip(stls, meshes, strict=True)):
        name, color = PARTS.get(stl.stem, (stl.stem, '#4abdc7'))
        checked = '' if stl.stem in REFERENCES else ' checked'
        variant = 'split' if stl.stem in SPLIT_PARTS else 'adapter'
        if stl.stem in REFERENCES or stl.stem == 'latch':
            variant = 'both'
        controls.append(f'<label data-variant="{variant}">'
                        f'<input type="checkbox" data-color="{color}"{checked}>'
                        f'{escape(name)}</label>')
        packed = pack('<I', len(vertices)) + ((vertices - center) / radius).astype('<f4').tobytes()
        packed += indices.astype('<u4').tobytes()
        payload = b64encode(compress(packed, compresslevel=6, mtime=0)).decode('ascii')
        payloads.append(f'<script id="mesh-{index}" type="application/octet-stream">{payload}</script>')

    output.write_text(TEMPLATE.read_text().replace('__CONTROLS__', '\n'.join(controls))
                      .replace('__MESHES__', '\n'.join(payloads)), encoding='utf-8')
    return output


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('stls', nargs='*', type=Path)
    args = parser.parse_args()
    exports = Path('exports')
    order = {name: index for index, name in enumerate(PARTS)}
    stls = args.stls or sorted(exports.glob('*.stl'),
                              key=lambda path: (order.get(path.stem, len(order)), path.name))
    if not stls:
        parser.error('No STL files found in exports/')
    if not args.stls:
        euc = exports / 'sherman-p-prepared' / 'merged.stl'
        if euc.is_file():
            stls.append(euc)
        seat = Path('reference/fusion/surron-seat.stl')
        if seat.is_file() and exports / seat.name not in stls:
            stls.append(seat)
    print(write_preview(stls, stls[0].with_name('preview.html')))


if __name__ == '__main__':
    main()
