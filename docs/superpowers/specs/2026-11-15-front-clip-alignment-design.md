# Approved front clip alignment

The user approved `Build123d/exports/front-clip-alignment-proposal.png` and explicitly
requested implementation. Translate the whole adapter by (0, -2.426787168466774, 0)
mm in the permanent Build123d frame. The clip center becomes Y=-220.37430326680117
mm, directly below the estimated front-handle center; both centers keep their Z.
The handle center was estimated by fitting its upper scan silhouette, not supplied
as an exact design datum.

## Approach

Move the completed manufacturing geometry before subtracting the stationary prepared
wheel body. Moving the already imprinted export alone would misplace its underside
relative to the wheel. Keep the latch separate and apply the same placement so its
mating relationship follows the adapter. Keep the wheel, handles, source recipes,
fit scale, clearances and all earlier modeling decisions unchanged.
