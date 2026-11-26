"""Editable millimeter reconstruction from the portable Fusion-derived recipe."""
from pathlib import Path
import argparse
import json
import time
from build123d import Axis, Wire, Face, Solid, Plane, Vector, Keep, Compound, ShapeList, export_step, import_step

from adapter_profiles import RECIPE, SKETCHES, profiles
from coordinates import source_to_model, ADAPTER_TRANSLATION_MM
from reference.wheel import SEATING_DEPTH_MM, load_wheel_cutter
from export_mesh import export_stl_mm

ROOT = Path(__file__).resolve().parent
HISTORY = []


def tool(index, depth, direction=None, offset=0, symmetric=False, taper=0):
    selected = next(p for p in RECIPE['selectedProfiles'] if p['sourceTimelineIndex']==index)
    s = SKETCHES[selected['profiles'][0]['sketch']]
    n = Vector(s['normal'] if direction is None else direction).normalized()
    solids = []
    for f in profiles(index, sherman_p_bottom=index == 9, seat_shoulders=index == 79, manufacturing_offsets=True):
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


def seat_edge_relief():
    """Sweep the original relief opening from the lower flank at a shallower angle."""
    original = tool(97, 240, symmetric=True).translate(ADAPTER_TRANSLATION_MM)
    flank = Plane((62.8589058205, -84.9726967486, 0),
                  z_dir=(0.654991476223, 0.755636265722, 0))
    opening, = original.intersect(flank).faces()
    direction = Vector(SKETCHES['SeatCutoutSketch']['normal']).normalized()
    horizontal_axis = Axis((0, 0, 0), (-direction.Y, direction.X, 0))
    sweep = direction.rotate(horizontal_axis, 13)
    return Solid.extrude(opening.translate(-120 * sweep), 240 * sweep)


