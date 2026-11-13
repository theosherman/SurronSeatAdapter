# Modular Latch Native-History Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Only the main session may edit the live CAD document. This amendment replaces Task 1's extraction strategy in `2026-11-12-modular-latch.md`; its Tasks 2/3 and acceptance checks still apply after the migration gate passes.

**Goal:** Finish the approved modular latch using a verified standalone copy of the current native master history, without relying on the refused `component.extract` operation.

**Architecture:** Copy the saved native container into an isolated destination, retain every AdapterBody feature and embedded asset, and move that history to the document root. Rebuild with no model cache, compare against the source, then reconnect the captured current printing branch to a linked master in an isolated assembly. Promote files only after geometry, feature health and changed/restored dependency checks pass.

**Tech Stack:** Installed SolidCraft desktop/CLI, Node.js built-ins, PowerShell/.NET ZIP support, existing desktop MCP helper, local Git. No new kernel or dependencies.

**Spec:** [Approved design and migration amendment](../specs/2026-11-12-modular-latch-design.md). Original implementation details: [original plan](2026-11-12-modular-latch.md).

## Global Constraints

- Preserve root `SeatAdapter`, source `adapter-body.sc`, latch `latch.sc`, and assembly `SeatAdapter.sc`.
- Default order: Adapter Body, Adapter Body Split, Latch, Wheel Scan Reference. Preserve internal names `AdapterBody`, `AdapterBodySplit`, `Latch`, `WheelScanReference`.
- Original `models/seat-adapter.sc` stays a recovery checkpoint. Never overwrite it during migration. Existing app-only changes must be saved and captured before reading the container.
- Full native editable master history is required. Body-only imports, stale historical generators and faceted curve substitutions remain prohibited.
- Keep imprint, unsplit master, printing split, five connector cuts, placements, analytic R20 cuts and twelve mounting-ceiling checks. No fillets, Fusion writes, Onshape calls, wheel-fit changes or SaddleBagMount work.
- `rearDovetailTopHalfWidth=10 mm`; hidden `RearDovetailInterface` is a 1 mm extrusion from the same driving sketch. `latchClearance=0.2 mm` drives three negative 0.2 mm face offsets.
- Do not relax numerical acceptance thresholds or disable kernel validation to pass migration. Errors remain errors even when their reported magnitude is small.
- One writer per native file; one live editor. CLI trials write only isolated files. Check dirty state before replacing the active desktop document.
- No push. Commit verified milestones locally.

## Evidence already collected

- Recovery commit `e56b2ce`; failed-extraction evidence and recovery tooling commit `e05c8bb`.
- Both direct extraction and the approved temporary-copy extraction refused. The exact internal cause of the second refusal remains unknown.
- **Successful feasibility probe:** current master history was copied to an isolated root-only native container; all model caches were removed; all 58 master features rebuilt successfully. Result: one closed master, volume **1507476.065203498 mm³**, 948 faces. Bounds, area and center of mass exactly matched the baseline measurements.
- The native exporter produced 59 root-only command steps, including embedded scan geometry. Its only reported omission was appearances. Independent replay also produced one closed master with exactly matching volume, bounds, COM, area, face and edge counts.
- A field audit of the throwaway PowerShell serialization found three negative-zero coordinates normalized to positive zero; other feature values were unchanged. Production container IO must treat the Node-generated document as bytes, with a serializer that explicitly retains negative zero (available `JSON.rawJSON('-0.0')`), rather than round-tripping the document through PowerShell objects. No causal connection between signed zero and the printing error has been established.
- **Unresolved integration probe:** `timeline.add` refuses the recorded body-transfer feature as referencing an unknown component despite that component existing in the seed. Using `component.move_bodies` for that transfer got as far as the recorded split, which failed `SmCone::Test #5 Bad Cone GenCurve LineScale` on a cylinder, reporting offset `2.2415403e-12`, tolerance `2e-12`. Later connector failures were consequences of the absent rear half. Neither observation establishes the internal engine cause.
- These are throwaway probes under `models/experiments/`; no probe native file is an authoritative modular part.

## Review Focus

