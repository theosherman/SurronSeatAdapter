"""Separate editable latch with a native side profile and shared dovetail cut.

All geometry is constructed in Build123d's permanent (-x,-y,z) model frame.
The dovetail cutter consumes the adapter's selected profile, not a traced copy.
"""
from pathlib import Path
import argparse
import json
import math
from build123d import Edge, Wire, Face, Solid, Plane, Vector, Keep, Compound, ShapeList, export_step, export_stl, import_step, Mesher
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from coordinates import source_to_model, ADAPTER_TRANSLATION_MM
from adapter_profiles import profiles as adapter_profiles
from trunk_cavity import REAR_SIDE_X_MM, REAR_WALL_NORMAL, REAR_WALL_POINT_MM

ROOT = Path(__file__).resolve().parent
RECIPE = json.loads((ROOT/'cad-rebuild/accessories/latch-recipe.json').read_text())
FEATURES = {f['index']: f for f in RECIPE['features']}
# Run and inward movement of one straight outer ceiling edge in the XY view.
REAR_CEILING_TAPER = (54.0 - 28.183821804872828) / (260.01919499427396 - 174.31392815517032)
NOMINAL_CLEARANCE_MM = 0.2


TONGUE_RISE_MM = 18.0
TONGUE_THICKNESS_MM = 14.393670059803053
TONGUE_CORNER = Vector(0, 222.4245484695098, -29.76219965660978 + TONGUE_RISE_MM)
TONGUE_FILLET_MM = 10.0
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
    top_front = Vector(0, 149.9532667443008, 31.702071992564846)
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
    inner_corner_plane = corner - TONGUE_THICKNESS_MM * wall_normal
    underside = Vector(0, 1, UNDERSIDE_SLOPE)
    inner_root = shelf_front + underside * (
        (inner_corner_plane-shelf_front).dot(wall_normal) / underside.dot(wall_normal)
    )
    inner_corner = inner_tip + tip_direction * (
        (inner_corner_plane-inner_tip).dot(wall_normal) / tip_direction.dot(wall_normal)
    )

    points = (top_rear, top_front, shelf_front, inner_root, inner_corner, inner_tip)
    edges = [Edge.make_line(a, b) for a, b in zip(points, points[1:])]
    edges.extend((Edge.make_three_point_arc(inner_tip, rounded_tip, outer_tip),
                  Edge.make_line(outer_tip, corner), Edge.make_line(corner, top_rear)))
    return Face(Wire(edges))


def selected_faces(index):
    if index == 102:
        return [latch_side_profile()]
    if index == 104:
        # Rectangular width cap. Its rear edge lies beyond the latch blank.
        front_y, rear_y = 149.9532667443008, 263.445982162752
        x = REAR_SIDE_X_MM
        return [Face(Wire.make_polygon(
            [(-x, front_y, 0), (x, front_y, 0), (x, rear_y, 0), (-x, rear_y, 0)],
            close=True,
        ))]
    if index == 105:
        return adapter_profiles(18)
    raise ValueError(f'Unsupported latch profile: {index}')


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
    seam = (Vector(REAR_WALL_POINT_MM) - Vector(ADAPTER_TRANSLATION_MM)
            + normal * NOMINAL_CLEARANCE_MM + Vector(0, 0, TONGUE_RISE_MM))
    # Lift the taper planes with the tongue while retaining the 110 mm width cap.
    for side in (-1, 1):
        plane = Plane(
            (side * REAR_SIDE_X_MM, seam.Y, seam.Z),
            z_dir=(side, REAR_CEILING_TAPER, REAR_CEILING_TAPER * normal.Z / normal.Y),
        )
        envelope = envelope.split(plane, Keep.BOTTOM)
    return envelope


def fillet_latch(body, dovetail_cutter):
    """Round the exterior while preserving the full dovetail slot boundary."""
    tolerance = 1e-6
    edges = body.edges()
    tongue_edge, = [edge for edge in edges if (edge.center() - TONGUE_CORNER).length < tolerance]
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
            fillet.Add(EDGE_FILLET_MM, edge.wrapped)
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
    report = dict(clearanceMm=clearance, fillets=dict(tongueMm=TONGUE_FILLET_MM, exteriorMm=EDGE_FILLET_MM),
                  coordinateFrame='source (x,y,z) -> model (-x,-y,z)',
                  placementTranslationMm=ADAPTER_TRANSLATION_MM, stages=stages, reopened=reopened, physicalFitTested=False)
    report_path = Path(__file__).parent/'logs/latch-validation.json'
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2)+'\n')
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
