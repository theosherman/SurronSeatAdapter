# Sherman P preparation implementation plan

**Goal:** Prepare the Sherman P independently of the adapter, using the user-approved cut preview.

**Design:** Split the corrected-frame scan at Y=-191 and +170 mm into front handle, body and rear handle. Uniformly scale only the body by 1.003 about model origin (implementation choice). Fuse the scaled body with unchanged handles, accepting overlap. Preserve the source and adapter exports. Export the three original pieces, scaled body and merged tool with measured validation. No Sherman L geometry or scaling pivot is reused.

**Architecture:** A standalone build123d preparation module consumes the original aligned STL through the existing frame converter. Its result remains separate from the adapter until integration is requested.

**Verification:** Test native split volumes, fixed handle coordinates, body scale and merged validity on an analytic fixture; then verify actual scan partition conservation, three original solids, unchanged handles, factor-cubed volume, overlap and a single valid merged solid. Reopen prepared STEP/STL.

- [x] Add preparation regression tests and observe failure before implementation.
- [x] Implement `Build123d/prepare_sherman_p.py` and pass tests.
- [x] Generate prepared scan exports and validation report; reopen outputs.
- [x] Document scope and scaling origin, review diff and make local milestone commit.

Verification: all 7 unittest tests passed. Actual scan partition error −1.02e−8 mm³; scale-volume error 9.31e−10 mm³. Original and scaled parts and merged result are each valid single solids. Reopened merged STEP and STL are valid single solids; STL volume differs by 0.140 mm³ from in-memory result. Read-only independent review found no material issues; actual-handle containment is guaranteed by union construction, with explicit containment/overlap regression checks on the analytic fixture. No adapter integration performed.
