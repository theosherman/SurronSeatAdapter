"""Separate editable latch with a native side profile and shared dovetail cut.

All geometry is constructed in Build123d's permanent (-x,-y,z) model frame.
The dovetail cutter consumes the adapter's selected profile, not a traced copy.
"""
from pathlib import Path
import argparse
import json
import math
from build123d import Edge, Wire, Face, Solid, Plane, Vector, GeomType, Keep, Compound, ShapeList, export_step, export_stl, import_step
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from coordinates import source_to_model, ADAPTER_TRANSLATION_MM
from adapter_profiles import profiles as adapter_profiles
from scripts.validate_mesh import inspect_stl
from trunk_cavity import REAR_SIDE_X_MM, REAR_WALL_NORMAL

ROOT = Path(__file__).resolve().parent
RECIPE = json.loads((ROOT/'cad-rebuild/accessories/latch-recipe.json').read_text())
FEATURES = {f['index']: f for f in RECIPE['features']}
NOMINAL_CLEARANCE_MM = 0.2


MATING_WALL_TOP = Vector(0, 149.9532667443008, 31.702071992564846)
# Preserve the original taper's width at the outer tongue plane.
TONGUE_OUTER_HALF_WIDTH_MM = 44.23611308441336
TONGUE_RISE_MM = 18.0
TONGUE_THICKNESS_MM = 14.393670059803053
TONGUE_CORNER = Vector(0, 222.4245484695098, -29.76219965660978 + TONGUE_RISE_MM)
TONGUE_INNER_WALL_POINT = TONGUE_CORNER - Vector(REAR_WALL_NORMAL) * TONGUE_THICKNESS_MM
TONGUE_FILLET_MM = 10.0
TONGUE_ROOT_FILLET_MM = 4.5
EDGE_FILLET_MM = 1.0
BODY_THICKENING_MM = 3.0
# Approximate rise per millimeter rearward from the side-view redline.
UNDERSIDE_SLOPE = 0.154
# Lower edge of the sloped adapter wall after the approved underside trim.
MATING_WALL_BOTTOM_Z_MM = -8.769549214940586


def latch_side_profile():
    """Construct the latch as a single YZ profile before the shared dovetail cut."""
    wall_normal = Vector(REAR_WALL_NORMAL)
    toward_tip = Vector(0, wall_normal.Z, -wall_normal.Y)
    top_front = MATING_WALL_TOP
    wall_bottom = top_front + toward_tip * ((MATING_WALL_BOTTOM_Z_MM - top_front.Z) / toward_tip.Z)
    # Extend the mating wall along its plane to meet the offset underside.
    underside_normal = Vector(0, UNDERSIDE_SLOPE, -1).normalized()
    shelf_front = wall_bottom + toward_tip * (BODY_THICKENING_MM / toward_tip.dot(underside_normal))

    # Original faces 1 and 6 meet at corner. Keep its Y and the length of face 6.
    corner = TONGUE_CORNER
    outer_tip = Vector(0, 215.4245484695093, -43.00018346988403 + TONGUE_RISE_MM)
    tip_direction = (outer_tip-corner).normalized()
    tip_normal = Vector(0, -tip_direction.Z, tip_direction.Y)
    inner_tip = outer_tip - TONGUE_THICKNESS_MM * tip_normal
    rounded_tip = (outer_tip+inner_tip)*0.5 + tip_direction * (TONGUE_THICKNESS_MM*0.5)

    # Faces 7 and 10 are parallel offsets of the outer tongue faces.
    # The offset underside meets the original face 7 plane.
    top_rear = top_front + wall_normal * (corner-top_front).dot(wall_normal)
    underside = Vector(0, 1, UNDERSIDE_SLOPE)
    inner_root = shelf_front + underside * (
        (TONGUE_INNER_WALL_POINT-shelf_front).dot(wall_normal) / underside.dot(wall_normal)
    )
    inner_corner = inner_tip + tip_direction * (
        (TONGUE_INNER_WALL_POINT-inner_tip).dot(wall_normal) / tip_direction.dot(wall_normal)
    )

    points = (top_rear, top_front, shelf_front, inner_root, inner_corner, inner_tip)
    edges = [Edge.make_line(a, b) for a, b in zip(points, points[1:])]
    edges.extend((Edge.make_three_point_arc(inner_tip, rounded_tip, outer_tip),
                  Edge.make_line(outer_tip, corner), Edge.make_line(corner, top_rear)))
    return Face(Wire(edges))


def selected_faces(index):
    if index == 102:
        return [latch_side_profile()]
    if index == 105:
        return adapter_profiles(18)
    raise ValueError(f'Unsupported latch profile: {index}')


def extrusion(index, direction, distance=500):
    vector = Vector(direction).normalized()
    solids = [Solid.extrude(f, vector*distance)
              for f in selected_faces(index)]
    return solids[0].fuse(*solids[1:]) if len(solids)>1 else solids[0]