1. Cached geometry can conceal missing history or assets: discard caches and independently replay the exported master in Task 1.
2. Stale captures or unknown native fields can silently drop app edits: capture the current file and compare the full feature/asset inventory before any transformations in Task 1.
3. Imported-body serialization may affect the printing split: isolate import/copy/transfer/split stages, preserve strict checks, and identify the first failing stage in Task 2.
4. Feature/component ID collisions or transfer substitutions can alter ownership or dependency: resolve actual component IDs and compare all captured printing definitions and placements in Task 2.
5. Nested reference solids can contaminate counts/exports or hide a stale refresh: retain the explicit-role manifest, changed/restored experiments and failure tests in original Tasks 2/3, owned by Task 4 here.

## File responsibilities

- Create `SolidCraft/scripts/native-container.ps1`: bounded ZIP entry read/write for isolated destinations; preserve embedded assets, replace `document.json`, remove `cache/` entries, refuse source overwrite and existing output.
- Create `SolidCraft/scripts/modular-native-history.mjs`: pure history partition/ownership transformation, source hashes, feature/asset inventory comparison; no CAD mutation.
- Create `SolidCraft/scripts/modular-native-history.test.mjs`: archive/history fidelity, nonidentity-placement refusal, stale-source refusal and geometry-report checks.
- Revise `SolidCraft/scripts/migrate-modular-master.mjs`: replace the refused extraction path only after the isolated route passes; automatic recovery remains mandatory.
- Extend `SolidCraft/scripts/validate-modular-latch.mjs`: fresh standalone replay, restored manufacturing geometry, dependency evidence and explicit failure checks. Existing migration/geometry stages must continue to reject absent reports.
- Keep original plan's generator, refresh, manifest, native-file, export and documentation responsibilities after the migration gate.
- Put durable evidence in `SolidCraft/logs/modular-latch/`; temporary probes and trial commands remain in `SolidCraft/models/experiments/`.

### Task 1: Make the standalone full-history migration reproducible

**Interfaces:** `partitionCurrentDocument(document, {masterComponentId})` returns `{masterDocument, printingFeatures, printingComponents, printingOccurrences, inventory}`. It consumes the freshly saved current native document, not `source-document.json` from a prior run. It preserves native IDs and geometry definitions; changes only master ownership, root name, assembly membership and inapplicable occurrence visibility.

- [x] Add failing tests: all 58 current master definitions survive unchanged after removing only their `component` ownership field, including `Object.is(value,-0)` for signed-zero coordinates; every source asset survives byte-for-byte; original input bytes remain unchanged; nonidentity/multiple master occurrences and an occupied destination are refused; absent replay measurements fail acceptance.
- [x] Run `node --test SolidCraft/scripts/modular-native-history.test.mjs`. Expected: failures for the missing transformation/guards before implementation.
- [x] Implement bounded native-container IO and the pure partition function. Discover component IDs from current names. Require identity placement for this migration; do not silently transform a differently placed future model. Preserve unrelated top-level metadata unless explicitly excluded as assembly-only; refuse unsupported dependent data rather than dropping it.
- [x] Capture fresh desktop inspection, file hash and current native definitions. Compare the file hash again before consuming or promoting output. Expected: saved, unchanged source and unambiguous AdapterBody ownership.
- [x] Rebuild the root-only copy with caches removed using CLI, export its command script, inspect `omitted`, and independently replay the script to another isolated native file.
- [x] Measure both rebuilt sources. Expected: one closed master and all 58 master entries present/healthy; volume within `max(0.001 mm³, baselineVolume*1e-7)`; bounds and COM within 0.001 mm. Reject omitted model history or missing mesh data. Confirm analytic R20 cuts and all twelve mounting ceilings from fresh output.
- [x] Run the tests and standalone report validator; commit verified transformation/tooling and evidence. Keep authoritative targets unchanged.

### Task 2: Preserve the existing printing history behind a native link

**Execution status:** Blocked at native link fidelity and split validation. The fresh link loses 0.545830799266696 mm³, exceeding the 0.15074760652034977 mm³ limit; its split also fails the kernel check. Native transfer replay itself is resolved. Task 1 is verified; Tasks 3/4 have not started. See SolidCraft/logs/modular-latch/IMPLEMENTATION-STATUS.md.

