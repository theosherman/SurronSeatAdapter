# Single-file Latch Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task in the main session. Only the main session may mutate the desktop CAD document. Steps use checkboxes for tracking.

**Goal:** Deliver a visible, editable, separately printable latch inside the existing working SolidCraft file.

**Architecture:** Add a native Latch sibling component to `SolidCraft/models/seat-adapter.sc`; retain the current master and printing history in place. Reference the existing dovetail sketch within that document. Checkpoints and disposable validation copies do not become additional authoritative design files.

**Tech Stack:** Desktop-connected SolidCraft MCP, native parametric features, Node scripts and existing measured-geometry validators.

**Spec:** `docs/superpowers/specs/2026-11-12-single-file-latch-design.md`.

## Global constraints

- This supersedes both modular-file implementation plans. Do not rerun extraction, linked-master migration or printing reconnection.
- Read project CAD instructions and source recipe before geometry changes. Inspect the live document and preserve unsaved edits before opening/replacing anything.
- One authoritative native design: `SolidCraft/models/seat-adapter.sc`. Separate component and solid for Latch; no union with adapter.
- Preserve all existing adapter/printing geometry, placements, scan imprint and no-fillets decisions. No Fusion or Onshape mutations.
- Use exact recipe-selected analytic loops and explicit target bodies; do not extrude every region or substitute faceted arcs.
- Strict kernel validation stays enabled. Missing evidence fails acceptance; never describe an intermediate blank as the finished latch.
- Save verified visible milestones, make local commits, and never push without authorization.

## Review focus

1. Wrong live document or unsaved user edits: capture current path, dirty state and recovery checkpoint before construction (Task 1).
2. Incorrect oblique cap or selected regions: verify intermediate volumes and exact limiting planes (Tasks 1–2).
3. Accidental adapter cuts or duplicate printable references: explicit Latch targets and before/after body-role checks (Tasks 2–3).
4. Static dovetail copy or reversed clearance: changed/restored width and signed-clearance experiments (Tasks 2–3).
5. Cached success that fails on reopen or contaminated export: fresh rebuild and Latch-only STEP/STL checks (Task 3).

### Task 1: Put a visible native latch blank in the working UI

**Files:** Modify `SolidCraft/models/seat-adapter.sc`; create `SolidCraft/scripts/build-single-file-latch.mjs` and `SolidCraft/logs/single-file-latch/baseline.json`, `blank.json`; reuse `SolidCraft/scripts/modular-cad.mjs` only for command transport if useful.

**Interfaces:** Builder consumes the current saved native document and accessory recipe; outputs named native Latch features and stage measurements. It must refuse an existing Latch rather than duplicate a partial build.

- [ ] Inspect desktop path, dirty state, component tree, feature health and measured bodies. Save current user work and preserve a recovery copy before construction; capture fresh baseline, not just historical logs.
- [ ] Discover current sketch/extrusion/split/component command contracts and install the recipe's exact frames and selected loops in the builder. Keep build operations staged, with rollback boundaries and explicit targets.
- [ ] Add Latch at identity placement. Create the selected SideSketch regions with analytic R15/R5 arcs. Extrude in +X beyond the recipe's side plane and trim to that exact oblique plane. Choose the retained half by recipe geometry, not arbitrary split ordering.
- [ ] Measure source stage 102: one closed half, volume 161420.26040408312 mm³ within 0.01%. Investigate a discrepancy before continuing.
- [ ] Mirror about world YZ and join only the latch halves. Measure source stage 103: one closed Latch, volume 322840.5208081663 mm³ within 0.01%.
- [ ] Show Latch, hide obstructing references as needed, frame it in the desktop viewport, save the file and capture a screenshot plus measured evidence. Verify adapter/printing baseline unchanged. Commit this visible-blank milestone.

### Task 2: Complete the top shape, dependent slot and clearance

**Files:** Extend `SolidCraft/scripts/build-single-file-latch.mjs`; modify the same native design; create `SolidCraft/logs/single-file-latch/geometry.json` and `SolidCraft/scripts/validate-single-file-latch.mjs`.

