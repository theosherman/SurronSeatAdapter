# CAD viewers

## View the CAD model

For a local build, open `exports/preview.html` in T3 Code’s Files panel or in
your browser. Use the top picker to switch
between **Adapter** and **Adapter Split**. The **View** menu holds part
visibility, zoom, reset, and gesture help. Drag to rotate, right-drag to pan,
and scroll to zoom. The viewer runs offline and needs WebGL 2.
In **View**, **Parts** controls model visibility. Under **Labels**, turn on
**Features** to identify adapter landmarks and split hardware, or **Faces** to
number the larger planar faces in the exported STEP
parts. Rotate or zoom to reveal more labels.
Each group has **Invert** and **All** buttons. **All** changes to **None** when
every visible checkbox in the group is selected.
On a touchscreen, drag with one finger to rotate, drag with two fingers to
pan, and pinch to zoom.

The local and release builds generate this file from the exported STEP parts.
Run `python3.14 -m scripts.preview_stl` from the repo root to refresh it from
existing exports. Pass STEP or binary STL paths to select specific files and
write `preview.html` beside the first input. Use the STEP keys to show them
seated in the adapter.
Refreshing the default preview removes legacy per-part HTML files from `exports/`.

The top **EUC** and **Seat** checkboxes toggle the prepared Sherman P and
Luna Surron seat overlays for either adapter variant. Both start hidden.
The HTML embeds the checked-in [wheel mesh](../reference/wheel/merged.stl)
and [seat mesh](../reference/seat/surron-seat.stl) on every default preview refresh.

## Automatic preview browser

From the repository root, run `python3 preview_server.py start`.
It starts a background server and opens http://127.0.0.1:8766 in your browser.
Keep that page open: it displays the newest image under `tmp/`
and checks for changes every second, including when an image is overwritten.
All proposal images and server logs stay in that ignored directory.

Use `python3 preview_server.py stop` to stop it, or `status` to check it.
`start --no-open` starts it without opening another browser tab; `--port` selects
another port. Python's standard library is sufficient; no CAD environment is needed.

## View and edit in VS Code

Open this repository folder in VS Code with the Python and OCP CAD Viewer extensions installed. The supplied launch configuration selects the external Python environment. Open `view_adapter.py`, then press **Ctrl+F5** (Run Without Debugging), choosing **View adapter in OCP CAD Viewer** if prompted. If the viewer panel does not open automatically, run **OCP CAD Viewer: Open viewer** from **Ctrl+Shift+P**, then rerun.

The script rebuilds the native Python geometry and sends it to the interactive viewer; it does not overwrite the STEP/STL exports. It displays the scaled Sherman P body and both unscaled, aligned handles as three separate translucent reference objects in the same corrected frame. Only the middle body is used for subtraction; the handles remain visible to check clip and future latch alignment. Set `SHOW_WHEEL_SCAN = False` for the adapter alone, or adjust `SCAN_OPACITY` (0–1) to change transparency. The scan is never joined into the manufactured body. Edit `AIR_TAG_POCKET_DEPTH` in the viewer script or operations in `adapter.py`, save, and rerun to see changes. Select **Python: Select Interpreter** and the environment under `~/.local/share/venvs/surron-build123d/bin/python` if running with the editor's Python button. The extension and Python package are both version 4.2.0.
