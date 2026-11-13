# Sherman P body-only subtraction preparation

User intent: separate the wheel scan into rear handle, front handle and middle body; enlarge the middle subtraction body slightly for printing fit; subtract only that body so the adapter's front clip is not cut away by the handle.

Inspection found the three Sherman L bodies in the **linked Veteran Sherman L asset**, not editable split/scale steps in the seat-adapter timeline. The linked L document is direct/non-parametric, so the original clearance scale cannot be read. Its rear/front handle boundary planes are at global Y = -180 and +190 mm. The middle body's expanded bounds are approximately -180.460 to +190.650 mm, but that does not establish the original uniform scale or pivot.

The linked Sherman P asset is still one combined body. Its native source parameter 0.1 is the source normalization already accounted for in the aligned millimeter STL. Do not apply 0.1 again or confuse it with a new fit allowance.

Pending user answers: apply changes in SolidCraft only, Fusion only, or both; and the exact fit scale (1.01 was offered as the interpretation of “0.01 bigger,” but is not yet confirmed). Source/live CAD models have not been modified by this inspection. The last full-scan, zero-clearance subtraction remains active until replaced deliberately.

Technical trial: a local SolidCraft split of the converted P scan at Y=190 mm failed SMLib validity checks for coincident/partially coincident face edges. It saved no candidate model and did not affect the live model. The remaining separation must be solved in the selected target before applying its Boolean; do not treat the trial as completed. Raw evidence is in `../cad-rebuild/wheel-reference-preparation.json` and a top view is in `../SolidCraft/logs/wheel-p-before-split.png`.

This new request supersedes the former zero-added-clearance decision once a factor is confirmed. Preserve the untouched original scan and make any fit scale explicit and editable. Keep both handles out of the Boolean tools, and preserve the master-to-split-child dependency.
