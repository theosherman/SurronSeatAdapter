"""Production SideSketch roof step and rear seat notch cutter, in millimeters."""
from math import isclose

from build123d import Face, Plane, Solid, Vector, Wire

from adapter_profiles import SKETCHES
from cut_offsets import REAR_NOTCH_OUTER_U_MM


EDGE_INSET_MM = 3
SUPPORT_RISE_MM = 2
NOTCH_RISE_MM = 3
NOTCH_DEPTH_MM = 8
NOTCH_FRONT_V = 244.70896933768438
NOTCH_REAR_V = 264.7089693376844


def notch_datum():
    sketch = SKETCHES['RearSeatNotchSketch']
    return tuple(Vector(sketch[key]) for key in ('originMm', 'yAxis', 'normal'))


def support_rear_y():
    origin, longitudinal, normal = notch_datum()
    old_floor_edge = origin + longitudinal * NOTCH_FRONT_V - normal * NOTCH_DEPTH_MM
    return old_floor_edge.Y - EDGE_INSET_MM


def stepped_roof_curves(curves):
    """Continue the lower roof to the full step and square the rear wall to the roof."""
    rear_roof = next((c for c in curves
                      if c['startMm'][0] < c['endMm'][0] < 0
                      and c['startMm'][1] > c['endMm'][1] > 85), None)
    if rear_roof is None:
        yield from curves
        return

    start, end = rear_roof['startMm'], rear_roof['endMm']
    rear_u = -support_rear_y()
    front_u = end[0] - EDGE_INSET_MM
    rear_slope = (end[1] - start[1]) / (end[0] - start[0])
    _, _, normal = notch_datum()
    rear_z = start[1] + rear_slope * (rear_u - start[0])
    front_z = start[1] + rear_slope * (front_u - start[0]) + SUPPORT_RISE_MM
    rear_wall = normal * (SUPPORT_RISE_MM * normal.Z)
    lower_roof = next(c for c in curves
                      if isclose(c['startMm'][0], end[0]) and c['endMm'][0] > 0)
    lower_start, lower_end = lower_roof['startMm'], lower_roof['endMm']
    lower_slope = (lower_end[1] - lower_start[1]) / (lower_end[0] - lower_start[0])
    lower_front = [front_u, lower_start[1] + lower_slope * (front_u - lower_start[0]), 0]

    for curve in curves:
        if curve is rear_roof:
            points = [start, [rear_u, rear_z, 0],
                      [rear_u - rear_wall.Y, rear_z + rear_wall.Z, 0],
                      [front_u, front_z, 0], lower_front]
            yield from (dict(type='Line3D', startMm=a, endMm=b) for a, b in zip(points, points[1:]))
        elif curve is lower_roof:
            yield dict(curve, startMm=lower_front)
        elif not all(isclose(curve[key][0], end[0]) for key in ('startMm', 'endMm')):
            yield curve


def rear_notch_tools():
    """Extrude two mirrored notch profiles to the raised floor datum."""
    origin, longitudinal, normal = notch_datum()
    # The extrusion direction is parallel to the rear step wall, so the
    # profile can start directly at its intersection with the rear roof.
    front_v = (support_rear_y() - origin.Y) / longitudinal.Y
    profile = Face(Wire.make_polygon([
        origin + longitudinal * v + Vector(x, 0, 0)
        for x, v in ((13.5, front_v), (REAR_NOTCH_OUTER_U_MM, front_v),
                     (REAR_NOTCH_OUTER_U_MM, NOTCH_REAR_V), (13.5, NOTCH_REAR_V))
    ], close=True))
    depth = NOTCH_DEPTH_MM - NOTCH_RISE_MM * normal.Z
    cutter = Solid.extrude(profile, -normal * depth)
    return cutter, cutter.mirror(Plane.YZ)
