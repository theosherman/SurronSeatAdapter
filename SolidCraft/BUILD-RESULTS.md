# SolidCraft rebuild results

Built with SolidCraft 0.40.1 on 2026-11-12 (Chicago). The native document is `models/seat-adapter.sc`; its full replay script is `scripts/seat-adapter-build.json`. The app is connected on port 7878 and displays the master. No Onshape API calls were made for this port.

## Parts and feature history

- `AdapterBodyMaster`: one unsplit solid, corrected screw ceilings, downward access cavities, hangers, handle mount, both dovetails, side/rear/notch cuts, drafted underside cavity, AirTag pocket, and zero-clearance aligned Sherman P scan imprint.
- `AdapterBodySplit` component: a timeline copy of the completed master, split into `AdapterBodyFront` and `AdapterBodyRear`, then five 8 mm connector recesses. The master is not split or connector-cut. Hide the master before showing the child to avoid coincident bodies on screen.
- No fillets, loose connector inserts, or extra fit clearance.
- Latch and saddle bag mount: extracted separately from Fusion, not yet built in SolidCraft. See `../docs/ACCESSORY-PARTS.md`.

The original build had 69 timeline entries and 25 sketches, each fixed at zero degrees of freedom. The later component reorganization adds a hidden reference-mesh feature, making 70 entries; see `REORGANIZATION.md`. This preserves source coordinates; it does not reproduce Fusion's entire dimensional constraint graph. `airtagPocketDepth` is a named driving parameter. Other editable feature dimensions remain in their native feature definitions.

## Verification

| Body | Closed | Volume (mm³) |
|---|---|---:|
| Master | Yes | 1,507,476.8189659615 |
| Front printing half | Yes | 853,718.9764494072 |
| Rear printing half | Yes | 636,139.6010264895 |

- No feature errors or warnings in the final design.
- First five body features match Fusion's volume to reported precision: 2,096,156.9173983494 mm³. Rear dovetail trimmed to its proper plane gives 2,121,657.2265613466 mm³, agreeing with Fusion within numerical tolerance.
- Twelve material tests on the exported master STL passed: each of the four bolt locations has material in its annular ledge, empty space immediately below it, and an open small bore. Two independent ray directions agreed at every test point. Rerun `node scripts/validate-mounting-ceilings.mjs` after re-exporting the master.
- Changing `airtagPocketDepth` from 8.5 to 8.6 mm removed 102.4295078183 mm³ from the master and 102.4295078153 mm³ from the combined child. The rear half stayed unchanged; the front half updated. No errors or warnings occurred, and the original 8.5 mm state was restored.
- The scan was imported in millimeters at its saved aligned coordinates, converted to a closed faceted solid, and consumed by a native subtraction. No historical Onshape 0.001 scale correction was applied.

Detailed evidence: `logs/build-validation.json`, `logs/inheritance-test.json`, `logs/mounting-ceiling-validation.json`, `logs/open-final.json`, and `logs/exports.json`.

## Target adaptations and limits

1. **Rear dovetail end plane:** SolidCraft's point-based extrusion limit did not reproduce Fusion's oblique end condition. A long extrusion, exact planar split, and removal of the excess match the source volume.
2. **Front draft:** native draft87 returns “not supported yet: SMLib draft for this geometry.” The exact source triangular wedge is subtracted instead. Its volume is 17,378.64556355038 mm³, matching Fusion's draft removal to numerical precision. Source plane/boundaries are saved in `../cad-rebuild/accessories/master-draft87-reference.json`.
3. **Left side circular cut:** the analytic cylinder cutter silently removed no material, including when built as a separate tool. Changing span or seam did not fix it. A 256-sided inscribed cutter works, with the exact R20 circle retained as construction geometry. Maximum radial deviation is `20*(1-cos(pi/256)) = 0.0015059632 mm`. The un-imprinted port volume is approximately 0.7532 mm³ larger than the expected corrected-ceiling Fusion result because of this approximation. The opposite side remains analytic.
4. **Mirrors of cuts:** explicit reflected sketches avoid an ineffective cut-feature mirror and a second mirror's “invalid B-rep record: flat arrays” failure. Reflected frame handedness is included when choosing connector extrusion directions.
5. **Onshape comparison:** accepted Onshape master volume is 1,511,781.8419273874 mm³. This SolidCraft master is about 4,305.023 mm³ smaller (0.285%). The prior Onshape port included documented adaptations; exact parity between the two ports has not been established. Do not call this an exact Onshape copy. The source Fusion pre-fillet/pre-imprint master is 1,527,477.0129629427 mm³; the corresponding SolidCraft result is about 1,527,475.2504 mm³, including the corrected ceiling and tiny cutter approximation.

No whole-model STEP XOR comparison or physical print-fit test has been performed. Successful kernel health and scalar measurements do not establish exact topology equality.

## Files to use

- `models/seat-adapter.sc`: complete master and dependent split child; primary document.
- `models/adapter-body-imprinted.sc`: unsplit finished master checkpoint.
- `models/adapter-body-native.sc`: master before wheel imprint.
- `exports/adapter-body.step`, `exports/adapter-body.stl`: master only.
- `exports/adapter-body-split.step`, `exports/adapter-body-split.3mf`: two printing halves only, excluding the overlapping master.
- `exports/adapter-front.stl`, `exports/adapter-rear.stl`: individual halves, in the design's coordinates.
- `scripts/generate-adapter.mjs`, `scripts/generate-child.mjs`: stage generators. Each also refreshes the combined replay when the other stage inputs exist; the combined script includes the scan stage.
- `models/experiments/`: superseded investigations, not final deliverables.
