# Portable master feature sequence

Use this with [the rebuild guide](CAD-REBUILD.md), [sketch catalog](SKETCH-CATALOG.md), and [recipe.json](../cad-rebuild/recipe.json). Exact selected profile loops, areas, and centroids are in the recipe. Do not extrude every region of a sketch indiscriminately.

| Step | Fusion indices | Operation | Sketch / datum | Main dimensions |
|---|---|---|---|---|
| M01 | 8, 9 | NEW | BottomSketch | positiveDepthMm: 150; negativeDepthMm: 50 |
| M02 | 10 | MIRROR_AND_UNION |  |  |
| M03 | 11, 12 | INTERSECT | SideSketch | depthMm: 120 |
| M04 | 13, 14 | INTERSECT | RearSketch | depthMm: 490 |
| M05 | 15 | MIRROR_AND_UNION |  |  |
| M06 | 17, 18 | ADD_UP_TO_PLANE | TrunkDovetailSketch |  |
| M07 | 74, 75 | REMOVE_THROUGH_ALL_BOTH_DIRECTIONS | BoltHolesSketch | diameterMm: 7 |
| M08 | 76 | REMOVE_DOWNWARD_FROM_OFFSET_PLANE | BoltHolesSketch | diameterMm: 17; roofOffsetMm: 3 |
| M09 | 77 | REMOVE_BOUNDED_ABOVE_AND_THROUGH_ALL_BELOW | BoltHolesSketch | diameterMm: 17; nominalRoofOffsetMm: 3 |
| M10 | 78, 79 | NEW | SeatHangerSketch | depthMm: 1 |
| M11 | 80, 81, 82 | DRAFT_MIRROR_UNION | draft 80 | angleDegrees: 45 |
| M12 | 83, 84 | ADD_SYMMETRIC | HandleMountSketch | totalDepthMm: 98 |
| M13 | 85, 86 | REMOVE_THROUGH_ALL | FrontCutSketch |  |
| M14 | 87 | DRAFT | draft 87 | angleDegrees: -35 |
| M15 | 88, 89 | REMOVE | RearSeatNotchSketch | depthMm: 8 |
| M16 | 90, 91 | ADD_SYMMETRIC | FrontDovetailSketch | totalDepthMm: 80 |
| M17 | 94, 95, 96, 97, 98 | REMOVE_CYLINDER_AND_MIRROR | SeatCutoutSketch |  |
| M18 | 119, 120, 121, 122 | REMOVE_THROUGH_ALL_BOTH_DIRECTIONS_AND_MIRROR | RearCutSketch |  |
| M19 | 123, 124 | REMOVE_DRAFTED_THROUGH_ALL | BodyCutSketch | startOffsetMm: -12; draftDegrees: 15 |
| M20 | 125, 126 | REMOVE | AirtagCutSketch | depthMm: 8.5 |
| M21 | 199 | SUBTRACT_ALIGNED_WHEEL_SCAN |  | clearanceMm: 0 |

## Draft datums

- 80 Draft1: 45 degrees; neutral origin `(51, -3.127587857, 44.795680319)`, normal `(1, 0, 0)`. Selected face points and normals are in the recipe.
- 87 Draft4: -35 degrees; neutral origin `(0, -186.530738589, -29.885206794)`, normal `(0, 0.118403968, -0.992965508)`. Selected face points and normals are in the recipe.

## Selected profile evidence

