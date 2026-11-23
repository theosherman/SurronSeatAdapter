"""Continue the existing rear seat-support shoulder into the narrow body.

The selected half-profile uses source sketch coordinates. Its existing outer
rear edge supplies the continuation angle; the regular master mirror creates
the other support. Seat-contact edges and the original underside draft stay put.
"""
from copy import deepcopy
from math import isclose

from adapter_profiles import SKETCHES


REAR_EXTENSION_MM = 19.0


def continued_shoulder_curves(curves):
    result=deepcopy(curves)
    close=lambda a,b:isclose(a,b,abs_tol=1e-7)
    rear=next(c for c in curves if close(c['startMm'][0],-35.379898392003156)
              and close(c['endMm'][0],-51.0))
    a,b=rear['startMm'],rear['endMm']
    body_u=-22.0
    body_v=a[1]+(b[1]-a[1])*(body_u-a[0])/(b[0]-a[0])
    changed=0
    for c in result:
        for key in ('startMm','endMm'):
            p=c[key]
            if close(p[0],body_u) and close(p[1],27.29000122145888):
                p[1]=body_v
                changed+=1
    if changed!=2:
        raise ValueError('Seat shoulder source no longer has the expected return vertex')
    # Extend the original rear edge in sketch coordinates, then translate
    # the entire mirrored shoulder outline by 10 mm along placed Y.
    shift = 10.0 / SKETCHES['SeatHangerSketch']['yAxis'][1]
    rear_v = (a[1], b[1], body_v)
    for curve in result:
        for key in ('startMm', 'endMm'):
            point = curve[key]
            if any(close(point[1], v) for v in rear_v):
                point[1] += REAR_EXTENSION_MM
            point[1] += shift
    return result