**Interfaces:** consumes Task 1's verified master and captured printing definitions; produces an isolated linked assembly plus `{baseline, after, stageReports, inheritance, adaptation}`. The final printing replay must consume the linked master, keep the existing split/connector features and retain editable definitions.

- [ ] Add failing acceptance assertions before generating reports: one closed master, two closed printing halves, identical world placements, current feature definitions retained, no feature errors/warnings, and equal changed/restored master/combined-child volume deltas within `1e-5 mm³`.
- [ ] Capture an exact baseline native printing replay without a new link. Separately inspect linked master, copied body, transferred body and split. Store bounded fresh stage measurements and command failures; compare numerical geometry before and after the first operation that fails.
- [ ] Investigate the two observed command/kernel failures using current native feature definitions and installed command contracts. Do not repeat full latch builds or unrelated model experiments. Test one cause at a time; no random perturbations, tolerance relaxation or body-only replacements.
- [ ] Resolve the transfer issue by a supported command preserving the same transfer semantics, or by preserving its native definition in an isolated container with valid component membership. Record exactly which fields/IDs change and why; compare against the captured original branch.
- [ ] Resolve the split only through a demonstrated geometry-preserving correction or an engine-supported serialization/rebuild path. If neither works, retain the recovered original and report the isolated reproducer and remaining failure. Never promote an assembly with a failed split or bypassed checks.
- [ ] On a healthy isolated assembly, change source `airtagPocketDepth` 8.5→8.6, save, refresh the linked assembly and measure master/combined-child deltas. Restore 8.5, save/refresh and verify baseline geometry returns.
- [ ] Run migration assertions with fresh smooth-cut and ceiling evidence. Expected: all original manufacturing checks and dependency restoration pass. Commit the verified linked-printing milestone.

### Task 3: Add the shared interface and promote the verified migration

**Interfaces:** consumes Task 2's healthy source/assembly. Produces the original plan's Task 1 outputs: `adapter-body.sc`, `SeatAdapter.sc`, `adapter-body-build.json`, captured printing commands, baseline report and provisional role manifest.

- [ ] Parameterize the existing `M06_RearDovetailProfile` using `rearDovetailTopHalfWidth=10 mm`, preserving all baseline coordinates and the 8 mm depth/30-degree flanks. Add hidden 1 mm `RearDovetailInterface` from that same sketch.
- [ ] Rebuild source and linked assembly; rerun the exact Task 2 geometry and inheritance checks. Expected: unchanged manufactured solids; only the hidden interface is added.
- [ ] Export/replay the root-only master again, retaining complete native history and embedded assets. Resolve qualified manufactured/reference body identities from inspections.
- [ ] Check the live desktop for dirty edits and source-hash drift. Promote only verified files to the specified targets, preserving earlier target checkpoints. Open and inspect saved `SeatAdapter.sc`; verify exact root name and original placements.
- [ ] Run migration acceptance; commit. This completes the replacement for original Task 1, not the latch project.

### Task 4: Complete original latch and integration tasks

**Interfaces:** exactly the interfaces of original Tasks 2 and 3. The established source hierarchy and captured printing branch replace only the refused extraction prerequisite.

- [ ] Execute original Task 2: selected analytic profiles, exact oblique cap, linked face projection, staged volume checks, signed clearance test, separate manufactured Latch and latch-only STEP/STL exports.
- [ ] Execute original Task 3: linked assembly, browser order, dependency-ordered refresh, width 10→10.25→10 experiment, failure/dirty-state tests, isolated full replay and restored geometry.
- [ ] Update authoritative-path/refresh documentation only after the corresponding files pass acceptance. Keep hidden interfaces/nested references out of exports and manufactured counts.
- [ ] Run bounded acceptance and final review; commit verified integration. Report actual limitations and commit IDs. No further permission round is needed for these already requested actions.

## Self-review

The design and acceptance thresholds remain unchanged. Native container migration supersedes only the refused extraction route. Task 1 proves history/asset fidelity; Task 2 owns the currently unresolved printing failure; Task 3 promotes only a verified modular master; Task 4 carries the original latch/refresh requirements. This plan does not claim the feasibility probes are production implementations.
