# Adapter body port

Use the accepted millimeter recipe in `inputs/recipe.json`. Preserve the Fusion world frame. Rebuild exact selected profile loops rather than every source sketch region. No fillets or added clearance.

1. M01–M05: bottom profile, 150/50 mm two-sided extrusion, X mirror, side and rear intersections, final X mirror. Base extrusion expected volume: 5,180,659.431997455 mm³ before the first mirror. Compare each subsequent stage against saved source dimensions and final reference.
2. M06–M09: rear dovetail; four 7 mm holes; downward 17 mm access cavities, preserving rear and front mounting ceilings. Front cap plane is explicitly saved in the recipe.
3. M10–M20: hanger and draft, handle mount, front cut and draft, notches, front dovetail, mirrored side/rear cutouts, drafted underside cavity and AirTag pocket.
4. M21: aligned millimeter scan subtraction with zero clearance, if supported by SolidCraft's mesh/body workflow. Do not replace unsupported operations with an unreported approximation.
5. Preserve the unsplit master; build a dependent print variant with the saved split plane and five connector recesses. Verify the target's inheritance behavior before claiming it is linked.

Final accepted Onshape reference: one master solid, 1,511,781.8419273874 mm³; child two solids, 1,494,140.907663128 mm³. These are comparison targets, not measurements of this port. Check feature errors, closed bodies, volume, bounding box and mounting-ceiling material. Export native `.sc` checkpoints and reproducible command scripts under this folder.

Current implementation starts with stage 1. Numeric sketch geometry is a coordinate reconstruction; source dimension constraints still require explicit mapping before claiming full parameter equivalence.
