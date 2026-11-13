# Modular Latch Implementation Plan

**Migration update:** Direct and temporary-copy extraction both refused. The user authorized a full-native-history alternative; [the replacement migration plan](2026-11-12-modular-latch-native-history.md) supersedes Task 1's extraction method. Tasks 2/3 and all geometry acceptance criteria below remain in force.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Only the main session edits the live CAD model.

**Goal:** Rebuild the Fusion latch in its own editable SolidCraft file, linked to an independent Adapter Body source and placed in the SeatAdapter assembly.

**Architecture:** `adapter-body.sc` owns the current master history and a hidden mating-interface solid; `latch.sc` references it through linked geometry. `SeatAdapter.sc` links both files and retains the existing assembly-local printing split. Refresh in dependency order, never by linking the assembly back into either part.

**Tech Stack:** Installed SolidCraft 0.40.1 desktop/CLI, Node.js ES modules using built-ins, existing `SolidCraft/scripts/mcp-call.mjs`, native command JSON, local Git. Do not install a new CAD kernel or dependencies.

**Spec:** [Approved design](../specs/2026-11-12-modular-latch-design.md).

## Global Constraints

- Root name exactly **SeatAdapter**; authoritative assembly `SolidCraft/models/SeatAdapter.sc`. Existing `models/seat-adapter.sc` is the migration input/checkpoint, not the new root name. Keep `adapter-body.sc` and `latch.sc` as part file names.
- Default component order: Adapter Body, Adapter Body Split, Latch, Wheel Scan Reference. Preserve existing internal names `AdapterBody`, `AdapterBodySplit`, `WheelScanReference`; new component `Latch`.
- Use current native geometry, preserving app-only edits. Fusion is read-only reference; no Onshape calls or wheel-imprint changes.
- Latch source: `cad-rebuild/accessories/latch-recipe.json`, mm/degrees; selected profiles and signed offsets are authoritative. No fillets or faceted curve substitutions.
- Positive `latchClearance=0.2 mm` drives a negative 0.2 mm material offset on the three source mating faces. Named master driver `rearDovetailTopHalfWidth=10 mm`; reference extrusion `RearDovetailInterface`, depth 1 mm.
- One live editor and one writer per native file. CLI experiments write only isolated temporary files. Inspect/preserve dirty app state before switching or overwriting documents.
- Export only manufactured bodies by resolved component/body identity; hidden input/reference solids are never printing outputs.

## Review Focus

1. Extraction may cross `C01_DependentMasterCopy`; Task 1 must preserve/rewire that input without dropping the printing feature history.
2. Imported files expose bodies, not sketches; Task 2 must project a linked interface face and prove a changed master reaches the slot.
3. Unsaved documents and missing source paths; Task 3 must stop safely without discarding edits or claiming a successful stale refresh.
4. Nested links may expose duplicate reference solids; Tasks 2/3 must hide them and exclude them from exports and manufactured-body counts.
5. Oblique cap/frame and signed-clearance errors can produce healthy but wrong geometry; Task 2 must check the staged source metrics and mating planes, not only feature success.

## File responsibilities

- Create `SolidCraft/scripts/migrate-modular-master.mjs`: one-time native migration, baseline snapshots, shared parameter/interface creation, and migration report.
- Create `SolidCraft/scripts/generate-latch.mjs`: pure generator of standalone `latch-build.json` from the extracted recipe and master path.
- Create `SolidCraft/scripts/generate-modular-assembly.mjs`: assembly command generator using a captured current printing command list; writes `SeatAdapter-build.json`.
- Create `SolidCraft/scripts/refresh-modular-design.mjs`: dependency-ordered refresh through the single desktop session; structured failures and last-good state handling.
- Create `SolidCraft/scripts/validate-modular-latch.mjs`: checks baseline migration, latch metrics, exported-body selection, and restored dependency experiments from fresh CAD reports.
- Create `SolidCraft/modular-manifest.json`: paths, exact part/occurrence/body roles, reference exclusions, and default order. Resolve qualified body names from inspection rather than assuming global uniqueness.
- Generate `SolidCraft/scripts/adapter-body-build.json`, `latch-build.json`, `SeatAdapter-build.json`, `models/adapter-body.sc`, `models/latch.sc`, `models/SeatAdapter.sc`, and latch-only STEP/STL exports. Store evidence under `SolidCraft/logs/modular-latch/`.
- Modify `SolidCraft/README.md` and `AGENTS.md` with authoritative paths/refresh steps. Preserve older build logs as historical evidence.

### Task 1: Preserve and modularize the master

**Interfaces:** consumes the current desktop document and existing native component/history; produces the linked assembly, `adapter-body.sc`, manifest, baseline report, and current printing branch as `{commands:[{command,params}]}`. Do not populate that branch from stale recipe data unless inspection proves it identical to the live history.

