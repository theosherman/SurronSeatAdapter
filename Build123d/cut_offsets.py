"""Approved 1 mm outward offsets of original manufacturing profile lines.

Intersect the moved diagonals with their original adjoining lines. The portable
recipe remains the source reference; no finished-body patches are introduced.
"""
from copy import deepcopy
from math import hypot, isclose

OUTWARD_OFFSET_MM = 1.0


def offset_cut_curves(index, curves):
    curves = deepcopy(curves)
    replacements = []
    if index == 14:
        # RearSketch (u,v): global Z = -v. Outward normal is (+u,-v).
        top = (21.689542263650967, -109.10684591063722)
        bottom = (90.0, 25.580075473268877)
        du, dv = bottom[0]-top[0], bottom[1]-top[1]
        length = hypot(du, dv)
        replacements = [(top, (top[0]+OUTWARD_OFFSET_MM*length/dv, top[1])),
                        (bottom, (bottom[0], bottom[1]-OUTWARD_OFFSET_MM*length/du))]
    elif index == 86:
        # FrontCutSketch XY: move toward the removed corner, shrinking the cut.
        a = (49.0, 193.15953208748562)
        b = (80.0, 163.31122810793568)
        length = hypot(b[0]-a[0], b[1]-a[1])
        for side in (-1, 1):
            replacements += [((side*a[0], a[1]),
                              (side*(a[0]+OUTWARD_OFFSET_MM*length/(a[1]-b[1])), a[1])),
                             ((side*b[0], b[1]),
                              (side*b[0], b[1]+OUTWARD_OFFSET_MM*length/(b[0]-a[0])))]
    for curve in curves:
        for key in ('startMm', 'endMm'):
            point = curve[key]
            for old, new in replacements:
                if all(isclose(point[i], old[i], abs_tol=1e-7) for i in (0, 1)):
                    point[:2] = new
                    break
    return curves
