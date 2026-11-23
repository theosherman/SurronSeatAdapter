# CAD rebuild guide

## Purpose and authoritative inputs

Use the original Fusion geometry and documented corrections as a portable baseline. See the [Build123d README](../README.md) for later model revisions and manufacturing exports. This guide records what was extracted, which features were reproduced, what changed at the user's request, and how the finished parent/child relationship works.

The source was the active Fusion document `Surron Seat Adapter v3 v2`, in project/folder `Sherman P`. It had 200 timeline entries. Relevant components were `AdapterBody` and `AdapterBodySplit`; the source assembly also contained a seat, latch, saddlebag mount, old trunk branches, and reference wheel geometry that were outside the requested rebuild.

Use [recipe.json](../cad-rebuild/recipe.json) as the machine-readable specification and [FEATURE-RECIPE.md](FEATURE-RECIPE.md) as its table of operations. Every source marker is indexed in [FUSION-TIMELINE.md](FUSION-TIMELINE.md). Timeline indices in this documentation are **zero-based**.

The baseline records the corrected screw access, the Sherman P imprint, and the original Fusion connector recesses. The current Build123d model applies finishing fillets separately and uses three connector recesses in the printing variant.

## Final model structure

```mermaid
flowchart TD
  sketches[Master sketches and datums] --> master[Unsplit adapter geometry]
  master --> holes[Through-holes and downward access recesses]
  holes --> finished[Other cuts, drafts and AirTag recess]
  scan[Aligned Sherman P wheel-top scan] --> imprint[Subtract scan from underside]
  finished --> imprint
  imprint --> parent[Adapter Body: one finished master solid]
  parent --> derived[Live associative child copy]
  derived --> split[Split at placed Y=37 mm]
  split --> connectors[Three shoulder and cavity-wall recesses]
  connectors --> child[Adapter Body Split: two printable solids]
```

The master retains its own editable history. The child references the finished master and adds print-specific geometry. Build123d creates the printing variant from the completed master export.

## Units and coordinate frames

| Data | Lengths | Angles |
|---|---|---|
| Raw Fusion extracts | centimeters | radians for numeric parameter values |
| Portable recipe and this guide | millimeters | degrees |
| Original and aligned STL files | unitless numbers interpreted as millimeters for this project | n/a |

Conversions: `mm = Fusion_cm * 10`, `inches = Fusion_cm / 2.54`, `meters = mm / 1000`, `degrees = radians * 180/pi`. Preserve the original expressions separately from numerical conversions. `Gap` is a Fusion user parameter with expression `-0.2 mm`; its numeric Fusion API value is `-0.02` centimeters.

Global X is the adapter width, Y runs along the adapter with the screen/front cutout toward positive Y, and Z is up. The center mirror plane is global `X=0`.

A saved sketch point `(u,v,w)` is **not** automatically a global point. Transform it as:

```text
N = cross(sketchXAxis, sketchYAxis)
globalPoint = sketchOrigin + u*sketchXAxis + v*sketchYAxis + w*N
```

All terms must use the same length unit. Directions are unitless. The rear sketch contains nonzero sketch-space Z, about `-263.445982 mm`; dropping that coordinate moves its plane to the wrong location. Its source X axis is global +X, source Y axis is global -Z, and its normal is global +Y.

## Geometry and profile selection

The first extraction saved 18 sketches and 233 source curves, with dimensions and frames. This includes three split-variant sketches that no longer exist in the master. Their geometry remains in the portable recipe because it is needed to reconstruct the child.

Most curves are exact lines, circles, and arcs. One `RearSeatNotchSketch` ellipse was initially sampled, then replaced with an exact native ellipse. In its original Fusion sketch frame it has center `(-14.5, 196.70896933768436)` mm, major radius `3.5` mm, minor radius `3.4895137853640384` mm, and major axis +U. The portable recipe contains these exact parameters, not the temporary segments.

An extrusion often selects only some regions of a sketch. The profile-loop extraction saves **37 selected profiles across 20 extrusion features**, including outer/inner loops, analytic curve data, areas, and centroids. Use those loops to identify or build the intended regions. Fusion arc bounding boxes can be loose. Use the exact loops and measured areas to identify profiles.

If building CSG rather than native sketch features, construct a planar face from each selected outer loop minus its inner loops, merge adjacent selected regions where appropriate, and extrude that face. The curve list can contain reversed edges and collinear segments. Order/orient a loop by endpoint connectivity; do not assume every curve is already in traversal order.

The saved original dimensions and 149 model parameters preserve numerical values and expressions. The complete original sketch constraint graph and every constraint-to-entity association were **not** exported. Geometry can be reproduced from the saved coordinates; restoring all original parametric design intent requires additional work.

## Master reconstruction

