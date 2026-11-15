# build123d adapter reconstruction

The full, unsplit adapter is reconstructed as editable Python solid geometry from the repository's millimeter recipe. The final wheel imprint subtracts only the prepared Sherman P middle body, with the source screen patch reconnected before preparation and uniformly scaled by **1.003** about model origin after cuts at Y=-191/+170 mm. Both handles move with the complete scan during alignment, remain unscaled after slicing, and are excluded from subtraction. The master has no fillets or connector recesses. The latch is a separate editable accessory; no split variant or saddlebag mount is built by this project.

## Run

Dependencies live outside this Git repository:

```bash
# Existing environment on this machine:
Build123d/run.sh

# Recreate on another machine (use a Python version supported by the pinned wheels):
python -m venv ~/.local/share/venvs/surron-build123d
~/.local/share/venvs/surron-build123d/bin/pip install -r Build123d/requirements.lock.txt
Build123d/run.sh
```

Set `BUILD123D_PYTHON` to use a different environment. Installed here with Python 3.14.7, build123d 0.13.0, and OCCT bindings 8.0.1.1.0. No system Python packages were modified. `requirements.txt` pins the main library; `requirements.lock.txt` records the complete environment.

`adapter.py` is the editable CAD source. It reads `../cad-rebuild/recipe.json` and `../Sherman_P_Scan_Aligned_To_Adapter_mm.stl` directly, so it needs the parent repository. All coordinates are millimeters. Build123d uses a permanent corrected frame: physical front is negative Y and Z is up. `coordinates.py` maps source global points and vectors to `(-x,-y,z)` before making any geometry; sketch-local coordinates and dimensions stay unchanged. Explicit extrusion directions, stopping/draft planes, and wedge vertices use this same frame. The scan vertices and normals are converted into `inputs/wheel-scan-model-frame.stl` before BREP import. No completed body is rotated. The authoritative shared recipe and original aligned scan retain their historical coordinates. It does not load a finished SolidCraft or Onshape model to construct the adapter.

```bash
Build123d/run.sh --no-imprint  # analytic body before scan subtraction
Build123d/run.sh --stop M05   # base checkpoint (also M01, M06, M09, M20)
```

Python callers can use `build_master(airtag_depth=8.5)` to regenerate the part with an editable AirTag pocket depth. Other dimensions remain in the recipe and named operations. Checkpoint builds update the validation log; rerun the full build to restore the final log.

## View and edit in VS Code

Open this repository folder in VS Code with the Python and OCP CAD Viewer extensions installed. The supplied launch configuration selects the external Python environment. Open `Build123d/view_adapter.py`, then press **Ctrl+F5** (Run Without Debugging), choosing **View adapter in OCP CAD Viewer** if prompted. If the viewer panel does not open automatically, run **OCP CAD Viewer: Open viewer** from **Ctrl+Shift+P**, then rerun.

The script rebuilds the native Python geometry and sends it to the interactive viewer; it does not overwrite the STEP/STL exports. It displays the scaled Sherman P body and both unscaled, aligned handles as three separate translucent reference objects in the same corrected frame. Only the middle body is used for subtraction; the handles remain visible to check clip and future latch alignment. Set `SHOW_WHEEL_SCAN = False` for the adapter alone, or adjust `SCAN_OPACITY` (0–1) to change transparency. The scan is never joined into the manufactured body. Edit `AIR_TAG_POCKET_DEPTH` in the viewer script or operations in `adapter.py`, save, and rerun to see changes. Select **Python: Select Interpreter** and the environment under `~/.local/share/venvs/surron-build123d/bin/python` if running with the editor's Python button. The extension and Python package are both version 4.2.0.

## Outputs

- `exports/adapter-body.step`: final single solid, analytic manufacturing faces plus faceted scan imprint.
- `exports/adapter-body.stl`: final printing mesh, tessellation tolerance 0.005 mm and angular tolerance 0.05 rad.
- `exports/adapter-body-pre-imprint.step` and `.stl`: retained analytic checkpoint (generated separately).
- `exports/adapter-body-preview.png`: top and underside overview; regenerate using `preview.py`.
- `logs/build-validation.json`: measured per-stage validity, body count, volume and elapsed time.

