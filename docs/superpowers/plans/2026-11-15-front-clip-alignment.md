# Front clip alignment implementation plan

> Execute inline using superpowers:executing-plans. User approved preview and execution.

**Goal:** Place the clip vertically under the front handle using the approved Y shift.
**Architecture:** Share a placement vector in coordinates.py; translate the finished
adapter before imprint and the separate finished latch before export/display.
**Tech stack:** Python/build123d, OCCT, unittest, STEP/STL.
**Spec:** docs/superpowers/specs/2026-11-15-front-clip-alignment-design.md

## Constraints and review focus

Preserve Z/X, separate latch, stationary wheel references, 1.003 body-only fit scale,
mounting ceilings, no fillets. Rebuild the imprint; do not translate an old imprint.
Early manufacturing checkpoints stay in the recipe frame; completed M20 and latch
placements are documented separately. Do not push.

## Task 1: Place, rebuild and verify

- [x] Add a geometric regression for the clip arc center and observe it fail.
- [x] Add shared placement to completed adapter and latch, before imprint/export.
- [x] Adjust mounting probes and latch source-datum comparisons for placement.
- [x] Regenerate pre-imprint, final adapter, separate latch and preview exports.
- [x] Run full unittest suite and reopen-export/parameter validation.
- [x] Document measurements, review diff, and commit locally.

Verification: clip-center regression failed by 2.426787 mm before placement and
passed afterward. Source checkpoint volumes are preserved. Full 15-test suite,
STEP/STL reopening and AirTag edit validator pass; final master volume is
1473734.600153 mm³ after STEP reopening.

Review found the JavaScript mesh validator still used unplaced source probes;
its red run failed both front ledges. Reading the same adapter-placement.json
as Python corrected all 12 checks with two-ray agreement. The shared JSON is the
placement authority; no duplication between engine and mesh validator.
