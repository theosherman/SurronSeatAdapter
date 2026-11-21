"""Write an offline interactive preview from STEP parts and binary STL meshes."""
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


def read_mesh(path):
    step = path.with_suffix('.step')
    if path.suffix.lower() == '.step' or (
            path.stem in ('butterfly-key-top', 'butterfly-key-cavity') and step.is_file()):
        # The printable key meshes are laid flat. The STEPs preserve the seated pose.
        from build123d import import_step

        vertices, triangles = import_step(path if path.suffix.lower() == '.step' else step).tessellate(.05, .15)
        unique, indices = np.unique(np.asarray([tuple(vertex) for vertex in vertices]),
                                    axis=0, return_inverse=True)
        return unique, indices[np.asarray(triangles)]

    raw = path.read_bytes()
    triangles = int.from_bytes(raw[80:84], 'little')
    if not triangles or len(raw) != 84 + TRIANGLE.itemsize * triangles:
        raise ValueError(f'{path} is not a nonempty binary STL')
    coordinates = np.frombuffer(raw, dtype=TRIANGLE, offset=84)['vertices'].reshape(-1, 3)
    return np.unique(coordinates, axis=0, return_inverse=True)


def write_preview(paths, output):
    paths = [path for path in paths if path.stem != 'adapter-body-pre-imprint']
    if not paths:
        raise ValueError('No previewable CAD files')
    meshes = [read_mesh(path) for path in paths]
    if any(not vertices.size or not np.isfinite(vertices).all() for vertices, _ in meshes):
        raise ValueError('Preview meshes must have finite vertices')
    low = np.min([vertices.min(axis=0) for vertices, _ in meshes], axis=0)
    high = np.max([vertices.max(axis=0) for vertices, _ in meshes], axis=0)
    center = (low + high) / 2
    radius = max(np.linalg.norm(vertices - center, axis=1).max() for vertices, _ in meshes)
    if radius <= 0:
        raise ValueError('Preview meshes have invalid bounds')

    controls = []
    euc_control = ''
    payloads = []
    for index, (path, (vertices, indices)) in enumerate(zip(paths, meshes, strict=True)):
        stem = path.stem
        name, color = PARTS.get(stem, (stem, '#4abdc7'))
        checked = '' if stem in REFERENCES else ' checked'
        variant = 'split' if stem in SPLIT_PARTS else 'adapter'
        if stem in REFERENCES or stem == 'latch':
            variant = 'both'
        control = (f'<label data-variant="{variant}">'
                   f'<input type="checkbox" data-mesh="{index}" data-color="{color}"{checked}>'
                   f'{escape(name)}</label>')
        if stem == 'merged' and not euc_control:
            euc_control = control
        else:
            controls.append(control)
        packed = pack('<I', len(vertices)) + ((vertices - center) / radius).astype('<f4').tobytes()
        packed += indices.astype('<u4').tobytes()
        payload = b64encode(compress(packed, compresslevel=6, mtime=0)).decode('ascii')
        payloads.append(f'<script id="mesh-{index}" type="application/octet-stream">{payload}</script>')

    output.write_text(TEMPLATE.read_text().replace('__CONTROLS__', '\n'.join(controls))
                      .replace('__EUC__', euc_control)
                      .replace('__MESHES__', '\n'.join(payloads)), encoding='utf-8')
    return output


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('parts', nargs='*', type=Path, help='STEP or binary STL files')
    args = parser.parse_args()
    exports = Path('exports')
    order = {name: index for index, name in enumerate(PARTS)}
    parts = args.parts or sorted(exports.glob('*.step'),
                                key=lambda path: (order.get(path.stem, len(order)), path.name))
    if not parts:
        parser.error('No STEP files found in exports/')
    if not args.parts:
        euc = exports / 'sherman-p-prepared' / 'merged.stl'
        if euc.is_file():
            parts.append(euc)
        for seat in (exports / 'surron-seat.stl', Path('reference/fusion/surron-seat.stl')):
            if seat.is_file() and seat.stem not in {part.stem for part in parts}:
                parts.append(seat)
                break
    print(write_preview(parts, parts[0].with_name('preview.html')))


if __name__ == '__main__':
    main()
