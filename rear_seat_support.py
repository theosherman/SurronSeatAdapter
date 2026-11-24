"""Production SideSketch roof step and rear seat notch cutter, in millimeters."""
from build123d import Face, Keep, Plane, Solid, Vector, Wire

from adapter_profiles import SKETCHES
from cut_offsets import REAR_NOTCH_OUTER_U_MM


EDGE_INSET_MM = 3
SUPPORT_RISE_MM = 5
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
    """Replace the rear roof line with the stepped SideSketch outline."""
    for curve in curves:
        start, end = curve['startMm'], curve['endMm']
        if start[0] < end[0] < 0 and start[1] > end[1] > 85:
            rear_u = -support_rear_y()
            front_u = end[0] - EDGE_INSET_MM
            points = [start]
            for u, lifts in ((rear_u, (0, SUPPORT_RISE_MM)), (front_u, (SUPPORT_RISE_MM, 0))):
                height = start[1] + (end[1] - start[1]) * (u - start[0]) / (end[0] - start[0])
                points.extend([u, height + lift, 0] for lift in lifts)
            points.append(end)
            yield from (dict(type='Line3D', startMm=a, endMm=b) for a, b in zip(points, points[1:]))
        else:
            yield curve


def rear_notch_tools():
    """Extrude two mirrored notch profiles to the raised floor datum."""
    origin, longitudinal, normal = notch_datum()
    # Start the sketch beyond the new front boundary, then trim the cutter
    # vertically so the two floors end exactly at the raised roof step.
    front_v = (support_rear_y() - origin.Y) / longitudinal.Y - EDGE_INSET_MM
    profile = Face(Wire.make_polygon([
        origin + longitudinal * v + Vector(x, 0, 0)
        for x, v in ((13.5, front_v), (REAR_NOTCH_OUTER_U_MM, front_v),
                     (REAR_NOTCH_OUTER_U_MM, NOTCH_REAR_V), (13.5, NOTCH_REAR_V))
    ], close=True))
    depth = NOTCH_DEPTH_MM - NOTCH_RISE_MM * normal.Z
    cutter = Solid.extrude(profile, -normal * depth)
    front_plane = Plane((0, support_rear_y(), 0), z_dir=(0, 1, 0))
    cutter = cutter.split(front_plane, Keep.TOP)
    return cutter, cutter.mirror(Plane.YZ)
