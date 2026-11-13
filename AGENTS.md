# Project context for future CAD work

Read `README.md`, `docs/CAD-REBUILD.md`, and `cad-rebuild/recipe.json` before changing CAD geometry. `docs/PORTING-AND-VALIDATION.md` describes validation for another CAD engine.

Additional user-requested parts: `Latch` and `SaddleBagMount` must remain separate from the adapter and from each other. Their extracted features and build sequences are in `docs/ACCESSORY-PARTS.md` and `cad-rebuild/accessories/`. Extraction does not mean they have been rebuilt in SolidCraft or Onshape.

The user initialized Git and explicitly requested check-ins at appropriate milestones. Make local commits after meaningful verified changes. Do not push to a remote without authorization. The SolidCraft reconstruction and its known limitations are documented in `SolidCraft/BUILD-RESULTS.md`.

Preserve these user decisions:

- Master `Adapter Body` is unsplit. The separate `Adapter Body Split` child inherits the completed master and is split into two solids.
- Only the child has the five 8 mm connector cutouts. No loose connector inserts were requested or created.
- No fillets: the user cancelled all fillet work.
- Conserve Onshape API calls. Prefer local preparation, batch meaningful inspections, and avoid per-edge trial loops or repeated full feature-tree reads.
- Larger screwdriver-access recesses open downward and retain the small through-hole mounting ceilings. The corrected front feature has `offsetOppositeDirection=false`; see `front-screw-ceiling-correction.json`.
- The initial exclusion of reference-asset subtraction was later superseded by explicit authorization to subtract the aligned Sherman P wheel-top scan from the master. Do not substitute the old Veteran Sherman L reference asset.
- The final imprint has zero added clearance. Do not silently add a fit allowance.
- Later reference-preparation request: Fusion must remain reference-only. The authoritative Sherman L v1 history verifies a uniform **1.003** fit scale on `Body` only, after splits at Y=190/-180 mm; both handles are excluded. See `cad-rebuild/sherman-l-preparation-verified.json`. This supersedes the guessed 1.01 interpretation. It has been inspected/documented, not yet applied to the SolidCraft subtraction. The recent P import in Fusion is experimental, not the source for the original preparation procedure.
- Public Onshape document creation was explicitly authorized. Credentials are in the OS keychain; never copy secrets into this folder or print them.

Use `cad-rebuild/onshape-current-manifest.json` for saved destination IDs. It is a dated snapshot, not a live API inventory. Old files and `docs/history` include stale IDs and superseded instructions. Do not automatically replay upload or mutation scripts.

For another CAD system, use the portable recipe's millimeter geometry and exact selected loops. Raw Fusion extracts use centimeters/radians. Preserve nonzero sketch-space Z, explicit extrusion directions, and reflected connector handedness. New target-specific implementations have not yet been written or tested.
