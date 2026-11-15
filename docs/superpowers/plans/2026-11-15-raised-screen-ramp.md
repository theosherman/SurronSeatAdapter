# Raised screen ramp implementation plan

> Execute inline using superpowers:executing-plans; implementation explicitly authorized by user.

**Goal:** Implement the approved thick front ramp and remove the front dovetail.
**Architecture:** Retain source checkpoints except omitted M16; after placement, replace only the front clip region with the vertically translated analytic original, and add native planar bridge material following the screen-front incline. Subtract the stationary prepared middle body afterward. No mesh deformation in manufacturing CAD.
**Tech stack:** Python/build123d, OCCT, STEP/STL.
**Spec:** docs/superpowers/specs/2026-11-15-raised-screen-ramp-design.md

## Constraints
Preserve placement, bore, screen aperture, rear latch connection, mounting ceilings, separate accessories, no fillets, zero imprint clearance, unchanged scans.

## Review focus
Check clip axis and bore, absence of front dovetail, continuity and single solid, retained rear geometry and underside, wheel-body-only subtraction, screen-ramp slope, STEP/STL reopening.

## Task 1: Native raised clip and thick bridge
- [x] Add and run failing geometry acceptance tests for raised bore, removed dovetail, unchanged rear and underside, thickened bridge.
- [x] Implement front reconstruction in a focused module; omit M16 only from manufacturing build, preserve source recipe.
- [x] Rebuild un-imprinted and imprinted exports, inspect native feature validity and rendered result.
- [x] Update old height/material probes explicitly superseded by raised front.
- [x] Run suite, mesh ceiling check, export/parameter validation; review diff and document results.
- [x] Commit verified work locally; no push.

## Execution record
Working in current project: .git is read-only in the ordinary sandbox, so worktree creation cannot run there. Keep backups of existing exports under /tmp; request escalation only for the user-authorized local commit once verified.

### Implementation decisions and evidence
- Native construction preserves the actual upper-face footprint and its screen boundary. Continued 55° ramp merges into the source ramp as one planar face.
- Exact plane intersection locates the clip split at approximately Y=-192.95; a local lower gusset ends at Y=-199, behind the bore tangent Y=-205.2743.
- New acceptance tests observed four failures on the old build (axis, thickness, dovetail, ramp), then six passing checks including retained-region symmetric volume difference and underbody material samples.
- Initial native face selection incorrectly assumed the imprinted bottom-face centroid; diagnosed on pre-imprint faces and corrected to the unique large underside plane. Intersections return ShapeList in build123d 0.13 and are explicitly wrapped as Compounds before fusion.
- M16 omission removes approximately 6380.418 mm³. Front reconstruction adds approximately 18617.804 mm³ before imprint.
- Full build returns one valid native solid, final volume approximately 1485971.9857 mm³. Twelve independent mounting-ceiling mesh checks pass.

Final verification: 21 tests pass (25.663 s); all 12 mesh ceiling checks pass; STEP/STL reopen as one valid solid. STEP volume 1485971.986136 mm³; STL volume 1485972.973202 mm³. AirTag depth edit removes 102.429956 mm³ (expected 102.429508). Independent reviewer found no actionable issues and verified zero intersection with a full 30.2 mm bore cylinder. Generated STEP whitespace is exporter-owned; source diff whitespace check passes.

Local viewer refresh submitted using exported adapter, separate latch and three unchanged scan references. Git author identity is inherited for this commit from the existing repository history via command-local configuration; no global configuration changes.
