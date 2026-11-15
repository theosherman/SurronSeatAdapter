# Seat-support shoulders and lowered screen walls

User scope: image one red marks extend both rear shoulder edges into the narrow
body, providing a continuous load path from seat-support tabs. Image two requests
screen side walls 8 mm lower, black-circled step flowing into the existing front
ramp, and inspection of the green-circled rounded-cutout junction. No fillets or
repeat of the old rounded cut. Retain approved suspension routing, trunk walls,
clip grip/axis, accessories, and scan preparation.

Implementation inline: adapt selected SeatHangerSketch rear return at source79
so the outer rear shoulder plane continues to X=22 rather than folding forward.
Use native sketches and original 45-degree underside draft. Add an explicit 8 mm
screen-top reduction parameter, trim the lifted clip wings across the ramp width,
and cap the screen region to the lower parallel plane or uphill ramp, whichever
is higher. The source portable recipe remains unchanged.

- [x] Write native material checks for both rear shoulder continuations and 8 mm
  screen-top height/absence of an upright at the wing-to-rail junction; run red.
- [x] Implement source-profile adaptation, lower the screen walls, and eliminate
  the full-width front step using native ramp/rail planes.
- [x] Inspect the rounded-cutout junction and actual upper/underside geometry.
- [x] Rebuild exports; run full suite, mounting, export and parameter checks.
- [x] Independent review, document actual results, commit, refresh OCP viewer.

Interpretation: red marks continue the existing rear shoulder plane to the body's
side; they do not move the seat-contact tabs or add wheel fit clearance. Native
geometry/material checks verify the load path, not certified load capacity.


Verification: material-continuity test failed on the old shoulder return; all
three initial lowering/step tests failed on the old screen. The implemented
profile now has two native rear shoulder planes of 529.281 mm² spanning 29 mm,
with their original normals. The measured parallel top plane is 8 mm lower.
Both 3.418 mm² extrusion ribbons at the rounded junction are absent in the final
STEP. Final suite: 33/33 passed; 12/12 ceiling checks passed; source references,
STEP/STL validity, scan cutter and AirTag edit passed. Independent review found
no blocking defect; stale comments were updated. Geometry is reviewed for
material continuity, not a certified printed load rating.
