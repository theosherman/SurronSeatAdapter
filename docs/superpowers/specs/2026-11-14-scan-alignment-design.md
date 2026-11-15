# Approved Sherman P alignment

The user approved the lower-outer-bottom preview: rotate the complete scan by
-3.4932161177016057 degrees about model +X at the origin, then translate by
(0, 0, 3.464786838041892) mm. Both handles move with the body before slicing.
The target is the lower outer bottom plane, not the cavity roof.

Use one rigid transform in scan preparation before the existing world-Y slices
at -191/+170 mm; only the resulting middle body receives the existing 1.003
origin-based scale. Continue excluding both handles from adapter subtraction.
This preserves the approved operation order; transforming already-sliced regions
would produce different partition boundaries and is rejected.

Rebuild prepared scan exports, adapter exports, viewer references and validation.
Original STL and shared cross-engine recipe remain authoritative and unchanged.

Implementation finding: the source has crossing screen facets. A local,
checksum-guarded connectivity recipe reconnects 31 triangles before alignment.
All original vertices, boundary edges and triangle count are preserved; no
clearance or smoothing is added. Native volume reconstruction alone did not
survive STEP/STL export; the final pipeline uses the reconnected scan directly.