The Python script is the parametric source; STEP is a geometry exchange file, not an exported feature tree. `preview.py` is a simple local renderer, not an interactive CAD editor. Its text font uses the CachyOS DejaVu font path.

## Verification

```bash
PYTHONPATH=Build123d XDG_CACHE_HOME=/tmp/surron-build123d-cache \
  ~/.local/share/venvs/surron-build123d/bin/python -m unittest discover -s Build123d/tests
XDG_CACHE_HOME=/tmp/surron-build123d-cache \
  ~/.local/share/venvs/surron-build123d/bin/python Build123d/validate_exports.py
node Build123d/validate-mounting-ceilings.mjs
```

Orientation tests check the initial profile, sketch frames and first extrusion, so an end-of-build rotation cannot pass. Material probes use the corrected frame. Tests compare 16 selected-profile sets against their saved areas, the M05 base against Fusion's volume, the finished body against an independent subtraction of the accepted prepared body STEP from the saved pre-imprint adapter, and all twelve mounting ledge/cavity/bore samples against native solid classification. The mesh ceiling check uses two independent ray directions at placed probe points. The export check reopens STEP and STL and rebuilds with an AirTag depth of 8.6 mm to check the expected 102.4295 mm³ change; it does not overwrite nominal exports.

The prior nominal in-memory master volume, before the approved alignment, was approximately **1,517,837.554 mm³**. After the scan alignment the master measured approximately **1,476,826.478 mm³**. After the approved front-clip placement the current master measures approximately **1,473,734.600 mm³**; see `logs/build-validation.json`. The earlier full-scan imprint measured **1,507,476.035 mm³**. Matching volume is useful regression evidence, not proof of whole-model equality or physical fit.

## Construction choices and limitations

- Exact selected line, arc and circle loops are assembled with their original sketch frames, including nonzero sketch-space Z. Profile-area tests use 0.01 mm² tolerance.
- Four 7 mm through-holes and downward 17 mm recesses retain their mounting ceilings. The front recesses use the exact saved sloped roof plane.
- Hanger draft uses native OCCT draft. The front draft uses the saved exact planar wedge equivalent, whose removed volume matches the earlier Fusion reconstruction.
- Both side-cut tools are analytic cylinders. No polygon cutter or smoothing is used.
- The underside cavity uses a negative 15 degree tapered extrusion toward the underside, starting 12 mm below its sketch plane.
- The wheel mesh becomes a closed faceted BREP using build123d's `Mesher`, then a native solid Boolean. Before patch reconnection, float conversion changed the imported volume by about 0.034 mm³. No mesh decimation or smoothing is applied. A local front-screen connectivity repair reconnects 31 triangles while preserving all 7,988 original vertices and the 16,000-triangle count. The original STL remains unchanged; `scan-screen-patch.json` records the exact replacement connectivity and source checksum. The body-only fit allowance is the explicitly requested 1.003 uniform scale, not an additional surface offset. The scan uses the same permanent coordinate-frame correction as all manufacturing geometry; its approved rigid alignment is applied before slicing.
- The separately documented Sherman L preparation is not replayed; the Sherman P uses its own approved cuts and model-origin scaling pivot.
- Like the earlier ports, the side bores use through cylinders instead of Fusion's nonparallel from-face start. Original constraint graphs are not recovered.
- Exact Onshape parity, full-model source-to-port XOR comparison, and physical print-fit testing have not been established. The orientation revision was separately checked against the previous Build123d STEP after aligning it for comparison: symmetric-difference volume was 0.0012 mm³. See `logs/orientation-validation.json`; this verifies preservation during reorientation, not source-to-port equality.

The existing SolidCraft and Onshape files remain unchanged. The latch remains separate; this source does not merge accessories into the master.

## Approved front-clip placement

