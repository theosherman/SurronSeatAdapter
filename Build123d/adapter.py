"""Editable millimeter reconstruction from the portable Fusion/Onshape recipe."""
from pathlib import Path
import argparse
import json
import time
from build123d import Edge, Wire, Face, Solid, Plane, Vector, Keep, Compound, ShapeList, Mesher, export_step, export_stl

ROOT = Path(__file__).resolve().parents[1]
RECIPE = json.loads((ROOT / 'cad-rebuild/recipe.json').read_text())
SKETCHES = {s['name']: s for s in RECIPE['sketches']}
HISTORY = []


def profiles(index, with_source=False):
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
            for c in loop['curves']:
                if c['type'] == 'Line3D':
                    edges.append(Edge.make_line(point(c['startMm']), point(c['endMm'])))
                elif c['type'] == 'Arc3D':
                    edges.append(Edge.make_three_point_arc(point(c['startMm']), point(c['midMm']), point(c['endMm'])))
                elif c['type'] == 'Circle3D':
                    edges.append(Edge.make_circle(c['radiusMm'], Plane(point(c['centerMm']), x_dir=x, z_dir=n)))
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


def tool(index, depth, direction=None, offset=0, symmetric=False, taper=0):
    selected = next(p for p in RECIPE['selectedProfiles'] if p['sourceTimelineIndex']==index)
    s = SKETCHES[selected['profiles'][0]['sketch']]
    n = Vector(s['normal'] if direction is None else direction).normalized()
    solids = []
    for f in profiles(index):
        f = f.translate(n*(offset-depth/2 if symmetric else offset))
        solids.append(Solid.extrude_taper(f,n*depth,taper) if taper else Solid.extrude(f,n*depth))
    return solids[0].fuse(*solids[1:]) if len(solids)>1 else solids[0]


def checked(name, shape):
    if isinstance(shape, (list, ShapeList)):
        shape = Compound(shape)
    shape = shape.clean()
    row = dict(step=name, volumeMm3=shape.volume, solids=len(shape.solids()), valid=shape.is_valid)
    HISTORY.append(row)
    print(json.dumps(row), flush=True)
    assert row['valid'] and row['solids']==1, row
    return shape


def build_master(stop=None, imprint=True, airtag_depth=8.5):
    HISTORY.clear()
    def stage(name, shape):
        return checked(name, shape)
    body = stage('M01',tool(9,200,offset=-50))
    if stop=='M01': return body
    body = stage('M02',body.fuse(body.mirror(Plane.YZ)))
    body = stage('M03',body.intersect(tool(12,120,[1,0,0])))
    body = stage('M04',body.intersect(tool(14,490,[0,1,0])))
    body = stage('M05',body.fuse(body.mirror(Plane.YZ)))
    if stop=='M05': return body
    rear = tool(18,300).split(Plane((0,-263.445982162752,0),z_dir=(0,1,0)),Keep.TOP)
    body = stage('M06',body.fuse(rear))
    if stop=='M06': return body
    body = stage('M07',body.cut(tool(75,1000,symmetric=True)))
    body = stage('M08',body.cut(tool(76,500,direction=-Vector(SKETCHES['BoltHolesSketch']['normal']),offset=3)))
    roof = next(s for s in RECIPE['masterSteps'] if s['id']=='M09')
    front = tool(77,1000,symmetric=True).split(Plane(roof['finalRoofPlanePointMm'],z_dir=roof['finalRoofPlaneNormal']),Keep.BOTTOM)
    body = stage('M09',body.cut(*(front if isinstance(front,list) else [front])))
    if stop=='M09': return body
    hanger = tool(79,1,direction=-Vector(SKETCHES['SeatHangerSketch']['normal']))
    d = RECIPE['drafts'][0]
    face = min(hanger.faces(),key=lambda f:(f.center()-Vector(d['selectedFaces'][0]['pointMm'])).length)
    hanger = hanger.draft([face],Plane(d['neutralPlane']['originMm'],z_dir=d['neutralPlane']['normal']),45)
    body = stage('M11',body.fuse(hanger,hanger.mirror(Plane.YZ)))
    body = stage('M12',body.fuse(tool(84,98,[1,0,0],symmetric=True)))
    body = stage('M13',body.cut(tool(86,1000,[0,0,1],symmetric=True)))
    # Exact planar wedge from saved source draft datums (same construction as SolidCraft).
    points = [(-43,159.1595320874856,11.33586233574399),(-43,159.1595320874856,34.33586233574536),(-43,176.73146895659514,36.4311889499611)]
    wedge = Solid.extrude(Face(Wire.make_polygon(points,close=True)),(86,0,0))
    body = stage('M14',body.cut(wedge))
    body = stage('M15',body.cut(tool(89,8,direction=-Vector(SKETCHES['RearSeatNotchSketch']['normal']))))
    body = stage('M16',body.fuse(tool(91,80,[1,0,0],symmetric=True)))
    side = tool(97,1000,symmetric=True)
    body = stage('M17',body.cut(side,side.mirror(Plane.YZ)))
    rearcut = tool(121,1000,symmetric=True)
    body = stage('M18',body.cut(rearcut,rearcut.mirror(Plane.YZ)))
    body = stage('M19',body.cut(tool(124,500,direction=-Vector(SKETCHES['BodyCutSketch']['normal']),offset=12,taper=-15)))
    body = stage('M20',body.cut(tool(126,airtag_depth,direction=-Vector(SKETCHES['AirtagCutSketch']['normal']))))
    if stop=='M20' or not imprint: return body
    print('Converting aligned wheel scan to faceted BREP (zero clearance)', flush=True)
    scan = Mesher().read(ROOT/'Sherman_P_Scan_Aligned_To_Adapter_mm.stl')
    assert len(scan)==1 and scan[0].is_valid and len(scan[0].solids())==1
    assert abs(scan[0].volume-4221287.872)<0.1
    return stage('M21',body.cut(scan[0]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-imprint',action='store_true')
    parser.add_argument('--stop',choices=['M01','M05','M06','M09','M20'])
    args = parser.parse_args()
    start = time.monotonic()
    body = build_master(stop=args.stop,imprint=not args.no_imprint)
    output = Path(__file__).parent/'exports'
    output.mkdir(exist_ok=True)
    stem = 'adapter-body' if not args.stop and not args.no_imprint else 'adapter-body-'+(args.stop or 'pre-imprint')
    export_step(body,output/(stem+'.step'))
    export_stl(body,output/(stem+'.stl'),tolerance=0.005,angular_tolerance=0.05)
    (Path(__file__).parent/'logs/build-validation.json').write_text(json.dumps(dict(elapsedSeconds=time.monotonic()-start,stages=HISTORY),indent=2)+'\n')

if __name__=='__main__':
    main()
