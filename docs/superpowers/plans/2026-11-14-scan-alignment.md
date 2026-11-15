# Scan alignment implementation plan

> Execute inline using superpowers:executing-plans.

**Goal:** Apply the approved rigid alignment to the complete scan before slicing.
**Architecture:** Shared prepare_parts performs alignment, slices, then scales body only.
**Tech stack:** Python/build123d, OCCT, existing STEP/STL validators.
**Spec:** docs/superpowers/specs/2026-11-14-scan-alignment-design.md

## Constraints and review focus

Exact approved angle/translation; no additional clearance or fillets. Keep handles
unscaled after whole-scan movement, use world-Y cut planes, preserve mounting
ceilings, update viewer and standalone preparation consistently. Do not push.

## Task 1: Align, rebuild, validate

- [x] Add regression comparing prepared partition against independently transformed
  synthetic scan; observe failure before implementation.
- [x] Add shared rigid alignment before splits; update preparation report and viewer wording.
- [x] Regenerate prepared scan and master exports.
- [x] Run full unittest suite, export validator, mounting-ceiling mesh probes.
- [x] Update documentation with actual measurements, review diff, commit locally.

Implementation finding: original self-intersecting screen facets required the
vertex-preserving connectivity recipe in `Build123d/scan-screen-patch.json`.
Temporary native volume-reconstruction experiments were removed.
