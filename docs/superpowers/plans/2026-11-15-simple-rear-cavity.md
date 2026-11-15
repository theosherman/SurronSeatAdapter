# Simple rear cavity redesign

User direction: replace the rejected face-patching implementation with a redrawn cavity sketch, leave the narrow middle as solid CAD material for slicer infill, provide a continuous thick rear wall, and retain only the original top dovetail. Simplicity is a project-wide priority.

Use one symmetric eight-line polygon on the existing BodyCutSketch plane, one existing-direction 15-degree drafted cut, and the original roof offset. Preserve the mounting cuts, original roof plane, and approved wheel preparation. Remove the rejected region translation, partial-face wall additions, and multiple-face latch extensions rather than layering another correction over them.

A decision is pending on the outer interface: original wall/latch/dovetail is the simpler option; retaining the earlier 10 mm inward shift requires additional original sketch changes to the matching latch and dovetail. Do not silently choose that tradeoff.

Steps:
- [x] Verify a test fails for the current narrow-middle cavity and incomplete wall.
- [x] Redraw an editable octagonal cavity profile in the original sketch frame, entirely behind the narrow middle, with a shorter rear reach for the thicker wall.
- [ ] Remove the rejected patch operations. Keep the outer-interface decision explicit.
- [ ] Render actual 3D geometry for review; verify the complete wall and a single original dovetail, not just solid validity.
- [ ] Run native, mounting-access and export checks appropriate to the final selected interface; commit a verified milestone locally.

Draft milestone: the old implemented body fails the narrow-middle material probe at Y=20 mm, Z=25 mm. The new independent native sketch/cutter has one eight-edge loop with no holes; its three checks pass for validity, exclusion of the entire middle Y<75 mm over body heights, and retained rear-wall sample positions. It is not yet wired into the master or exported assembly. Outer-interface choice remains pending with the user; do not infer an answer from elapsed time.
