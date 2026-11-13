# SolidCraft project instructions

Read the parent AGENTS.md, this folder's README, `../docs/CAD-REBUILD.md`, and `inputs/recipe.json` before modeling.

Save SolidCraft-specific native models, scripts, logs, screenshots and exports under this folder. Do not modify the accepted Onshape models while working on this port.

Use the desktop-connected `solidcraft` MCP server on `127.0.0.1:7878`. Inspect before modifying any open design. Do not reset or replace an existing unsaved model without first preserving it.

Required geometry: one unsplit master, corrected small bolt holes and downward access cavities with mounting ceilings, zero-clearance aligned wheel imprint, and a linked/dependent child split into two bodies with five 8 mm connector recesses. No fillets or separate loose connector inserts.

Read the installed server's `skill_reference` modeling and checking/porting material and discover current command contracts instead of assuming another CAD system's syntax. Reuse local source geometry, batch coherent steps, and verify body counts, dimensions and material placement. Neither a successful tool response nor a screenshot alone establishes that the full geometry is correct.

The current implementation is `models/seat-adapter.sc`, reproduced by `scripts/seat-adapter-build.json`. Read `SMOOTH-CUTS.md` and `logs/smooth-cut-validation.json` for current results; `BUILD-RESULTS.md` and `logs/build-validation.json` describe the earlier build. Parent/child propagation, closed solids, mesh subtraction, and mounting ceilings have been tested. The 256-gon side cutter has been removed: preserve the analytic cut and smooth-half mirror before the asymmetric wheel imprint. Exact Onshape parity remains unproven. `models/experiments` and diagnostic scripts contain failed or superseded attempts.

The master history now belongs to `AdapterBody`, a sibling of `AdapterBodySplit` and `WheelScanReference`; the root has no bodies or sketches. See `REORGANIZATION.md` and `logs/reorganization-validation.json` for current ownership. The hidden reference display mesh is not a manufactured part and must be excluded from part exports. The pre-reorganization recovery commit is `68993b6`. The reorganization stage is already included in the full replay; do not apply it twice.
