# Sherman P suspension outline implementation plan

> Execute inline using the executing-plans workflow; the user approved the final 10 mm preview and requested implementation.

Goal: implement the approved mirrored bottom outline in native Build123d geometry.

Design: preserve line 13 angle and extend to vertical line 16; remove 14/15. Translate line 17 forward 10 mm without rotation. Extend the screen opening forward 10 mm at line 19. Mirror all changes. The approved fixture is `Build123d/exports/bottom-outline-proposed-lines.json`; labels refer to the retained original numbering.

Architecture: adapt the selected BottomSketch loop locally before the initial extrusion. Keep the portable recipe and default source-profile inspection unchanged. Rebuild all dependent native features and body-only scaled-scan subtraction. No imported preview geometry drives manufacture.

Constraints: unsplit master; separate latch/accessories; no fillets; existing placement, wheel preparation and fit scale unchanged. Do not push.

Review focus: profile endpoints meet, bilateral symmetry, screen ramp continuity, mounting ceilings, one valid final solid. A larger opening may change the native face regions used by front reinforcement; inspect actual planes before updating selectors.

- [x] Add acceptance checks comparing the native base to the approved preview and watch them fail.
- [x] Implement a named local profile adaptation and connect it to the initial extrusion; keep source-profile comparisons available.
- [x] Inspect downstream native face construction and preserve the approved clip axis and printing planes.
- [x] Rebuild pre-imprint and finished STEP/STL; run all tests, export/parameter and mounting-ceiling checks.
- [x] Render the implemented result, document evidence, review the change, and commit verified milestones.


Execution evidence: initial native-blank acceptance failed with 952696.118 mm³
of excess material; after adaptation the approved-blank and M05 Boolean checks
pass with residuals below 0.001 mm³. Enlarging the screen opening required moving
the existing ramp along the same sloped planes and shortening the local gusset.
The clip bore is checked against a full 30.2 mm cylinder. A review caught a
ShapeList normalization omission in the independent test fixture; it was fixed.
Manufacturing STEP reopening differs by +0.010985 mm³, so native parameter-edit
volume and STEP round-trip error are now independently validated rather than
mixing them. No source recipe, reference scan, or accessory was modified.

Final verification: 27/27 tests pass, 12/12 mesh ceiling checks pass, portable
reference validation passes, and export/parameter validation reports ok=true.
Fresh review found no important manufacturing issues; the test fixture's empty
bore intersection is normalized as zero volume. Implemented inspection images
were rendered from manufacturing exports.