def source_plane(geometry):
    return Plane(source_to_model(geometry['origin']), z_dir=source_to_model(geometry['normal']))


def taper_sides(body):
    """Use one plane per side between the original front and rear widths."""
    wall_normal = Vector(REAR_WALL_NORMAL)
    front = MATING_WALL_TOP + wall_normal * NOMINAL_CLEARANCE_MM
    run = (TONGUE_CORNER - front).dot(wall_normal)
    taper = (REAR_SIDE_X_MM - TONGUE_OUTER_HALF_WIDTH_MM) / run
    for side in (-1, 1):
        plane = Plane(front + Vector(side * REAR_SIDE_X_MM, 0, 0),
                      z_dir=Vector(side, 0, 0) + wall_normal * taper)
        body = body.split(plane, Keep.BOTTOM)
    return body


def fillet_latch(body, dovetail_cutter):
    """Round the exterior while preserving the full dovetail slot boundary."""
    tolerance = 1e-6
    edges = body.edges()
    tongue_edge, = [edge for edge in edges if (edge.center() - TONGUE_CORNER).length < tolerance]
    # The preview numbers faces by area. Locate the inner tongue wall by its design plane.
    wall_normal = Vector(REAR_WALL_NORMAL)
    root_face, = [face for face in body.faces().filter_by(GeomType.PLANE)
                  if face.normal_at().dot(-wall_normal) > 1 - tolerance
                  and abs((face.center() - TONGUE_INNER_WALL_POINT).dot(wall_normal)) < tolerance]
    root_edges = sorted(root_face.edges(), key=lambda edge: edge.length)[-2:]
    faces = [(face, face.edges()) for face in body.faces()]
    fillet = BRepFilletAPI_MakeFillet(body.wrapped)
    fillet.Add(TONGUE_FILLET_MM, tongue_edge.wrapped)
    for edge in edges:
        if edge.is_same(tongue_edge) or edge.distance_to(dovetail_cutter) < tolerance:
            continue
        point = edge.position_at(0.5)
        first, second = [face.normal_at(point) for face, boundary in faces
                         if any(edge.is_same(segment) for segment in boundary)]
        # The existing rounded tip joins the tongue planes tangentially.
        if first.dot(second) < 1 - tolerance:
            radius = TONGUE_ROOT_FILLET_MM if any(edge.is_same(root) for root in root_edges) else EDGE_FILLET_MM
            fillet.Add(radius, edge.wrapped)
    fillet.Build()
    if not fillet.IsDone():
        raise ValueError('Latch fillets did not build')
    result = Solid(fillet.Shape()).clean()
    if not result.is_valid or len(result.solids()) != 1:
        raise ValueError('Latch fillets did not produce one valid solid')
    return result


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
    body = stage(104, taper_sides(body))
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
    body = fillet_latch(body, slot)
    # Follow the adapter assembly placement while retaining a separate solid.
    body = body.translate(ADAPTER_TRANSLATION_MM)
    body.label = 'Latch'
    return (body, stages) if with_stages else body


def export_latch(output, *, stl=False, clearance=NOMINAL_CLEARANCE_MM):
    body, stages = build_latch(clearance, with_stages=True)
    output.mkdir(exist_ok=True)
    step, stl_path = output/'latch.step', output/'latch.stl'
    export_step(body, step)
    reopened_step = import_step(step)
    bounds = reopened_step.bounding_box()
    reopened = {'step': dict(valid=reopened_step.is_valid, solids=len(reopened_step.solids()),
                             volumeMm3=reopened_step.volume,
                             boundsMm=[tuple(bounds.min), tuple(bounds.max)])}
    if stl:
        export_stl(body, stl_path, tolerance=0.005, angular_tolerance=0.05)
        reopened['stl'] = inspect_stl(stl_path)
    for name, metrics in reopened.items():
        if not metrics['valid'] or metrics['solids'] != 1 or abs(metrics['volumeMm3'] - body.volume) > body.volume * 1e-4:
            raise ValueError(f'Latch {name} export failed validation: {metrics}')
    report = dict(clearanceMm=clearance, fillets=dict(tongueMm=TONGUE_FILLET_MM,
                                                    tongueRootMm=TONGUE_ROOT_FILLET_MM, exteriorMm=EDGE_FILLET_MM),
                  coordinateFrame='source (x,y,z) -> model (-x,-y,z)',
                  placementTranslationMm=ADAPTER_TRANSLATION_MM, stages=stages, reopened=reopened, physicalFitTested=False)
    report_path = Path(__file__).parent/'logs/latch-validation.json'
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return step, reopened_step


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clearance', type=float, default=NOMINAL_CLEARANCE_MM)
    parser.add_argument('--stl', action='store_true', help='Also export the printable STL')
    args = parser.parse_args()
    export_latch(Path(__file__).resolve().parent / 'exports', stl=args.stl, clearance=args.clearance)


if __name__ == '__main__':
    main()
