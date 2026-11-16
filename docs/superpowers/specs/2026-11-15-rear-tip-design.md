# Approved lower rear tip and local wall

The user approved the browser geometry in `Build123d/tmp/rear-wall-section/wall.step`:
remove only the lower toe below the separate latch, leaving the upper seat support
and dovetail intact. Mirror the latch-wall normal across XY and anchor the cut at
(0,177.270005683283,-17.98689437242) mm. Limit removal to below this anchor's Z.
Retain 10 mm normal thickness at this new diagonal by locally limiting the original
cavity cutter. The rest of the long cavity, 18.5 mm roof, original 5 mm angled rear
wall, side cuts, wheel preparation and separate accessories retain their geometry.

Approach: direct toe trim plus an inward plane limiting the existing cavity cut.
A finished-body additive patch was considered and rejected in favor of retaining
material in the original cavity operation. Previewing both together was chosen
and the 10 mm result was explicitly approved for implementation.

Rebuild STEP/STL, preserve a durable section preview, verify preview parity and
regressions, and commit locally. No remote push.