The exact step records are `masterSteps` in the portable recipe. The following describes their purpose and the details most likely to be lost in another CAD system.

### Base shape: source 8–18

1. Build `BottomSketch` on the global XY frame. Extrude it 150 mm in +Z and 50 mm in -Z as a new body. This is a two-sided construction blank, not a 150 mm symmetric extrusion.
2. Mirror across `X=0` and union the mirror.
3. Build `SideSketch` in the YZ frame: local X is global +Y, local Y is global +Z. Intersect its selected profiles extruded 120 mm in +X with the blank. Source parameter `d16` confirms the 120 mm distance.
4. Build `RearSketch` at its saved offset and intersect its profile extruded 490 mm in +Y. Mirror the remaining half across `X=0` and union it.
5. Build `TrunkDovetailSketch` and join its selected small dovetail profile up to the rear datum plane. The target plane is global `Y=-263.445982162752` mm. Its source plane normal was `(0,-1,0)`.

Do not use the similarly named unrelated source trunk component as the adapter's dovetail profile. Selected loops for source feature 18 resolve the intended region.

### Bolt through-holes and screwdriver access: source 74–77

This was the main correction identified through user inspection. A successful feature regeneration alone did not prove that the screwdriver recess had the correct direction or retained its ceiling.

There are four small through-holes, diameter **7 mm**, and corresponding larger access recesses, diameter **17 mm**. The larger recesses must open toward the underside, leaving material around each small hole at the mounting ceiling.

The common bolt sketch frame, in millimeters, is:

```text
origin = (0, 8.627219333715026, 42.40413776674599)
X = (-1, 0, 0)
Y = (0, -0.9799247046208692, 0.1993679344170023)
N = (0, 0.1993679344170023, 0.9799247046208692)
```

The rear pair is at sketch coordinates `u=±14.5`, `v=193.9428441873774` mm; the front pair is at `u=±23`, `v=-64.05715581262262` mm. These are sketch coordinates, not global XY coordinates.

- Small holes: remove through all in both directions along N. This avoids copying broken source extent references.
- Rear larger recesses (`Extrude6`): start 3 mm below the top sketch plane, then cut through all in direction -N. The first attempt incorrectly made a shallow top counterbore instead of an underside access opening.
- Front larger recesses (`Extrude7`): bound the top of the cavity below its sloped top face, and extend the other side downward through all. Use the recorded plane below to preserve the mounting ceiling at the nominal 3 mm stopping offset.

For an exact as-built front ceiling, use an infinite plane through `(23, 73.86340632647599, 41.74904474222621)` mm with upward normal `(0, 0.26418906967888117, 0.964470909598733)`. The same plane serves the opposite hole because its normal has zero X component. Remove the large bore below that plane, retain material above it, and retain the independent 7 mm through-hole. The bore axis and this plane normal are not identical, so nominal offset direction matters; do not substitute an unexamined normal offset.

The [Fusion reference image](images/fusion-front-holes-reference.png) shows the original mounting holes.

### Hangers, front mount and dovetails: source 78–98

Create the selected `SeatHangerSketch` profile as a new body, 1 mm in the negative sketch-normal direction. Apply the source 45° draft, mirror the hanger across `X=0`, and union the hanger bodies with the adapter. The draft's neutral plane is the saved +X face at `X=51` mm. Its exact datum and selected-face point are in the recipe.

Create the handle mount from `HandleMountSketch` with a **98 mm total** symmetric join along X: 49 mm each side. Apply `FrontCutSketch`'s selected corner cuts, then the source `Draft4` angle of **-35°** relative to its saved bottom neutral plane. The neutral normal is `(0,0.11840396830649746,-0.9929655081065374)`. Use the selected face and datum in the recipe rather than assuming every front face should be drafted.

Apply the five selected `RearSeatNotchSketch` regions as an 8 mm cut in the negative sketch-normal direction. Join `FrontDovetailSketch` symmetrically along X for **80 mm total**, 40 mm each side.

Source `Extrude13` at index 93 could not be read as a valid extrusion. Inspection showed zero produced faces/bodies and identical `AdapterBody` volume and face count immediately before and after it. It was skipped, not guessed.

`HingeTrajectorySketch` is reference geometry. The selected circular `SeatCutoutSketch` region was cut through all in both directions and mirrored across `X=0`. Fusion specified a start from a nonparallel flank face; the portable baseline uses a through-cylinder. The original start-plane datum is saved in the recipe. This is a documented adaptation, not a proof of exact source topology equivalence.

### Rear relief, underside cavity and AirTag recess: source 119–126

Cut the selected `RearCutSketch` profiles through all in both directions and mirror them across `X=0`.

For `BodyCutSketch`, start **12 mm below** the sketch plane, remove through all toward the underside, and apply the **15° taper**. Its cavity widens toward the bottom.

