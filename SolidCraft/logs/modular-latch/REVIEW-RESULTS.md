# Native migration tooling review

Scope: replacement plan Task 1 and Task 2 diagnostic tooling. Reviewer was a separate read-only agent; no CAD mutations were delegated.

Findings fixed in one implementation pass:

- Printing validator accepted empty feature history and extra solids. Regression: `printing acceptance rejects empty health and extra solids`.
- Diagnostic conflated command success with geometric acceptance. Regression: `manufacturing comparison rejects successful import with changed volume`; actual diagnostic now records false geometry acceptance for the linked import and returns exit code 1.
- Failed reruns could retain stale success evidence. Regression: `failed or in-progress attempts cannot validate old successful evidence`; real in-progress controller refusal recorded in `stale-evidence-rejection.json`. All new command reports live in run-specific directories, with explicit latest-attempt status.
- Prepared snapshot/native source lacked provenance checks. Regression: `requires provenance of both prepared snapshot and native master`.
- Component/feature IDs were hardcoded in the diagnostic. It now consumes the partition of current named components/features. Regression: `rejects ambiguous ownership and unsupported dependent data, resolves changed component IDs`.
- Unknown dependent fields and duplicate master names were not rejected. Covered by the same ambiguity/dependency regression; original feature and asset fidelity remains covered separately.
- Direct container extraction could overwrite its output outside the Node wrapper. Reclassified as a data-protection issue and fixed with exclusive `CreateNew` IO, in addition to wrapper destination guards.

Verification: 10/10 Node tests pass; fresh end-to-end native preparation and standalone acceptance pass. The printing CAD diagnostic intentionally fails on the measured engine import/split defects. No acceptance tolerances were relaxed, and no source-model mutation was found. No deferred review findings remain in the implemented scope; later plan tasks remain unimplemented.