**Interfaces:** Consumes Task 1's native blank and source sketch resolved by name/ownership, not stale numeric IDs. Produces one final Latch and per-stage measurements, selected-face records and dependency metadata.

- [ ] Add acceptance assertions for stage volumes, final bounds, closedness, three offset faces, no latch fillet and unchanged existing body roles. Run against incomplete Task 1 evidence and confirm it rejects the blank as unfinished.
- [ ] Intersect only Latch with the three exact selected TopCutSketch regions through both directions. Verify stage 104 volume 238753.4027 mm³ within 0.01%.
- [ ] Resolve existing `M06_RearDovetailProfile`. Use it directly for the mating-slot tool; if cross-component use is unsupported, use native linked projection in Latch and verify the resulting frame/link. Do not trace an independent copy.
- [ ] Cut only Latch using the recipe direction and exact Y=-263.445982162752 end plane. Use an overlong tool plus planar trim if needed to preserve the cap. Consume/hide helpers and exclude them from manufactured outputs. Verify stage 105 volume 232662.8943 mm³ within 0.01%.
- [ ] Define `latchClearance=0.2 mm`. Resolve the three recipe mating faces using plane, point and area evidence; reject ambiguous selections. Apply signed `-latchClearance` offsets. Verify final volume 230819.7862464548 mm³ within 0.01% and all six bounds within 0.05 mm of the spec.
- [ ] In a disposable native copy, compare zero and 0.2 mm clearance: exactly the intended mating planes move with the material-removing sign. Restore nominal; record face distances and material change.
- [ ] Show and save the completed latch in the main UI. Run geometry acceptance with fresh evidence and verify adapter baseline unchanged. Commit the finished nominal geometry.

### Task 3: Prove updates and deliver printable files

**Files:** Extend `SolidCraft/scripts/validate-single-file-latch.mjs`; create `SolidCraft/logs/single-file-latch/integration.json`, `SolidCraft/exports/latch.step`, `SolidCraft/exports/latch.stl`; update `SolidCraft/BUILD-RESULTS.md` and `SolidCraft/README.md` with actual verified results and authoritative path.

**Interfaces:** Consumes final nominal single-file design; produces fresh rebuild/dependency/export evidence and a saved, usable desktop document.

- [ ] In a disposable copy, temporarily change the shared dovetail top half-width 10→10.25 mm symmetrically, preserving original sketch definition for restoration. Rebuild and measure both manufactured dovetail and latch-slot width changes; clearance remains 0.2 mm. Restore 10 mm and prove baseline latch/master/printing geometry returns. Never accept unchanged latch geometry as successful dependency propagation.
- [ ] Save and reopen a validation copy without relying on cached geometry. Confirm healthy features, one unsplit master, two printing halves, one closed Latch, original placements and no extra manufactured helpers. Compare existing bodies with Task 1 baseline using spec tolerances.
- [ ] Reuse the existing R20 and mounting-ceiling checks against fresh rebuilt output; confirm all five connector features remain child-only and unchanged. Preserve current print-child relationship without replaying or migrating its history.
- [ ] Export explicitly the Latch solid alone to STEP and STL. Reimport/check exports in an isolated document for one closed body, expected bounds and geometry; STL volume tolerance accounts for recorded tessellation quality. Leave references and adapter bodies out of these exports.
- [ ] Return to the saved authoritative file, show the finished Latch clearly, apply browser presentation order where supported, and record a final screenshot and measured state. Document same-document rebuild behavior and physical-fit limitation.
- [ ] Run geometry and integration validators; commit only verified results. Report the native design and printable export paths, any actual limitations, and the finished UI state.

## Failure handling

Keep the last healthy visible milestone if a later operation fails. Record the specific failing feature and measured discrepancy, investigate that operation in an isolated copy, and retain the original adapter unchanged. Do not restart modular migration or silently replace native dependencies with static imports. This plan is complete only when Task 3 passes; a visible blank is useful progress, not final acceptance.
