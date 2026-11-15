"""Separate editable latch, reconstructed from exact millimeter source loops.

All geometry is constructed in Build123d's permanent (-x,-y,z) model frame.
The dovetail cutter consumes the adapter's selected profile, not a traced copy.
"""
from pathlib import Path
import argparse
import json
import math
from build123d import Edge, Wire, Face, Solid, Plane, Vector, Keep, Compound, ShapeList, export_step, export_stl, import_step, Mesher
from coordinates import source_to_model, ADAPTER_TRANSLATION_MM
from adapter import profiles as adapter_profiles
from rear_cavity import REAR_WALL_MOVE_MM,dimension,extend_latch

ROOT = Path(__file__).resolve().parents[1]
RECIPE = json.loads((ROOT/'cad-rebuild/accessories/latch-recipe.json').read_text())
FEATURES = {f['index']: f for f in RECIPE['features']}
SKETCHES = {s['name']: s for s in RECIPE['sketches'] + RECIPE['externalDependencies']}


def selected_faces(index):
    """Evaluate exact selected loops in their original sketch frames."""
    if index == 105:
        # Both master and latch derive their mating interface from the same data.
        return adapter_profiles(18)
    faces = []
    for profile in FEATURES[index]['profiles']:
        sketch = SKETCHES[profile['sketch']]
        origin, x, y = (Vector(source_to_model(sketch[k])) for k in ('origin','xAxis','yAxis'))
        normal = x.cross(y)
        def point(p):
            return origin + x*p[0] + y*p[1] + normal*p[2]
        loops = []
        for loop in profile['loops']:
            edges = []
            for curve in loop['curves']:
                kind = curve['type'].split('::')[-1]
                if kind == 'Line3D':
                    edge = Edge.make_line(point(curve['start']), point(curve['end']))
                elif kind == 'Arc3D':
                    edge = Edge.make_three_point_arc(point(curve['start']), point(curve['mid']), point(curve['end']))
                else:
                    raise ValueError(f'Unsupported latch curve: {kind}')
                edges.append(edge)
            wire = Wire(edges)
            if not wire.is_closed:
                raise ValueError(f'Open latch profile at source {index}')
            loops.append((loop['outer'], wire))
        outer = [w for is_outer,w in loops if is_outer]
        if len(outer) != 1:
            raise ValueError('Expected one outer loop')
        face = Face(outer[0], [w for is_outer,w in loops if not is_outer])
        if abs(face.area-profile['areaMm2']) > 0.01:
            raise ValueError(f'Source profile area mismatch at {index}')
        faces.append(face)
    return faces


def extrusion(index, direction, distance=500, two_sided=False):
    vector = Vector(direction).normalized()
    solids = [Solid.extrude(f.translate(-vector*distance/2) if two_sided else f, vector*distance)
              for f in selected_faces(index)]
    return solids[0].fuse(*solids[1:]) if len(solids)>1 else solids[0]


def source_plane(geometry):
    return Plane(source_to_model(geometry['origin']), z_dir=source_to_model(geometry['normal']))


def build_latch(clearance=0.2, with_stages=False, rear_wall_move=REAR_WALL_MOVE_MM, adapter_body=None):
    """Return the separate extended latch; move=0 retains historical source geometry."""
    if not math.isfinite(clearance) or clearance < 0:
        raise ValueError('Latch clearance must be finite and nonnegative')
    dimension(rear_wall_move,'Rear wall movement')
    stages = []
    def stage(index, shape):
        if isinstance(shape, (list, ShapeList)):
            shape = Compound(shape)
        shape = shape.clean()
        bounds = shape.bounding_box()
        row = dict(sourceIndex=index, volumeMm3=shape.volume,
                   valid=shape.is_valid, solids=len(shape.solids()),
                   boundsMm=[tuple(bounds.min), tuple(bounds.max)])
        if not row['valid'] or row['solids'] != 1:
            raise ValueError(f'Invalid latch stage: {row}')
        stages.append(row)
        return shape

    first = FEATURES[102]['extentOne']
    # Extrude to the source oblique side plane, retaining the origin-side half.
    blank = extrusion(102, source_to_model(first['directionHint']))
    body = stage(102, blank.split(source_plane(first['entity']['geometry']), Keep.BOTTOM))
    body = stage(103, body.fuse(body.mirror(Plane.YZ)))
    body = stage(104, body.intersect(extrusion(104, (0,0,1), two_sided=True)))
    slot_extent = FEATURES[105]['extentOne']
    slot = extrusion(105, source_to_model(slot_extent['directionHint']))
    slot = slot.split(source_plane(slot_extent['entity']['geometry']), Keep.BOTTOM)
    body = stage(105, body.cut(slot))
    if clearance:
        # Two top shoulder faces share one infinite plane; the third is the
        # broad front mating face. Their outward normals define inward offsets.
        planes = []
        for selector in FEATURES[106]['inputFaces']:
            geometry = selector['geometry']
            normal = Vector(source_to_model(geometry['normal']))
            if selector['isParamReversed']:
                normal = -normal
            origin = Vector(source_to_model(geometry['origin'])) - normal*clearance
            if any(abs(normal.dot(n)-1)<1e-9 and abs((origin-o).dot(n))<1e-7 for o,n in planes):
                continue
            planes.append((origin, normal))
            body = body.split(Plane(origin, z_dir=normal), Keep.BOTTOM)
    body = stage(106, body)
    # Follow the adapter assembly placement while retaining a separate solid.
    body = body.translate(ADAPTER_TRANSLATION_MM)
    if rear_wall_move:
        if adapter_body is None:
            from adapter import build_master
            adapter_body=build_master(imprint=False,rear_wall_move=rear_wall_move)
        body=stage('rear-cavity',extend_latch(body,adapter_body,rear_wall_move,clearance))
    body.label = 'Latch'
    return (body, stages) if with_stages else body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clearance', type=float, default=0.2)
    args = parser.parse_args()
    body, stages = build_latch(args.clearance, with_stages=True)
    output = Path(__file__).parent/'exports'
    output.mkdir(exist_ok=True)
    step, stl = output/'latch.step', output/'latch.stl'
    export_step(body, step)
    export_stl(body, stl, tolerance=0.005, angular_tolerance=0.05)
    reopened = {}
    for name, shape in [('step', import_step(step)), ('stl', Compound(Mesher().read(stl)))]:
        bounds = shape.bounding_box()
        reopened[name] = dict(valid=shape.is_valid, solids=len(shape.solids()), volumeMm3=shape.volume,
                              boundsMm=[tuple(bounds.min), tuple(bounds.max)])
        if not shape.is_valid or len(shape.solids()) != 1 or abs(shape.volume-body.volume)>body.volume*1e-4:
            raise ValueError(f'Latch export failed validation: {reopened[name]}')
    report = dict(clearanceMm=args.clearance, rearWallMoveMm=REAR_WALL_MOVE_MM, fillets=False, coordinateFrame='source (x,y,z) -> model (-x,-y,z)',
                  placementTranslationMm=ADAPTER_TRANSLATION_MM, stages=stages, reopened=reopened, physicalFitTested=False)
    (Path(__file__).parent/'logs/latch-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
