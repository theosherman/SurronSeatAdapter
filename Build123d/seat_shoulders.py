"""Continue the existing rear seat-support shoulder into the narrow body.

The selected half-profile uses source sketch coordinates. Its existing outer
rear edge supplies the continuation angle; the regular master mirror creates
the other support. Seat-contact edges and the original underside draft stay put.
"""
from copy import deepcopy
from math import isclose


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
    return result
