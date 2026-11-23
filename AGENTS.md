# Project context for future CAD work

## Project-wide priority: simplicity

The user explicitly prioritizes simplicity in every part of this project, in every session. Prefer the simplest understandable, editable design that meets the requested function. Apply this to CAD geometry, sketches, feature history, code, instructions, and workflows.

- Prefer redrawing the controlling sketch or changing the original feature over stacking corrective face extrusions, Boolean patches, duplicate interfaces, or special-case instructions.
- Do not treat the user's selection of a proposed design as acceptance of hidden implementation complexity. If a proposal or requested change starts becoming more complex, point that out **before proceeding**, explain the practical maintenance/failure tradeoff, and present a simpler alternative so the user can steer.
- Replace or remove superseded workarounds rather than accumulating more layers. Preserve requested function and established geometry; simplicity does not authorize silently dropping requirements.

Rear-wall correction is approved and implemented: the original cavity cutter is limited by a plane parallel to the original sloped latch wall, offset 10 mm inward along its normal. Manufacturing exports are rebuilt from this corrected cut. Never repair the finished body by adding a wall patch. The outside latch interface and separate latch remain unchanged.

Lower rear toe cut is approved and implemented: trim only below the latch-root Z at placed point `(0,177.270005683283,-17.98689437242)`, using the original rear-wall angle mirrored across XY. Preserve the upper seat support and top dovetail. The original cavity cutter has a second inward limit retaining **14 mm** normal thickness at this new local diagonal. This supersedes the earlier 5 mm and 10 mm local toe walls; the original untrimmed sloped rear wall is 10 mm. Do not cut the upper rear support or recreate the local wall with a body patch. See `trunk_cavity.py` and the implemented rear-tip preview.

Current cavity direction (approved and implemented): one long sixteen-line central cavity extending through the narrow middle into the wider rear, with straight walls and a uniform 18.5 mm roof offset. The 8.5 mm AirTag recess is relocated 90 mm rearward along the tilted top plane, above the rear cavity. Replace the original cavity feature; do not overlay a second pocket and leave a stepped roof recess. Two symmetric rear side cuts use placed-model coordinates (78,126) to (55,140), then X=55 rearward, mirrored about X=0. Keep the central rear bridge, original latch and single top dovetail. This supersedes the rear-only octagon/solid-middle direction. The 10 mm outer-wall shift, latch extension, and face-patching implementation at historical commit `484bf2e` remain rejected.

Printing-face offsets are approved and implemented: faces 1 and 2 use a **10 mm total outward normal offset** of the original `RearSketch` diagonal and its mirror. Existing front print-plane trimming follows those native rear planes. Face 3 is the triangular `FrontCutSketch` / `Extrude12` corner cut beside the front clip, **not BottomSketch**; both diagonals move **3 mm outward** (total; supersedes the first 1 mm) toward the removed corners, retaining more material with unchanged angles and Z extrusion. `cut_offsets.py` edits the original manufacturing profiles; do not add finished-body patches.

The approved 18 mm seat lowering raises the Sherman P scan, front clip, and screen walls relative to the printed revision. The original underside plane is translated up 18 mm, clipping the lowest portion of the original cavity and rear toe. Maintain the upper latch interface, mounting datums, and existing cavity cutter limits.

The approved production latch raises the original face 1–6 edge 18 mm in Z at the original X/Y position and preserves the outer tongue length. In the single native side profile, face 2 follows the sloped adapter wall to its lower edge, face 5 follows the approved shallow rearward rise from the side-view mark-up, and face pairs 1–7 and 6–10 both have 14.39 mm normal thickness. Keep the shared dovetail, separate solid, and nominal mating clearance. The preview labels the hook **Latch tongue**.

The approved front-clip underside ramp is tangent to the native rounded rear jaw. The bridge and gusset share this lower profile at the lift boundary. Preserve the upper screen-ramp tangent and the full 30.2 mm clip bore.

The approved suspension adjuster clearance uses a 30° underside draft on the original mirrored seat shoulders. Preserve the outer seat-contact edge and full shoulder span. The rear seat notch profiles extend through the widened flanks at the original 8 mm depth.

The approved seat-edge relief (M17, option C) uses mirrored 28 mm cylindrical cuts at the original sketch center and tilt. Apply the cuts after the raised underside trim and before the finishing fillets. The portable recipe retains the historical 40 mm source profile.

