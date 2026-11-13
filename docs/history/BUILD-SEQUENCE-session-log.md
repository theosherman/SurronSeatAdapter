# Sherman P Seat Adapter: Fusion to Onshape

> Historical session log only. Many statements below were superseded. Read the root README, current BUILD-SEQUENCE, and docs/CAD-REBUILD.md for final scope. Do not replay this file as an implementation plan.

## Latest completed work: user-authorized wheel-scan imprint

The user later explicitly requested importing `Sherman_P_Flush_Screen_Fusion_Default.stl` and subtracting it from the adapter underside to match the wheel top. This supersedes the original exclusion of asset subtraction for this specific scan. The imprint is complete in the master and propagated through the linked child.

Imported scan Part Studio: `b3b00a4315fe26c7bef8ae67`. Master scan Derived feature: `FjCgGoOEbJPUItD_1`. Scan unit conversion feature: `FdgqaKgEy09rg0Q_2` (0.001 scale). Master Boolean imprint: `FK8m1sWp7OUh9dE_2`. Boolean regenerated OK, leaving one master solid. Child Derived and connector features remain OK, leaving two child solids. No fillets were reintroduced and no fit clearance was added.

The aligned STL, exact Fusion placement, closed-mesh checks, upload helper, and final validation are saved as `Sherman_P_Scan_Aligned_To_Adapter_mm.stl`, `wheel-scan-alignment.json`, `prepare-wheel-scan.mjs`, `upload-wheel-scan.mjs`, and `wheel-imprint-state.json`. The upload helper reuses the connected MCP auth provider without saving or printing credentials. A pre-imprint version is available as `1e8c886e61f4df0b52f97731`.

## Scope correction — latest user instruction

### API budget and fillets — superseding instruction

### Linked child authorized and created

### Connector cutouts added to child

### Screwdriver access correction

#### Front ceiling follow-up (supersedes prior front offset)

User screenshots showed that the front large recesses were still through the mounting ledge. Corrected `FXQWXmmJub3ISHs_1` to use `offsetOppositeDirection=false` for the 3 mm up-to-face roof offset; its second direction still cuts downward through all. Verified two annular ceiling faces, approximately 188.9 mm² each. Saved final feature payload and master/child material checks in `front-screw-ceiling-correction.json`. Prefer this payload over the older front offset in `screw-access-correction.json`.

The user identified larger screw-access recesses cutting upward rather than downward. Corrected both master features: `F9orq0gyXHsXnGW_1` and `FXQWXmmJub3ISHs_1`. Rear pair starts 3 mm below the top sketch plane and cuts downward through all. Front pair preserves the roof 3 mm below the sloped top face and extends downward through all using the second direction. The small through-hole feature was unchanged. Both corrected features regenerate OK; the master remains one solid. The linked child automatically updated and remains two solids with a healthy derived link and connector feature. See `screw-access-correction.json`.

When updating saved Onshape feature payloads, remove stale `deterministicIds` from queries that already contain valid stable `queryString` values. The API otherwise prioritizes obsolete transient IDs and may erase selections.

The user requested all five connector cutouts from the Fusion split variant. These are now represented by child-only feature `FP66VefeBgmVRj3_1`, named `Five connector cutouts — 8 mm`. It uses the two saved top-joint profiles as one top connector and the two side-joint profiles plus the source mirrors as four side connectors. The master is untouched. No fillets or separate connector inserts were added. Exact extracted profile lines and mirror planes are in `fusion-connector-source.json`; the implementation is in `connector-cutouts.fs`; IDs and validation are in `connector-cutouts-state.json`.

The user subsequently requested a linked child with the split applied in that child only. `Adapter Body Split` Part Studio: `c9c1cb2f1b6e54ba33df5e8a`. Master remains `69186d95d4c9dc45ec42f803`.

The child uses native Derived feature `FT7jAdxtqUea5gk_0` referencing the master Part Studio in this document/workspace. Split plane feature `FowdGEq1Dm4kagK_1` reproduces the first line of Fusion's SplitBodySketch, the actual tool used by the source Split1 feature. Its origin in meters is (0, -0.09288539833894989, 0.06305711325274752); its normal is proportional to (0, 8.380901422620052, -1.705113665673723). A native Split feature keeps both sides. No fillets or print-joint details were added to the child.

See `child-split-state.json` for IDs and final validation. The master remains unsplit. Do not recreate any fillets. Conserve API calls.

