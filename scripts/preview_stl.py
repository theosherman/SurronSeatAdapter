"""Write an offline interactive preview from STEP parts and binary STL meshes."""
from argparse import ArgumentParser
from base64 import b64encode
from gzip import compress
from html import escape
from json import dumps
from pathlib import Path
from struct import pack

import numpy as np

TRIANGLE = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])
TEMPLATE = Path(__file__).with_name('stl_preview.html')
REFERENCE_DIR = Path(__file__).resolve().parents[1] / 'reference'
REFERENCE_MESHES = (REFERENCE_DIR / 'wheel/merged.stl', REFERENCE_DIR / 'seat/surron-seat.stl')
PARTS = {
    'adapter-body-split-front': ('Split front', '#5ea5e7'),
    'adapter-body-split-rear': ('Split rear', '#efa55b'),
    'butterfly-key-top': ('Top key', '#65cf92'),
    'butterfly-key-cavity': ('Cavity key', '#65cf92'),
    'latch': ('Latch', '#c0a5eb'),
    'adapter-body': ('Full adapter', '#4abdc7'),
    'merged': ('EUC', '#788698'),
    'surron-seat': ('Seat', '#a69680'),
}
SPLIT_PARTS = {'adapter-body-split-front', 'adapter-body-split-rear',
               'butterfly-key-top', 'butterfly-key-cavity'}
REFERENCES = {'merged', 'surron-seat'}
TOP, BOTTOM = (0, 0, 1), (0, 0, -1)
# Placed model coordinates in millimeters, with a preferred viewing direction.
# Openings are marked at their mouths so their labels stay near the visible rim.
FEATURE_LABELS = {
    ('adapter-body', 'adapter-body-split-front'): (
        ('Front clip', (0, -225, 66.8), TOP),
        ('Screen opening', (0, -150, 37), TOP),
        ('AirTag pocket', (0, 20, 48.7), TOP),
        ('Front mounting holes', (23, -76.4, 44.5), TOP),
        ('Underside cavity', (0, 42, 34.3), BOTTOM),
        ('Clip bore', (0, -220.4, 40.9), BOTTOM),
        ('Screen ramp', (0, -194, 50), (0, .7, .7)),
        ('Screen side wall', (47, -167, 37.7), TOP),
        ('Front seat support', (50, -90, 39.7), TOP),
        ('Front screw access', (23, -76.4, 15), BOTTOM),
        ('Wheel imprint', (38, -70, 9.6), BOTTOM),
        ('Cavity roof', (0, -38, 18), BOTTOM),
    ),
    ('adapter-body', 'adapter-body-split-rear'): (
        ('Rear dovetail', (0, 207.47, 58), (0, .51, -.86)),
        ('Rear mounting holes', (14.5, 179.5, 81), TOP),
        ('Rear seat support', (30, 215, 94.9), TOP),
        ('Rear bridge', (0, 145, 74.2), TOP),
        ('Rear side relief', (55, 140, 24), (.85, .25, 0)),
        ('Lower rear toe', (0, 166, -24.4), (0, .7, -.7)),
        ('Latch wall', (0, 165.4, 1.6), (0, .86, .51)),
        ('Rear screw access', (14.5, 179.5, 42), BOTTOM),
    ),
    ('adapter-body-split-front', 'adapter-body-split-rear'): (
        ('Split seam', (33, 94, 62.3), TOP),
        ('Top key recess', (0, 97, 64.4), TOP),
        ('Cavity key recess', (51, 100.2, 15), (-.6, 0, -.8)),
    ),
    ('butterfly-key-top',): (
        ('Top butterfly key', (0, 94, 58), TOP),
    ),
    ('butterfly-key-cavity',): (
        ('Cavity butterfly key', (-51, 100.2, 15), (.6, 0, -.8)),
    ),
    ('latch',): (
        ('Latch tongue', (0, 216.498, -18.381), (0, .884, -.467)),
    ),
}

FACE_PREFIXES = {
    'adapter-body-split-front': 'Front face',
    'adapter-body-split-rear': 'Rear face',
    'latch': 'Latch face',
    'butterfly-key-top': 'Top key face',
    'butterfly-key-cavity': 'Cavity key face',
}


def planar_labels(shape, stem):
    from build123d import GeomType

    faces = [face for face in shape.faces() if face.geom_type == GeomType.PLANE]
    if not faces:
        return []
    # Keep the larger CAD faces and omit small imprint facets and blends.
    minimum_area = min(120, max(face.area for face in faces) * .02)
    faces = sorted((face for face in faces if face.area >= minimum_area),
                   key=lambda face: (-round(face.area, 6), tuple(face.center())))
    prefix = FACE_PREFIXES.get(stem, 'Face')
    labels = []
    for number, face in enumerate(faces, start=1):
        vertices, triangles = face.tessellate(.05, .15)
        if triangles:
            # A triangle centroid stays inside the trimmed face, even around holes.
            corners = np.asarray([tuple(vertex) for vertex in vertices])[triangles]
            areas = np.linalg.norm(np.cross(corners[:, 1] - corners[:, 0],
                                            corners[:, 2] - corners[:, 0]), axis=1)
            point = corners[areas.argmax()].mean(axis=0)
            labels.append((f'{prefix} {number}', point, tuple(face.normal_at())))
    return labels


