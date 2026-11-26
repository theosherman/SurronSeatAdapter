"""Run this file in VS Code to rebuild and display the editable adapter."""
from ocp_vscode import show, set_port, Camera, Render
from build123d import import_step
from adapter import build_master
from latch import build_latch
from reference.wheel import WHEEL_REFERENCE, WHEEL_RISE_MM, load_wheel_cutter

# Edit this depth in millimeters, or edit the operations in adapter.py, then rerun.
AIR_TAG_POCKET_DEPTH = 8.5
SHOW_WHEEL_SCAN = True
SCAN_OPACITY = 0.9
LATCH_CLEARANCE = 0.2  # Positive inward offset on the three mating faces.

set_port(3939)  # Default port of the first OCP CAD Viewer panel.

adapter = build_master(airtag_depth=AIR_TAG_POCKET_DEPTH)
latch = build_latch(clearance=LATCH_CLEARANCE)
if SHOW_WHEEL_SCAN:
    parts = [load_wheel_cutter()]
    parts.extend(import_step(WHEEL_REFERENCE / f'{name}.step')
                              .translate((0, 0, WHEEL_RISE_MM))
                 for name in ('front-handle', 'rear-handle'))
    show(adapter, latch, *parts,
         names=['Adapter body', 'Latch', 'Sherman P body (scaled subtraction reference)',
                'Sherman P front handle (reference only)', 'Sherman P rear handle (reference only)'],
         colors=['steelblue', 'seagreen', 'orange', 'goldenrod', 'goldenrod'],
         alphas=[1.0, 1.0, SCAN_OPACITY, SCAN_OPACITY, SCAN_OPACITY],
         modes=[Render.ALL, Render.ALL, Render.FACES, Render.FACES, Render.FACES],
         reset_camera=Camera.RESET)
else:
    show(adapter, latch, names=['Adapter body', 'Latch'], colors=['steelblue', 'seagreen'])
