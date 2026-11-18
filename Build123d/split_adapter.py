"""Export the two-piece printing child from the completed master STEP."""
from collections import Counter
from copy import deepcopy
from pathlib import Path

from build123d import Edge, Face, Keep, Plane, Solid, Vector, Wire, export_step, import_step

from adapter import RECIPE
from coordinates import ADAPTER_TRANSLATION_MM, source_to_model
from export_mesh import export_stl_mm


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


def cavity_connector(top, x_offset):
    """Place a scaled top hourglass on the underside of the 18.5 mm roof."""
    instance = deepcopy(top)
    instance['name'] = f'cavity-{x_offset:+g}'
    roof_offset = Vector(top['extrusionDirection']) * 18.5
    instance['originMm'] = tuple(Vector(top['originMm']) + roof_offset + Vector(x_offset, 0, 0))
    instance['extrusionDirection'] = [-value for value in top['extrusionDirection']]

    # Scale around the waist so it still lands on the split plane.
    waist_v = 103.59226295038653
    for curve in instance['curves']:
        for key in ('startMm', 'endMm'):
            u, v, w = curve[key]
            curve[key] = (0.30 * u, waist_v + 0.30 * (v - waist_v), w)
    return instance


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
    instances = [top, side, opposite_side, cavity_connector(top, -33), cavity_connector(top, 33)]
    tools = [connector_tool(instance) for instance in instances]
    for name, half in zip(('front', 'rear'), halves):
        for instance, tool in zip(instances, tools):
            cut = half.cut(tool)
            if not cut.is_valid or len(cut.solids()) != 1 or half.volume - cut.volume < 0.01:
                raise ValueError(f"{name}: invalid or missing {instance['name']} connector recess")
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
