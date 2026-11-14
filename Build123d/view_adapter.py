"""Run this file in VS Code to rebuild and display the editable adapter."""
from ocp_vscode import show, set_port
from adapter import build_master

# Edit this depth in millimeters, or edit the operations in adapter.py, then rerun.
AIR_TAG_POCKET_DEPTH = 8.5

set_port(3939)  # Default port of the first OCP CAD Viewer panel.

adapter = build_master(airtag_depth=AIR_TAG_POCKET_DEPTH)
show(adapter, names=['Adapter body'], colors=['steelblue'])
