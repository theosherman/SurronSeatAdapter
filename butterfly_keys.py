"""Export the two printable butterfly keys from the shared connector profiles."""
from argparse import ArgumentParser
from pathlib import Path

from build123d import GeomType, Plane, export_step

from export_mesh import export_stl_mm
from split_adapter import RECESS_RIM_RADIUS_MM, connector_tools, split_plane


def build_keys():
    blanks = dict(connector_tools(split_plane()))
    for name, blank in (('top', blanks['top']), ('cavity', blanks['cavity-negative-x'])):
        key = blank.fillet(RECESS_RIM_RADIUS_MM, blank.edges())
        if not key.is_valid or len(key.solids()) != 1:
            raise ValueError(f'{name}: fillets must produce one valid butterfly key')
        yield name, key


def lay_flat(key):
    # Both end caps provide a flat print base.
    base = max((face for face in key.faces()
                if face.geom_type == GeomType.PLANE and len(face.edges()) > 4),
               key=lambda face: face.area)
    return Plane(base.center(), z_dir=-base.normal_at()).to_local_coords(key)


def export_keys(output, *, stl=False):
    output.mkdir(exist_ok=True)
    for name, key in build_keys():
        step = output / f'butterfly-key-{name}.step'
        if not export_step(key, step):
            raise ValueError(f'STEP export failed: {step}')
        if stl:
            export_stl_mm(lay_flat(key), step.with_suffix('.stl'))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--stl', action='store_true', help='Also export flat printable STLs')
    args = parser.parse_args()
    export_keys(Path(__file__).resolve().parent / 'exports', stl=args.stl)


if __name__ == '__main__':
    main()
