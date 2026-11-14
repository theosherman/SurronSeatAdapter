# SurronSeatAdapter

This folder records the reconstruction of the Fusion design **Surron Seat Adapter v3 v2** in Onshape, including the later wheel-scan imprint and a linked printing variant. It is intended to let a future agent rebuild the accepted geometry in another CAD system, including SolidCraft or Zoo Design Studio.

## Start here

The [SolidCraft project](SolidCraft/README.md) now contains a native reconstruction: unsplit imprinted master, dependent two-piece printing variant, and five connector recesses. Read its [build results](SolidCraft/BUILD-RESULTS.md) for verification and the small cutter approximation. Exact Onshape parity has not been established.

The separate **Latch** and **SaddleBagMount** are now extracted too: see [accessory build sequences](docs/ACCESSORY-PARTS.md) and the independent millimeter recipes under `cad-rebuild/accessories/`. They remain separate parts and have not been built in the destination CAD systems.

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