- [ ] Inspect active path, dirty state, feature health, components/placements, qualified manufactured body names, metrics and source parameter values. Save the user's current state; commit a recovery checkpoint before mutation. Preserve any older open checkpoint occupying a target path.
- [ ] Write the migration-stage assertions in `validate-modular-latch.mjs` before producing its report: the master and both halves stay closed; volume changes are at most `max(0.001 mm³, baselineVolume*1e-7)`, bounds/COM at most 0.001 mm; current smooth R20 cuts and 12 mounting-ceiling checks remain valid. The missing report must fail clearly.
- [ ] Implement `migrate-modular-master.mjs --apply`: first attempt `component.extract` for existing `AdapterBody`. Inspect notices/warnings. If boundary references block it, use a saved temporary native copy with only the print branch/shared copy removed, extract its complete master history, then insert the source link and rewire the original assembly's existing copy. Restore the checkpoint if the history or child cannot be preserved; never use a body-only substitute.
- [ ] In the master, parameterize the existing dovetail profile's symmetric top half-width at 10 mm without changing its baseline coordinates. Add the 1 mm `RearDovetailInterface` extrusion from that same sketch, hide it, and save the master. Keep all unrelated dimensions/geometry unchanged.
- [ ] Save the assembly as `models/SeatAdapter.sc`; verify the root reads `SeatAdapter`. Keep the existing split/connector features and world placement. Capture exact current command definitions for its printing branch for later assembly replay.
- [ ] Export the standalone master history to `adapter-body-build.json`. Inspect the exporter’s `omitted` output: components/assemblies are not supported by `timeline.export_script`; do not use it as an assembly serializer. Replay the root-only master script separately and compare its manufactured body/interface to the saved source; omissions of model history are a failure.
- [ ] Change `airtagPocketDepth` 8.5→8.6 in the source master, save and refresh the assembly, verify equal master/combined-child material deltas within 1e-5 mm³, then restore 8.5 and refresh. Run migration assertions and commit the verified migration.

### Task 2: Build the standalone latch and its linked slot

**Interfaces:** `buildLatchCommands({masterPath, clearanceMm:0.2})` in `generate-latch.mjs` returns `{commands:[{command,params}]}` and writes `latch-build.json`. Consumes Task 1's source master/interface and role manifest. Produces `models/latch.sc`, body `Latch`, and staged measurements.

- [ ] Add geometry-stage assertions before building: one closed manufactured latch; nominal volume `230819.7862464548 mm³` within 0.01%; bounds `[-60.865103223,-222.424548470,-45.662921353]` to `[60.865103223,-150.227353849,47.321249211]` within 0.05 mm; three signed mating-face offsets of -0.2 mm; zero fillet features. Missing geometry/report must fail.
- [ ] Generate explicit selected-loop sketches and operations from source indices 102–106. Preserve analytic arcs and nonzero sketch-local Z. Explicitly target `Latch`, never the linked master/interface. For index 102 use a long half extrusion trimmed by the exact saved oblique side plane; do not rely on a perpendicular point-limit cap.
- [ ] Insert the master as a hidden linked reference. Attach the slot sketch to the linked interface's original-profile cap; read its actual frame, and project with `projection_link:true, construction:false`. Use the saved end plane for the slot, then native `solid.offset_face` driven by `-latchClearance` on the recorded oriented faces.
- [ ] Build into an isolated file first. Compare intermediate volumes after source 102/103/104/105/106 against approximately `161420.2604 / 322840.5208 / 238753.4027 / 232662.8943 / 230819.7862 mm³`. Investigate mismatches before adding later operations; do not launch unrelated full-model experiments.
- [ ] Save the validated part as `latch.sc`. Test clearance 0.2→0.3 mm: cavity expands and latch material decreases while the master is unchanged; restore 0.2. Export only the manufactured Latch to STEP and STL, verify no reference-body bounding boxes are included, then commit.

### Task 3: Link, order, and verify the refresh workflow

**Interfaces:** `generateAssemblyCommands({masterPath,latchPath,printingCommands})` returns assembly command JSON. `refresh-modular-design.mjs` consumes the manifest and emits `{ok,updated,failed,errors,warnings}` to `logs/modular-latch/refresh.json`. It refreshes latch before assembly and leaves the main assembly active.

- [ ] Add integration assertions: root `SeatAdapter`, four part/reference components in the specified order, unchanged source placements, separate manufactured latch, two printing halves, no model errors; dependency restoration and failure behavior below must pass.
- [ ] Insert `latch.sc` as the linked `Latch` at identity/Fusion placement. Resolve and hide nested reference bodies and the master interface. Save explicit manufactured-body roles in the manifest. Use `browser.order` with `folder:'components'`, root component and inspected component-ID keys to set AdapterBody → AdapterBodySplit → Latch → WheelScanReference; do not reorder manufacturing history to sort the browser.
- [ ] Implement ordered refresh: reject/preserve unsaved state; open latch, update its master reference, verify health and save; open `SeatAdapter.sc`, update links, verify master/child/latch health and save. Stop on any nonempty `failed`/error list, retain last-good geometry, and never interpret an unchanged stale link as success. Handle a latch-only save with the assembly-only refresh path.
- [ ] Prove real dependency: source width 10→10.25 mm, save master, refresh latch then assembly. Master top width and slot width at the same interface-local mid-depth plane must both increase by 0.5 mm (within 0.01 mm), with each mating-plane allowance remaining 0.2 mm. Restore width 10 and refresh; baseline volumes/bounds return.
- [ ] In isolated test files only, make a linked master path unavailable and verify refresh reports failure and keeps the last-good bodies. Verify the refresh controller refuses to replace dirty open work. Do not rename/delete the live source to test failure.
- [ ] Write the assembly script explicitly from links plus the captured current printing command list; do not use the unsupported native assembly exporter. Replay master, latch and assembly in an isolated temporary tree, refresh it, and compare the manufactured outputs/placement against the saved live design.
- [ ] Update README/AGENTS with the exact root/filenames, shared-profile scope, reference exclusions, source→latch→assembly refresh sequence and physical-fit limitations. Save the main assembly, run the bounded validators, commit the verified integration, and report the recovery/final commits plus any actual remaining limitation.

## Self-review

All five Review Focus cases have an owning task/check. No Fusion writes, wheel preparation, saddle-bag mount, new fillets, or additional printing variant migration are included. Preserve the current live model rather than rebuilding it from historical generated JSON. Execution remains with the main editing session; do not run concurrent CAD editors.
