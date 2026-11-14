# Porting and validation checklist

## Scope

SolidCraft and Zoo Design Studio are intended future targets. Neither implementation nor API compatibility was tested in this session. Use the saved geometry and operation intent; do not assume either target accepts Onshape payloads, FeatureScript, Fusion tokens, or the same mesh Boolean operations.

Start with [recipe.json](../cad-rebuild/recipe.json), [CAD-REBUILD.md](CAD-REBUILD.md), and the [aligned millimeter scan](../Sherman_P_Scan_Aligned_To_Adapter_mm.stl). The large historical Onshape schema responses are not needed for another CAD engine.

## Check the target's capabilities first

| Required operation | Possible fallback |
|---|---|
| Arbitrary planar line/circle/arc/ellipse sketches | Transform exact planar faces into 3D and use CSG |
| Selected profiles and inner loops | Outer faces minus inner faces |
| Two-sided/symmetric extrusion | Separate signed extrusions, then union |
| Union, intersection and subtraction | Equivalent target-kernel Boolean operations |
| Neutral-plane draft/taper | Drafted tools or equivalent ruled surfaces, checked against source datums |
| Up-to-plane bounds | Trim a long extruded tool against a half-space |
| Associative parent/child relationship | Rebuild the child from a shared master-body function |
| Solid split by infinite plane | Intersect copies with complementary half-spaces |
| Subtract closed mesh from analytic solid | Mixed modeling, faceted BREP conversion, or a documented mesh-Boolean stage |

Record representation changes and tolerances. Preserve analytic geometry and editable source where supported; an STL-only output does not restore a parametric feature tree.

## Suggested implementation structure

This is pseudocode, not a target-specific API:

```text
source = load_portable_recipe_in_millimeters()

function build_master(source):
    shape = base_extrusions_intersections_and_mirrors(source.M01_to_M06)
    shape = small_through_holes_and_downward_access_with_ceilings(shape)
    shape = hangers_handle_mount_dovetails_drafts_and_reliefs(shape)
    shape = underside_cavity_and_AirTag_recess(shape)
    return subtract(shape, load_aligned_scan_in_millimeters())

master = build_master(source)

function build_child(master):
    halves = split_keep_both(master, source.child.splitPlane)
    tools = []
    for instance in source.child.connectorInstances:
        profile = regions_from_exact_loops(instance)
        tools += extrude(profile, instance.extrusionDirection, 8 mm)
    return subtract(halves, union(tools))

child = build_child(master)
```

Use a native linked body in history-based CAD or a dependency between these functions in code-generated CAD. A detached copy does not meet the desired inheritance behavior. Keep splits and connector recesses out of the master.

## Geometry rules

- Convert units once. Portable geometry is already millimeters; directions are unitless. Raw Fusion extracts use centimeters/radians.
- Preserve full sketch frames, including nonzero local Z. Map curves into the target sketch's actual basis.
- Prefer exact selected loops, analytic arcs and circles, and the corrected exact ellipse.
- Outer and inner loops matter. A ring profile is not automatically a disk.
- Loop curves can be reversed or split into collinear segments. Order them by endpoint connectivity rather than list order.
- Match regions by boundaries, area and centroid. Fusion's loose arc boxes and a different kernel's tight boxes need not coincide.
- Check symmetric depth semantics: handle mount = 98 mm total; front dovetail = 80 mm total.
- Keep axis direction, depth, starting offset and taper separate. Flipping one is not equivalent to flipping another.
- Use each mirrored connector's explicit extrusion direction. A reflected frame changes handedness.
- Extend splitting and stopping datums to infinite planes where the source did so.
- Do not add fillets, loose connector inserts, Gap-based insert clearance, or the old Veteran Sherman L cut.

## Scan rules

The aligned STL is already rotated and translated into the adapter's millimeter coordinates. Do not apply the alignment transform twice. Do not apply the Onshape-specific 0.001 scale correction unless the new target actually imports those millimeter numbers as meters.

Expected source measurements:

- 16,000 triangles; 7,988 quantized unique vertices.
- Bounds approximately `(-105.8896,-249.6149,-71.7699)` to `(103.8810,243.8011,34.5095)` mm.
- Closed scan volume approximately `4,221,287.872 mm³`.
- Positive-Y screen opening and negative-Y rear end aligned correctly.