def build_master(stop=None, imprint=True, airtag_depth=8.5):
    HISTORY.clear()
    def stage(name, shape):
        return checked(name, shape)
    body = stage('M01',tool(9,200,offset=-50))
    if stop=='M01': return body
    body = stage('M02',body.fuse(body.mirror(Plane.YZ)))
    body = stage('M03',body.intersect(tool(12,120,source_to_model([1,0,0]))))
    body = stage('M04',body.intersect(tool(14,490,source_to_model([0,1,0]))))
    body = stage('M05',body.fuse(body.mirror(Plane.YZ)))
    if stop=='M05': return body
    rear = tool(18,300).split(Plane(source_to_model((0,-263.445982162752,0)),z_dir=source_to_model((0,1,0))),Keep.TOP)
    body = stage('M06',body.fuse(rear))
    if stop=='M06': return body
    body = stage('M07',body.cut(tool(75,1000,symmetric=True)))
    body = stage('M08',body.cut(tool(76,500,direction=-Vector(SKETCHES['BoltHolesSketch']['normal']),offset=3)))
    roof = next(s for s in RECIPE['masterSteps'] if s['id']=='M09')
    front = tool(77,1000,symmetric=True).split(Plane(roof['finalRoofPlanePointMm'],z_dir=roof['finalRoofPlaneNormal']),Keep.BOTTOM)
    body = stage('M09',body.cut(*(front if isinstance(front,list) else [front])))
    if stop=='M09': return body
    underside = -Vector(SKETCHES['SeatHangerSketch']['normal'])
    hanger = tool(79,1,direction=underside)
    d = RECIPE['drafts'][0]
    face = max(hanger.faces(), key=lambda f: f.normal_at().dot(underside))
    # The 30-degree draft raises the inner underside clear of the adjusters.
    hanger = hanger.draft([face],Plane(d['neutralPlane']['originMm'],z_dir=d['neutralPlane']['normal']),30)
    body = stage('M11',body.fuse(hanger,hanger.mirror(Plane.YZ)))
    body = stage('M12',body.fuse(tool(84,98,source_to_model([1,0,0]),symmetric=True)))
    body = stage('M13',body.cut(tool(86,1000,source_to_model([0,0,1]),symmetric=True)))
    # Exact planar wedge from saved source draft datums.
    points = [(-43,159.1595320874856,11.33586233574399),(-43,159.1595320874856,34.33586233574536),(-43,176.73146895659514,36.4311889499611)]
    # Carry the front opening's existing ramp along its sloped top/bottom planes.
    from bottom_outline import SCREEN_EXTENSION_MM
    slope = (points[2][2]-points[1][2])/(points[2][1]-points[1][1])
    points = [(x,y+SCREEN_EXTENSION_MM,z+slope*SCREEN_EXTENSION_MM) for x,y,z in points]
    wedge = Solid.extrude(Face(Wire.make_polygon([source_to_model(p) for p in points],close=True)),source_to_model((86,0,0)))
    body = stage('M14',body.cut(wedge))
    from rear_seat_support import rear_notch_tools
    body = stage('M15',body.cut(*rear_notch_tools()))
    # M16 front dovetail omitted by explicit user request; rear dovetail retained.
    rearcut = tool(121,1000,symmetric=True)
    body = stage('M18',body.cut(rearcut,rearcut.mirror(Plane.YZ)))
    from trunk_cavity import rear_cavity_tool
    cavity = rear_cavity_tool(SKETCHES['BodyCutSketch'])
    body = stage('M19',body.cut(cavity))
    tag_sketch = SKETCHES['AirtagCutSketch']
    tag = tool(126, airtag_depth, direction=-Vector(tag_sketch['normal']))
    body = stage('M20', body.cut(tag.translate(Vector(tag_sketch['yAxis']) * 90)))
    # Place the finished geometry before the stationary wheel-body subtraction.
    body = body.translate(ADAPTER_TRANSLATION_MM)
    from front_clip import redesign_front, trim_main_underside
    body = stage('M20-front-redesign', redesign_front(body))
    from screen_surround import reinforce_screen
    body = stage('M20-screen-surround', reinforce_screen(body))
    from print_planes import trim_to_rear_print_planes
    body = stage('M20-print-planes', trim_to_rear_print_planes(body))
    from trunk_cavity import rear_side_tools,trim_lower_rear_tip
    body = stage('M20-rear-side-relief', body.cut(*rear_side_tools()))
    body = stage('M20-lower-rear-tip', trim_lower_rear_tip(body))
    body = stage('M20-raised-underside', trim_main_underside(body))
    relief = seat_edge_relief()
    body = stage('M20-seat-edge-relief', body.cut(relief, relief.mirror(Plane.YZ)))
    if stop=='M20' or not imprint: return body
    from body_fillets import fillet_body
    body = stage('M20-body-fillets', fillet_body(body))
    cutter = load_wheel_cutter()
    return stage('M21', body.cut(cutter))


def export_master(output, *, stl=False, stop=None, imprint=True):
    start = time.monotonic()
    body = build_master(stop=stop, imprint=imprint)
    output.mkdir(exist_ok=True)
    stem = 'adapter-body' if not stop and imprint else 'adapter-body-'+(stop or 'pre-imprint')
    step = output / (stem + '.step')
    if not export_step(body, step):
        raise ValueError(f'STEP export failed: {step}')
    if stl:
        export_stl_mm(import_step(step), step.with_suffix('.stl'))
    report_path = Path(__file__).parent/'logs/build-validation.json'
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(dict(coordinateFrame="source (x,y,z) -> model (-x,-y,z); physical front is negative Y; Z up",adapterTranslationMm=ADAPTER_TRANSLATION_MM,seatingDepthMm=SEATING_DEPTH_MM,elapsedSeconds=time.monotonic()-start,stages=HISTORY),indent=2)+'\n')
    return step, body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-imprint',action='store_true')
    parser.add_argument('--stop',choices=['M01','M05','M06','M09','M20'])
    parser.add_argument('--stl', action='store_true', help='Also export the printable STL')
    args = parser.parse_args()
    export_master(ROOT / 'exports', stl=args.stl, stop=args.stop, imprint=not args.no_imprint)


if __name__=='__main__':
    main()
