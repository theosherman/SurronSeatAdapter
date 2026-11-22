"""Export the two-piece printing child from the completed master STEP."""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path

from build123d import Edge, Face, Keep, Plane, Solid, Vector, Wire, export_step, import_step

from adapter_profiles import RECIPE, SKETCHES
from coordinates import ADAPTER_TRANSLATION_MM, source_to_model
from export_mesh import export_stl_mm
from measure import volume
from trunk_cavity import REAR_CAVITY_POINTS


CONNECTOR_DEPTH_MM = 10.0
RECESS_RIM_RADIUS_MM = 1.0


def placed_point(point):
    return Vector(source_to_model(point)) + Vector(ADAPTER_TRANSLATION_MM)


def recess_tool(mouth, direction, rim_radius):
    tool = Solid.extrude(mouth, direction)
    if not rim_radius:
        return tool

    # Create the rim on a flat reference surface so the round can run out
    # naturally where the real cavity wall bends next to the recess.
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


def connector_tool(instance, depth, rim_radius=0):
    origin = placed_point(instance['originMm'])
    x = Vector(source_to_model(instance['xAxis']))
    y = Vector(source_to_model(instance['yAxis']))
    normal = x.cross(y)
    segments = [
        tuple(tuple(round(value, 10) for value in curve[key]) for key in ('startMm', 'endMm'))
        for curve in instance['curves']
    ]
    degree = Counter(point for segment in segments for point in segment)

    def point(coords):
        u, v, w = coords
        return origin + u*x + v*y + w*normal

    # The two adjacent profiles share one internal divider between the waist vertices.
    wire = Wire([Edge.make_line(point(a), point(b)) for a, b in segments
                 if degree[a] == 2 or degree[b] == 2])
    direction = Vector(source_to_model(instance['extrusionDirection']))
    return recess_tool(Face(wire), direction.normalized()*depth, rim_radius)


def cavity_connector(split_plane, side, depth, rim_radius=0):
    """Place an hourglass on the angled cavity wall at the split seam."""
    sketch = SKETCHES['BodyCutSketch']
    origin = Vector(sketch['originMm']) + Vector(ADAPTER_TRANSLATION_MM)
    x, y, roof_normal = (Vector(sketch[key]) for key in ('xAxis', 'yAxis', 'normal'))
    # The widening wall segment immediately before the straight 48 mm section.
    (u0, v0), (u1, v1) = REAR_CAVITY_POINTS[4:6]
    wall_point = origin + x*(side*u0) + y*v0
    tangent = x*(side*(u1-u0)) + y*(v1-v0)
    inward = tangent.cross(roof_normal).normalized()
    if inward.X*wall_point.X > 0:
        inward = -inward

    z = 18  # Retain full recess depth above the raised underside and wheel imprint.
    seam_normal = split_plane.z_dir
    seam_y = split_plane.origin.Y - (z-split_plane.origin.Z)*seam_normal.Z/seam_normal.Y
    wall_x = wall_point.X - ((seam_y-wall_point.Y)*inward.Y + (z-wall_point.Z)*inward.Z)/inward.X
    center = Vector(wall_x, seam_y, z)
    across = (seam_normal - inward*seam_normal.dot(inward)).normalized()
    along = inward.cross(across).normalized()
    outline = [(-8,-6), (8,-6), (4.5,0), (8,6), (-8,6), (-4.5,0)]
    face = Face(Wire.make_polygon([center + along*u + across*v for u, v in outline], close=True))
    outward = -inward
    # Keep the waist on the seam while measuring the depth normal to the wall.
    direction = outward - seam_normal * outward.dot(seam_normal)
    return recess_tool(face, direction * (depth / direction.dot(outward)), rim_radius)


def split_plane():
    datum = RECIPE['child']['splitPlane']
    return Plane(placed_point(datum['originMm']), z_dir=source_to_model(datum['normal']))


def connector_tools(plane, rim_radius=0):
    instances = RECIPE['child']['connectorInstances']
    top = next(instance for instance in instances if instance['name'] == 'top')
    return [
        ('top', connector_tool(top, CONNECTOR_DEPTH_MM, rim_radius)),
        ('cavity-positive-x', cavity_connector(plane, -1, CONNECTOR_DEPTH_MM, rim_radius)),
        ('cavity-negative-x', cavity_connector(plane, 1, CONNECTOR_DEPTH_MM, rim_radius)),
    ]


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
