# Latch and saddle bag mount: Fusion extraction

These are **separate parts**, extracted from `Surron Seat Adapter v3 v2` for reference. Build123d provides a [separate editable latch](../README.md#separate-latch). The saddlebag mount remains extracted only. Read the [adapter guide](CAD-REBUILD.md) for the shared assembly coordinate convention. This accessory scope was added after that guide was written.

The source API uses centimeters and radians; both accessory recipes use **millimeters and degrees**. All timeline indices are zero-based. Extraction temporarily rolled the source timeline and restored marker **200**; no source geometry was edited or document saved.

## Files

- [Latch recipe](../cad-rebuild/accessories/latch-recipe.json)
- [Saddle bag mount recipe](../cad-rebuild/accessories/saddle-bag-mount-recipe.json)
- [Raw Fusion evidence](../reference/fusion/accessories/fusion-accessories-raw.json)
- [Extraction verification](../reference/fusion/accessories/extraction-validation.json)
- [Rerunnable Fusion extraction script](../reference/fusion/accessories/extract-fusion-accessories.py)
- [Local recipe generator](../cad-rebuild/accessories/generate-accessory-recipes.mjs)

## Shared references and reconstruction rules

Both parts use the adapter's **TrunkDovetailSketch**, not merely their own sketches. Each standalone recipe includes that external sketch's full frame, curves, dimensions and constraints as a dependency, plus the exact selected loops for the accessory operations. The original parts are nested under AdapterBody in the assembly, but remain separate bodies/components. Their saved occurrence matrices are identity, so component and assembly coordinates coincide. Do not union them into the adapter.

Rebuild sketches from exact line, arc, circle and elliptical-arc geometry. Source projected/reference curves have their evaluated geometry saved; they can become explicit target sketch geometry if the target cannot reproduce the original projection relationship. Preserve construction flags, local Z, constraint intent and original expressions. Dimensions are extracted, with source constraint entity references where exposed by the API; this is not a fully serialized Fusion constraint solver. Exact selected loops are authoritative when a sketch contains adjoining regions.

A profile loop is in its **named sketch frame**; transform using origin, X, Y and cross(X,Y). Do not use the source `startExtent.profilePlane` as a global plane: Fusion reports that in profile-local coordinates. Explicit FromEntity start and ToEntity end planes are global, with component/body context. The ToEntity `directionHint` is dimensionless. Preserve signed blind distances and taper values. For through-all intersection, preserve the two-sided extent arrangement and intersect with the correct current part.

Offset face selectors record the pre-feature global point, geometry, area and `isParamReversed`; the actual oriented face normal is the surface normal reversed when that flag is true. Use the signed source distance, including negative `Gap=-0.2 mm` and `Gap*1.5=-0.3 mm`. These are source functional fit offsets, separate from the adapter wheel-imprint's zero added clearance.

Source fillets are documented with edge geometry and radii, but **must be omitted** under the user's no-fillets instruction. Use the pre-fillet metrics below for a new build.

## SaddleBagMount

The saddle bag mount remains a distinct accessory part. 3 local sketches; 9 source features, including one archival fillet.

| Timeline | Sketch | Curves | Dimensions | Constraints | Origin mm | X axis | Y axis |
|---:|---|---:|---:|---:|---|---|---|
| 108 | BaseSketch | 20 | 8 | 20 | (0, -25.18244446, -42.40091371) | (1, 0, 0) | (0, -0.8597932986, 0.5106422267) |
| 111 | ArmCutSketch | 22 | 3 | 17 | (0, -150.499337, 89.38347935) | (-1, 0, 0) | (0, 0.5106422267, 0.8597932986) |
| 115 | IndentionSketch | 20 | 0 | 8 | (0, -31.31015118, -52.71843329) | (1, 0, 0) | (0, -0.8597932986, 0.5106422267) |

Build features in **timeline order**, not the API collection order:

| Timeline | Feature | Action | Volume after, mm^3 |
|---:|---|---|---:|
| 109 | Extrude1 | newBody: 16 selected region(s) from BaseSketch; 12 millimeter (source `12 mm`). | 94361.72324 |
| 110 | Extrude2 | cut: 1 selected region(s) from TrunkDovetailSketch; up to saved AdapterBody/Body1 target plane, offset 0 millimeter (source `0.00 mm`). | 74754.97212 |
| 112 | Extrude3 | cut: 4 selected region(s) from ArmCutSketch; -100 millimeter (source `-100 mm`). | 66946.94126 |
| 113 | OffsetFaces1 | Offset 2 selected faces by -40 millimeter (source `-40 mm`). Select by saved global point, surface normal, area and body/component, not transient IDs. | 60883.92824 |
| 114 | Extrude4 | join: 2 selected region(s) from ArmCutSketch; -10 millimeter (source `-10.00 mm`); start from saved entity plane (not sketch plane). | 61256.24415 |
| 116 | Extrude5 | cut: 5 selected region(s) from IndentionSketch; -1 millimeter (source `-1 mm`). | 58032.08479 |
| 117 | OffsetFaces2 | Offset 4 selected faces by -0.2 millimeter (source `Gap`). Select by saved global point, surface normal, area and body/component, not transient IDs. | 56173.05231 |
| 118 | OffsetFaces3 | Offset 2 selected faces by -0.3 millimeter (source `Gap * 1.5`). Select by saved global point, surface normal, area and body/component, not transient IDs. | 55620.93486 |
| 127 | Fillet1 | Record source edge selections and radii; omit from this rebuild (no fillets). | 55130.14029 |

Expected no-fillet result: **1 solid**, volume **55620.93486 mm^3**, bounding box **(-35, -280.6857175, 36.76717451)  to  (35.00000052, -175.9558686, 105.534463) mm**. Source final filleted volume (archival): 55130.14029 mm^3. Verify each intermediate volume in the recipe as the target features are created.

## Latch

The latch mates with the rear adapter dovetail. 2 local sketches; 6 source features, including one archival fillet.

| Timeline | Sketch | Curves | Dimensions | Constraints | Origin mm | X axis | Y axis |
|---:|---|---:|---:|---:|---|---|---|
| 100 | SideSketch | 15 | 5 | 20 | (0, 0, 0) | (0, 1, 0) | (0, 0, 1) |
| 101 | TopCutSketch | 7 | 1 | 11 | (0, 0, 0) | (1, 0, 0) | (0, 1, 0) |

Build features in **timeline order**, not the API collection order:

| Timeline | Feature | Action | Volume after, mm^3 |
|---:|---|---|---:|
| 102 | Extrude1 | newBody: 2 selected region(s) from SideSketch; up to saved AdapterBody/Body1 target plane, offset 0 millimeter (source `0.00 mm`). | 161420.2604 |
| 103 | Mirror2 | Mirror Body about YZ; combine = true. | 322840.5208 |
| 104 | Extrude2 | intersect: 3 selected region(s) from TopCutSketch; through all; second extent also recorded. | 238753.4027 |
| 105 | Extrude3 | cut: 1 selected region(s) from TrunkDovetailSketch; up to saved AdapterBody/Body1 target plane, offset 0 millimeter (source `0.00 mm`). | 232662.8943 |
| 106 | OffsetFaces2 | Offset 3 selected faces by -0.2 millimeter (source `Gap`). Select by saved global point, surface normal, area and body/component, not transient IDs. | 230819.7862 |
| 128 | Fillet5 | Record source edge selections and radii; omit from this rebuild (no fillets). | 231178.3087 |

Expected no-fillet result: **1 solid**, volume **230819.7862 mm^3**, bounding box **(-60.86510322, -222.4245485, -45.66292135)  to  (60.86510322, -150.2273538, 47.32124921) mm**. Source final filleted volume (archival): 231178.3087 mm^3. Verify each intermediate volume in the recipe as the target features are created.

## Verification and limits

The saved extraction has zero property-read errors. The timeline marker before/after is 200/200. Both source parts are single solids; all eight extrusions have their selected profile loops, end definitions and start definitions saved. All four offset features have explicit face selectors; the latch mirror includes its global YZ plane and combine flag. No physical print test has been performed. Transient Fusion body names such as Body1 are ambiguous across components; always use the recorded component plus geometry. Use the no-fillet checkpoints, not the source final filleted metrics, when checking the requested rebuild.

Run the local-only generator with `node cad-rebuild/accessories/generate-accessory-recipes.mjs`. The Python extractor requires the original Fusion design open and temporarily changes the timeline marker; do not label that invocation read-only, and do not run it during an unfinished interactive command. It restores the marker in a finally block and never saves the document.
