"""Approved Sherman P changes to the original selected BottomSketch half-loop.

Values here use source sketch millimeters, before the permanent half-turn and
assembly placement. The normal master mirror supplies the opposite side.
"""
from copy import deepcopy
from math import isclose

FRONT_SHOULDER_SHIFT_MM = 10.0  # original line 17, parallel toward screen
SCREEN_EXTENSION_MM = 10.0     # original line 19, toward front


def sherman_p_curves(curves):
    """Extend line 13 to line 16, remove 14/15, and move 17/19 forward."""
    curves = deepcopy(curves)
    close = lambda a, b: isclose(a, b, abs_tol=1e-7)
    rear_x, rear_y = 64.68750101999127, -100.0
    outer_x, outer_y = 77.93135238304326, -111.68245530911433
    waist_x = 22.0
    intersection_y = outer_y+(rear_y-outer_y)*(waist_x-outer_x)/(rear_x-outer_x)
    result = []
    for curve in curves:
        assert curve['type'] == 'Line3D'
        # Both obsolete segments meet at the original rear shoulder vertex.
        if any(close(curve[k][0], rear_x) and close(curve[k][1], -79.96131101324718)
               for k in ('startMm', 'endMm')):
            continue
        for key in ('startMm', 'endMm'):
            p = curve[key]
            if ((close(p[0], rear_x) and close(p[1], rear_y)) or
                (close(p[0], waist_x) and close(p[1], -18.114927052326223))):
                p[0], p[1] = waist_x, intersection_y
            elif close(p[1], 37.12908768541572) or close(p[1], 87.40394523824223):
                p[1] += FRONT_SHOULDER_SHIFT_MM
            elif close(p[1], 159.1595320874856):
                p[1] += SCREEN_EXTENSION_MM
        result.append(curve)
    if len(result) != len(curves)-2:
        raise ValueError('BottomSketch no longer matches the expected source shoulder')
    return result