Cut the selected `AirtagCutSketch` region **8.5 mm** in the negative sketch-normal direction.

### Exclusions from the original assembly

The old source split/cut at index 131 used `Veteran Sherman L v2 / Body` as its tool. It and the associated body removal at 132 were initially omitted. The later wheel imprint uses a different, explicitly supplied **Sherman P** scan; do not replay both cuts.

Source fillets 127–128 belong to accessory branches. The current adapter uses a separate [Build123d finishing operation](../body_fillets.py).

## Wheel-top scan imprint

The user later supplied `Sherman_P_Flush_Screen_Fusion_Default.stl` and authorized subtracting its shape from the underside so the adapter seats on the wheel.

The raw file was a closed 16,000-triangle binary STL with 7,988 unique vertices. Edge-incidence checks found no boundary/non-manifold edges at the recorded quantization. Its volume matched the already placed Fusion `Sherman P Body Top Refined v4` body: about **4,221,287.872 mm³**. A sampled vertex matched to about `5.7e-14` mm after the local translation, confirming that it was the same scan rather than just a similarly sized mesh.

The exact final transform from original STL coordinates to adapter coordinates, in millimeters, is:

```text
x' = -x + 215.596105105428
y' = -y + 305.1260529610669
z' =  z - 372.6817016601563
```

The two sign changes are a proper 180° rotation about Z, not an orientation-reversing reflection. Normals must be rotated too. The aligned mesh bounds are approximately:

```text
minimum = (-105.889551633, -249.614913836, -71.769897461) mm
maximum = ( 103.881040103,  243.801132307,  34.509460449) mm
```

The transform was recovered from the Fusion component's local geometry and occurrence transform. [align-source.mjs](../reference/wheel/align-source.mjs) reproduces it during [explicit wheel preparation](../README.md#sherman-p-body-only-fit-preparation). Routine builds use the checked-in prepared body BREP. The adapter imprint has zero added clearance.

## Linked printing child

### Historical Fusion split plane

Create a live copy/reference of the completed master, including corrected holes and the wheel imprint. Do not cut the master into pieces.

Fusion's actual split tool was the **first line** of `SplitBodySketch`, not all four lines in that sketch. In global millimeters, that line runs from:

```text
A = (0, -92.88539833894989,  63.05711325274752)
B = (0, -109.93653499568712, -20.751900973452995)
```

Extend it across the width in the global X direction to form an infinite splitting plane. A normal is `normalize(cross((1,0,0), B-A))`, approximately `(0,0.9799247046208692,-0.1993679344170023)`. Keep both sides. The plane therefore follows the intended tilted split through the adapter, not the center mirror plane `X=0`.

### Connector recesses

The production Build123d variant uses a transverse split at placed Y=37 mm, one top recess cut 12.8 mm perpendicular to the roof, and two 3.8 mm cavity-wall recesses. See the [current split workflow](../README.md#two-piece-printing-variant). The portable recipe preserves the original Fusion geometry described below, including its original 8 mm pocket depth and four side recesses.

The top connector combines two neighboring trapezoidal profiles into one hourglass recess. In the original top-joint sketch frame its overall U range is approximately `±26.547005384` mm, with a 30 mm-wide waist at `v=103.59226295038653` mm and ends at `v=83.59226295038653` and `v=123.59226295038653` mm. Do not mistake the two selected profile regions for two separate connectors.

The original Fusion side connector combined two neighboring profiles in four placements:

1. Original side profile/frame.
2. Original reflected across source plane 192.
3. Original reflected across `X=0` (source 193).
4. Original reflected across plane 192, then across `X=0`.

Plane 192 has origin `(43.08329799343095,-106.6165550021415,21.629452186156035)` mm and unit normal `(0.25881904510252096,-0.19257463678729542,-0.9465345800119827)`.

The portable recipe includes both the original mirror definitions and **five already expanded connector frames/profiles with explicit extrusion direction vectors**. Prefer these expanded instances if the next CAD tool handles reflected sketch handedness differently. For a plane with point O and unit normal n:

```text
reflectPoint(P)  = P - 2*dot(P-O,n)*n
reflectVector(V) = V - 2*dot(V,n)*n
```

Transform positions, sketch axes, and extrusion direction independently. A reflection reverses frame handedness; recomputing a normal and always cutting in its negative direction can send a mirrored pocket outward. The recipe's `extrusionDirection` avoids that mistake.

The original Fusion source made loose inserts with a different clearance. The current [Build123d keys](../README.md#two-piece-printing-variant) have 1 mm edge fillets and at least 0.4 mm clearance. One top key and two copies of the same cavity key fill the three recesses.

## Evidence and limits

See the [porting checklist](PORTING-AND-VALIDATION.md) for dimensional and material checks and the [Build123d README](../README.md#verification) for the current validation commands.
