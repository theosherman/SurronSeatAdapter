# Simple rear cavity redesign

User direction: replace the rejected face-patching implementation with a redrawn cavity sketch, leave the narrow middle as solid CAD material for slicer infill, provide a continuous thick rear wall, and retain only the original top dovetail. Simplicity is a project-wide priority.

Use one symmetric eight-line polygon on the existing BodyCutSketch plane, one existing-direction 15-degree drafted cut, and the original roof offset. Preserve the mounting cuts, original roof plane, and approved wheel preparation. Remove the rejected region translation, partial-face wall additions, and multiple-face latch extensions rather than layering another correction over them.

Decision: the user explicitly selected the original outer wall/latch interface. Cancel the earlier 10 mm outer-wall movement and latch extension. Restore original interface geometry; change only the cavity sketch.

Steps:
- [x] Verify a test fails for the current narrow-middle cavity and incomplete wall.
- [x] Redraw an editable octagonal cavity profile in the original sketch frame, entirely behind the narrow middle, with a shorter rear reach for the thicker wall.
- [x] Remove the rejected patch operations. User selected original interface; exact native fixture comparison passes.
- [x] Render actual 3D geometry for review; verify the complete wall and a single original dovetail, not just solid validity.
- [x] Run native, mounting-access and export checks appropriate to the final selected interface; commit a verified milestone locally.

Draft milestone: the old implemented body fails the narrow-middle material probe at Y=20 mm, Z=25 mm. The new independent native sketch/cutter has one eight-edge loop with no holes; its three checks pass for validity, exclusion of the entire middle Y<75 mm over body heights, and retained rear-wall sample positions. It is not yet wired into the master or exported assembly. The user subsequently chose the original interface, allowing simple sketch integration.

Integrated milestone: source adapter/latch/viewer restored from8746492, replacing only M19 with the new profile/tool. Deleted the rejected rear_cavity.py and all region/face patch calls and mode switches. Five native integration checks pass, including exact original outer interface/dovetail symmetry and full rear screwdriver paths; all twelve final mesh ceiling probes pass. New profile is independent of the removed side-wall envelope guard. Narrow-middle tests now require material, reflecting the user's explicit infill direction.

Final: 41 tests passed in46.755seconds;12meshceiling checks passed; STEP/STL/parameter validation passed; independent review no blockers. Actual exported original-interface XOR0mm³, adapter/latch overlap0mm³. Final adapter1,667,774.540mm³; original latch230,819.786mm³. Renderer provides an unobstructed finished underside and a separate pre-imprint shape view. No push or merge authorized/performed.
