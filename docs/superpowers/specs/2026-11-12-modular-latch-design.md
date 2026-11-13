# Modular adapter master and linked latch

Status: proposed design for review; implementation has not started.

## Intent and chosen approach

Recreate Fusion's Latch as an editable SolidCraft part that mates with the rear adapter dovetail. The user chose separate native files to keep modeling timelines short, and accepts explicit refreshes between files. Preserve a dependable relationship between the master dovetail and the latch's mating slot.

Chosen architecture:

```text
SolidCraft/models/adapter-body.sc  (authoritative master history)
               │
               ├──► latch.sc      (latch history; linked master reference)
               │       │
               └───────┴──► seat-adapter.sc  (assembly and existing print split)
```

`seat-adapter.sc` must never be an input to `latch.sc`: that would create a circular file dependency. The existing split component stays assembly-local in this iteration, dependent on the linked master. Moving its short timeline into a fourth file is outside this change.

Alternatives considered: keep the latch in the current document with linked sketch projections (simpler live updates but a growing timeline); import a static latch (short timeline but loses editable history/dependency). The user selected separate files with explicit refreshes.

## Master migration and shared mating geometry

1. Save the current open SolidCraft document and commit a recovery checkpoint, preserving app-only changes. Fusion remains reference-only; do not edit or save it.
2. Use `component.extract` on the existing nonlinked `AdapterBody` component to write `models/adapter-body.sc`. This command transfers its history and makes the assembly component linked. Inspect notices and warnings. Retain the existing source geometry, world placement, smooth R20 cuts, imprint and print-child relationship; do not reconstruct the master from stale snapshots.
3. In the master file, expose a hidden solid called `RearDovetailInterface`, built from the same `M06_RearDovetailProfile` that drives the manufactured dovetail. It is a short 1 mm reference extrusion, not a printed part. File links expose solids, not source sketch history; the reference cap supplies the exact mating outline to another document.
4. Expose `rearDovetailTopHalfWidth` as an editable driver with baseline 10 mm. Drive the corresponding existing sketch coordinates/constraints from it while preserving every baseline curve and coordinate. The other baseline profile values remain the saved source values (8 mm depth, 30-degree flanks). Both the manufactured dovetail and reference extrusion use that one profile. Do not create an independently maintained duplicate outline.
5. The dependency contract covers edits to this driving dovetail profile. Arbitrary downstream face edits that bypass the profile are not claimed to propagate through the reference body automatically.

Extraction and baseline parameterization must leave the manufactured master and both printing halves unchanged within numerical tolerance. The implementation may rewire the assembly-root `C01_DependentMasterCopy` source to the new linked master while retaining the existing printing sketches, split, connector cuts, names and placement. This reference change is part of migration, not a printing-geometry redesign.

If direct extraction refuses that boundary-crossing dependency, work on a saved temporary copy of the current native document: remove only its assembly-local print branch and shared copy, then extract the self-contained master history into `adapter-body.sc`. In the original assembly, insert that master link and rewire the existing shared copy to it before replacing the old master component. Do not derive the source from stale build scripts. If neither route preserves the master history and printing feature definitions, restore the checkpoint and report the limitation; do not use a body-only master import.

## Latch file

Create `models/latch.sc` with native latch sketches and named features. Insert `adapter-body.sc` as a linked reference, without copying its modeling history into the latch timeline. Hide input/reference bodies and explicitly target only `Latch` in destructive operations.

Authoritative geometry: `cad-rebuild/accessories/latch-recipe.json`, in millimeters/degrees. It contains two local sketches, exact selected loops, the shared dovetail frame, limiting planes, three offset-face selectors, and intermediate metrics. Preserve evaluated geometry and selected regions; do not extrude every available source region.

Recreate these five nonfillet source operations in order:

| Source index | Operation | Baseline volume after (mm³) |
|---:|---|---:|
| 102 | Side-profile half, bounded by the saved oblique side plane | 161420.26040408312 |
| 103 | Mirror about YZ and join | 322840.5208081663 |
| 104 | Two-sided intersection with the three selected top-profile regions | 238753.4027 |
| 105 | Cut the dovetail slot using the linked interface outline and saved end plane | 232662.8943 |
| 106 | Offset the three mating faces by source `Gap = -0.2 mm` | 230819.7862464548 |

