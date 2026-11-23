# Reference preparation

## Sherman P body-only fit preparation

Run the wheel preparation explicitly when the source scan or its fit changes.
This command uses Node.js for the original Fusion alignment.

```bash
python3.14 -m reference.wheel.prepare
```

The script reads the [original Fusion scan](../reference/fusion/Sherman_P_Flush_Screen_Fusion_Default.stl),
corrects the frame and reconnects the screen patch. It then rotates the entire
wheel **-3.4932161177016057° about model +X** and translates it **+29.464786838041892 mm in Z**,
including the 26 mm total seating adjustment. It slices at **Y=-191 mm**
and **Y=+170 mm**, then scales only the middle body by **1.003** about `(0,0,26)`.

The script validates the outputs before replacing the checked-in files in
`reference/wheel/`. The adapter subtracts `body-scaled.brep` with zero added
clearance. The CAD viewer reads that same body and the two unscaled handle
STEPs. The HTML preview reads `merged.stl`, which reunites the body and handles
for display. Commit the regenerated reference files with any intentional
preparation changes. The source scan is preserved.

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

## Luna Surron seat reference

The [original seat scan](../reference/seat/LunaSurronSeat_30k.stl) and the
[stud-corrected mesh](../reference/seat/LunaSurronSeat_Studs_5p3x15.stl) share the
original scan coordinates. The corrected mesh uses four smooth Ø5.3 mm studs
with 15 mm exposed length from the surrounding plastic mounting faces. Each
axis and base location is fitted from the scan. The seat meshes are reference
assets for checking fit. The preview uses the [aligned seat](../reference/seat/surron-seat.stl),
prepared by rigidly fitting the four stud bases to the adapter hole mouths.
Regenerate it with `python3.14 -m reference.seat.prepare` when the seat
reference or its placement changes.

## Historical Veteran Sherman L procedure

Current documentation scope: the original **Veteran Sherman L** asset and its preparation. The later Sherman P import was an unfinished replacement experiment and is excluded from this source-history task. Existing destination-model records describe separate later work; this documentation update changes no CAD geometry.

### Verified correction from Sherman L version 1

The user clarified that Fusion is reference-only and the Sherman L supplies the original preparation procedure; the recent P import is experimental. The earlier **Veteran Sherman L v1** retains the missing history. Its `Scale1` (timeline index 14) is **uniform 1.003**, a **0.3% enlargement**, applied only to `Body`. Both handles remain unscaled. The selected scale point is approximately **(-0.0616645813, -26.7304611206, -2.6051712036) mm** in that asset's coordinate frame.

`Split1` at index 11 cuts at **Y=190 mm**; `Split2` at index 13 cuts at **Y=-180 mm**. Both have normal +Y. The order is front split, rear split, then body-only scaling. Exact definitions and the complete earlier timeline are saved in `../reference/fusion/sherman-l-preparation-verified.json`.

The earlier version was opened for inspection, its cursor was restored to 61, and it was closed without saving. The original seat-adapter project remained active afterward. No Fusion features were edited or saved. This source inspection does not itself alter the existing SolidCraft subtraction.

### Procedure to preserve in other CAD tools

The splits isolate the central wheel body so it can be subtracted from the adapter without subtracting either handle or cutting away the adapter's front clip. Keep the original asset and both handle pieces as separate reference geometry.

1. In the Sherman L asset coordinate frame, split the front handle at Y=190 mm and the rear handle at Y=-180 mm. Both cutting planes have normal (0, 1, 0).
2. Select only the isolated central `Body`. Uniformly scale it by **1.003**, meaning **100.3% of its original size**, about the recorded point **(-0.061664581298828125, -26.73046112060547, -2.6051712036132812) mm**. A factor of 0.003 would shrink it to 0.3% of its size and is not the source operation. Neither handle is scaled.
3. For a body-only imprint, use only that prepared central body as the subtraction tool. Exclude both handles from the Boolean selection. Preserve the adapter master and its dependent split child.

For each point p in the body, the scale transform is `p_new = pivot + 1.003 * (p - pivot)`. Convert the pivot and split planes consistently with import units; apply the asset-to-assembly placement afterward, or transform all these references consistently. This is a proportional enlargement, not a constant 0.003 mm offset.

The dimensions and pivot above belong to the **Sherman L** source asset. When preparing another wheel scan, preserve the body-only split/scale/subtract intent and verify its own handle boundaries, coordinate frame, units and scale pivot. Do not substitute the L scan for the accepted Sherman P reference.

This documents the verified source preparation; it does not apply it to the current SolidCraft model. The existing Sherman P imprint remains at zero added clearance until deliberately rebuilt. Fusion remains reference-only.

### Historical inspection notes (superseded)

The notes below describe the **superseded initial inspection** of flattened version 2. The scale uncertainty is now resolved; **do not use the earlier proposed 1.01 factor**. Any pending questions or proposed changes below are historical, not current instructions.

User intent: separate the wheel scan into rear handle, front handle and middle body; enlarge the middle subtraction body slightly for printing fit; subtract only that body so the adapter's front clip is not cut away by the handle.

Inspection found the three Sherman L bodies in the **linked Veteran Sherman L asset**, not editable split/scale steps in the seat-adapter timeline. The linked L document is direct/non-parametric, so the original clearance scale cannot be read. Its rear/front handle boundary planes are at global Y = -180 and +190 mm. The middle body's expanded bounds are approximately -180.460 to +190.650 mm, but that does not establish the original uniform scale or pivot.

The linked Sherman P asset is still one combined body. Its native source parameter 0.1 is the source normalization already accounted for in the aligned millimeter STL. Do not apply 0.1 again or confuse it with a new fit allowance.

Open questions at the time of inspection: apply changes in SolidCraft only, Fusion only, or both; and the exact fit scale (1.01 was offered as the interpretation of “0.01 bigger,” but is not yet confirmed). Source/live CAD models have not been modified by this inspection. The last full-scan, zero-clearance subtraction remains active until replaced deliberately.

Technical trial: a local SolidCraft split of the converted P scan at Y=190 mm failed SMLib validity checks for coincident/partially coincident face edges. It saved no candidate model and did not affect the live model. The remaining separation must be solved in the selected target before applying its Boolean; do not treat the trial as completed. Raw evidence is in `../reference/fusion/wheel-reference-preparation.json`.

This new request supersedes the former zero-added-clearance decision once a factor is confirmed. Preserve the untouched original scan and make any fit scale explicit and editable. Keep both handles out of the Boolean tools, and preserve the master-to-split-child dependency.
