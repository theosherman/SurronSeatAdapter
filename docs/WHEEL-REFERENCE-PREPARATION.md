# Sherman P body-only subtraction preparation

## Verified correction from Sherman L version 1

The user clarified that Fusion is reference-only and the Sherman L supplies the original preparation procedure; the recent P import is experimental. The earlier **Veteran Sherman L v1** retains the missing history. Its `Scale1` (timeline index 14) is **uniform 1.003**, a **0.3% enlargement**, applied only to `Body`. Both handles remain unscaled. The selected scale point is approximately **(-0.0616645813, -26.7304611206, -2.6051712036) mm** in that asset's coordinate frame.

`Split1` at index 11 cuts at **Y=190 mm**; `Split2` at index 13 cuts at **Y=-180 mm**. Both have normal +Y. The order is front split, rear split, then body-only scaling. Exact definitions and the complete earlier timeline are saved in `../cad-rebuild/sherman-l-preparation-verified.json`.

The earlier version was opened for inspection, its cursor was restored to 61, and it was closed without saving. The original seat-adapter project remained active afterward. No Fusion features were edited or saved. This source inspection does not itself alter the existing SolidCraft subtraction.

The notes below are the **superseded initial inspection** of flattened version 2. The scale uncertainty is now resolved; **do not use the earlier proposed 1.01 factor**.

User intent: separate the wheel scan into rear handle, front handle and middle body; enlarge the middle subtraction body slightly for printing fit; subtract only that body so the adapter's front clip is not cut away by the handle.

Inspection found the three Sherman L bodies in the **linked Veteran Sherman L asset**, not editable split/scale steps in the seat-adapter timeline. The linked L document is direct/non-parametric, so the original clearance scale cannot be read. Its rear/front handle boundary planes are at global Y = -180 and +190 mm. The middle body's expanded bounds are approximately -180.460 to +190.650 mm, but that does not establish the original uniform scale or pivot.

The linked Sherman P asset is still one combined body. Its native source parameter 0.1 is the source normalization already accounted for in the aligned millimeter STL. Do not apply 0.1 again or confuse it with a new fit allowance.

Pending user answers: apply changes in SolidCraft only, Fusion only, or both; and the exact fit scale (1.01 was offered as the interpretation of “0.01 bigger,” but is not yet confirmed). Source/live CAD models have not been modified by this inspection. The last full-scan, zero-clearance subtraction remains active until replaced deliberately.

Technical trial: a local SolidCraft split of the converted P scan at Y=190 mm failed SMLib validity checks for coincident/partially coincident face edges. It saved no candidate model and did not affect the live model. The remaining separation must be solved in the selected target before applying its Boolean; do not treat the trial as completed. Raw evidence is in `../cad-rebuild/wheel-reference-preparation.json` and a top view is in `../SolidCraft/logs/wheel-p-before-split.png`.

This new request supersedes the former zero-added-clearance decision once a factor is confirmed. Preserve the untouched original scan and make any fit scale explicit and editable. Keep both handles out of the Boolean tools, and preserve the master-to-split-child dependency.
