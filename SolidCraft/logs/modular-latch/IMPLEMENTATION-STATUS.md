# Modular latch implementation attempt — 2026-11-12

The replacement plan's Task 1 now has implemented native-container/history tooling, ten passing tests, and fresh standalone rebuild/replay validation. Task 2 isolates a linked-import fidelity failure and a subsequent printing-split kernel failure. The latch build and final integration have not started. No authoritative modular assembly or latch is claimed to exist.

Recovery checkpoint: `e56b2ce`, branch `feat/modular-latch`. The authoritative model remains `models/seat-adapter.sc`. No original native geometry, printing history, wheel imprint, Fusion document or Onshape model was modified.

## Observed failures

1. Direct `component.extract` of AdapterBody refused the printing boundary: `C02_PrintSplit, C03_top, C03_side_original, C03_side_mirrored_192, C03_side_mirrored_193 depend on the history of AdapterBody`. The batch rolled back.
2. In a saved temporary native copy, removing the captured current printing branch and shared copy left the master unchanged at **1507476.065203498 mm³**, with no feature errors. Extraction still refused: `body AdapterBodyMaster would look different without the history of AdapterBody`.
3. Removing the duplicate wheel display import in that temporary copy did not resolve the refusal. The diagnostic batch rolled back its deletion. This rules out the display import as a sufficient explanation; the internal extraction failure cause is not established.

The approved plan explicitly requires recovery if extraction cannot preserve the master history and printing branch. No body-only import or historical-generator substitute was made.

## Artifacts

- `source-document.json`: current saved native feature definitions, extracted from the native container without editing it.
- `baseline.json`: current desktop measurements and component placements before temporary edits.
- `printing-branch.json`: captured current native printing definitions, not yet replayed or rewired.
- `*-response.json`: native command evidence, including extraction errors and rollback reports.
- `migration-attempt.json`: failed extraction and fresh restored model inspection from the controller's recovery path.
- `scripts/migrate-modular-master.mjs --prepare`: captures the current saved desktop source, preserves all native master definitions/assets including signed zeros, creates an isolated root-only source, rebuilds it, independently replays its exported script, and checks feature health, analytic R20 cuts and mounting ceilings. It does not promote files or replace the live editor. This is **not a completed modular assembly migration**.
- `scripts/validate-modular-latch.mjs`: initial migration/latch acceptance assertions. Both stages intentionally reject absent acceptance reports. Geometry and integration acceptance have not passed.

## Revised route and feasibility evidence

See [the replacement migration plan](../../../docs/superpowers/plans/2026-11-12-modular-latch-native-history.md). The standalone native-history copy rebuilt all 58 master features with caches removed, and the exported 59-step script independently replayed to exactly matching master measurements. `history-feasibility.json` records the comparisons and a signed-zero serialization audit.

An isolated printing reconnection trial still failed at the recorded split: `SmCone::Test #5 Bad Cone GenCurve LineScale`, reporting offset `2.2415403e-12` against tolerance `2e-12`. The cause remains unknown; numerical thresholds were not relaxed. `printing-feasibility-failure.json` records the command and observed failure. The revised plan addresses that case before promoting any files. Physical latch fit remains untested.

## Implemented replacement-plan results

- `node --test`: ten passing tests; new behavior and review fixes were observed failing before implementation. Coverage includes signed-zero/history fidelity, embedded-asset hashes, untouched input, nonidentity/multiple placement refusal, source/snapshot/master provenance, occupied destinations, missing/changed replay measurements, explicit manufactured roles, nonempty expected history, changed component IDs, unsupported dependent fields and stale-run rejection.
- `node SolidCraft/scripts/validate-modular-latch.mjs standalone`: validates 58 healthy master features, unchanged native/replay volume/bounds/COM, two analytic R20 cylinders and twelve fresh ceiling material checks. Evidence: `native-history-validation.json`, `native-master-rebuild.json`, `native-master-replay.json`, `native-master-ceilings.json`.
- Cache-free original assembly baseline also rebuilt with unchanged master/front/rear volumes: `printing-baseline-rebuild.json`.
- `node SolidCraft/scripts/diagnose-modular-printing.mjs`: isolates link, copy, native transfer and split stages. Native container replay preserves the recorded `BodyTransfer1` without the `timeline.add` parser limitation. No transfer substitution is needed in this route.
- Actual first geometric failure is **the linked import**: master volume **1507475.5193726986 mm³**, versus source **1507476.065203498 mm³**, delta **−0.545830799266696 mm³**, beyond the permitted **0.15074760652034977 mm³**. Copy and transfer retain the imported result. See `printing-stage-comparison.json`.
- The next split fails strict kernel validation even when its original native definition is preserved. Supported `body.repair` refuses because the transferred solid is already accepted and has no gaps/holes. Reversing only the orientation of the identical split plane still produces the same kernel failure on the other named half; no coordinates or validation tolerances were perturbed.
- The native linked import feature stores STEP data; that implementation detail and the first failing stage point to the link/import path, but the precise numerical engine defect has not been established. The volume mismatch and kernel check are independently sufficient to reject promotion.

The original assembly remains saved and unchanged, with 72 healthy features and its original three closed manufactured solids. Task 2's strict acceptance gate has not passed; Tasks 3/4 are not claimed complete. A corrected engine link/import/split path is required to finish this plan without changing its acceptance criteria.

## Evidence safety and review

An independent read-only review found acceptance/provenance/evidence weaknesses in the initial reusable tooling. Those findings were fixed in one pass with failing-then-passing regression tests. The controller now records per-run evidence and an explicit running/complete/failed attempt state. The standalone validator refuses an older success during a failed or in-progress attempt. The diagnostic verifies hashes of the original source, captured document and prepared master, resolves source IDs, and distinguishes command completion from geometric acceptance. It returns nonzero for the present import/split failures. Unknown document fields are refused for explicit dependency review rather than silently transplanted across removed component membership. Direct PowerShell extraction also refuses an occupied output.

The latest exact report locations and prepared-file hashes are in `current-run.json`; `native-attempt.json` must be complete before that evidence is accepted. `printing-attempt.json` and the run-specific diagnostic summary record the current failure. Prior direct-name logs are historical; the active attempt and its run directory determine freshness. `stale-evidence-rejection.json` records a real refusal while a new preparation run was still active.
