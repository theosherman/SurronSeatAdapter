# Modular latch implementation attempt — 2026-11-12

Initial implementation stopped at the master-extraction gate in Task 1. The user subsequently authorized a full-native-history alternative. Standalone master rebuild and independent script replay now pass an isolated feasibility check; reconnection to the printing split remains unresolved. The latch build and final integration have not started. No authoritative modular assembly or latch is claimed to exist.

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
- `scripts/migrate-modular-master.mjs`: guarded extraction stage with checkpoint recovery. This is a diagnostic scaffold, **not a completed modular migration**; do not advertise it as the final build/refresh workflow.
- `scripts/validate-modular-latch.mjs`: initial migration/latch acceptance assertions. Both stages intentionally reject absent acceptance reports. Geometry and integration acceptance have not passed.

## Revised route and feasibility evidence

See [the replacement migration plan](../../../docs/superpowers/plans/2026-11-12-modular-latch-native-history.md). The standalone native-history copy rebuilt all 58 master features with caches removed, and the exported 59-step script independently replayed to exactly matching master measurements. `history-feasibility.json` records the comparisons and a signed-zero serialization audit.

An isolated printing reconnection trial still failed at the recorded split: `SmCone::Test #5 Bad Cone GenCurve LineScale`, reporting offset `2.2415403e-12` against tolerance `2e-12`. The cause remains unknown; numerical thresholds were not relaxed. `printing-feasibility-failure.json` records the command and observed failure. The revised plan addresses that case before promoting any files. Physical latch fit remains untested.