The user explicitly requested conservative Onshape API usage and cancellation of all fillets. Both native fillet features were deleted: `F953S6gN65wUQ7Q_1` and `FBjPOxiHcTTcn9O_1`. Do not recreate fillets, run per-edge trials, or perform redundant remote inspection. Prefer local preparation and the fewest necessary remote calls. Historical fillet notes below describe superseded work only. The existing milestone version retains its historical state; the current workspace has the fillets removed.

The user approved the concept of a separate Part Studio using Derived to inherit the master body's finished geometry automatically. Do not split the master body. A derived printing variant has not yet been created.

Rebuild only the original `AdapterBody`, in its unsplit form. The separate `AdapterBodySplit` component is a printing variant and is explicitly excluded. Do not implement steps 18–20 below; those earlier steps are superseded. The split-variant sketches and construction planes were removed from Onshape. No solid split or joint feature was applied. The user is discussing one remaining imperfection; wait for its details before changing that geometry.

An unsplit milestone version exists: `6fc7581e82a4b84cb8cd893f` (`Unsplit adapter — assets excluded`). The current body has native sketches, extrusions, mirrors, drafts, and fillets. The source ellipse was replaced with an exact native ellipse. Bottom fillet succeeds on 36 of 38 selected edges; adapter edge fillet succeeds on 240 of 251 selected edges. Remaining selections caused overlap/kernel failures at the source radius and were omitted. The imported-asset split at source timeline 131 and its dependent body removal were intentionally excluded.

## Objective and agreed scope

Recreate the open Fusion design, `Surron Seat Adapter v3 v2`, in Onshape with editable sketches and reproducible modeling features. Prioritize `AdapterBody` and `AdapterBodySplit`. Exclude imported STL/reference assets and the subtraction that uses an imported asset. Adjust or omit dependent features only where the missing asset makes recreation impossible; record each omission.

The user authorized a public Onshape document because this account cannot create private documents. Continue the authorized rebuild without requesting approval for routine implementation choices.

## Destination

- Document: `b1a1f737761c2581236d5ec3`
- Workspace: `eb902961c90530f7f212e211`
- Part Studio: `69186d95d4c9dc45ec42f803`, named `Adapter Body`
- URL: https://cad.onshape.com/documents/b1a1f737761c2581236d5ec3/w/eb902961c90530f7f212e211/e/69186d95d4c9dc45ec42f803

## Saved source data

- `fusion-adapter-extraction.json`: 18 sketches, 233 curves, sketch frames, dimensions, feature inventory. Coordinates and lengths are in centimeters.
- `fusion-adapter-extrusions.json`: readable extrusion operations, selected profile bounding boxes, distances, extents, taper angles, and starting offsets.
- `fusion-adapter-parameters.json`: 149 model parameters, expressions, values, roles, and creating feature names.
- `onshape-response-1794459614325.json`: full Onshape feature specifications. Large generated API response; inspect selectively.

Fusion API lengths are centimeters and angles radians. Onshape convenience tools use inches and degrees. Convert lengths with `inches = centimeters / 2.54`. Raw API/FeatureScript units must be handled explicitly.

## Build sequence

