# Project context for future CAD work

## Project-wide priority: simplicity

The user explicitly prioritizes simplicity in every part of this project, in every session. Prefer the simplest understandable, editable design that meets the requested function. Apply this to CAD geometry, sketches, feature history, code, instructions, and workflows.

- Prefer redrawing the controlling sketch or changing the original feature over stacking corrective face extrusions, Boolean patches, duplicate interfaces, or special-case instructions.
- Do not treat the user's selection of a proposed design as acceptance of hidden implementation complexity. If a proposal or requested change starts becoming more complex, point that out **before proceeding**, explain the practical maintenance/failure tradeoff, and present a simpler alternative so the user can steer.
- Replace or remove superseded workarounds rather than accumulating more layers. Preserve requested function and established geometry; simplicity does not authorize silently dropping requirements.

Rear-wall correction is approved and implemented: the original cavity cutter is limited by a plane parallel to the original sloped latch wall, offset 5 mm inward along its normal. Manufacturing exports are rebuilt from this corrected cut. Never repair the finished body by adding a wall patch. The outside latch interface and separate latch remain unchanged.

Lower rear toe cut is approved and implemented: trim only below the latch-root Z at placed point `(0,177.270005683283,-17.98689437242)`, using the original rear-wall angle mirrored across XY. Preserve the upper seat support and top dovetail. The original cavity cutter has a second inward limit retaining **14 mm** normal thickness at this new local diagonal. This supersedes the earlier 5 mm and 10 mm local toe walls; the original untrimmed sloped rear wall remains 5 mm. Do not cut the upper rear support or recreate the local wall with a body patch. See `trunk_cavity.py` and the implemented rear-tip preview.

Current cavity direction (approved and implemented): one long sixteen-line central cavity extending through the narrow middle into the wider rear, with straight walls and a uniform 18.5 mm roof offset. The existing 8.5 mm AirTag recess leaves 10 mm of sampled roof material. Replace the original cavity feature; do not overlay a second pocket and leave a stepped roof recess. Two symmetric rear side cuts use placed-model coordinates (78,126) to (55,140), then X=55 rearward, mirrored about X=0. Keep the central rear bridge, original latch and single top dovetail. This supersedes the rear-only octagon/solid-middle direction. The 10 mm outer-wall shift, latch extension, and face-patching implementation at historical commit `484bf2e` remain rejected.

Printing-face offsets are approved and implemented: faces 1 and 2 use a **1 mm outward normal offset** of the original `RearSketch` diagonal and its mirror. Existing front print-plane trimming follows those native rear planes. Face 3 is the triangular `FrontCutSketch` / `Extrude12` corner cut beside the front clip, **not BottomSketch**; both diagonals move **3 mm outward** (total; supersedes the first 1 mm) toward the removed corners, retaining more material with unchanged angles and Z extrusion. `cut_offsets.py` edits the original manufacturing profiles; do not add finished-body patches.

## CAD context

For user-visible proposal previews, use the automatic browser viewer: `python preview_server.py start --no-open` (omit `--no-open` when initially opening it). Write the final image under `tmp/` last so it becomes the newest image; the open browser at http://127.0.0.1:8766 updates automatically. Do not ask the user to hunt for image paths.

Temporary correction proposals and discussion previews (images, STEP/STL studies, HTML viewers, and their scratch reports) belong under `tmp/` inside this repository, never in tracked exports or commits. Keep durable, updated previews of implemented geometry in the repository. Preview generators must write proposal outputs to `tmp/` (not system `/tmp` and with no `exports` subdirectory); do not stage temporary assets. Historical proposal assets have been purged from Git history.

Read `README.md`, `docs/CAD-REBUILD.md`, and `cad-rebuild/recipe.json` before changing CAD geometry. `docs/PORTING-AND-VALIDATION.md` describes validation for another CAD engine.

Additional user-requested parts: `Latch` and `SaddleBagMount` must remain separate from the adapter and from each other. Their extracted features and build sequences are in `docs/ACCESSORY-PARTS.md` and `cad-rebuild/accessories/`.

The user initialized Git and explicitly requested check-ins at appropriate milestones. Make local commits after meaningful verified changes. Do not push to a remote without authorization.

Preserve these user decisions:

- Master `Adapter Body` is unsplit. The separate `Adapter Body Split` child inherits the completed master and is split into two solids.
- Only the child has the three 8 mm connector recesses: the large top recess and one butterfly-key recess on each inner cavity wall. The cavity-key waists follow the split plane through the full cut depth. No loose connector inserts were requested or created.
- Fillets: the November 15 request supersedes the earlier cancellation for Build123d only. Apply 1 mm fillets to practical adapter-body edges, excluding the running dovetail rail; its rear terminal edges may be rounded. The five connected edges at the body/dovetail junction (shoulders and trapezoidal root around Y=147.5–151.6 mm) and the three-edge side return on each side must remain sharp for latch clearance; this is distinct from the terminal end at Y=261 mm. Accessories remain unchanged. Symmetry is mandatory: each fillet must have the same mirrored fillet, or be removed on both sides. The screen walls extend to the tangent ramp. The finishing feature has 131 selected edges. Exclude mirrored pairs whose generated fillet faces touch the asymmetric wheel cutter. Validate actual pre-imprint symmetry with `validate_fillets.py`. See `body_fillets.py`.
- Larger screwdriver-access recesses open downward and retain the small through-hole mounting ceilings. The exact front ceiling plane is recorded in `cad-rebuild/recipe.json` under M09.
- The initial exclusion of reference-asset subtraction was later superseded by explicit authorization to subtract the aligned Sherman P wheel-top scan from the master. Do not substitute the old Veteran Sherman L reference asset.
- The final imprint has zero added clearance. Do not silently add a fit allowance.
- Later reference-preparation request: Fusion must remain reference-only. The authoritative Sherman L v1 history verifies a uniform **1.003** fit scale on `Body` only, after splits at Y=190/-180 mm; both handles are excluded. See `reference/fusion/sherman-l-preparation-verified.json`. This supersedes the guessed 1.01 interpretation. The recent P import in Fusion is experimental, not the source for the original preparation procedure.

For another CAD system, use the portable recipe's millimeter geometry and exact selected loops. Raw Fusion extracts use centimeters/radians. Preserve nonzero sketch-space Z, explicit extrusion directions, and reflected connector handedness. New target-specific implementations have not yet been written or tested.
