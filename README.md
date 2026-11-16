# SurronSeatAdapter

## Project priority: simplicity

**Simplicity is a priority in every part of this project and in every session.** Prefer clear sketches, direct features, readable code, and short workflows over layered corrections and special cases. When a change or proposed option adds complexity, explain that tradeoff before proceeding and offer a simpler alternative so the user can weigh it. Selecting an option does not imply acceptance of hidden complexity. Remove superseded workarounds instead of adding more patches, while preserving the requested function.

The approved Build123d cavity now extends through the narrow middle into the wider rear as one sixteen-line, straight-sided pocket. A single 18.5 mm roof offset retains 10 mm beneath the existing AirTag recess at sampled locations. The original cavity cutter follows the angled rear latch wall at a 5 mm inward normal offset. Two symmetric rear side cuts reduce the exterior corners while retaining the rear bridge and separate original latch. This supersedes the rear-only octagon and filled-middle direction; see [current Build123d results](Build123d/README.md).

The lower toe beneath the rear latch is now trimmed at the latch-wall angle mirrored across XY, with a local **14 mm** wall retained by limiting the original cavity cutter. The upper seat support, top dovetail and separate latch are preserved; see [the implemented section](Build123d/exports/rear-tip-implemented.png).

This folder records the reconstruction of the Fusion design **Surron Seat Adapter v3 v2** in Onshape, including the later wheel-scan imprint and a linked printing variant. It is intended to let a future agent rebuild the accepted geometry in another CAD system, including SolidCraft or Zoo Design Studio.

The printing-plane boundaries (faces 1 and 2) and mirrored triangular front corner cuts (face 3 beside the front clip) now sit **1 mm outward**, preserving their angles and retaining more material. These edits change the original manufacturing profiles; see [implemented offsets](Build123d/exports/one-mm-face-offsets-implemented.png).

## Start here

The [build123d project](Build123d/README.md) reconstructs the unsplit adapter locally from editable Python source, with STEP/STL exports, a body-only Sherman P imprint at 1.003 fit scale, aligned, unscaled handle references, and mounting-ceiling validation. The Build123d fit preparation supersedes its earlier full-scan zero-clearance imprint; other CAD systems retain their documented state. Dependencies are installed in an external Python environment.

The [SolidCraft project](SolidCraft/README.md) now contains a native reconstruction: unsplit imprinted master, dependent two-piece printing variant, and five connector recesses. Read its [build results](SolidCraft/BUILD-RESULTS.md) for verification and the small cutter approximation. Exact Onshape parity has not been established.

The separate **Latch** and **SaddleBagMount** are now extracted too: see [accessory build sequences](docs/ACCESSORY-PARTS.md) and the independent millimeter recipes under `cad-rebuild/accessories/`. The latch is now rebuilt as a separate editable solid in [Build123d](Build123d/README.md#separate-latch); the saddlebag mount remains extracted only. SolidCraft has its separately documented latch implementation.

1. Read [CAD rebuild guide](docs/CAD-REBUILD.md) for the final scope, feature sequence, coordinate rules, and corrections.
2. Use [portable recipe](cad-rebuild/recipe.json) for millimeter geometry, exact selected profile loops, draft datums, and all five connector instances.
3. Consult [Fusion timeline](docs/FUSION-TIMELINE.md), [sketch catalog](docs/SKETCH-CATALOG.md), and [feature recipe](docs/FEATURE-RECIPE.md) for individual markers and dimensions.
4. Read [porting and validation checklist](docs/PORTING-AND-VALIDATION.md) before implementing in another CAD application.

## Final accepted design

- **Master:** one unsplit adapter solid, with small bolt through-holes, larger downward screwdriver-access recesses, retained mounting ceilings, and the aligned Sherman P wheel-top imprint.
- **Child:** an associative copy of the finished master, split into two solids for smaller printers, with five connector recesses, each 8 mm deep.
- **No fillets.** The user explicitly cancelled them and requested conservative Onshape API usage.
- The child contains connector cutouts, not separate loose connector inserts. The original Fusion `Gap = -0.2 mm` insert details were recorded but not implemented.

[Onshape master](https://cad.onshape.com/documents/b1a1f737761c2581236d5ec3/w/eb902961c90530f7f212e211/e/69186d95d4c9dc45ec42f803) · [Onshape split child](https://cad.onshape.com/documents/b1a1f737761c2581236d5ec3/w/eb902961c90530f7f212e211/e/c9c1cb2f1b6e54ba33df5e8a)

The Onshape document is public, as explicitly authorized for the account's free-plan restriction.

## What is saved

| Material | Location |
|---|---|
| All 200 Fusion timeline entries and user parameter | [fusion-timeline-and-user-parameters.json](fusion-timeline-and-user-parameters.json) |
| 18 sketches, originally 233 curves, dimensions and frames | [fusion-adapter-extraction.json](fusion-adapter-extraction.json) |
| Exact loops for 37 selected profiles across 20 source extrusions, plus draft datums | [fusion-selected-profile-loops.json](fusion-selected-profile-loops.json) |
| Original readable extrusion definitions | [fusion-adapter-extrusions.json](fusion-adapter-extrusions.json) |
| 149 original model parameters and expressions | [fusion-adapter-parameters.json](fusion-adapter-parameters.json) |
| Exact connector profiles and two mirror planes | [fusion-connector-source.json](fusion-connector-source.json) |
| Millimeter recipe for another CAD engine | [cad-rebuild/recipe.json](cad-rebuild/recipe.json) |
| Final Onshape IDs and validation | [cad-rebuild/onshape-current-manifest.json](cad-rebuild/onshape-current-manifest.json) |
| Complete custom Onshape FeatureScript source | [cad-rebuild/onshape-feature-studio.fs](cad-rebuild/onshape-feature-studio.fs) |
| Original scan and correctly aligned millimeter scan | [original STL](Sherman_P_Flush_Screen_Fusion_Default.stl), [aligned STL](Sherman_P_Scan_Aligned_To_Adapter_mm.stl) |
| Scan transform, closed-mesh checks and final Boolean state | [wheel-scan-alignment.json](wheel-scan-alignment.json), [wheel-imprint-state.json](wheel-imprint-state.json) |
| Final underside view | [wheel-imprint-underside.png](wheel-imprint-underside.png) |

Raw Fusion lengths are centimeters and angles are radians. **The portable recipe uses millimeters and degrees.** Do not mix these files without converting units.

## Regenerate the reference tables locally

With Node.js available:

```powershell
node scripts/generate-cad-reference.mjs
node scripts/validate-cad-reference.mjs
```

The first command regenerates the portable recipe, catalogs, manifest and current handoff from saved files. The second checks record counts, units, coordinate frames, profile references, connector directions and local documentation links. Neither makes CAD or network calls. [prepare-wheel-scan.mjs](prepare-wheel-scan.mjs) reproduces the aligned STL locally. [upload-wheel-scan.mjs](upload-wheel-scan.mjs) is a historical live upload helper; do not run it as part of documentation regeneration.

`AdapterBody.3mf` was already present in this workspace before the reconstruction. It was not used as the authoritative native-feature source and is not an export of the final imprinted Onshape model.

The old incremental notes are preserved under [docs/history](docs/history/BUILD-SEQUENCE-session-log.md). They contain superseded instructions and are not the current build specification. Likewise, early `onshape-build-state.json` and `onshape-current-sketch-ids.json` are historical; use the current manifest.

This is a documented geometric reconstruction, not a complete export of Fusion's constraint solver. SolidCraft validation and target adaptations are recorded in its build results; a Zoo implementation has not been made.