1. Inspect the existing destination Part Studio before writing. It was created successfully; no modeling feature has yet been confirmed created. Do not create duplicate documents or tabs.
2. Establish consistent coordinate frames. Preserve each Fusion sketch's saved origin, X direction, and Y direction. Resolve default Onshape plane orientations before transferring curves.
3. Recreate `BottomSketch` (timeline 8), then `BottomExtrusion` (9). Source extrusion is a new body with two distance extents: 150 mm and 50 mm. Verify direction and both extents rather than collapsing them into an assumed symmetric extrusion.
4. Recreate `Mirror1` (10), retaining the source mirror plane and merge behavior.
5. Recreate `SideSketch` (11) and `SideIntersection` (12). The component feature collection calls the latter `Extrude2`; inspect its definition/parameters to resolve this alias and reproduce the intersection.
6. Recreate `RearSketch` (13), `RearIntersection` (14), and `Mirror2` (15). Rear intersection uses a 490 mm distance extent; verify sketch orientation and direction.
7. Recreate `TrunkDovetailSketch` (17) and its join extrusion `Extrude4` (18). Replace asset-dependent up-to references with explicit geometry only when their intended boundary can be established from the source.
8. Skip unrelated seat, trunk, latch, saddlebag, and reference-asset branches while following adapter dependencies.
9. Recreate `BoltHolesSketch` (74), `ScrewHoleExtrude` (75), and counterbore/counterseat cuts `Extrude6` (76), `Extrude7` (77). Transfer the selected profiles, not all regions indiscriminately. The source screw extrusion reports reference failures; preserve intended hole geometry without recreating broken references.
10. Recreate `SeatHangerSketch` (78), `Extrude8` (79), `Draft1` (80), `Mirror3` (81), and `Combine1` (82).
11. Recreate `HandleMountSketch` (83), `Extrude9` (84), `FrontCutSketch` (85), `Extrude12` (86), and `Draft4` (87).
12. Recreate `RearSeatNotchSketch` (88), `Extrude10` (89), `FrontDovetailSketch` (90), and `Extrude11` (91).
13. Inspect `Plane1` (92) and `Extrude13` (93). The extrusion API currently throws an internal validation error for this entry. Determine its intended geometry from parameters/dependencies; omit it if it is the asset subtraction or cannot be reproduced without the excluded asset. Do not silently invent geometry.
14. Recreate `HingeTrajectorySketch` (94), `SeatCutoutPlane` (95), `SeatCutoutSketch` (96), `Extrude15` (97), and `Mirror4` (98), where independent of excluded assets.
15. Recreate `RearCutoutPlane` (119), `RearCutSketch` (120), `Extrude16` (121), and `Mirror5` (122).
16. Recreate `BodyCutSketch` (123), `Extrude18` (124), `AirtagCutSketch` (125), and `Extrude19` (126). Body cut starts at -12 mm with a 15 degree taper; AirTag cut depth is -8.5 mm.
17. Inspect and reproduce applicable fillets around timeline 127–133, `Split2` (131), and the corresponding body removal (132). Determine whether a splitting/subtraction tool is an imported asset and skip that operation as instructed.
18. Inspect copy/move operations around timeline 179–182 and establish the intended `AdapterBodySplit` branch without duplicating unwanted solids.
19. Recreate `SplitBodySketch` (183), `Split1` (184), `TopJointSketch` (185), and the joint extrusion (186). Entry 186 currently throws an internal validation error when its extrusion operation is queried; inspect parameters and native component ownership to resolve it.
20. Recreate `SideJointSketch` (187), `Extrude2` (188), construction planes (189–190), `Fillet2` (191), mirrors (192–193), `Extrude3` (194), `Extrude4` (195), `OffsetFaces1` (196), `Fillet4` (197), and `Fillet3` (198), preserving order and applicable body selection.
21. Exclude the imported `Sherman P Body Top Refined v4` reference at timeline 199 and all reference asset geometry.
22. Verify the feature regeneration state, sketch placement, body count, dimensions, and rendered appearance. Compare against the source before the excluded asset operation where appropriate. Record deviations and unsupported or intentionally skipped operations.

## Implementation notes

- Prefer native Onshape sketches and features. A STEP/STL import alone does not satisfy the editable feature-tree request.
- Use stable geometric queries for selected profiles, faces, and edges where possible.
- Some Fusion sketches report lost projected references but retain cached curves. Transfer the saved geometry without importing the missing asset dependency.
- Feature collection names/ownership can differ from timeline names. Use timeline order as the reference and inspect problematic entries individually.
- Never include credentials in saved files. Onshape authentication is configured in the OS keychain.

## Progress checklist

- [x] Inspect active Fusion document and timeline.
- [x] Confirm asset/reference exclusions with user.
- [x] Extract sketches and model parameters locally.
- [x] Authenticate Onshape.
- [x] Obtain permission for a public document.
- [x] Create public document and Adapter Body Part Studio.
- [x] Retrieve Onshape feature specifications.
- [ ] Confirm destination feature tree and plane frames.
- [ ] Rebuild base sketches, extrusion, mirrors, and intersections.
- [ ] Rebuild adapter cuts, mounts, drafts, and fillets.
- [ ] Rebuild applicable split-body joints and finishing features.
- [ ] Verify and document differences.

## Current execution state

Part Studio creation succeeded after session permissions changed. The earlier approval error is no longer the active blocker.

Onshape plane frames were verified with FeatureScript: Top has normal +Z and X +X; Front has normal -Y and X +X; Right has normal +X and X +Y. BottomSketch therefore belongs on Top; SideSketch matches Right.

Feature-tree reads and the native BottomSketch creation request stalled without returning a result. The waiting calls were cancelled. The BottomSketch request may have reached Onshape: inspect the Part Studio before retrying to avoid duplicate sketches. No extrusion has been submitted. A narrowed REST feature-tree read also stalled. `onshape-selected-feature-specs.json` contains the extracted specifications for sketch, extrude, mirror, and plane features.
