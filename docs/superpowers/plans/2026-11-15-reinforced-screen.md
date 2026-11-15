# Reinforced screen sides implementation plan

> Execute inline; user approved continuous-screen-ramp-preview.png and requested implementation.

**Goal:** Raise screen-side tops parallel to the underside, retaining an uninterrupted central incline into the clip.
**Architecture:** Native upward additions over the current top faces, limited by the plane through the rear screen edge parallel to the underside. Exclude the aperture and all central material above the original 55 degree ramp. Apply after front redesign, before print-plane restoration and stationary scan subtraction.
**Spec:** docs/superpowers/specs/2026-11-15-continuous-screen-ramp-preview.md, with the parallel-screen correction.
**Constraints:** Preserve underside, screen opening, clip bore/axis, rear/latch, printing planes, no fillets, body-only imprint, zero new clearance, current design branch and earlier checkpoint.

- [x] Add acceptance checks and observe missing reinforcement fail.
- [x] Implement focused screen_surround module; update earlier retained-region regression for this explicitly changed region.
- [x] Rebuild STEP/STL and previews; compare to approved prototype.
- [x] Run full tests, mounting ceilings, export/AirTag edit validation and independent review.
- [x] Refresh viewer, document evidence, commit locally.

## Verification record
- New acceptance tests failed on old geometry for missing raised-side material and incorrect top-plane height; all three pass after implementation.
- Full suite: 26 tests pass in 31.238 s. All 12 independent mesh mounting-ceiling checks pass.
- Final native in-memory volume: 1506519.135783 mm³; reopened STEP: 1506519.136130 mm³. Approved prototype differs by only 0.0000078 mm³.
- Independent review found zero Boolean difference from the approved prototype, zero missing original material, and zero bore intrusion. Original printing-plane residuals stay below 2.1e-11 mm. Continuous original ramp remains one face.
- Inspection and full-body previews now render actual manufacturing exports. Original preview/prototype files are retained as historical approval evidence.

Export reopening and AirTag edit checks pass: STEP/STL each one valid solid; STL volume 1506521.372764 mm³. AirTag +0.1 mm depth removes 102.429855 mm³ (expected 102.429508). Viewer refresh submitted. Saved locally on design/restore-print-bed-planes; prior checkpoint branch preserved.
