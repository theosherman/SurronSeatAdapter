# Restore print-bed planes implementation plan

> Execute inline with executing-plans; user approved exact preview and requested implementation.

**Goal:** Reapply both original rear printing planes through the raised front.
**Architecture:** Extract unique left/right native rear side faces after front reconstruction; retain their inward half-spaces before stationary scan subtraction. Record an explicit native build stage. Preserve zero offset, placement, bore, source recipe and accessories.
**Tech stack:** build123d/OCCT, Python unittest, STEP/STL.
**Spec:** docs/superpowers/specs/2026-11-15-print-bed-plane-trim-preview.md (approved in conversation).

## Review focus
Exact existing plane points/normals, no protruding vertices, same result as approved preview, one valid solid, bore and screen retained, mounting ceiling and editable AirTag regression.

## Task 1
- [x] Add geometry tests against the approved plane report and observe existing build fail.
- [x] Implement native symmetric plane trimming in a focused module and invoke before imprint.
- [x] Rebuild pre-imprint and final exports; run full suite, ceiling and export/parameter checks.
- [x] Regenerate manufacturing previews; compare with approved preview; refresh viewer.
- [x] Review, document, and commit locally on design/restore-print-bed-planes. Preserve checkpoint/raised-front-clip.

## Execution record
- Both new tests failed on the untrimmed build: maximum protrusion 4.547544 mm and no coplanar front contact patches. Both pass after native trim.
- Full suite: 23 tests pass in 28.390 s. All 12 independent mesh mounting checks pass.
- Reopened manufacturing STEP is one valid solid, volume 1485451.787234 mm³. Difference from approved preview is -0.0000577 mm³; maximum signed protrusion is approximately 2.1e-11 mm on either side.
- Independent review found no actionable issues: Boolean differences with the approved preview are zero in both directions, and a full bore cylinder has zero material intrusion.
- Manufacturing detail and overview previews regenerated. Local viewer refresh submitted using rebuilt exports. Pre-trim checkpoint branch still points to 6021f13.

STEP/STL reopening and AirTag edit validation pass: STL volume 1485453.993614 mm³, STEP volume 1485451.787234 mm³; the 0.1 mm AirTag edit removes 102.429954 mm³ versus expected 102.429508 mm³.