The approved shoulder split uses the finite mirrored shoulder sketch, with its rear edge continued 19 mm in sketch space and then shifted 10 mm rearward in placed Y. The front vertices stay at their source positions, 10 mm ahead of the former uniformly rear-shifted profile. Keep the 30° draft. The top butterfly has a 43 mm tip-width pocket, and the two cavity-wall keys have wider 9.8 mm nominal tips before finishing. The earlier continuous shoulder extension into the rear body was rejected.

## CAD context

Use `./build.sh --preview` for routine master-body edits. Use `./build.sh` when the change needs the split halves, keys, or latch in the preview. The GitHub release build generates printable STLs.

For user-visible proposal previews, use the automatic browser viewer: `python preview_server.py start --no-open` (omit `--no-open` when initially opening it). Write the final image under `tmp/` last so it becomes the newest image; the open browser at http://127.0.0.1:8766 updates automatically. Do not ask the user to hunt for image paths.

Temporary correction proposals and discussion previews (images, STEP/STL studies, HTML viewers, and their scratch reports) belong under `tmp/` inside this repository, never in tracked exports or commits. Keep historical design illustrations under `docs/images/cad/`. The release build generates current part previews. The ignored `exports/` directory is for generated output. Preview generators must write proposal outputs to `tmp/` (not system `/tmp` and with no `exports` subdirectory); do not stage temporary assets. Historical proposal assets have been purged from Git history.

Read `README.md`, `docs/CAD-REBUILD.md`, and `cad-rebuild/recipe.json` before changing CAD geometry. `docs/PORTING-AND-VALIDATION.md` describes validation for another CAD engine.

Additional user-requested parts: `Latch` and `SaddleBagMount` must remain separate from the adapter and from each other. Their extracted features and build sequences are in `docs/ACCESSORY-PARTS.md` and `cad-rebuild/accessories/`.

The user initialized Git and explicitly requested check-ins at appropriate milestones. Make local commits after meaningful verified changes. Do not push to a remote without authorization.

Preserve these user decisions:

- Master `Adapter Body` is unsplit. The separate `Adapter Body Split` child inherits the completed master and is split into two solids.
- Only the child has the three connector recesses at the placed Y=37 mm transverse split. The top recess cuts 12.8 mm perpendicular to the roof, with its waist centered on the split at the opening. The matched cavity-wall recesses are 6.8 mm deep and their waists follow the split plane through the full cut depth. Recesses have 1 mm fillets at the opening and sharp floor edges. `butterfly_keys.py` builds the 12 mm top key and a shared 6 mm cavity key (60% of the 10 mm sidewall) with 1 mm fillets on every edge and at least 0.4 mm clearance. The split viewer shows the top key and one cavity key seated.
- Fillets: the November 15 request supersedes the earlier cancellation for Build123d only. Apply 1 mm fillets to practical adapter-body edges, excluding the running dovetail rail; its rear terminal edges may be rounded. The five connected edges at the body/dovetail junction (shoulders and trapezoidal root around Y=147.5–151.6 mm) and the three-edge side return on each side must remain sharp for latch clearance; this is distinct from the terminal end at Y=261 mm. Accessories remain unchanged. Symmetry is mandatory: each fillet must have the same mirrored fillet, or be removed on both sides. The screen walls extend to the tangent ramp. Exclude mirrored pairs whose generated fillet faces touch the asymmetric wheel cutter. Validate actual pre-imprint symmetry with `python3.14 -m scripts.validate_fillets`. See `body_fillets.py`.
- Larger screwdriver-access recesses open downward and retain the small through-hole mounting ceilings. The exact front ceiling plane is recorded in `cad-rebuild/recipe.json` under M09.
- The initial exclusion of reference-asset subtraction was later superseded by explicit authorization to subtract the aligned Sherman P wheel-top scan from the master. Do not substitute the old Veteran Sherman L reference asset.
- Wheel and seat preparation live under `reference/` and run only by explicit request. Routine adapter builds and previews read the checked-in prepared references. Keep the original scans and commit regenerated references only when their preparation changes.
- The final imprint has zero added clearance. Do not silently add a fit allowance.
- Later reference-preparation request: Fusion must remain reference-only. The authoritative Sherman L v1 history verifies a uniform **1.003** fit scale on `Body` only, after splits at Y=190/-180 mm; both handles are excluded. See `reference/fusion/sherman-l-preparation-verified.json`. This supersedes the guessed 1.01 interpretation. The recent P import in Fusion is experimental, not the source for the original preparation procedure.

For another CAD system, use the portable recipe's millimeter geometry and exact selected loops. Raw Fusion extracts use centimeters/radians. Preserve nonzero sketch-space Z, explicit extrusion directions, and reflected connector handedness. New target-specific implementations have not yet been written or tested.
