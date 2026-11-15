"""Reopen deliverables and verify a real editable-parameter change."""
import json
from pathlib import Path
from build123d import import_step, Mesher
from adapter import build_master
from OCP.BOPAlgo import BOPAlgo_ArgumentAnalyzer

folder = Path(__file__).resolve().parent
base = import_step(folder/'exports/adapter-body.step')
mesh = Mesher().read(folder/'exports/adapter-body.stl')[0]
nominal = build_master()
changed = build_master(airtag_depth=8.6)
# STEP serialization can change measured volume slightly; do not conflate that
# round-trip error with the native pocket-depth edit being verified.
delta = nominal.volume-changed.volume
roundtrip_delta = base.volume-nominal.volume
cutter = import_step(folder/'exports/sherman-p-prepared/body-scaled.step')
analysis = BOPAlgo_ArgumentAnalyzer()
analysis.SetShape1(cutter.wrapped)
analysis.SelfInterMode = True
analysis.Perform()
cutter_ok = cutter.is_valid and bool(cutter.solids()) and not analysis.HasFaulty() and not analysis.HasErrors()
report = dict(
    step=dict(valid=base.is_valid,solids=len(base.solids()),volumeMm3=base.volume,
              boundsMm=dict(min=list(base.bounding_box().min),max=list(base.bounding_box().max))),
    stl=dict(valid=mesh.is_valid,solids=len(mesh.solids()),volumeMm3=mesh.volume),
    scanCutter=dict(valid=cutter.is_valid, solids=len(cutter.solids()), selfIntersectionFree=cutter_ok),
    airtagParameterTest=dict(depthMm=8.6,removedMm3=delta,expectedRemovedMm3=102.4295078183),
    stepRoundtripVolumeDeltaMm3=roundtrip_delta,
    ok=cutter_ok and base.is_valid and len(base.solids())==1 and mesh.is_valid and len(mesh.solids())==1
       and abs(delta-102.4295078183)<0.01 and abs(roundtrip_delta)<0.1
       and abs(mesh.volume-base.volume)<5)
(folder/'logs/export-and-parameter-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
assert report['ok'], report
