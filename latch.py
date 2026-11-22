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
from adapter_profiles import profiles as adapter_profiles
from trunk_cavity import REAR_SIDE_X_MM, REAR_WALL_NORMAL, REAR_WALL_POINT_MM

ROOT = Path(__file__).resolve().parent
RECIPE = json.loads((ROOT/'cad-rebuild/accessories/latch-recipe.json').read_text())
FEATURES = {f['index']: f for f in RECIPE['features']}
SKETCHES = {s['name']: s for s in RECIPE['sketches'] + RECIPE['externalDependencies']}
# Run and inward movement of one straight outer ceiling edge in the XY view.
REAR_CEILING_TAPER = (54.0 - 28.183821804872828) / (260.01919499427396 - 174.31392815517032)
NOMINAL_CLEARANCE_MM = 0.2


def selected_faces(index):
    """Evaluate exact selected loops in their original sketch frames."""
    if index == 105:
        # Both master and latch derive their mating interface from the same data.
        return adapter_profiles(18)
    if index == 104:
        # Redraw TopCutSketch as a rectangle, keeping its original front edge.
        # The rear edge lies beyond the latch blank.
        front_y = 149.9532667443008
        rear_y = 263.445982162752
        x = REAR_SIDE_X_MM
        return [Face(Wire.make_polygon(
            [(-x, front_y, 0), (x, front_y, 0), (x, rear_y, 0), (-x, rear_y, 0)],
            close=True,
        ))]
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


def width_envelope():
    envelope = extrusion(104, (0, 0, 1), two_sided=True)
    normal = Vector(REAR_WALL_NORMAL)
    seam = Vector(REAR_WALL_POINT_MM) - Vector(ADAPTER_TRANSLATION_MM) + normal * NOMINAL_CLEARANCE_MM
    # In each horizontal section the taper starts at the sloped mating wall.
    # Keep the original width cap ahead of that wall.
    for side in (-1, 1):
        plane = Plane(
            (side * REAR_SIDE_X_MM, seam.Y, seam.Z),
            z_dir=(side, REAR_CEILING_TAPER, REAR_CEILING_TAPER * normal.Z / normal.Y),
        )
        envelope = envelope.split(plane, Keep.BOTTOM)
    return envelope


def build_latch(clearance=NOMINAL_CLEARANCE_MM, with_stages=False):
    """Return one latch solid; positive clearance moves three mating faces inward."""
    if not math.isfinite(clearance) or clearance < 0:
        raise ValueError('Latch clearance must be finite and nonnegative')
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
    body = stage(104, body.intersect(width_envelope()))
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
    body.label = 'Latch'
    return (body, stages) if with_stages else body


def export_latch(output, *, stl=False, clearance=NOMINAL_CLEARANCE_MM):
    body, stages = build_latch(clearance, with_stages=True)
    output.mkdir(exist_ok=True)
    step, stl_path = output/'latch.step', output/'latch.stl'
    export_step(body, step)
    exports = [('step', import_step(step))]
    if stl:
        export_stl(body, stl_path, tolerance=0.005, angular_tolerance=0.05)
        exports.append(('stl', Compound(Mesher().read(stl_path))))
    reopened = {}
    for name, shape in exports:
        bounds = shape.bounding_box()
        reopened[name] = dict(valid=shape.is_valid, solids=len(shape.solids()), volumeMm3=shape.volume,
                              boundsMm=[tuple(bounds.min), tuple(bounds.max)])
        if not shape.is_valid or len(shape.solids()) != 1 or abs(shape.volume-body.volume)>body.volume*1e-4:
            raise ValueError(f'Latch export failed validation: {reopened[name]}')
    report = dict(clearanceMm=clearance, fillets=False, coordinateFrame='source (x,y,z) -> model (-x,-y,z)',
                  placementTranslationMm=ADAPTER_TRANSLATION_MM, stages=stages, reopened=reopened, physicalFitTested=False)
    (Path(__file__).parent/'logs/latch-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return step, exports[0][1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clearance', type=float, default=NOMINAL_CLEARANCE_MM)
    parser.add_argument('--stl', action='store_true', help='Also export the printable STL')
    args = parser.parse_args()
    export_latch(Path(__file__).resolve().parent / 'exports', stl=args.stl, clearance=args.clearance)


if __name__ == '__main__':
    main()
