# Hybrid rear cavity implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans inline. Steps use checkbox syntax for tracking.

**Goal:** Implement the user-approved native 10 mm inward rear-wall move, additional 10 mm cavity-side wall, and matching separate latch.

**Architecture:** Add a native rear-web operation after the existing pre-imprint adapter features, then reapply the unchanged Sherman P body cutter. Extend the separate source-derived latch and trim its adapter-facing transition against the same adapter with the existing requested planar running clearance. Preserve access to the source latch and pre-change body for historical source checks; production defaults use the approved revision.

**Tech Stack:** Existing build123d/OCP Python environment and offline STL validation.

**Spec:** User-approved native preview and dimensions in `Build123d/exports/concepts/rear-cavity/hybrid-10-10/README.md`; user authorized implementation after preview commit `8746492`.

## Global constraints

- Both dimensions run toward negative model Y: outer wall -10 mm; inner cavity boundary -20 mm total.
- Keep the latch and adapter separate; retain original wheel-contact face and hook position.
- Preserve the approved whole-scan alignment, body-only 1.003 scale, unscaled handles and existing source exclusions.
- No fillets; preserve mounting ceilings and access; keep the authoritative portable recipe unchanged.
- Stay on `design/rear-cavity-coverage`; commit verified milestones locally; do not merge or push this branch without authorization.

## Review focus

1. Dimensions apply to actual native planes rather than a mesh deformation: assert rear face plane offsets.
2. Source geometry/clearance remains inspectable: retain explicit zero-move path and source checkpoints.
3. Latch extension must not overlap the adapter or alter contact/hook: independent material and face checks.
4. Roof and front must not shift: compare unchanged regions with pre-change native body.
5. Historical source cuts must still validate; new body and latch exports must match editable builds and retain all mounting-ceiling probes.

### Task 1: Editable native adapter and latch

Files: `Build123d/rear_cavity.py`, `Build123d/adapter.py`, `Build123d/latch.py`, `Build123d/tests/test_rear_cavity.py`, historical source-specific tests.

Interfaces: `build_master(..., rear_wall_move=10.0, rear_wall_extra=10.0)`; `build_latch(..., rear_wall_move=10.0, adapter_body=None)`; shared native operations in `rear_cavity.py` accept native shapes, not saved exports.

- [x] Add failing behavior tests for inner/outer plane offsets, retained front/roof/contact, valid solids and noninterference.
- [x] Run the new tests against current production defaults; confirm failure due to unchanged wall dimensions.
- [x] Implement rear wall operation from the approved native prototype against the fresh editable build.
- [x] Extend the latch and remove overlap; apply requested clearance outward from native planar adapter mating faces without changing wheel fit allowance.
- [x] Retain original latch source-check tests with `rear_wall_move=0`; run default production tests against updated solids.
- [x] Run new checks and full unit suite; fix genuine geometry failures before export.

### Task 2: Rebuilt deliverables and review

Files: adapter/latch STEP and STL exports, validation logs, viewer, preview PNGs and `Build123d/README.md`.

- [x] Rebuild master, pre-imprint adapter and separate latch from Python.
- [x] Reopen STEP/STL; validate editable AirTag parameter and all twelve mounting ceilings.
- [x] Render implemented geometry and display it in OCP viewer where available.
- [x] Request a fresh review of the complete change; resolve blocking findings.
- [x] Record actual validation and limitations; commit all verified changes locally.

## Execution ledger

- Baseline: clean worktree at `8746492`; native preview committed. Its STL passes all twelve mounting-ceiling probes. Historical native preview uses exact mating contact with no additional running clearance; production must restore requested 0.2 mm planar latch clearance.

- Regression found and corrected: translation moved lower access-bore material. A new test failed at rear access depth 19 mm, X offset -6 mm; reapplying original stationary bores and screwdriver cuts made all seven rear-cavity tests pass. No dimension or wheel-clearance change.

- Review ruling: global minimum separation is zero in the original source latch too. A proposed global 0.2 mm-gap assertion exceeded the selected-planar-face clearance contract. Overbroad planar rectangles would remove original wheel-contact area and were rejected. Final tests independently sample the top and both dovetail planar interiors, retain the broad rear plane offset check, and verify exact hook-region preservation below Z=-25. Exact curved/spline contacts are documented. Reviewer confirmed no remaining blocker.

- Final verification: 40 unit tests passed in 56.688 seconds; all twelve final STL mounting-ceiling checks passed; native STEP/STL and AirTag parameter validation passed. Final adapter volume 1,347,951.258 mm³; separate latch 291,282.601 mm³. No volumetric overlap. Final artifacts rendered and visually inspected; exported STEP assembly sent to OCP port3939 (viewer measurements/properties backend reported disconnected). No push or merge performed.
