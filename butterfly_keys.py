"""Export the two printable butterfly key shapes from the adapter's recesses."""
from pathlib import Path

from build123d import Kind, Plane, export_step

from export_mesh import export_stl_mm
from split_adapter import connector_tools, split_plane


KEY_CLEARANCE_MM = 0.4


def build_keys():
    recesses = dict(connector_tools(split_plane()))
    for name, recess_name in (('top', 'top'), ('cavity', 'cavity-negative-x')):
        recess = recesses[recess_name]
        key = recess.offset_3d([], -KEY_CLEARANCE_MM, kind=Kind.INTERSECTION)
        if not key.is_valid or len(key.solids()) != 1:
            raise ValueError(f'{name}: clearance must produce one valid butterfly key')
        yield name, key


def lay_flat(key):
    base = max(key.faces(), key=lambda face: face.area)
    return Plane(base.center(), z_dir=-base.normal_at()).to_local_coords(key)


def main():
    output = Path(__file__).resolve().parent / 'exports'
    for name, key in build_keys():
        step = output / f'butterfly-key-{name}.step'
        if not export_step(key, step):
            raise ValueError(f'STEP export failed: {step}')
        export_stl_mm(lay_flat(key), step.with_suffix('.stl'))


if __name__ == '__main__':
    main()
