"""Run this file in VS Code to rebuild and display the editable adapter."""
from ocp_vscode import show, set_port, Camera, Render
from build123d import Mesher
from pathlib import Path
from adapter import build_master
from latch import build_latch
from prepare_sherman_p import prepare_parts

# Edit this depth in millimeters, or edit the operations in adapter.py, then rerun.
AIR_TAG_POCKET_DEPTH = 8.5
SHOW_WHEEL_SCAN = True
SCAN_OPACITY = 0.9
LATCH_CLEARANCE = 0.2  # Positive inward offset on the three mating faces.

set_port(3939)  # Default port of the first OCP CAD Viewer panel.

adapter = build_master(airtag_depth=AIR_TAG_POCKET_DEPTH)
latch = build_latch(clearance=LATCH_CLEARANCE)
if SHOW_WHEEL_SCAN:
    # prepare_parts applies the same approved whole-scan alignment as the cutter.
    scan_path = Path(__file__).parent/'inputs/wheel-scan-model-frame.stl'
    scan = Mesher().read(scan_path)[0]
    parts = prepare_parts(scan, reunite=False)
    show(adapter, latch, parts['body-scaled'], parts['front-handle'], parts['rear-handle'],
         names=['Adapter body', 'Latch', 'Sherman P body (scaled subtraction reference)',
                'Sherman P front handle (reference only)', 'Sherman P rear handle (reference only)'],
         colors=['steelblue', 'seagreen', 'orange', 'goldenrod', 'goldenrod'],
         alphas=[1.0, 1.0, SCAN_OPACITY, SCAN_OPACITY, SCAN_OPACITY],
         modes=[Render.ALL, Render.ALL, Render.FACES, Render.FACES, Render.FACES],
         reset_camera=Camera.RESET)
else:
    show(adapter, latch, names=['Adapter body', 'Latch'], colors=['steelblue', 'seagreen'])
