"""Validate the printable exports and package them with orthographic PNGs."""
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
from PIL import Image
from build123d import import_step

from scripts.validate_mesh import inspect_stl

PARTS = (
    'adapter-body', 'adapter-body-split-front', 'adapter-body-split-rear',
    'butterfly-key-top', 'butterfly-key-cavity', 'latch',
)
VIEWS = (
    ('front-oblique', (1, -1, .85)),
    ('rear-oblique', (-.8, 1, .9)),
    ('underside', (1, -.45, -1.2)),
)
STL_TRIANGLE = np.dtype([
    ('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attribute', '<u2'),
])


def render(mesh, direction):
    """Rasterize visible triangles with an orthographic camera and depth buffer."""
    width, height = 1000, 650
    eye = np.array(direction, dtype=float)
    eye /= np.linalg.norm(eye)
    right = np.cross((0, 0, 1), eye)
    right /= np.linalg.norm(right)
    up = np.cross(eye, right)
    projected = mesh @ np.column_stack((right, up, eye))
    low = projected[:, :, :2].min(axis=(0, 1))
    high = projected[:, :, :2].max(axis=(0, 1))
    scale = min((width - 85) / (high[0] - low[0]), (height - 85) / (high[1] - low[1]))
    xy = (projected[:, :, :2] - (low + high) / 2) * (scale, -scale) + (width / 2, height / 2)

    normals = np.cross(mesh[:, 1] - mesh[:, 0], mesh[:, 2] - mesh[:, 0])
    visible = normals @ eye > 0
    normals = normals[visible]
    xy = xy[visible]
    z = projected[visible, :, 2]
    light = eye + .8 * up - .45 * right
    light /= np.linalg.norm(light)
    shade = .4 + .6 * np.maximum(0, (normals @ light) / np.linalg.norm(normals, axis=1))
    colors = (shade[:, None] * (66, 158, 166)).astype(np.uint8)

    rgb = np.full((height, width, 3), (246, 249, 252), dtype=np.uint8)
    depth = np.full((height, width), -np.inf)
    bounds_min = np.ceil(xy.min(axis=1) - .5).astype(int)
    bounds_max = np.floor(xy.max(axis=1) - .5).astype(int)
    drawable = np.flatnonzero(np.all(bounds_min <= bounds_max, axis=1))
    for i in drawable:
        xmin, ymin = bounds_min[i]
        xmax, ymax = bounds_max[i]
        region = np.s_[ymin:ymax + 1, xmin:xmax + 1]
        (ax, ay), (bx, by), (cx, cy) = xy[i]
        denominator = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        yy, xx = np.ogrid[ymin:ymax + 1, xmin:xmax + 1]
        x, y = xx + .5 - cx, yy + .5 - cy
        a = ((by - cy) * x + (cx - bx) * y) / denominator
        b = ((cy - ay) * x + (ax - cx) * y) / denominator
        c = 1 - a - b
        distance = a * z[i, 0] + b * z[i, 1] + c * z[i, 2]
        covered = (a >= 0) & (b >= 0) & (c >= 0) & (distance > depth[region])
        depth[region][covered] = distance[covered]
        rgb[region][covered] = colors[i]
    png = BytesIO()
    Image.fromarray(rgb).save(png, format='PNG')
    return png.getvalue()


def main():
    exports = Path(__file__).resolve().parents[2] / 'exports'
    output = exports / 'SurronSeatAdapter.zip'
    staging = output.with_suffix('.zip.tmp')
    try:
        with ZipFile(staging, 'w', ZIP_DEFLATED) as release:
            for part in PARTS:
                stl = exports / f'{part}.stl'
                step = exports / f'{part}.step'
                mesh_check = inspect_stl(stl)
                if not mesh_check['valid'] or mesh_check['solids'] != 1:
                    raise ValueError(f'{stl} must be one closed solid: {mesh_check}')
                solid = import_step(step)
                if not solid.is_valid or len(solid.solids()) != 1:
                    raise ValueError(f'{step} must be one valid solid')
                release.write(stl, stl.name)
                release.write(step, f'step/{step.name}')
                mesh = np.fromfile(stl, offset=84, dtype=STL_TRIANGLE)['vertices'].astype(float)
                for name, direction in VIEWS:
                    release.writestr(f'previews/{part}/{name}.png', render(mesh, direction))
                print(f'Packaged {part}', flush=True)
        staging.replace(output)
    finally:
        staging.unlink(missing_ok=True)
    print(output)


if __name__ == '__main__':
    main()