| Fusion feature index | Marker | Sketch | Area (mm²) | Centroid in sketch coordinates (mm) |
|---:|---|---|---:|---|
| 9 | BottomExtrusion | BottomSketch | 25903.297159987 | (33.965844208, -58.390653344, 0) |
| 12 | SideIntersection | SideSketch | 21933.796290149 | (-53.265960797, 26.976073892, 0) |
| 12 | SideIntersection | SideSketch | 173.964535852 | (106.57818777, 32.310641785, 0) |
| 14 | RearIntersection | RearSketch | 10221.560299134 | (34.995349705, -9.909812695, -263.445982163) |
| 18 | Extrude4 | TrunkDovetailSketch | 196.950417228 | (0, -53.565391359, 0) |
| 75 | ScrewHoleExtrude | BoltHolesSketch | 38.484510006 | (14.5, 193.942844187, 0) |
| 75 | ScrewHoleExtrude | BoltHolesSketch | 38.484510006 | (-14.5, 193.942844187, 0) |
| 75 | ScrewHoleExtrude | BoltHolesSketch | 38.484510006 | (-23, -64.057155813, 0) |
| 75 | ScrewHoleExtrude | BoltHolesSketch | 38.484510006 | (23, -64.057155813, 0) |
| 76 | Extrude6 | BoltHolesSketch | 188.495559215 | (14.5, 193.942844187, 0) |
| 76 | Extrude6 | BoltHolesSketch | 188.495559215 | (-14.5, 193.942844187, 0) |
| 77 | Extrude7 | BoltHolesSketch | 188.495559215 | (-23, -64.057155813, 0) |
| 77 | Extrude7 | BoltHolesSketch | 188.495559215 | (23, -64.057155813, 0) |
| 79 | Extrude8 | SeatHangerSketch | 989.307802213 | (-36.249924, 23.022570528, 0) |
| 84 | Extrude9 | HandleMountSketch | 1013.515973883 | (216.998054104, 22.784037102, 0) |
| 84 | Extrude9 | HandleMountSketch | 85.09613166 | (198.105793797, 35.033966185, 0) |
| 86 | Extrude12 | FrontCutSketch | 462.648711683 | (69.666666667, 183.210097428, 0) |
| 86 | Extrude12 | FrontCutSketch | 462.648711683 | (-69.666666667, 183.210097428, 0) |
| 89 | Extrude10 | RearSeatNotchSketch | 160.198422701 | (-29.781873985, 254.173873459, 0) |
| 89 | Extrude10 | RearSeatNotchSketch | 53.567570335 | (-34.570710383, 258.042302671, 0) |
| 89 | Extrude10 | RearSeatNotchSketch | 243.359928185 | (-19.610559844, 254.3274889, 0) |
| 89 | Extrude10 | RearSeatNotchSketch | 213.765993036 | (30.981907381, 255.143262233, 0) |
| 89 | Extrude10 | RearSeatNotchSketch | 243.359928185 | (19.610559844, 254.3274889, 0) |
| 91 | Extrude11 | FrontDovetailSketch | 80.784609691 | (199.557341738, 42.330310967, 0) |
| 97 | Extrude15 | SeatCutoutSketch | 1256.637061436 | (98.00000146, 39.000000581, 0) |
| 121 | Extrude16 | RearCutSketch | 297.980460611 | (61.231561035, 161.247444161, 0) |
| 121 | Extrude16 | RearCutSketch | 145.829048541 | (72.171981403, 155.417716909, 0) |
| 124 | Extrude18 | BodyCutSketch | 6257.819742047 | (0, -88.671742092, 0) |
| 126 | Extrude19 | AirtagCutSketch | 1024.295078056 | (0, 31.726541746, 0) |
| 186 | Extrude20 | TopJointSketch | 830.940107676 | (0, 92.665841958, 0) |
| 186 | Extrude20 | TopJointSketch | 830.940107676 | (0, 114.518683942, 0) |
| 188 | Extrude2 | SideJointSketch | 67.549981495 | (104.650487293, -7.807839061, 0) |
| 188 | Extrude2 | SideJointSketch | 67.549981495 | (110.126197696, -6.654493905, 0) |
| 194 | Extrude3 | TopJointSketch | 830.940107676 | (0, 92.665841958, 0) |
| 194 | Extrude3 | TopJointSketch | 830.940107676 | (0, 114.518683942, 0) |
| 195 | Extrude4 | SideJointSketch | 67.549981495 | (104.650487293, -7.807839061, 0) |
| 195 | Extrude4 | SideJointSketch | 67.549981495 | (110.126197696, -6.654493905, 0) |
