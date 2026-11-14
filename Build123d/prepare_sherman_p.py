"""Prepare the Sherman P scan independently; handles retain their original placement."""
from pathlib import Path
import hashlib
import json
import time
from build123d import Mesher, Plane, Keep, export_step, export_stl, import_step
from coordinates import prepare_scan

ROOT = Path(__file__).resolve().parents[1]
FRONT_Y = -191.0
REAR_Y = 170.0
BODY_SCALE = 1.003
SCALE_ORIGIN = (0, 0, 0)


def prepare_parts(scan):
    """Return original three regions, scaled body, and reunited solid in model mm."""
    front_plane = Plane(origin=(0, FRONT_Y, 0), z_dir=(0, 1, 0))
    rear_plane = Plane(origin=(0, REAR_Y, 0), z_dir=(0, 1, 0))
    front = scan.split(front_plane, keep=Keep.BOTTOM)
    remainder = scan.split(front_plane, keep=Keep.TOP)
    body = remainder.split(rear_plane, keep=Keep.BOTTOM)
    rear = remainder.split(rear_plane, keep=Keep.TOP)
    scaled = body.scale(BODY_SCALE, about=SCALE_ORIGIN)
    merged = scaled.fuse(front, rear)
    return {'front-handle': front, 'body-original': body, 'rear-handle': rear,
            'body-scaled': scaled, 'merged': merged}


def measurements(shape):
    box = shape.bounding_box()
    return dict(valid=bool(shape.is_valid), solids=len(shape.solids()),
                volumeMm3=shape.volume, boundsMm=[list(box.min), list(box.max)])


def main():
    start = time.monotonic()
    source = ROOT/'Sherman_P_Scan_Aligned_To_Adapter_mm.stl'
    scan_path = prepare_scan(source, ROOT/'Build123d/inputs/wheel-scan-model-frame.stl')
    scan = Mesher().read(scan_path)[0]
    print('Splitting scan and scaling body only; fusing fixed handles', flush=True)
    parts = prepare_parts(scan)
    report = dict(source=source.name, sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  frame='Build123d (-source X, -source Y, source Z), millimeters',
                  cutPlanesYmm=[FRONT_Y, REAR_Y], bodyScale=BODY_SCALE,
                  scaleOriginMm=SCALE_ORIGIN, handleTransform='identity',
                  adapterUpdated=False, sourceScan=measurements(scan),
                  parts={name: measurements(p) for name, p in parts.items()})
    for name, p in parts.items():
        assert p.is_valid and len(p.solids()) == 1, name
    original = [parts[k] for k in ('front-handle', 'body-original', 'rear-handle')]
    partition_error = sum(p.volume for p in original) - scan.volume
    assert abs(partition_error) < 0.1, partition_error
    scale_error = parts['body-scaled'].volume - parts['body-original'].volume * BODY_SCALE**3
    assert abs(scale_error) < 0.1, scale_error
    # Independently reclip the original scan to prove fixed-handle geometry survived.
    handle_errors = {}
    for name, y, side in [('front-handle', FRONT_Y, Keep.BOTTOM), ('rear-handle', REAR_Y, Keep.TOP)]:
        reference = scan.split(Plane(origin=(0,y,0), z_dir=(0,1,0)), keep=side)
        handle_errors[name] = abs(reference.volume-parts[name].volume)
        assert handle_errors[name] < 0.1
        assert measurements(reference)['boundsMm'] == measurements(parts[name])['boundsMm']
    report['validation'] = dict(partitionVolumeErrorMm3=partition_error,
                                bodyScaleVolumeErrorMm3=scale_error,
                                unchangedHandleVolumeErrorsMm3=handle_errors)
    output = ROOT/'Build123d/exports/sherman-p-prepared'
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
    path = ROOT/'Build123d/logs/sherman-p-preparation.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
