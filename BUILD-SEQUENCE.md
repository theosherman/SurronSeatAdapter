# Build and validation

Install the [locked Python 3.14 dependencies](README.md#run) before building.
The launcher uses `BUILD123D_PYTHON` if set, then `python3.14` on `PATH`, then
`/opt/az/bin/python3.14`. Use the same interpreter for the commands below.

| Command | Output |
| --- | --- |
| `./build.sh` | Full STEP set and interactive preview |
| `./build.sh --preview` | Master STEP and master-only preview |
| `./build.sh --stl` | Fresh STEP and STL set with the full preview |
| `./build.sh --release` | Fresh exports, release checks, and `exports/SurronSeatAdapter.zip` |
| `./build.sh --no-imprint` | Analytic master STEP before finishing and wheel subtraction |
| `./build.sh --stop M05` | Base checkpoint STEP. Also supports M01, M06, M09 and M20 |

Use `./build.sh --help` for the full option list. Checkpoint and pre-imprint
exports also accept `--stl`. The older `scripts/build-release.sh` entry point
delegates to `./build.sh --release`. Node.js is required for the release checks.

Routine builds read the checked-in wheel and seat references. The default and
preview modes reuse STEP files while inputs and outputs match the hashes in
`exports/build-state.json`. Delete that file for a fresh local build. The split
halves depend on the finished master STEP. Preview and release outputs go under
`exports/`. For individual parts, run `split_adapter.py`, `butterfly_keys.py`, or
`latch.py` with the same interpreter from the repository root. Build the master
before running `split_adapter.py`.

## Verification

The [release workflow](.github/workflows/cad-release.yml) runs the same release
command on GitHub Actions. It runs the Python regression suite, probes the
mounting ceilings in the STL, and reopens all six STEP and STL files to check
that each is a single valid solid before packaging. Successful builds publish
the ZIP to Releases and deploy `exports/preview.html` to GitHub Pages.

The following checks can also be run individually from the repository root.
Set `XDG_CACHE_HOME=/tmp/surron-build123d-cache` if your normal cache directory
is unavailable.

```bash
python3.14 -m unittest discover -s tests
node scripts/validate-cad-reference.mjs
node cad-rebuild/accessories/validate-accessory-recipes.mjs
```

For deeper checks, first run `./build.sh --stl`. Generate the pre-imprint
STEP with `./build.sh --no-imprint` after that if running the dovetail-root
or fillet-cutter checks.

| Command | Checks |
| --- | --- |
| `node scripts/validate-mounting-ceilings.mjs` | All 12 STL mounting ceiling probes, also run during releases |
| `python3.14 -m scripts.validate_exports` | Master STEP round-trip volume, STL agreement, scan cutter, and AirTag depth edit |
| `python3.14 -m scripts.validate_cavity` | Cavity boundaries and thickness. Optionally compare with `--approved-step PATH` |
| `python3.14 -m scripts.validate_dovetail_root` | Sharp latch-clearance edges |
| `python3.14 -m scripts.validate_fillets` | Mirrored pre-imprint fillets |
| `python3.14 -m scripts.validate_fillet_cutter` | Clearance between fillet faces and the scan cutter |

Validation reports in `logs/` are generated locally or attached to the GitHub
Actions run. The master report records per-stage validity, body count, volume,
and elapsed time. A checkpoint build updates that report. Historical
measurements are linked from the [design history](docs/DESIGN-HISTORY.md).