The adapter and separate latch now translate **-2.426787168466774 mm along Y**
(about 2.43 mm toward the front), with X and Z unchanged. This implements the
approved [side-view preview](exports/front-clip-alignment-proposal.png).
The clip's circular center is now Y=-220.37430326680117 mm, Z=14.8216096181789 mm,
vertically aligned with the front-handle center estimated from its scan silhouette
(Y approximately -220.3743 mm, Z approximately 32.6991 mm).

`adapter-placement.json` controls this assembly placement through
`coordinates.ADAPTER_TRANSLATION_MM`, shared with the mesh ceiling validator. Manufacturing
profiles and early checkpoints remain in their original corrected model frame.
The completed M20 body is placed before the stationary wheel-body subtraction;
`--no-imprint` and `--stop M20` return that placed geometry. The latch is placed
after its source checkpoints, remains separate, and keeps its existing clearance.
Scan alignment, slicing, scale and reference exports are unchanged. The final
imprint is regenerated at the new position rather than translated from an old cut.
This supersedes the earlier statement that the drawn scan line exactly coincides
with the adapter lower plane: the scan retains that approved orientation, while
its position relative to the translated sloped adapter has changed slightly.

## Sherman P body-only fit preparation

The separately prepared Sherman P uses approved vertical planes at **Y=-191 mm** (front) and **Y=+170 mm** (rear), in the corrected build123d frame. Run:

```bash
~/.local/share/venvs/surron-build123d/bin/python Build123d/prepare_sherman_p.py
```

Before slicing, the complete scan (including both handles) rotates **-3.4932161177016057° about model +X**, around `(0,0,0)`, then translates **+3.464786838041892 mm in Z**. This is the approved lower-outer-bottom alignment: clockwise in the front-left side view. The user-drawn top reference line aligns with the adapter’s lower outer bottom plane, not its cavity roof. The original source scan remains unchanged.

The moved scan is then split into three regions at the existing world-Y planes. Only the middle body is uniformly scaled by **1.003** (0.3%) about the model origin `(0,0,0)`; both handles retain their moved geometry and coordinates without any fit scaling. The scaled body is then fused with the unscaled aligned handles, accepting their small overlaps. This is a proportional fit allowance, not a constant-distance surface offset. It is specific to the Sherman P; the older Sherman L pivot is not reused.

`exports/sherman-p-prepared/` contains the three aligned, unscaled regions, scaled body, and merged scan as separate STEP/STL files. `logs/sherman-p-preparation.json` records source hash, planes, pivot, measured volumes, bounds, partition conservation and reopened-export checks. `exports/sherman-p-proposed-handle-cuts.png` records the original cut-location preview before the alignment revision.

The adapter build now calls this preparation with `reunite=False` and subtracts only `body-scaled`. The viewer displays the two unscaled aligned handles separately. The merged export remains available for whole-scan inspection, but is never used as the adapter cutter. This supersedes the earlier request to use the reunited scan. Original scans remain unchanged.

The rear slice now contains two disconnected solids (including a small 353.26 mm³
scan fragment). Both are retained in the rear-handle reference; the reunited scan
remains a single solid. No fragments are discarded or used as adapter cutters.

The original scan passes ordinary solid-validity checks but has 38 self-intersection
reports near its front screen. The approved placement made the direct Boolean
fail. `scan_patch.py` applies the checksum-guarded connectivity recipe before
alignment and slicing. It changes triangle connections only: no vertex moves,
no smoothing, no triangle-count reduction and no clearance offset. The repaired
mesh has zero self-intersection reports; its signed volume changes by about
-38.209 mm³ out of 4.22 million mm³. This resolves the folded surface ambiguity;
it does not reproduce every original facet interior. The source points and patch
boundary remain exact. The export validator checks the reopened cutter again.

## Separate latch

`latch.py` builds the Latch as one separate solid in the same corrected model
frame. `view_adapter.py` displays it in green alongside the adapter and scan
references. Change `LATCH_CLEARANCE` there to adjust its three mating faces;
the default is **0.2 mm inward**, preserving the source functional clearance.
The latch is never fused into the adapter. No fillets or saddlebag mount are added.

```bash
XDG_CACHE_HOME=/tmp/surron-build123d-cache \
  ~/.local/share/venvs/surron-build123d/bin/python Build123d/latch.py
```

