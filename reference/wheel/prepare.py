"""Prepare the Sherman P scan independently; align the complete scan before slicing and body-only scaling."""
from argparse import ArgumentParser
from pathlib import Path
import struct
import subprocess
from tempfile import TemporaryDirectory
from build123d import Mesher, Plane, Keep, Axis, Compound, export_brep, import_brep, export_step, export_stl, import_step
from coordinates import source_to_model
from . import SEATING_DEPTH_MM, WHEEL_REFERENCE
from .scan_patch import PATCH, repair_screen_patch

FRONT_Y = -191.0
REAR_Y = 170.0
BODY_SCALE = 1.003
# Translate the fit-scale pivot with the wheel to preserve its exact rise after scaling.
SCALE_ORIGIN = (0, 0, SEATING_DEPTH_MM)
# Approved lower-outer-bottom alignment, in the permanent Build123d frame.
ALIGNMENT_ANGLE_DEG = -3.4932161177016057
ALIGNMENT_TRANSLATION_MM = (0, 0, 3.464786838041892 + SEATING_DEPTH_MM)


def align_scan(scan):
    """Rigidly move the entire EUC, including handles, about model origin."""
    return scan.rotate(Axis.X, ALIGNMENT_ANGLE_DEG).translate(ALIGNMENT_TRANSLATION_MM)


def prepare_parts(scan):
    """Return the three regions, scaled body, and reunited preview solid."""
    scan = align_scan(scan)
    front_plane = Plane(origin=(0, FRONT_Y, 0), z_dir=(0, 1, 0))
    rear_plane = Plane(origin=(0, REAR_Y, 0), z_dir=(0, 1, 0))
    remainder, front = scan.split(front_plane, keep=Keep.BOTH)
    rear, body = remainder.split(rear_plane, keep=Keep.BOTH)
    scaled = body.scale(BODY_SCALE, about=SCALE_ORIGIN)
    front = Compound(front) if isinstance(front, list) else front
    rear = Compound(rear) if isinstance(rear, list) else rear
    return {'front-handle': front, 'body-original': body, 'rear-handle': rear,
            'body-scaled': scaled, 'merged': scaled.fuse(front, rear)}


def prepare_scan(source, destination):
    """Convert source vertices and normals, then repair the exact source patch."""
    data = bytearray(source.read_bytes())
    count = struct.unpack_from('<I', data, 80)[0]
    if len(data) != 84 + count * 50:
        raise ValueError('Expected a binary STL')
    for i in range(count):
        for j in range(4):
            offset = 84 + i * 50 + j * 12
            xyz = struct.unpack_from('<3f', data, offset)
            struct.pack_into('<3f', data, offset, *source_to_model(xyz))
    repaired = repair_screen_patch(data)
    # The approved connectivity repair preserves every original vertex.
    def vertices(mesh):
        return {struct.unpack_from('<3f', mesh, 84 + i * 50 + j * 12)
                for i in range(count) for j in (1, 2, 3)}

    assert len(repaired) == len(data) and repaired != data
    assert vertices(repaired) == vertices(data)
    destination.write_bytes(repaired)


def main():
    ArgumentParser(description=__doc__).parse_args()
    with TemporaryDirectory(dir=WHEEL_REFERENCE) as work:
        work = Path(work)
        aligned = work / 'aligned.stl'
        subprocess.run(['node', str(WHEEL_REFERENCE / 'align-source.mjs'), str(aligned)], check=True)
        repaired = work / 'repaired.stl'
        prepare_scan(aligned, repaired)
        scan, = Mesher().read(repaired)
        assert scan.is_valid and len(scan.solids()) == 1
        assert abs(scan.volume - PATCH['repairedSignedVolumeMm3']) < 0.1
        parts = prepare_parts(scan)
        assert all(part.is_valid for part in parts.values())
        assert len(parts['body-scaled'].solids()) == len(parts['merged'].solids()) == 1
        partition = sum(parts[name].volume for name in ('front-handle', 'body-original', 'rear-handle'))
        assert abs(partition - scan.volume) < 0.1
        assert abs(parts['body-scaled'].volume - parts['body-original'].volume * BODY_SCALE**3) < 0.1

        cutter = work / 'body-scaled.brep'
        if not export_brep(parts['body-scaled'], cutter):
            raise ValueError(f'Could not export {cutter.name}')
        reopened = import_brep(cutter)
        assert reopened.is_valid and len(reopened.solids()) == 1
        assert abs(reopened.volume - parts['body-scaled'].volume) < 0.2
        for name in ('front-handle', 'rear-handle'):
            step = work / f'{name}.step'
            if not export_step(parts[name], step):
                raise ValueError(f'Could not export {step.name}')
            reopened = import_step(step)
            assert reopened.is_valid and len(reopened.solids()) == len(parts[name].solids())
            assert abs(reopened.volume - parts[name].volume) < 0.2
        merged = work / 'merged.stl'
        if not export_stl(parts['merged'], merged, tolerance=0.005, angular_tolerance=0.05):
            raise ValueError(f'Could not export {merged.name}')
        reopened, = Mesher().read(merged)
        assert reopened.is_valid and len(reopened.solids()) == 1
        assert abs(reopened.volume - parts['merged'].volume) < 0.2
        for name in ('body-scaled.brep', 'front-handle.step', 'rear-handle.step', 'merged.stl'):
            (work / name).replace(WHEEL_REFERENCE / name)
            print(WHEEL_REFERENCE / name)


if __name__ == '__main__':
    main()
