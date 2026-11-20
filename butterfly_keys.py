"""Export the two printable butterfly key shapes from the adapter's recesses."""
from pathlib import Path

from build123d import GeomType, Kind, Plane, Solid, export_step

from export_mesh import export_stl_mm
from split_adapter import connector_tools, split_plane


KEY_CLEARANCE_MM = 0.4
KEY_FILLET_RADIUS_MM = 1.0
# A 1 mm concave fillet adds up to 0.106 mm back at the waist.
KEY_FILLET_SIDE_RELIEF_MM = 0.11


def build_keys():
    recesses = dict(connector_tools(split_plane()))
    for name, recess_name in (('top', 'top'), ('cavity', 'cavity-negative-x')):
        recess = recesses[recess_name]
        inset = recess.offset_3d([], -(KEY_CLEARANCE_MM + KEY_FILLET_SIDE_RELIEF_MM),
                                 kind=Kind.INTERSECTION)
        # The two butterfly ends have more edges than the four-sided extrusion walls.
        cap, opposite = (face for face in inset.faces() if len(face.edges()) > 4)
        sweep = opposite.center() - cap.center()
        # Restore the cap spacing while keeping the extra inset on the sides.
        extension = sweep * (KEY_FILLET_SIDE_RELIEF_MM / abs(sweep.dot(cap.normal_at())))
        blank = Solid.extrude(cap.translate(-extension), sweep + 2 * extension)
        key = blank.fillet(KEY_FILLET_RADIUS_MM, blank.edges())
        if not key.is_valid or len(key.solids()) != 1:
            raise ValueError(f'{name}: clearance must produce one valid butterfly key')
        yield name, key


def lay_flat(key):
    base = next(face for face in key.faces()
                if face.geom_type == GeomType.PLANE and len(face.edges()) > 4)
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
