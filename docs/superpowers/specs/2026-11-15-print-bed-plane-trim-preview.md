# Proposed restoration of the printing side planes — awaiting approval

User request: preserve the raised clip and thicker bridge, but extend the existing
large rear sloped side face through the entire body, mirrored on both sides, so
front protrusions no longer stop the adapter resting flat on either printing face.
Prepare a preview before implementation.

`Build123d/concepts/preview_print_plane_trim.py` reads the current manufacturing
STEP and extracts the two actual rear faces. Each outward half-space is discarded
using a native planar split. No face offsets, body rotation, or manufacturing
source changes. The right outward normal is (0.8918512712, 0, 0.4523287632), and
the left is its X mirror; the exact plane points are in the JSON report.

The source protrudes 4.547544 mm beyond each plane. The proposed result removes
520.198818 mm³ total and remains one valid native solid. All resulting vertices
are inside both planes within 2.1e-11 mm numerical residual. Green on the preview
shows new front contact faces; orange shows discarded material. Lower views
rigidly orient the same plane onto an illustrative print bed for comparison only.

Preview: `Build123d/exports/print-plane-trim-preview.png`.
Review-only STEP/STL and numeric report:
`Build123d/exports/concepts/print-plane-trim-*`.
The authoritative adapter source and exports remain untouched. Checkpoint
`checkpoint/raised-front-clip` at 6021f13 preserves the approved pre-trim model.
No implementation approval has been given yet.
