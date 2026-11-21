"""Prepare the Sherman P scan independently; align the complete scan before slicing and body-only scaling."""
from pathlib import Path
import hashlib
import json
import time
from build123d import Mesher, Plane, Keep, Axis, Compound, export_step, export_stl, import_step
from coordinates import prepare_scan

ROOT = Path(__file__).resolve().parent
FRONT_Y = -191.0
REAR_Y = 170.0
BODY_SCALE = 1.003
SEAT_LOWERING_MM = 15.0  # Relative to the printed 8 mm deeper-seating revision.
SEATING_DEPTH_MM = 8.0 + SEAT_LOWERING_MM
# Translate the fit-scale pivot with the wheel to preserve the exact rise.
SCALE_ORIGIN = (0, 0, SEATING_DEPTH_MM)
# Approved lower-outer-bottom alignment, in the permanent Build123d frame.
ALIGNMENT_ANGLE_DEG = -3.4932161177016057
ALIGNMENT_TRANSLATION_MM = (0, 0, 3.464786838041892 + SEATING_DEPTH_MM)


def align_scan(scan):
    """Rigidly move the entire EUC, including handles, about model origin."""
    return scan.rotate(Axis.X, ALIGNMENT_ANGLE_DEG).translate(ALIGNMENT_TRANSLATION_MM)


def prepare_parts(scan, reunite=True):
    """Return the three regions and scaled body; optionally add a reunited solid."""
    scan = align_scan(scan)
    front_plane = Plane(origin=(0, FRONT_Y, 0), z_dir=(0, 1, 0))
    rear_plane = Plane(origin=(0, REAR_Y, 0), z_dir=(0, 1, 0))
    front = scan.split(front_plane, keep=Keep.BOTTOM)
    remainder = scan.split(front_plane, keep=Keep.TOP)
    body = remainder.split(rear_plane, keep=Keep.BOTTOM)
    rear = remainder.split(rear_plane, keep=Keep.TOP)
    scaled = body.scale(BODY_SCALE, about=SCALE_ORIGIN)
    front = Compound(front) if isinstance(front, list) else front
    rear = Compound(rear) if isinstance(rear, list) else rear
    parts = {'front-handle': front, 'body-original': body, 'rear-handle': rear,
            'body-scaled': scaled}
    if reunite:
        parts['merged'] = scaled.fuse(front, rear)
    return parts


def measurements(shape):
    box = shape.bounding_box()
    return dict(valid=bool(shape.is_valid), solids=len(shape.solids()),
                volumeMm3=shape.volume, boundsMm=[list(box.min), list(box.max)])


def main():
    start = time.monotonic()
    source = ROOT/'reference/fusion/Sherman_P_Scan_Aligned_To_Adapter_mm.stl'
    scan_path = prepare_scan(source, ROOT/'inputs/wheel-scan-model-frame.stl')
    scan = Mesher().read(scan_path)[0]
    print('Aligning entire scan, splitting, scaling body only; fusing unscaled handles', flush=True)
    parts = prepare_parts(scan)
    aligned = align_scan(scan)
    report = dict(source=source.name, sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  frame='Build123d (-source X, -source Y, source Z), millimeters',
                  cutPlanesYmm=[FRONT_Y, REAR_Y], bodyScale=BODY_SCALE,
                  scaleOriginMm=SCALE_ORIGIN, seatingDepthMm=SEATING_DEPTH_MM,
                  alignment=dict(axis='+X', angleDegrees=ALIGNMENT_ANGLE_DEG,
                                 pivotMm=[0,0,0], translationMm=ALIGNMENT_TRANSLATION_MM,
                                 order='whole scan rigid motion, world-Y slices, body-only scale'),
                  handleTransform='whole-scan alignment only; no fit scale',
                  adapterUpdated=False, sourceScan=measurements(scan), alignedScan=measurements(aligned),
                  parts={name: measurements(p) for name, p in parts.items()})
    for name, p in parts.items():
        assert p.is_valid and len(p.solids()) >= 1, name
        if name in ('body-original', 'body-scaled', 'merged'):
            assert len(p.solids()) == 1, name
    original = [parts[k] for k in ('front-handle', 'body-original', 'rear-handle')]
    partition_error = sum(p.volume for p in original) - scan.volume
    assert abs(partition_error) < 0.1, partition_error
    scale_error = parts['body-scaled'].volume - parts['body-original'].volume * BODY_SCALE**3
    assert abs(scale_error) < 0.1, scale_error
    # Independently reclip the moved whole scan to verify unscaled handle geometry.
    handle_errors = {}
    for name, y, side in [('front-handle', FRONT_Y, Keep.BOTTOM), ('rear-handle', REAR_Y, Keep.TOP)]:
        reference = aligned.split(Plane(origin=(0,y,0), z_dir=(0,1,0)), keep=side)
        reference = Compound(reference) if isinstance(reference, list) else reference
        handle_errors[name] = abs(reference.volume-parts[name].volume)
        assert handle_errors[name] < 0.1
        assert measurements(reference)['boundsMm'] == measurements(parts[name])['boundsMm']
    report['validation'] = dict(partitionVolumeErrorMm3=partition_error,
                                bodyScaleVolumeErrorMm3=scale_error,
                                unscaledAlignedHandleVolumeErrorsMm3=handle_errors)
    output = ROOT/'exports/sherman-p-prepared'
    output.mkdir(parents=True, exist_ok=True)
    for name, part in parts.items():
        export_step(part, output/f'{name}.step')
        export_stl(part, output/f'{name}.stl', tolerance=0.005, angular_tolerance=0.05)
    print('Reopening merged STEP and STL', flush=True)
    reopened_step = import_step(output/'merged.step')
    reopened_stl = Mesher().read(output/'merged.stl')[0]
    for name, part in [('step', reopened_step), ('stl', reopened_stl)]:
        report['validation'][f'reopened_{name}'] = measurements(part)
        assert part.is_valid and len(part.solids()) == 1
        assert abs(part.volume-parts['merged'].volume) < 0.2
    report['elapsedSeconds'] = time.monotonic()-start
    path = ROOT/'logs/sherman-p-preparation.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