def read_mesh(path, shape=None):
    step = path.with_suffix('.step')
    if shape is not None or path.suffix.lower() == '.step' or (
            path.stem in ('butterfly-key-top', 'butterfly-key-cavity') and step.is_file()):
        # The printable key meshes are laid flat. The STEPs preserve the seated pose.
        from build123d import import_step

        if shape is None:
            shape = import_step(path if path.suffix.lower() == '.step' else step)
        vertices, triangles = shape.tessellate(.05, .15)
        unique, indices = np.unique(np.asarray([tuple(vertex) for vertex in vertices]),
                                    axis=0, return_inverse=True)
        faces = [] if path.stem in REFERENCES else planar_labels(shape, path.stem)
        return unique, indices[np.asarray(triangles)], faces

    raw = path.read_bytes()
    triangles = int.from_bytes(raw[80:84], 'little')
    if not triangles or len(raw) != 84 + TRIANGLE.itemsize * triangles:
        raise ValueError(f'{path} is not a nonempty binary STL')
    coordinates = np.frombuffer(raw, dtype=TRIANGLE, offset=84)['vertices'].reshape(-1, 3)
    vertices, indices = np.unique(coordinates, axis=0, return_inverse=True)
    return vertices, indices, []


def write_preview(paths, output, *, shapes=None):
    paths = [path for path in paths if path.stem != 'adapter-body-pre-imprint']
    if not paths:
        raise ValueError('No previewable CAD files')
    shapes = {} if shapes is None else shapes
    meshes = [read_mesh(path, shapes.get(path)) for path in paths]
    if any(not vertices.size or not np.isfinite(vertices).all() for vertices, _, _ in meshes):
        raise ValueError('Preview meshes must have finite vertices')
    low = np.min([vertices.min(axis=0) for vertices, _, _ in meshes], axis=0)
    high = np.max([vertices.max(axis=0) for vertices, _, _ in meshes], axis=0)
    center = (low + high) / 2
    radius = max(np.linalg.norm(vertices - center, axis=1).max() for vertices, _, _ in meshes)
    if radius <= 0:
        raise ValueError('Preview meshes have invalid bounds')

    controls = []
    reference_controls = []
    payloads = []
    for index, (path, (vertices, indices, _)) in enumerate(zip(paths, meshes, strict=True)):
        stem = path.stem
        name, color = PARTS.get(stem, (stem, '#4abdc7'))
        variant = 'split' if stem in SPLIT_PARTS else 'adapter'
        if stem in REFERENCES or stem == 'latch':
            variant = 'both'
        mesh_attributes = f'data-mesh="{index}" data-color="{color}"'
        if stem in REFERENCES:
            midpoint = ((vertices.min(axis=0) + vertices.max(axis=0)) / 2 - center) / radius
            position = ' '.join(str(value) for value in midpoint)
            reference_controls.append(
                f'<label class="reference-opacity" data-variant="{variant}">{escape(name)}'
                f'<input type="range" min="0" max="100" value="0" {mesh_attributes}'
                f' data-center="{position}" aria-label="{escape(name)} opacity">'
                '<span aria-hidden="true">0%</span></label>')
        else:
            controls.append(f'<label data-variant="{variant}">'
                            f'<input type="checkbox" {mesh_attributes} checked>'
                            f'{escape(name)}</label>')
        packed = pack('<I', len(vertices)) + ((vertices - center) / radius).astype('<f4').tobytes()
        packed += indices.astype('<u4').tobytes()
        payload = b64encode(compress(packed, compresslevel=6, mtime=0)).decode('ascii')
        payloads.append(f'<script id="mesh-{index}" type="application/octet-stream">{payload}</script>')

    labels = []
    for stems, features in FEATURE_LABELS.items():
        owners = [index for index, path in enumerate(paths) if path.stem in stems]
        if owners:
            labels.extend(dict(name=name, meshes=owners, point=((point - center) / radius).tolist(),
                               normal=normal) for name, point, normal in features)
    for index, (_, _, faces) in enumerate(meshes):
        labels.extend(dict(name=name, meshes=[index], point=((point - center) / radius).tolist(),
                           normal=normal, face=True) for name, point, normal in faces)

    output.write_text(TEMPLATE.read_text().replace('__CONTROLS__', '\n'.join(controls))
                      .replace('__REFERENCES__', '\n'.join(reference_controls))
                      .replace('__FEATURE_LABELS__', dumps(labels))
                      .replace('__MESHES__', '\n'.join(payloads)), encoding='utf-8')
    return output


def preview_parts(exports):
    order = {name: index for index, name in enumerate(PARTS)}
    return sorted(exports.glob('*.step'),
                  key=lambda path: (order.get(path.stem, len(order)), path.name))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('parts', nargs='*', type=Path, help='STEP or binary STL files')
    args = parser.parse_args()
    exports = Path('exports')
    parts = args.parts or preview_parts(exports)
    if not parts:
        parser.error('No STEP files found in exports/')
    if not args.parts:
        parts.extend(REFERENCE_MESHES)
    output = write_preview(parts, parts[0].with_name('preview.html'))
    if not args.parts:
        for legacy in exports.glob('*.preview.html'):
            legacy.unlink()
    print(output)


if __name__ == '__main__':
    main()
