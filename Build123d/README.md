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

Orientation tests check the initial profile, sketch frames and first extrusion, so an end-of-build rotation cannot pass. Material probes use the corrected frame. Tests compare 16 selected-profile sets against their saved areas, the revised M01/M05 base against the approved outline using independent native geometry, the finished body against an independent subtraction of the accepted prepared body STEP from the saved pre-imprint adapter, and all twelve mounting ledge/cavity/bore samples against native solid classification. The mesh ceiling check uses two independent ray directions at placed probe points. The export check reopens STEP and STL and rebuilds with an AirTag depth of 8.6 mm to check the expected 102.4295 mm³ change; it does not overwrite nominal exports.

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

## Restored side printing planes

`print_planes.py` extends both existing large rear sloped side planes through the
raised front, retaining each inward half-space without an offset. It runs after
`M20-front-redesign` and before scan subtraction as `M20-print-planes`, and is
included in pre-imprint/`--stop M20` results. Plane datums come from the native
rear faces rather than copied coordinates or guessed angles. The front protruded
4.547544 mm beyond each plane; the approved cut removes approximately
520.1988 mm³ total. This restores coplanar front/rear printing contact on either
side. Adapter placement, screen ramp, clip bore, rear latch, separate accessories,
scan preparation and imprint clearance remain unchanged.

`exports/print-plane-trim-preview.png` and `exports/concepts/print-plane-trim-*`
retain the approved **historical proposal**. The concept script refuses to
regenerate that comparison from already-trimmed manufacturing exports. The current
manufacturing result is `exports/front-clip-implemented.png`, regenerated using
`preview_front_clip.py`, with new contact faces highlighted green.

Current trimmed model verification: **23 tests** and **12 mesh ceiling checks**
pass. Reopened STEP is one valid solid of **1,485,451.787 mm³**, matching the
approved trim preview within 0.001 mm³. Independent review found zero Boolean
difference from that preview in either direction and zero material intrusion
into the clip bore. `logs/print-plane-validation.json` records both original
plane datums and the resulting negligible signed protrusion residuals.

## Reinforced screen-side walls and uninterrupted front incline

`screen_surround.py` adds material above the screen-side walls, starting at the
rear edge of the screen opening (Y=-101.586319 mm, Z=37.923506 mm). The new
side tops use the exact native underside slope, **6.8°**, instead of aiming at
the clip height. The central original **55°** screen-front incline remains one
continuous planar face into the clip: no added upright ledge and no fillets.

This native operation runs as `M20-screen-surround`, after front reconstruction
and before restoring both rear printing planes. Additions exclude the screen
aperture and all central space above the original ramp. The original body is
never subtracted during reinforcement; underside, clip bore/axis and rear/latch
geometry remain unchanged. The resulting addition after the print-plane cuts
is approximately **21,067.349 mm³**. Native construction uses the recipe-built
faces, not the approved preview STEP/STL as an input.

The earlier rear/screen retained-region regression now compares the original
body behind the rear screen edge, since changing the side walls beside the
screen is explicitly authorized. Original underside material probes remain.
Historical concept images and prototypes are retained as approval evidence.

Verified current reinforced model: **26 tests** and **12 mesh ceiling checks**
pass. Reopened STEP is one valid solid of **1,506,519.136 mm³**, matching the
approved continuous-ramp prototype within 0.001 mm³. Independent Boolean review
confirms zero missing original material and zero difference from the approved
prototype. `preview_screen_surround.py` renders the implemented join directly
from manufacturing STEP to `exports/screen-surround-implemented.png`.


## Implemented Sherman P suspension-access outline

The user-approved [numbered proposal](exports/bottom-outline-sherman-p-proposed.png)
is now native manufacturing geometry. `bottom_outline.py` adapts the original
selected BottomSketch half-loop before the first extrusion; the normal mirror
produces the opposite side. Source recipes and `profiles(9)` inspection remain
original; `profiles(9, sherman_p_bottom=True)` exposes the revised native half.

Using the original line numbers: 13 retains its angle and extends to vertical
16; 14 and 15 are removed. Line 17 translates 10 mm toward the front without
rotation. Line 19 moves 10 mm forward, enlarging the screen opening from 60 to
70 mm in the bottom sketch. The center remains 44 mm wide. Both changes are
mirrored, and the saved proposal coordinates are in the placed model frame.

The existing 55-degree screen ramp follows the extended opening: its datum
moves forward 10 mm along the original sloped top/bottom planes. Its top join
is now Y=-202.950417 mm. The clip-root gusset ends at Y=-204.112360 mm, between
that join and the unchanged bore rear tangent at Y=-205.274303 mm. The original
30.2 mm clip bore and its axis remain fixed. The side reinforcement and both
printing planes rebuild from native faces. The separate latch, adapter placement,
scan preparation and body-only 1.003 fit scale are unchanged; no fillets are added.

Current native pre-imprint volume is **1,374,123.431 mm³**; imprinted volume is
**1,337,167.667 mm³**. STEP reopens as one valid solid of **1,337,167.678 mm³**;
STL is one valid solid of **1,337,167.470 mm³**. These current values supersede
the earlier section volumes. Export validation measures the AirTag edit using
two native builds separately from STEP serialization: removed volume is
102.429507785 mm³ and STEP round-trip volume error is +0.010984917 mm³.

`preview_suspension_outline.py` renders the [implemented top and oblique views](exports/suspension-outline-implemented.png)
from the actual manufacturing STL. The old numbered sketch image is historical
reference geometry; its line IDs remain stable. Existing seat-hanger features
remain, including their protrusions outside the narrow base outline. Physical
cover removal, print fit and printed strength have not been tested.

Verification for this outline: all **27 tests** pass, all **12 mesh mounting-ceiling
checks** pass, portable reference validation passes, and export/parameter validation
passes. Native blank and M05 geometry agree with the independently constructed
approved proposal within 0.001 mm³ in both Boolean directions. Full-cylinder
intersection confirms the 30.2 mm clip bore contains no adapter material.
