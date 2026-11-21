# Surron Seat Adapter

The full, unsplit adapter is reconstructed as editable Python solid geometry from the repository's millimeter recipe. The final wheel imprint subtracts only the prepared Sherman P middle body, with the source screen patch reconnected before preparation and uniformly scaled by **1.003** about model origin after cuts at Y=-191/+170 mm. Both handles move with the complete scan during alignment, remain unscaled after slicing, and are excluded from subtraction. The master has 1 mm finishing fillets and no connector recesses. The project also builds a two-piece printing variant and a separate editable latch. The saddlebag mount has a saved reference recipe.

**Project priority.** Keep the geometry, feature history, and build workflow simple and editable.

## Download

Download `SurronSeatAdapter.zip` from the [latest successful build](https://github.com/theosherman/SurronSeatAdapter/releases/latest).
The ZIP opens directly to the six printable STLs. The `step/` folder contains
matching CAD solids, and `previews/<part>/` contains PNGs from three angles.
Every successful push build on `main` gets a release tagged with its commit.
The [release history](https://github.com/theosherman/SurronSeatAdapter/releases)
keeps previous print files available.

## Run

The original Sherman P wheel scan is tracked under `reference/fusion/`.
Run `./run.sh` to build the STEP parts and the offline preview in the ignored
`exports/` directory. Use `./run.sh --stl` to also generate printable STLs,
or `scripts/build-release.sh` to validate and package a release ZIP.
A full build clears prior generated exports, including any old release ZIP.
Keep reference meshes for the preview alongside the project inputs or in `exports/`.
The [historical Bambu Studio project](reference/slicer/adapter-body.3mf)
preserves the earlier slicer settings and geometry.

Dependencies live outside this Git repository:

```bash
# Existing environment on this machine:
./run.sh

# Recreate on another machine (use a Python version supported by the pinned wheels):
python -m venv ~/.local/share/venvs/surron-build123d
~/.local/share/venvs/surron-build123d/bin/pip install -r requirements.lock.txt
./run.sh
```

To rebuild the split halves or latch individually, run:

```bash
~/.local/share/venvs/surron-build123d/bin/python split_adapter.py
~/.local/share/venvs/surron-build123d/bin/python latch.py
```

Set `BUILD123D_PYTHON` to use a different environment. Installed here with Python 3.14.7, build123d 0.13.0, and OCCT bindings 8.0.1.1.0. No system Python packages were modified. `requirements.txt` pins the main library; `requirements.lock.txt` records the complete environment.

`adapter.py` is the editable CAD source. It reads `cad-rebuild/recipe.json` and `reference/fusion/Sherman_P_Scan_Aligned_To_Adapter_mm.stl` directly. All coordinates are millimeters. Build123d uses a permanent corrected frame: physical front is negative Y and Z is up. `coordinates.py` maps source global points and vectors to `(-x,-y,z)` before making any geometry; sketch-local coordinates and dimensions stay unchanged. Explicit extrusion directions, stopping/draft planes, and wedge vertices use this same frame. The scan vertices and normals are converted into `inputs/wheel-scan-model-frame.stl` before BREP import. No completed body is rotated. The authoritative shared recipe and original aligned scan retain their historical coordinates.

```bash
./run.sh --no-imprint  # analytic body before scan subtraction
./run.sh --stop M05   # base checkpoint (also M01, M06, M09, M20)
```

Python callers can use `build_master(airtag_depth=8.5)` to regenerate the part with an editable AirTag pocket depth. Other dimensions remain in the recipe and named operations. Checkpoint builds update the validation log; rerun the full build to restore the final log.

## View CAD in T3 Code

Open `exports/preview.html` in the Files panel. Use the top picker to switch
between **Adapter** and **Adapter Split**. The **View** menu holds part
visibility, zoom, reset, and gesture help. Drag to rotate, right-drag to pan,
and scroll to zoom. The viewer runs offline and needs WebGL 2.
In **View**, **Parts** controls model visibility. Under **Labels**, turn on
**Features** to identify adapter landmarks and split hardware, or **Faces** to
number the larger planar faces in the exported STEP
parts. Rotate or zoom to reveal more labels.
On a touchscreen, drag with one finger to rotate, drag with two fingers to
pan, and pinch to zoom.

The local and release builds generate this file from the exported STEP parts.
Run `python -m scripts.preview_stl` from the repo root to refresh it from
existing exports. Pass STEP or binary STL paths to select specific files and
write `preview.html` beside the first input. Use the STEP keys to show them
seated in the adapter.
Refreshing the default preview removes legacy per-part HTML files from `exports/`.

The top **EUC** checkbox toggles the prepared Sherman P overlay for either variant.
The default local build embeds the wheel mesh in `preview.html` and deletes the
intermediate STL. To include the EUC when refreshing just the HTML, first run
`python prepare_sherman_p.py --preview-only` to recreate that mesh.
To include a **Surron Seat** overlay, use a binary `surron-seat.stl` positioned
in the adapter's model frame. The default build checks `exports/` and
`reference/fusion/` for that file. Both overlays start hidden.

## Automatic preview browser

From the repository root, run `python preview_server.py start`.
It starts a background server and opens http://127.0.0.1:8766 in your browser.
Keep that page open: it displays the newest image under `tmp/`
and checks for changes every second, including when an image is overwritten.
All proposal images and server logs stay in that ignored directory.

Use `python preview_server.py stop` to stop it, or `status` to check it.
`start --no-open` starts it without opening another browser tab; `--port` selects
another port. Python's standard library is sufficient; no CAD environment is needed.

## View and edit in VS Code

Open this repository folder in VS Code with the Python and OCP CAD Viewer extensions installed. The supplied launch configuration selects the external Python environment. Open `view_adapter.py`, then press **Ctrl+F5** (Run Without Debugging), choosing **View adapter in OCP CAD Viewer** if prompted. If the viewer panel does not open automatically, run **OCP CAD Viewer: Open viewer** from **Ctrl+Shift+P**, then rerun.

The script rebuilds the native Python geometry and sends it to the interactive viewer; it does not overwrite the STEP/STL exports. It displays the scaled Sherman P body and both unscaled, aligned handles as three separate translucent reference objects in the same corrected frame. Only the middle body is used for subtraction; the handles remain visible to check clip and future latch alignment. Set `SHOW_WHEEL_SCAN = False` for the adapter alone, or adjust `SCAN_OPACITY` (0–1) to change transparency. The scan is never joined into the manufactured body. Edit `AIR_TAG_POCKET_DEPTH` in the viewer script or operations in `adapter.py`, save, and rerun to see changes. Select **Python: Select Interpreter** and the environment under `~/.local/share/venvs/surron-build123d/bin/python` if running with the editor's Python button. The extension and Python package are both version 4.2.0.

## Outputs

- `exports/adapter-body.step`: final single solid, analytic manufacturing faces plus faceted scan imprint.
- `exports/adapter-body.stl`: optional printing mesh, tessellation tolerance 0.005 mm and angular tolerance 0.05 rad.
- `exports/SurronSeatAdapter.zip`: release bundle generated by `scripts/build-release.sh`.
- `logs/build-validation.json`: measured per-stage validity, body count, volume and elapsed time.

The Python build scripts contain the parametric feature history. STEP provides exchange geometry.

## Verification

Generate the prepared wheel exports before running the geometry tests. Use
`./run.sh --stl` before running the STL validators.

```bash
~/.local/share/venvs/surron-build123d/bin/python prepare_sherman_p.py
XDG_CACHE_HOME=/tmp/surron-build123d-cache \
  ~/.local/share/venvs/surron-build123d/bin/python -m unittest discover -s tests
XDG_CACHE_HOME=/tmp/surron-build123d-cache \
  ~/.local/share/venvs/surron-build123d/bin/python validate_exports.py
node validate-mounting-ceilings.mjs
```

Orientation tests check the initial profile, sketch frames and first extrusion, so an end-of-build rotation cannot pass. Material probes use the corrected frame. Tests compare 16 selected-profile sets against their saved areas, the revised M01/M05 base against the approved outline using independent native geometry, the finished body against an independent subtraction of the accepted prepared body STEP from the in-memory pre-imprint adapter, and all twelve mounting ledge/cavity/bore samples against native solid classification. The mesh ceiling check uses two independent ray directions at placed probe points. The export check reopens STEP and STL and rebuilds with an AirTag depth of 8.6 mm to check the expected 102.4295 mm³ change; it does not overwrite nominal exports.

The prior nominal in-memory master volume, before the approved alignment, was approximately **1,517,837.554 mm³**. After the scan alignment the master measured approximately **1,476,826.478 mm³**. After the approved front-clip placement the current master measures approximately **1,473,734.600 mm³**; see `logs/build-validation.json`. The earlier full-scan imprint measured **1,507,476.035 mm³**. Matching volume is useful regression evidence, not proof of whole-model equality or physical fit.

## Source references

The [Fusion extracts](reference/fusion/) preserve the original source geometry, parameters, accessory data, and wheel scans. The [millimeter recipe](cad-rebuild/recipe.json) provides build inputs for the editable Python model.

## Implemented 1 mm body fillets

The November 15 request supersedes the earlier no-fillet decision for Build123d.
`body_fillets.py` applies one 1 mm fillet feature to 131 geometrically selected
edges of the placed adapter, before the wheel subtraction. The running dovetail
rail and its body junction are excluded. The two shoulder edges and three
trapezoidal-root edges at Y=147.5–151.6 mm remain sharp for latch clearance.
The three-edge side return on each side also remains sharp: eleven junction
edges in total. Rear terminal edges at Y=261 mm retain their original fillets.
`validate_dovetail_root.py` verifies three interior samples on each of the eleven
sharp junction edges in the final manufacturing STEP; results are in
`logs/dovetail-root-validation.json`. The latch and other
accessories remain separate and unchanged. Every selected edge has its mirror; incompatible pairs are omitted on both sides.
Pairs whose generated fillet faces touch the asymmetric wheel cutter are also
omitted on both sides, so the wheel cut cannot trim the blends unequally.
Incompatible edges and the faceted
EUC contact surface remain sharp. This is broad practical coverage, not every edge.

`body-fillets.json` stores geometric selectors rather than unstable edge numbers.
Changed or ambiguous selectors stop regeneration explicitly. AirTag floor and depth-dependent corner edges remain sharp to preserve the pocket-depth parameter. The sharp
`--no-imprint` / M20 checkpoint stays available for source-feature inspection.
The final manufacturing STEP/STL include the fillets. Curved-surface validation
uses adaptive volume integration; the STL topology is checked directly without
constructing a BREP face for each triangle. `export_mesh.py` tessellates the saved
STEP with **absolute 0.005 mm** deflection and 0.05 rad angular tolerance. This
avoids relative tessellation over-refining tiny blend junctions. STL topology uses a 0.000001 mm
coordinate tolerance to ignore float32 collapsed triangles and sub-micron seams.
The curved STEP round-trip volume limit is 2 ppm (about 2.45 mm³). This is a numerical export limit, not wheel-fit clearance.

`validate_fillets.py` checks reflected boundary points before the intentionally
asymmetric wheel-scan subtraction. Its report is saved in
`logs/fillet-symmetry-validation.json`. `validate_fillet_cutter.py` also checks
that generated edge and corner blend faces clear the prepared wheel cutter;
its report is `logs/fillet-cutter-validation.json`. This supersedes the first, asymmetric
150-edge selection. Symmetry takes priority over fillet coverage.

The [saved top and underside views](docs/images/cad/body-fillets-implemented.png) show the implemented fillets.

## Implemented 5 mm angled rear wall

The source cavity cutter now stops at a plane parallel to the original angled
latch wall and 5 mm inward along its normal. This corrects the original cavity
operation rather than adding material to the completed adapter. The approved correction is rebuilt into manufacturing STEP/STL exports.
All 47 regression tests, twelve mounting-ceiling mesh checks, and 75 material
samples through the corrected rear wall pass. The original
outer latch face, separate latch, roof offset and rear side cuts are retained.

## Implemented long cavity and rear side relief

The approved browser preview is implemented in `trunk_cavity.py` and M19 of
`adapter.py`: one editable sixteen-line profile extends through the middle and
widens at the rear. Straight downward walls start 18.5 mm below BodyCutSketch;
the original pocket is replaced, so no higher residual roof recess remains.
The existing 8.5 mm AirTag pocket retains 10 mm of material below it at sampled
locations. `rear_side_tools()` defines two mirrored, full-height exterior corner
cuts in the placed model frame, applied before the unchanged wheel subtraction.
The separate latch, mounting features, rear bridge and original top dovetail remain.
This supersedes the rear-only octagon, filled-middle assertions and 12 mm/15°
cavity settings described in historical sections below. Other CAD engines are
unchanged.

Validation: **47 tests pass**, all **12 mounting-ceiling checks pass**, and
STEP/STL reopening plus the AirTag 8.6 mm edit pass. The exported STEP is one
valid solid, **1,203,492.083 mm³**. Its measured symmetric difference from the
approved scratch STEP is **0 mm³**. A 2 mm grid gives **2,120** interior
roof-normal samples with a **10 mm** minimum. Run `validate_cavity.py` for roof samples and optional preview parity,
the standard regression suite, `validate_exports.py`, and the mounting-ceiling
mesh checker for manufacturing validation. Sampling is not a continuous minimum
thickness proof; physical fit and strength remain untested.

## Implemented 8 mm deeper seating

The approved 8 mm placement preview is implemented in the editable source and
manufacturing STEP/STL exports. `SEATING_DEPTH_MM = 8.0` in `prepare_sherman_p.py`
raises the whole prepared EUC, including both unscaled handles, exactly 8 mm.
The existing 1.003 body fit scale is retained: its pivot moves from `(0,0,0)`
to `(0,0,8)` with the wheel. This is mathematically the original prepared cutter
translated by 8 mm, without the extra 0.024 mm that scaling the new translation
about the old pivot would introduce. Rotation, Y slice planes and X/Y placement
are unchanged. This supersedes the original scan Z position described below.

The front clip follows by exactly 8 mm, placing its bore axis at
Y=-220.37430326680117, Z=40.87424168191536 mm. The existing front reconstruction
extends the 55 degree ramp to meet it, keeps the original jaw separation datum,
and carries the original 30.2 mm circular opening through the connector wedge.
The original printing planes still trim the sides. Screen walls, mounting
ceilings, simple rear cavity, original rear interface and separate latch retain
their controlling geometry. The deeper wheel imprint is regenerated from the
prepared body; both handles remain reference-only and unscaled.

[Implemented seating and front connection](docs/images/cad/deeper-seating-8mm-implemented.png)
shows actual manufacturing meshes. The earlier silhouette preview is conceptual.
An open viewer updates when `view_adapter.py` is rerun. Physical fit remains untested.

Validation: **41 tests** and **12 mesh mounting-ceiling checks** pass. The reopened
manufacturing STEP is one valid solid, **1,525,564.716 mm³**, with zero material
in the full grip-bore cylinder. Every exported wheel-reference vertex matches
the corresponding previous export translated 8 mm, within 0.000004 mm STL
rounding. See [seating measurements](logs/deeper-seating-validation.json).

## Construction choices and limitations

- Exact selected line, arc and circle loops are assembled with their original sketch frames, including nonzero sketch-space Z. Profile-area tests use 0.01 mm² tolerance.
- Four 7 mm through-holes and downward 17 mm recesses retain their mounting ceilings. The front recesses use the exact saved sloped roof plane.
- Hanger draft uses native OCCT draft. The front draft uses the saved exact planar wedge equivalent, whose removed volume matches the earlier Fusion reconstruction.
- Both side-cut tools are analytic cylinders. No polygon cutter or smoothing is used.
- The underside cavity uses a negative 15 degree tapered extrusion toward the underside, starting 12 mm below its sketch plane.
- The wheel mesh becomes a closed faceted BREP using build123d's `Mesher`, then a native solid Boolean. Before patch reconnection, float conversion changed the imported volume by about 0.034 mm³. No mesh decimation or smoothing is applied. A local front-screen connectivity repair reconnects 31 triangles while preserving all 7,988 original vertices and the 16,000-triangle count. The original STL remains unchanged; `scan-screen-patch.json` records the exact replacement connectivity and source checksum. The body-only fit allowance is the explicitly requested 1.003 uniform scale, not an additional surface offset. The scan uses the same permanent coordinate-frame correction as all manufacturing geometry; its approved rigid alignment is applied before slicing.
- The separately documented Sherman L preparation is not replayed; the Sherman P uses its own approved cuts and model-origin scaling pivot.
- Like the earlier ports, the side bores use through cylinders instead of Fusion's nonparallel from-face start. Original constraint graphs are not recovered.
- Full-model comparison against the Fusion source and physical print-fit testing remain open. The orientation revision was separately checked against the previous Build123d STEP after aligning it for comparison: symmetric-difference volume was 0.0012 mm³. See `logs/orientation-validation.json`; this verifies preservation during reorientation, not source-to-port equality.

The latch remains a separate solid.

## Approved front-clip placement

The adapter and separate latch now translate **-2.426787168466774 mm along Y**
(about 2.43 mm toward the front), with X and Z unchanged. This implements the
approved side-view preview (temporary proposal preview; excluded from Git).
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
~/.local/share/venvs/surron-build123d/bin/python prepare_sherman_p.py
```

Before slicing, the complete scan (including both handles) rotates **-3.4932161177016057° about model +X**, around `(0,0,0)`, then translates **+3.464786838041892 mm in Z**. This is the approved lower-outer-bottom alignment: clockwise in the front-left side view. The user-drawn top reference line aligns with the adapter’s lower outer bottom plane, not its cavity roof. The original source scan remains unchanged.

The moved scan is then split into three regions at the existing world-Y planes. Only the middle body is uniformly scaled by **1.003** (0.3%) about the model origin `(0,0,0)`; both handles retain their moved geometry and coordinates without any fit scaling. The scaled body is then fused with the unscaled aligned handles, accepting their small overlaps. This is a proportional fit allowance, not a constant-distance surface offset. It is specific to the Sherman P; the older Sherman L pivot is not reused.

`prepare_sherman_p.py` writes ignored local exports to `exports/sherman-p-prepared/`, containing the three aligned, unscaled regions, scaled body, and merged scan as separate STEP/STL files. `logs/sherman-p-preparation.json` records source hash, planes, pivot, measured volumes, bounds, partition conservation and reopened-export checks.

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
  ~/.local/share/venvs/surron-build123d/bin/python latch.py
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

The [saved front clip view](docs/images/cad/front-clip-implemented.png) shows the adapter and reference handle.
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

The [saved front clip view](docs/images/cad/front-clip-implemented.png) highlights the contact faces in green.

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
prototype. The [saved screen surround view](docs/images/cad/screen-surround-implemented.png) shows the implemented join.


## Implemented Sherman P suspension-access outline

The user-approved numbered proposal (temporary proposal preview; excluded from Git)
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
is Y=-202.950417 mm. The complete original clip is lifted using the original
Y=-192.950417 mm separation boundary; the root gusset retains Y=-199 mm.
The upper connector is trimmed to the moved screen-ramp plane. The original
30.2 mm clip bore and its axis remain fixed. Side reinforcement uses the native
ramp/top plane intersection, and both printing planes rebuild from native faces.
The separate latch, placement, scan preparation and body-only 1.003 fit scale
remain unchanged; no fillets are added.

At the trunk/clip repair milestone, pre-imprint volume was **1,425,603.413 mm³**; imprinted native
volume is **1,387,005.793 mm³**. STEP reopens as one valid solid of
**1,387,005.792 mm³**; STL is one valid solid of **1,387,007.322 mm³**.
These values supersede the initial outline implementation and earlier volumes.
Export validation separately measures the native AirTag edit (102.429507809 mm³)
and STEP round-trip volume error (-0.000375059 mm³).

The [saved top and oblique views](docs/images/cad/suspension-outline-implemented.png) show the implemented outline. The old numbered sketch image is historical
reference geometry; its line IDs remain stable. Existing seat-hanger features
remain, including their protrusions outside the narrow base outline. Physical
cover removal, print fit and printed strength have not been tested.

Verification at the trunk/clip repair milestone: all **29 tests** passed, all **12 mesh mounting-ceiling
checks** pass, portable reference validation passes, and export/parameter validation
passes. Native blank and M05 geometry agree with the independently constructed
approved proposal within 0.001 mm³ in both Boolean directions. Full-cylinder
intersection confirms the 30.2 mm clip bore contains no adapter material.


### Trunk walls and complete clip repair

The initial outline implementation left the original M19 pocket unchanged, which
cut completely through the narrowed side walls. Its clip-lifting split also
followed the relocated ramp and stranded part of the original jaw below the
raised clip. Earlier tests verified validity and bore clearance but missed both
functional defects; the initial green suite was insufficient.

`trunk_cavity.py` now intersects the original tapered pocket tool with an envelope
formed from the revised outer footprint, offset inward **8 mm in the XY plane**.
Prior-model lower-wall samples were approximately 8–15 mm thick. The constraint
restores the straight narrowed walls and routes the pocket around the changed
rear diagonal, while retaining a hollow cavity, its original roof plane, and
15-degree taper wherever the old cutter fits. This wall allowance is unrelated
to scan fit clearance. It does not assert an 8 mm minimum through every later
cut or scan imprint; final-material probes check the affected neck after imprint.

Independent STEP sections confirm 8 mm straight cavity walls and approximately
12.09 mm horizontal walls beside the diagonal. The original roof is unchanged,
including its pre-existing local source notch. The M19 pocket still removes
approximately **539,715.733 mm³** before later cuts.

The clip repair lifts the entire original jaw independently of the larger screen
opening, retaining its original lower envelope and grip geometry. A historical
native clip fixture checks for added hanging material and preserved grip volume.
New material probes verify the hollow pocket, side walls, roof, and final imprinted
walls. All 29 tests and existing exported checks pass.

The [saved underside comparison](docs/images/cad/cavity-and-clip-repair.png) shows the original, defective, and repaired versions from left to right. Rerun `view_adapter.py` to refresh an already-open viewer.


## Seat-support continuations and screen walls lowered 8 mm

The two later user reference images are preserved as [shoulder marks](docs/images/seat-shoulder-support-request.png)
and [screen-junction circles](docs/images/screen-wall-lowering-request.png).
`seat_shoulders.py` extends the existing rear shoulder edge of each seat-support
tab into the narrow body, replacing the forward-folding return shown in image one.
The original shoulder plane, outer seat-contact edge, and 45-degree underside
draft are retained. Each rear shoulder face now spans X=22–51 mm (29 mm total)
and has approximately **529.281 mm²** area, compared with the prior 15.620 mm span
and **162.039 mm²**. This adds material continuity along the marked load path;
printed load capacity has not been established.

The manufacturing profile uses `profiles(79, seat_shoulders=True)`; default
source-profile inspection and the shared portable recipe remain original.
The change flows through the normal mirrored M11 operation and subsequent cuts.

`SCREEN_WALL_LOWERING_MM = 8.0` in `screen_surround.py` lowers the parallel side-top
plane from Z=37.923506 to **29.923506 mm** at Y=-101.586319 mm. A scoped native cut
caps both original rail material and added reinforcement, retaining the higher
55-degree front incline. `front_clip.py` trims the raised connector across the
full width, removing the two side-wing upright steps seen in the black circle.
The two former 3.418 mm² extrusion ribbons near `(±55.84,-103.407,38)` in the
green circle disappear after lowering. The original rounded cutout is retained;
no replacement circular cut or fillet is added.

At the shoulder/screen milestone, native pre-imprint volume was **1,413,939.801 mm³**; imprinted volume was
**1,375,342.181 mm³**. STEP reopens as one valid solid of **1,375,342.180 mm³**;
STL is one valid solid of **1,375,343.706 mm³**. These values supersede the
previous milestone volumes. All **33 tests**, all **12 mesh mounting-ceiling
checks**, source reference validation, export reopening and AirTag depth-edit
validation pass. Native shoulder material is checked after the wheel imprint,
not just on the pre-imprint blank. Clip, trunk-wall and printing-plane regressions
remain active. The separate accessories and wheel fit preparation are unchanged.

See the [before/after implemented comparison](docs/images/cad/shoulders-and-lowered-screen.png)
and [native measurements](logs/shoulder-screen-validation.json).

## Historical rear-only cavity (superseded by approved long cavity)

The rejected face/region patch implementation has been removed. The user
explicitly chose the **original outer wall/latch interface**, cancelling the
10 mm wall relocation and latch extension. The latch source, its placement,
and the single original top dovetail are restored to the accepted pre-patch
configuration. The outer rear interface is checked against an immutable native
fixture from commit `8746492` by symmetric difference.

`trunk_cavity.py` contains one controlling **eight-line polygon** on the existing
`BodyCutSketch` plane. `REAR_CAVITY_POINTS` is the complete editable outline in
sketch millimeters. The usual M19 feature removes this polygon with the original
**12 mm roof offset** and **15 degree downward draft**. There are no extra wall
extrusions, moved regions, duplicated dovetails, or follow-up clearance patches.
The original mounting features and approved body-only Sherman P cutter remain.

The pocket is confined to the wider rear section. Its shorter rear reach leaves
a continuous thicker rear wall. The narrow middle is now solid CAD geometry;
the slicer's infill setting controls how that material prints. It is not a
request for 100% print infill. No new fillets or wheel-fit allowance are added.

The original latch remains a separate source-derived solid with its established
0.2 mm selected-face clearance; it is not thickened or extended. The source
planar-clearance and original contact/outline tests apply to the normal build
again, without a legacy-mode switch. `rear_cavity.py` and its workaround API have
been deleted rather than retained as another selectable implementation.

The [implemented cavity view](docs/images/cad/rear-cavity-implemented.png) shows the rebuilt cavity.

Checks cover the eight-edge sketch, no draft intrusion into the narrow middle,
filled middle material, empty pocket without blocks, continuous rear wall,
exact original exterior/dovetail interface, original latch checkpoints, full rear
screwdriver paths, mounting ceilings, printing planes, and unchanged wheel
preparation. Physical printed fit and strength remain untested.

Final validation: **41 tests pass**, all **12 mounting-ceiling mesh checks pass**,
and STEP/STL reopening plus the AirTag 8.6 mm depth edit pass. Exported native
interface symmetric difference is **0 mm³** against the original fixture. The
finished adapter is **1,667,774.540 mm³** and the original separate latch is
**230,819.786 mm³**. See [native measurements](logs/rear-cavity-validation.json).

## Existing body-top slope continued onto screen walls

The original body-top plane now continues down onto both lowered screen walls,
meeting their parallel tops at **Y=-121.934061, Z=32.349827 mm**. The change is
in the existing `screen_surround.py` wall-top envelope, using the native body-top
face as its datum. It introduces no separate slope angle, raised cap or fillet.
The screen aperture and original rounded side cuts remain open.

The reopened manufacturing STEP has one continuous coplanar body-top face,
including both wall transitions. Its comparison with commit `158e916` shows
**2,761.715 mm³ added**, confined to Y=-121.934061 through -101.586319 mm,
and **0 mm³ removed**. Final STEP volume is **1,528,326.431 mm³**. See
`logs/screen-slope-validation.json`. Both pre-imprint and final STEP/STL exports
are regenerated. Temporary review images remain in `/tmp`, outside the repo.
Validation: **42 tests** and all **12 mounting-ceiling mesh checks** pass;
STEP/STL reopening, cutter integrity and the AirTag depth-edit check pass.
Physical fit and printed strength remain untested.

## Implemented lower rear toe cut and local 14 mm wall

The lower tip beneath the latch root is trimmed at the latch-wall angle mirrored
across XY. `REAR_TIP_POINT_MM` anchors the cut at
`(0,177.270005683283,-17.98689437242)` mm. Removal is confined below the anchor's
Z so the upper seat support and single top dovetail remain. The separate latch
is unchanged. `trim_lower_rear_tip()` applies this one exterior trim before the
wheel subtraction.

The original cavity cutter is additionally limited by the mirrored cut plane
shifted 14 mm inward along its normal. This retains only the local wall material
needed beside the lower diagonal; it introduces no added-body patch or second
pocket. The original rear-wall 5 mm limit, 18.5 mm roof offset, rest of the long
cavity, side relief and wheel preparation remain in force.

Run `validate_cavity.py --approved-step <approved STEP>` for optional exact preview
parity and the new diagonal's distance to the cavity tool. The normal command
validates current exports without loading a historical scratch file.
The [saved section view](docs/images/cad/rear-tip-implemented.png) shows the implemented rear cut.

The local wall was subsequently increased from 10 mm to **14 mm** by changing
only `REAR_TIP_WALL_THICKNESS_MM`. The approved exterior trim stays fixed.
Current verification is recorded in `logs/approved-cavity-validation.json`
and `logs/export-and-parameter-validation.json`.

The 14 mm revision passes all 49 tests and 12 mounting-ceiling checks. STEP/STL
reopen as single valid solids; STEP volume is **1,205,253.602 mm³**. Comparing
against the 10 mm version shows **0 mm³** of removed prior material and
**3,832.887 mm³** retained in the extra normal-depth band from 10 to 14 mm.
The AirTag parameter-edit and cutter self-intersection checks pass.

## Outward face offsets

The original `RearSketch` diagonal and its mirror now sit **1 mm outward**, measured
normal to the original printing planes (faces 1 and 2). The existing front trim
uses these shifted native rear planes. Both `FrontCutSketch` triangular corner-cut
diagonals (face 3 beside the front clip) move **3 mm outward in total** into the removed
corner, reducing those cuts. Original angles, adjoining horizontal/vertical lines,
and extrusion directions are preserved. `cut_offsets.py` adjusts these original
manufacturing profiles before extrusion/intersection; the portable historical
recipe remains unchanged. No finished-body patches are used.

### Two-piece printing variant

After rebuilding the master, run `split_adapter.py` with the same Python environment. It reads `exports/adapter-body.step` and writes separate front and rear STEP and STL files. The child uses the portable recipe's sloped split plane and has three 10 mm connector recesses. One large recess spans the top and one 16 × 12 mm butterfly-key recess opens onto each inner cavity wall. Each cavity-key waist follows the split plane through the full 10 mm depth, measured normal to the cavity wall.

The three recess openings have 1 mm rim fillets. Their floors and the edges where the walls meet the floors stay sharp.

Run `butterfly_keys.py` to export the two printable key shapes. Print the top key once and the cavity key twice. Every key edge has a 1 mm fillet. The keys are 9.2 mm thick, with at least 0.4 mm clearance from the recess faces, including at the rounded waist. STEP files retain assembled positions, and STLs lie flat at Z=0.

- `butterfly-key-top.stl`, print once
- `butterfly-key-cavity.stl`, print twice

In the model orientation, the front is approximately 152 × 354 × 88 mm, and the rear is 156 × 171 × 137 mm. With Z up, the front needs about 339 mm square before slicer margins, even when rotated in the bed plane.

To inspect the two halves in VS Code, open **OCP CAD Viewer: Open viewer**
from the command palette, then select **View split adapter in OCP CAD Viewer**
in the Run and Debug dropdown and press **Ctrl+F5**. The viewer loads both
halves, the seated top key, and the seated negative X cavity key. The positive X
recess is open for inspection. Use the object tree to hide either half or key.
**View adapter in OCP CAD Viewer** opens the unsplit master.

## Screen ramp tangent to the front clip

The front reconstruction derives a **57.982°** ramp from the existing lower
screen edge and the clip's **26.338 mm** outer radius. In the placed center
section, they meet at Y=-198.043 mm and Z=54.838 mm with a shared tangent.
The same profile bounds the raised jaw and its bridge. The separate
**30.2 mm** clip bore stays on its established axis.

The [front-clip preview](docs/images/cad/front-clip-implemented.png) shows the change
before finishing and wheel subtraction.

Both screen cutout walls continue along their existing top plane until it
intersects the tangent ramp. The screen opening remains 86 mm wide between
the walls. The two lower wall-to-ramp edges stay sharp where a 1 mm fillet
would meet the wheel imprint. See the [before and after 3D view](docs/images/cad/screen-walls-to-ramp.png).
The updated geometry is in the STEP and STL exports. The saved 3MF slicer
project still contains the earlier wall geometry.
