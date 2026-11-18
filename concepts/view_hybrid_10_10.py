"""Run in VS Code to inspect the separate native 10+10 mm cavity preview.

Uses cached review STEP files; never rebuilds or changes the manufacturing model.
"""
from pathlib import Path
from build123d import import_step
from ocp_vscode import show,set_port,Camera,Render

(Path(__file__).resolve().parents[1]/'tmp').mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[1]
PREVIEW=(Path(__file__).resolve().parents[1]/'tmp/concepts/rear-cavity/hybrid-10-10')
COMPARE_CURRENT=False # True: current assembly beside proposed assembly.
SHOW_WHEEL=True
SCAN_OPACITY=.9

parts=[import_step(PREVIEW/'adapter-preview.step'),import_step(PREVIEW/'latch-preview.step')]
names=['PREVIEW: wall 10 mm inward + 10 mm thicker','PREVIEW: latch extended 10 mm; contact end fixed']
colors=['turquoise','seagreen'];alphas=[1,1];modes=[Render.ALL,Render.ALL]
if SHOW_WHEEL:
    for name,path in [('Sherman P body (approved fit scale)','body-scaled.step'),('Rear handle (unscaled reference)','rear-handle.step')]:
        parts.append(import_step(ROOT/'exports/sherman-p-prepared'/path))
        names.append(name);colors.append('goldenrod');alphas.append(SCAN_OPACITY);modes.append(Render.FACES)
if COMPARE_CURRENT:
    for name,path,color in [('CURRENT: adapter','adapter-body.step','steelblue'),('CURRENT: latch','latch.step','seagreen')]:
        parts.append(import_step(ROOT/'exports'/path).translate((220,0,0)))
        names.append(name);colors.append(color);alphas.append(1);modes.append(Render.ALL)
    if SHOW_WHEEL:
        for path in ['body-scaled.step','rear-handle.step']:
            parts.append(import_step(ROOT/'exports/sherman-p-prepared'/path).translate((220,0,0)))
            names.append('CURRENT: '+path);colors.append('goldenrod');alphas.append(SCAN_OPACITY);modes.append(Render.FACES)
set_port(3939)
show(*parts,names=names,colors=colors,alphas=alphas,modes=modes,reset_camera=Camera.RESET)