The recorded quantized edge incidence was two for every edge. This is useful evidence, not a guarantee that every kernel accepts every facet. Onshape produced a principal solid and tiny auxiliary fragments/sheets; its principal volume matched the full scan within float-rounding tolerance and was used for the imprint.

If repair or decimation is necessary elsewhere, preserve the original and record the procedure/tolerance. Do not silently smooth the fit surface or add clearance. The accepted imprint uses zero added clearance.

## Verification checkpoints

### Master before the scan

- One solid and the expected silhouette.
- Four open 7 mm through-holes.
- Four 17 mm access recesses opening downward, with mounting material retained above them.
- Front ceilings present on both sides of the screen opening, not 17 mm through-holes.
- Nominal 3 mm ceiling offset; use the exact saved front plane for the accepted Onshape geometry because its normal differs from the bore axis.
- Interior cavity starts 12 mm below its sketch and expands toward the underside with a 15° taper.
- AirTag recess is 8.5 mm deep.
- No fillets or old reference-wheel cut.

Recorded pre-imprint master volume: **1,531.834017805817 cm³**, after the front-ceiling correction and removal of fillets.

### Master after the scan

- One solid, with the scan consumed as a tool rather than left as another output body.
- Underside follows the aligned scan.
- Recorded volume: **1,511.781841927387 cm³**.
- Material removed from that pre-imprint state: approximately **20.052175878429 cm³**.

### Child

- Master remains unchanged and unsplit.
- Child inherits the current master, including corrected holes and imprint.
- Two principal printable solids.
- Split plane contains the saved two endpoints and spans X.
- Five connector locations: one top, four side, each 8 mm deep.
- No added loose inserts, insert clearance or fillets.
- Recorded total volume: **1,494.140907663128 cm³**.

### Front ceiling material tests

The final screw correction tested three points for each front hole in the child: solid material inside the annular ledge, empty space below it in the access recess, and an empty central small hole.

The exact cap origins/normals are in [front-screw-ceiling-correction.json](../front-screw-ceiling-correction.json). For each cap, the recorded material point was 1.5 mm opposite the downward cap normal plus 5.5 mm in global X. The cavity point was 1.5 mm along the downward normal plus the same X offset. The central-hole point omitted the X offset. These tests were recorded before the scan imprint; recheck after a port if a changed scan intersection affects this area.

## Cross-kernel comparison

For the verified Veteran Sherman L reference preparation, see [wheel reference preparation](WHEEL-REFERENCE-PREPARATION.md): split off both handles first, then uniformly scale only the central body by 1.003 about its saved pivot, and exclude both handles from subtraction. This source procedure has not yet been applied to the existing SolidCraft Sherman P imprint.

Use body count, silhouette, dimensions, selected-profile areas and material tests together. Choose and record the target tolerance. A single matching volume does not prove identical topology. Investigate substantial discrepancies before spending remote calls on finishing details.

Save the target's editable code/project, dependency versions, key views, measurements, import units and any deviations. A comparison STEP/STL should accompany rather than replace the editable source where supported. No physical print/fit test was recorded in this session.

## API lessons

- Prepare geometry, conversions and payloads locally before remote writes.
- An accepted Onshape write can still create a failed feature. Check feature state before claiming success.
- When reusing a stable query string, remove stale transient `deterministicIds`; otherwise they can override the query and erase selections.
- Native Boolean feature type is `booleanBodies`, not `boolean`.
- Explicitly set `startOffsetBound=BLIND` for a blind start offset.
- Use a typed FeatureScript length bound such as `LENGTH_BOUNDS`; the untyped map attempted in this session failed at runtime.
- The upload helper was necessary because the connector had no multipart upload tool. It reuses the installed auth provider without saving/printing credentials.
- Check imported geometry size. The supplied upload unit field did not prevent the 1000x scale issue.
- Avoid repeated full feature-tree calls and per-edge fillet trials. The user explicitly requested conservative API use and cancellation of fillets.

No new Onshape API calls were made for this documentation. Additional Fusion profile/datum extraction restored the original timeline marker.
