"""Export the two-piece printing child from the completed master STEP."""
from collections import Counter
from pathlib import Path

from build123d import Edge, Face, Keep, Plane, Solid, Vector, Wire, export_step, import_step

from adapter import RECIPE, SKETCHES
from coordinates import ADAPTER_TRANSLATION_MM, source_to_model
from export_mesh import export_stl_mm
from trunk_cavity import REAR_CAVITY_POINTS


def placed_point(point):
    return Vector(source_to_model(point)) + Vector(ADAPTER_TRANSLATION_MM)


def connector_tool(instance):
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
    return Solid.extrude(Face(wire), direction.normalized()*instance['depthMm'])


def cavity_connector(split_plane, side, depth):
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

    z = 15
    seam_normal = split_plane.z_dir
    seam_y = split_plane.origin.Y - (z-split_plane.origin.Z)*seam_normal.Z/seam_normal.Y
    wall_x = wall_point.X - ((seam_y-wall_point.Y)*inward.Y + (z-wall_point.Z)*inward.Z)/inward.X
    center = Vector(wall_x, seam_y, z)
    across = (seam_normal - inward*seam_normal.dot(inward)).normalized()
    along = inward.cross(across).normalized()
    outline = [(-8,-6), (8,-6), (4.5,0), (8,6), (-8,6), (-4.5,0)]
    face = Face(Wire.make_polygon([center + along*u + across*v for u, v in outline], close=True))
    return Solid.extrude(face, -inward*depth)


def build_split(master):
    child = RECIPE['child']
    datum = child['splitPlane']
    plane = Plane(placed_point(datum['originMm']), z_dir=source_to_model(datum['normal']))
    sides = master.split(plane, keep=Keep.BOTH)
    halves = sorted((solid for side in sides if side for solid in side.solids()),
                    key=lambda solid: solid.center().Y)
    if len(halves) != 2 or abs(sum(half.volume for half in halves) - master.volume) > 0.1:
        raise ValueError('Split did not partition the master into two solids')
    top, side, _, opposite_side, _ = child['connectorInstances']
    tools = [(instance['name'], connector_tool(instance)) for instance in (top, side, opposite_side)]
    tools += [(f'cavity-wall-{sign:+d}', cavity_connector(plane, sign, top['depthMm']))
              for sign in (-1, 1)]
    for name, half in zip(('front', 'rear'), halves):
        for connector_name, tool in tools:
            cut = half.cut(tool)
            if not cut.is_valid or len(cut.solids()) != 1 or half.volume - cut.volume < 0.01:
                raise ValueError(f"{name}: invalid or missing {connector_name} connector recess")
            half = cut
        yield name, half.clean()


def main():
    output = Path(__file__).resolve().parent / 'exports'
    master = import_step(output / 'adapter-body.step')
    for name, half in list(build_split(master)):
        step = output / f'adapter-body-split-{name}.step'
        if not export_step(half, step):
            raise ValueError(f'STEP export failed: {step}')
        exported = import_step(step)
        if not exported.is_valid or len(exported.solids()) != 1:
            raise ValueError(f'Invalid exported solid: {step}')
        export_stl_mm(half, step.with_suffix('.stl'))
        print(f'{name}: {exported.bounding_box().size}', flush=True)


if __name__ == '__main__':
    main()
