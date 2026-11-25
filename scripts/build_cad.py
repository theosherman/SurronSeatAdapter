"""Build the CAD exports and preview in one Python process."""
from argparse import ArgumentParser
from fcntl import LOCK_EX, flock
from hashlib import file_digest
import json
from pathlib import Path
import sys

from build123d import __version__ as BUILD123D_VERSION, import_step
from OCP import __version__ as OCP_VERSION

from .preview_stl import REFERENCE_MESHES, preview_parts, write_preview

ROOT = Path(__file__).resolve().parents[1]
SHARED_INPUTS = ('adapter_profiles.py', 'coordinates.py', 'adapter-placement.json',
                 'cad-rebuild/recipe.json')
MASTER_INPUTS = (*SHARED_INPUTS, 'adapter.py', 'body_fillets.py', 'body-fillets.json',
                 'bottom_outline.py', 'cut_offsets.py', 'front_clip.py', 'print_planes.py',
                 'rear_seat_support.py',
                 'screen_surround.py', 'seat_shoulders.py', 'trunk_cavity.py',
                 'reference/wheel/__init__.py', 'reference/wheel/body-scaled.brep')
CONNECTOR_INPUTS = (*SHARED_INPUTS, 'split_adapter.py', 'trunk_cavity.py')
PART_INPUTS = {
    'adapter': MASTER_INPUTS,
    'split halves': (*CONNECTOR_INPUTS, 'measure.py'),
    'butterfly keys': (*CONNECTOR_INPUTS, 'butterfly_keys.py'),
    'latch': (*SHARED_INPUTS, 'latch.py', 'trunk_cavity.py',
              'cad-rebuild/accessories/latch-recipe.json'),
}
BUILD_ENVIRONMENT = [sys.version, BUILD123D_VERSION, OCP_VERSION]


def hashes(paths):
    result = {}
    for path in paths:
        with path.open('rb') as source:
            result[str(path)] = file_digest(source, 'sha256').hexdigest()
    return result


def read_records(path):
    try:
        records = json.loads(path.read_text())
    except (FileNotFoundError, ValueError):
        return {}
    return records if isinstance(records, dict) else {}


def build(output, *, preview_only, stl):
    record_path = output / 'build-state.json'
    if stl:
        # Printable exports start from a clean set of generated CAD files.
        stems = ('adapter-body', 'adapter-body-split-front', 'adapter-body-split-rear',
                 'adapter-body-pre-imprint', 'adapter-body-M[0-9][0-9]',
                 'butterfly-key-top', 'butterfly-key-cavity', 'latch')
        patterns = [f'{stem}.{extension}' for stem in stems for extension in ('step', 'stl')]
        patterns.extend(('preview.html', '*.preview.html'))
        for pattern in patterns:
            for path in output.glob(pattern):
                path.unlink()
        record_path.unlink(missing_ok=True)
    records = read_records(record_path)
    shapes = {}
    # Take a consistent snapshot before importing the model modules.
    used_inputs = [MASTER_INPUTS] if preview_only else PART_INPUTS.values()
    source_hashes = hashes(sorted({ROOT / name for group in used_inputs for name in group}))

    def update(name, filenames, run, *, generated_inputs=()):
        outputs = [output / filename for filename in filenames]
        sources = (str(ROOT / source) for source in PART_INPUTS[name])
        input_hashes = {source: source_hashes[source] for source in sources}
        input_hashes.update(hashes(generated_inputs))
        fingerprint = {'environment': BUILD_ENVIRONMENT, 'inputs': input_hashes}
        if not stl and all(path.is_file() for path in outputs):
            if records.get(name) == {**fingerprint, 'outputs': hashes(outputs)}:
                print(f'Reusing {name}', flush=True)
                return
        print(f'Building {name}', flush=True)
        run()
        records[name] = {**fingerprint, 'outputs': hashes(outputs)}

    def master_export():
        from adapter import export_master

        step, body = export_master(output, stl=stl)
        shapes[step] = body

    step = output / 'adapter-body.step'
    update('adapter', (step.name,), master_export)

    if preview_only:
        parts = [step]
    else:
        from butterfly_keys import export_keys
        from latch import export_latch
        from split_adapter import export_split

        def split_export():
            master = import_step(step)
            shapes.update(export_split(output, master, stl=stl))
            # The release preview reloads the master after the printable halves
            # have been meshed, since they may share faces with the master.
            if not stl:
                shapes[step] = master

        def latch_export():
            latch_step, latch = export_latch(output, stl=stl)
            shapes[latch_step] = latch

        update('split halves', ('adapter-body-split-front.step', 'adapter-body-split-rear.step'),
               split_export, generated_inputs=(step,))
        update('butterfly keys', ('butterfly-key-top.step', 'butterfly-key-cavity.step'),
               lambda: export_keys(output, stl=stl))
        update('latch', ('latch.step',), latch_export)
        if stl:
            shapes.pop(step)
        parts = preview_parts(output)

    preview = output / 'preview.html'
    temporary_preview = preview.with_suffix('.html.tmp')
    write_preview([*parts, *REFERENCE_MESHES], temporary_preview, shapes=shapes)
    temporary_preview.replace(preview)
    temporary_record = record_path.with_suffix('.json.tmp')
    temporary_record.write_text(json.dumps(records, indent=2) + '\n')
    temporary_record.replace(record_path)
    print(preview)


def main():
    parser = ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--preview', action='store_true', help='Build only the master and its preview')
    mode.add_argument('--stl', action='store_true', help='Rebuild all parts and export printable STLs')
    parser.add_argument('--no-imprint', action='store_true', help='Export the analytic master before finishing and imprint')
    parser.add_argument('--stop', choices=('M01', 'M05', 'M06', 'M09', 'M20'),
                        help='Export only a master checkpoint')
    args = parser.parse_args()
    master_only = args.no_imprint or args.stop is not None
    if master_only and args.preview:
        parser.error('--no-imprint and --stop cannot be combined with --preview')
    output = Path('exports')
    output.mkdir(exist_ok=True)
    with (output / '.build.lock').open('a') as lock:
        flock(lock, LOCK_EX)
        if master_only:
            from adapter import export_master

            export_master(output, stl=args.stl, stop=args.stop, imprint=not args.no_imprint)
        else:
            build(output, preview_only=args.preview, stl=args.stl)


if __name__ == '__main__':
    main()