Use exact analytic curves and planes. Where a native point-based To Object extrusion cannot reproduce an oblique end plane, use the proven equivalent of a long extrusion followed by an exact planar trim. Record the adaptation; do not substitute a perpendicular cap or faceted outline.

Create the slot sketch on the linked reference cap with an attached plane and `sketch.project` using `projection_link: true`, `construction: false`. Read the target sketch's actual frame before mapping geometry/direction; do not assume Fusion's sketch axes are reused by SolidCraft.

Expose positive `latchClearance = 0.2 mm`; the material-removing native face offset uses the corresponding negative signed distance. This retains the source's three-face allowance, not a uniform body scale or a new wheel-fit allowance. Preserve source face orientation when selecting faces. Omit archival `Fillet5` under the existing no-fillets instruction.

Expected nofillet result: one closed manufactured solid, nominal volume 230819.7862464548 mm³; bounds X ±60.865103223 mm, Y -222.424548470..-150.227353849 mm, Z -45.662921353..47.321249211 mm. Compare volume within 0.01% and each bound within 0.05 mm; investigate larger errors rather than accepting them as kernel differences. Exact face-count equality is not required.

## Assembly, references and refresh

Insert the saved latch into `seat-adapter.sc` as a linked `Latch` component at its existing Fusion world placement (identity transform). Master, latch and print variant remain separate physical parts. Imported reference geometry, including any master solids nested inside the latch link, must remain hidden and excluded from manufactured-part exports. Do not accidentally publish duplicated masters or the interface helper as printable parts.

Refresh order after changing the master: save `adapter-body.sc`; run `component.update_links` in `latch.sc`, rebuild and save it; run `component.update_links` in `seat-adapter.sc`, which also updates the print child. Refresh order after editing only the latch: save latch, refresh assembly. The helper can orchestrate these steps, but saving alone is not advertised as an automatic refresh.

Never replace unsaved open work to run a refresh. Inspect/save the user's state first. A missing source file or lost mating-face reference must produce a clear failure and retain the last good model, not silently switch to static geometry or report an update as successful.

## Rebuild files and acceptance checks

Keep target-specific generators, command JSON and tests under `SolidCraft/scripts/`. Maintain reproducible scripts for the master, standalone latch and assembly. Document which native files are authoritative and which older files remain historical checkpoints; app edits do not automatically rewrite JSON scripts.

Acceptance checks are deliberately bounded:

- Master migration: unchanged manufactured geometry/placement, existing smooth cuts and screw ceilings, two closed printing halves, five connector recesses, no feature errors.
- Latch: one closed manufactured solid, baseline bounds/volume and intermediate material changes agree with the saved recipe; three source mating-face offsets preserve the 0.2 mm allowance; no fillets.
- Dependency: temporarily change `rearDovetailTopHalfWidth` 10→10.25 mm, save and refresh in the documented order. The manufactured dovetail and latch slot must both widen while clearance stays 0.2 mm. Restore 10 mm and refresh; baseline geometry must return. Merely refreshing an unchanged file is insufficient proof.
- Integration: correct assembly placement and visibility; explicitly export only the `Latch` body to STEP/STL; references are not printed parts. Refresh/source-path failures must be reported, not treated as success.
- Preserve the existing print-child dependency through a changed/restored `airtagPocketDepth` check after extraction. Do not repeat unrelated full-model experiments once these checks pass.

Commit the migration and the verified latch/integration at meaningful milestones. Leave the saved main assembly usable and report any remaining limitation plainly. No physical print-fit test or exact whole-model STEP equality is implied by these checks.

Only the main editing session may mutate the live SolidCraft document. Reviewers remain read-only; isolated CLI experiments must use their own files.

## Scope boundaries

No saddle bag mount, wheel-scan separation/clearance changes, Fusion edits, Onshape calls, unrelated fillets, or broad master redesign. Preserve the current wheel imprint during this latch project; its separate preparation work remains pending.
