# Current build sequence and handoff

This is the current handoff for the completed Fusion-to-Onshape rebuild. The old incremental notes are preserved at [docs/history/BUILD-SEQUENCE-session-log.md](docs/history/BUILD-SEQUENCE-session-log.md). They contain superseded instructions and stale IDs.

## Read first

1. [README.md](README.md): final model structure and file map.
2. [CAD rebuild guide](docs/CAD-REBUILD.md): source geometry, corrections and datums.
3. [Portable recipe](cad-rebuild/recipe.json): millimeter geometry and selected loops for another CAD engine.
4. [Porting and validation](docs/PORTING-AND-VALIDATION.md): implementation and verification checklist.
5. [Current manifest](cad-rebuild/onshape-current-manifest.json): saved final IDs and measured state.

## Accepted sequence

1. Rebuild the unsplit master using the bottom, side and rear profiles, signed extrusions, intersections, mirrors and unions.
2. Add dovetails, drafted hangers, handle mount, relief cuts, underside tapered cavity and AirTag recess.
3. Preserve four 7 mm through-holes and four larger 17 mm downward screwdriver-access recesses with retained mounting ceilings. Apply the final front ceiling correction, not the earlier reversed offset.
4. Align the supplied Sherman P scan using the saved exact transform, check units, and subtract the zero-clearance underside imprint from the master.
5. Reference the completed master associatively in a separate printing child. Keep the master unsplit.
6. Split the child into two solids on the plane from the first Fusion SplitBodySketch line.
7. Add five 8 mm-deep connector recesses to the child: one top and four side locations using the saved mirror planes.
8. Verify one master solid, two child solids, retained screw ceilings, open small holes and access cavities, and healthy inherited/connector features.

No fillets or separate loose inserts are included. The old Veteran Sherman L cut is excluded; the later explicitly authorized Sherman P scan imprint is included. The source Gap parameter is recorded, but its insert offsets were not applied.

## Current status

The sequence above was completed and checked in Onshape. The user visually reviewed the close reconstruction and requested the documented corrections. The complete Fusion constraint graph and an exhaustive whole-assembly equality comparison were not captured.

Saved evidence includes all 200 source timeline markers, 18 sketches, 37 exact selected profiles, 149 model parameters, the Gap user parameter, exact scan placement, source scripts, final FeatureScript and validation. A SolidCraft or Zoo Design Studio implementation has not been built or tested.

Conserve future Onshape API calls. Run node scripts/generate-cad-reference.mjs to regenerate local tables and recipe files. Do not automatically replay live upload scripts or historical transient IDs.
