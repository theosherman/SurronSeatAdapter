"""Shared sketch recipe and profile construction for the adapter and latch."""
import json
from pathlib import Path

from build123d import Edge, Face, Plane, Vector, Wire

from coordinates import model_recipe

ROOT = Path(__file__).resolve().parent
RECIPE = model_recipe(json.loads((ROOT / 'cad-rebuild/recipe.json').read_text()))
SKETCHES = {s['name']: s for s in RECIPE['sketches']}


def profiles(index, with_source=False, sherman_p_bottom=False, seat_shoulders=False, manufacturing_offsets=False):
    """Make exact selected faces in global coordinates, preserving sketch-space Z."""
    selected = next(p for p in RECIPE['selectedProfiles'] if p['sourceTimelineIndex'] == index)
    result = []
    for source in selected['profiles']:
        s = SKETCHES[source['sketch']]
        origin, x, y = map(Vector, (s['originMm'], s['xAxis'], s['yAxis']))
        n = x.cross(y)
        def point(p):
            return origin + x*p[0] + y*p[1] + n*(p[2] if len(p)>2 else 0)
        loops = []
        for loop in source['loops']:
            edges = []
            curves = loop['curves']
            if manufacturing_offsets and index in (14, 86, 89):
                from cut_offsets import offset_cut_curves
                curves = offset_cut_curves(index, curves)
            if sherman_p_bottom:
                if index != 9:
                    raise ValueError('Sherman P bottom adaptation is only for BottomSketch')
                from bottom_outline import sherman_p_curves
                curves = sherman_p_curves(curves)
            if seat_shoulders:
                if index != 79:
                    raise ValueError('Seat shoulder continuation is only for SeatHangerSketch')
                from seat_shoulders import continued_shoulder_curves
                curves = continued_shoulder_curves(curves)
            for c in curves:
                if c['type'] == 'Line3D':
                    edges.append(Edge.make_line(point(c['startMm']), point(c['endMm'])))
                elif c['type'] == 'Arc3D':
                    edges.append(Edge.make_three_point_arc(point(c['startMm']), point(c['midMm']), point(c['endMm'])))
                elif c['type'] == 'Circle3D':
                    radius = 14.0 if manufacturing_offsets and index == 97 else c['radiusMm']
                    edges.append(Edge.make_circle(radius, Plane(point(c['centerMm']), x_dir=x, z_dir=n)))
                else:
                    raise ValueError(c['type'])
            wire = Wire(edges)
            assert wire.is_closed, (index, 'open wire')
            loops.append((loop['outer'], wire))
        outer = [w for is_outer,w in loops if is_outer]
        assert len(outer) == 1
        face = Face(outer[0], [w for is_outer,w in loops if not is_outer])
        result.append((face, source) if with_source else face)
    return result
