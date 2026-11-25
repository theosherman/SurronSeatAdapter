"""Export the two-piece printing child from the completed master STEP."""
from argparse import ArgumentParser
from pathlib import Path

from build123d import Face, Keep, Plane, Solid, Vector, Wire, export_step, import_step

from adapter_profiles import SKETCHES
from coordinates import ADAPTER_TRANSLATION_MM
from export_mesh import export_stl_mm
from measure import volume


SPLIT_Y_MM = 37.0
TOP_POCKET_DEPTH_MM = 12.8
CAVITY_POCKET_DEPTH_MM = 6.8
RECESS_RIM_RADIUS_MM = 1.0


def recess_tool(mouth, direction, rim_radius):
    tool = Solid.extrude(mouth, direction)
    if not rim_radius:
        return tool

    # Create the rim on a flat reference surface so the round can run out
    # naturally where the real cavity wall bends next to the recess.
    direction = Vector(direction)
    normal = mouth.normal_at()
    inward = normal if normal.dot(direction) > 0 else -normal
    frame = Plane(mouth.center(), z_dir=inward)
    local = frame.to_local_coords(tool)
    bounds = local.bounding_box()
    margin = 2 * rim_radius
    stock = Solid.make_box(bounds.size.X + 2 * margin, bounds.size.Y + 2 * margin,
                           bounds.max.Z + margin,
                           Plane((bounds.min.X - margin, bounds.min.Y - margin, 0)))
    pocket = stock.cut(local)
    opening = next(face for face in pocket.faces()
                   if abs(face.center().Z) < 1e-7 and face.inner_wires())
    relieved = pocket.fillet(rim_radius, opening.inner_wires()[0].edges())
    return frame.from_local_coords(stock.cut(relieved))


def butterfly_outline(waist, tip, length):
    """Symmetric outline from half-widths and half-length."""
    return [(-tip, -length), (tip, -length), (waist, 0),
            (tip, length), (-tip, length), (-waist, 0)]


def split_plane():
    return Plane((0, SPLIT_Y_MM, 0), z_dir=(0, 1, 0))


def connector_tools(plane, rim_radius=0):
    seam_y = plane.origin.Y
    sketch = SKETCHES['SeatHangerSketch']
    origin = Vector(sketch['originMm']) + Vector(ADAPTER_TRANSLATION_MM)
    normal = Vector(sketch['normal'])

    def top_z(y):
        return origin.Z - normal.Y / normal.Z * (y - origin.Y)

    top = Face(Wire.make_polygon([
        (x, seam_y+y, top_z(seam_y+y))
        for x, y in butterfly_outline(11.5, 21.5, 20.75)
    ], close=True))
    tools = [('top', recess_tool(top, -TOP_POCKET_DEPTH_MM * normal, rim_radius))]
    for side, name in ((-1, 'cavity-negative-x'), (1, 'cavity-positive-x')):
        # The long central cavity has parallel walls at X = +/-12 mm.
        mouth = Face(Wire.make_polygon([
            (side*12, seam_y+y, 23+z)
            for z, y in butterfly_outline(2.75, 5.5, 15)
        ], close=True))
        tools.append((name, recess_tool(mouth, (side*CAVITY_POCKET_DEPTH_MM, 0, 0), rim_radius)))
    return tools


def build_split(master):
    plane = split_plane()
    sides = master.split(plane, keep=Keep.BOTH)
    halves = sorted((solid for side in sides if side for solid in side.solids()),
                    key=lambda solid: solid.center().Y)
    master_volume = volume(master)
    partition_error = abs(sum(volume(half) for half in halves) - master_volume)
    # Splitting the saved, faceted wheel imprint can change the measured
    # volume slightly. Use the same 2 ppm limit as the STEP round-trip check.
    if (len(halves) != 2 or not all(half.is_valid for half in halves)
            or partition_error > max(0.1, master_volume * 2e-6)):
        raise ValueError('Split did not partition the master into two solids')
    tools = connector_tools(plane, rim_radius=RECESS_RIM_RADIUS_MM)
    for name, half in zip(('front', 'rear'), halves):
        for connector_name, tool in tools:
            cut = half.cut(tool)
            if not cut.is_valid or len(cut.solids()) != 1 or half.volume - cut.volume < 0.01:
                raise ValueError(f"{name}: invalid or missing {connector_name} connector recess")
            half = cut
        yield name, half.clean()


def export_split(output, master, *, stl=False):
    for name, half in list(build_split(master)):
        step = output / f'adapter-body-split-{name}.step'
        if not export_step(half, step):
            raise ValueError(f'STEP export failed: {step}')
        exported = import_step(step)
        if not exported.is_valid or len(exported.solids()) != 1:
            raise ValueError(f'Invalid exported solid: {step}')
        if stl:
            export_stl_mm(half, step.with_suffix('.stl'))
        print(f'{name}: {exported.bounding_box().size}', flush=True)
        yield step, exported


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--stl', action='store_true', help='Also export the printable STLs')
    args = parser.parse_args()
    export_dir = Path(__file__).resolve().parent / 'exports'
    list(export_split(export_dir, import_step(export_dir / 'adapter-body.step'), stl=args.stl))


if __name__ == '__main__':
    main()
