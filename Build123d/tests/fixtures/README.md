# Clip regression reference

`front-before-suspension.step` is the native front region of the accepted
pre-imprint export at commit `cf2f335`, before the bottom-outline implementation.
It retains Y < -192.96 mm in the placed Build123d frame. Its volume is
117457.98217141339 mm³. It is test evidence only; manufacture never imports it.

The full original grip forward of Y=-205.275 mm must remain, and the enlarged
screen opening must not add material outside this historical front envelope.

`original-rear-interface.step` is the external wall skin, original single top
dovetail and rear structure from the accepted pre-imprint STEP at commit
`8746492`, before the rejected cavity patches. It is the positive half-space of
plane point `(0,164.41714823915711,1.578677917809248)` and normal
`(0,0.8597932986247546,0.5106422266518543)`. The sketch-only cavity redesign must
preserve this region by symmetric difference, preventing extra interface rails
or an unintended outer wall/latch shift.
