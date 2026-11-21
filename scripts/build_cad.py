"""Build the CAD exports and preview in one Python process."""
from argparse import ArgumentParser
from pathlib import Path

from build123d import import_step

from adapter import export_master
from .preview_stl import REFERENCE_MESHES, preview_parts, write_preview


def main():
    parser = ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--preview', action='store_true', help='Build only the master and its preview')
    mode.add_argument('--stl', action='store_true', help='Also export printable STLs')
    args = parser.parse_args()
    output = Path('exports')
    step, body = export_master(output, stl=args.stl)

    if args.preview:
        parts = [step]
        shapes = {step: body}
    else:
        from butterfly_keys import export_keys
        from latch import export_latch
        from split_adapter import export_split

        master = import_step(step)
        # Meshing the printable halves can attach fine triangulations to faces
        # they share with the master. Reload its STEP for the release preview.
        shapes = {} if args.stl else {step: master}
        shapes.update(export_split(output, master, stl=args.stl))
        export_keys(output, stl=args.stl)
        latch_step, latch = export_latch(output, stl=args.stl)
        shapes[latch_step] = latch
        parts = preview_parts(output)

    print(write_preview([*parts, *REFERENCE_MESHES], output / 'preview.html', shapes=shapes))


if __name__ == '__main__':
    main()