This produces `exports/latch.step`, `exports/latch.stl` and
`logs/latch-validation.json`. Python callers can use
`build_latch(clearance=0.2)`; `with_stages=True` also returns checkpoint measurements.
The dovetail cutter directly consumes the master recipe's selected rear-dovetail
profile through `adapter.profiles(18)` so profile edits propagate into both parts.
Side and top regions use the accessory recipe's exact selected loops, including
analytic R5/R15 arcs. The source oblique extrusion limit is reproduced by a long
extrusion trimmed to its saved plane. The three face offsets are reproduced by
two inward-shifted limiting planes (the two shoulder faces are coplanar).

All five source checkpoint volumes match within **0.01 mm³**. The final nominal
solid measures **230819.786248 mm³**; corrected-frame bounds are approximately
`(-60.865103,147.800567,-45.662921)` to
`(60.865103,219.997761,47.321249)` mm. Tests check the frame, analytic cylinder
retention, all three inward offsets, clearance changes, and temporary shared
profile edits with restoration. Both exports reopen as one valid solid; STEP
retains the nominal volume and STL differs by about **0.256 mm³** due to
0.005 mm tessellation. These checks establish agreement with the extracted
source metrics; physical fit and a full source-to-port Boolean comparison
remain untested.


## Rear-handle / TPU latch preview

`preview_rear_handle.py` generates `exports/rear-handle-circle-preview.png` and
`logs/rear-handle-circle-preview.json` without changing geometry or creating a
cylinder. The user confirmed equal front/rear handle size matching the clip bore:
**30.2 mm diameter**, extracted from the adapter's analytic clip arcs. Only the
uppermost **3 mm** of each scan section is used to locate that fixed-size circle;
sides and underside are explicitly excluded. Sections at X=-40/-20/0/+20/+40 mm
are recorded; the central section drives the drawing. Cyan points identify the
trusted crown, magenta is the inferred circle, and orange is the 1 mm interference
target. The existing latch already crosses this estimate by about **2.44 mm**
normal to its back face, with the projected contact inside the actual face.
The user must review the circle before the latch geometry is revised; this is
an estimate from partial scan evidence, not a physical fit validation.

## Raised front clip and continuous screen ramp

The user-approved front redesign is implemented by `front_clip.py` after the
permanent adapter placement and before the stationary middle-body subtraction.
The existing 55° front wall of the screen opening continues upwards into a thicker
front bridge. Its intersection with the raised original top plane is computed
from the native face planes (approximately Y=-192.95 mm). The original underside
is retained behind that join; a short local root gusset meets the raised clip at
Y=-199 mm. The clip's original analytic circular bore and jaws move vertically
18.0526320637 mm to center Z=32.8742416819 mm, retaining center
Y=-220.3743032668 mm and diameter 30.2 mm. This center remains an estimate from
the trusted crown of the handle scan, not a physical measurement.

Only the M16 front dovetail addition is omitted. The rear dovetail and separate
latch remain unchanged. No fillets are added. Source recipes remain unchanged;
M20 source-stage volume now excludes the omitted dovetail, and the new
`M20-front-redesign` stage records the finished, placed front before imprint.
`--stop M20` and `--no-imprint` return that redesigned pre-imprint body.

`preview_front_clip.py` renders `exports/front-clip-implemented.png` directly from
the current manufacturing STL and reference handle. Earlier files under `concepts/`
and the three concept image sheets are appearance studies, not manufacturing
geometry. The native implementation replaces those mesh-deformation studies.
The general `preview.py` still renders the full adapter upper/underside sheet.
Physical snap fit, material stiffness and printed strength are not established by
the CAD checks.

Verified redesign results: all **21 tests** pass; all **12 mesh ceiling checks**
pass. Reopened STEP volume is **1,485,971.986 mm³**, with one valid solid; STL is
also one valid solid and differs by about **0.987 mm³** at export tessellation.
The AirTag depth-edit validator passes. Independent review additionally checked
that a full cylinder at the retained 30.2 mm bore axis intersects no adapter
material. See `logs/export-and-parameter-validation.json`.
