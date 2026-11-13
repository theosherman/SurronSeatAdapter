# Component hierarchy

The user authorized this organization change after requesting a saved Git recovery point. The open document was saved and committed as **68993b6** before any component changes. That commit is the full pre-reorganization state, including the native model. Older separate checkpoint tabs are not linked and were not reorganized.

```text
seat-adapter (container, no bodies or sketches)
├── AdapterBody
│   ├── AdapterBodyMaster
│   ├── 20 master sketches
│   └── Master features, scan conversion tool and wheel-imprint subtraction
├── AdapterBodySplit
│   ├── AdapterBodyFront
│   ├── AdapterBodyRear
│   └── Split, five connector sketches and five cuts
└── WheelScanReference
    └── Hidden aligned millimeter display mesh
```

The master-to-child copy is a shared root-level relationship feature. The child stays dependent on the master; their sibling positions do not imply independent geometry.

## Why the scan has a display mesh

SolidCraft refuses to move the master's history on its own: the imprint Boolean would use bodies split between components. Moving the original scan import and conversion history together with the master resolves that ownership constraint. The consumed Boolean tool is therefore part of the master history. A separate import of the identical aligned STL supplies the hidden `WheelScanReference` display mesh. It is reference-only, is not subtracted again, and adds no manufactured part.

All existing sketch/feature names and chronological order are retained. Component placements are identity transforms; no manufactured body is moved in world coordinates. No fillets, new clearances or geometry edits are introduced.

## Validation and replay

The before/after manufactured-body measurements match exactly: volume, surface area, center of mass, face count and bounding box. The AirTag-pocket parameter experiment is repeated at 8.6 mm and restored to 8.5 mm, checking the master and printing child together. Evidence is in `logs/reorganize-baseline.json`, `logs/reorganize-verification.json` and `logs/reorganization-validation.json`.

The complete updated script was also replayed in a separate CLI process. Its three manufactured-body volumes match the original document exactly, all three are closed, and the root contains no bodies. See `logs/reorganization-replay-validation.json`. Run `node scripts/validate-reorganization.mjs` to check these saved records together.

`scripts/reorganize-components.json` applies this change to the saved original 69-feature model. Do not apply it twice to the reorganized model. The main generator scripts append that stage to `scripts/seat-adapter-build.json`, so a full rebuild produces the new hierarchy.

The earlier `logs/build-validation.json` and `logs/open-final.json` remain historical evidence of the original build; use the reorganization record for current component ownership and the added display-mesh feature. Export the three manufactured bodies by explicit names, excluding the reference mesh.
