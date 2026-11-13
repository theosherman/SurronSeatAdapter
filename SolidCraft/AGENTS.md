# SolidCraft project instructions

Read the parent AGENTS.md, this folder's README, `../docs/CAD-REBUILD.md`, and `inputs/recipe.json` before modeling.

Save SolidCraft-specific native models, scripts, logs, screenshots and exports under this folder. Do not modify the accepted Onshape models while working on this port.

Use the desktop-connected `solidcraft` MCP server on `127.0.0.1:7878`. Inspect before modifying any open design. Do not reset or replace an existing unsaved model without first preserving it.

Required geometry: one unsplit master, corrected small bolt holes and downward access cavities with mounting ceilings, zero-clearance aligned wheel imprint, and a linked/dependent child split into two bodies with five 8 mm connector recesses. No fillets or separate loose connector inserts.

Read the installed server's `skill_reference` modeling and checking/porting material and discover current command contracts instead of assuming another CAD system's syntax. Reuse local source geometry, batch coherent steps, and verify body counts, dimensions and material placement. Neither a successful tool response nor a screenshot alone establishes that the full geometry is correct.

The current implementation is `models/seat-adapter.sc`, reproduced by `scripts/seat-adapter-build.json`. Read `BUILD-RESULTS.md` and `logs/build-validation.json` before changing it. Parent/child propagation, closed solids, mesh subtraction, and mounting ceilings have been tested. The port is not exact Onshape parity; preserve and disclose the recorded 256-gon side-cutter approximation and other adaptations. `models/experiments` and diagnostic scripts contain failed or superseded attempts.
