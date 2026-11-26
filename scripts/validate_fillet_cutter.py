"""Verify that the asymmetric wheel cutter cannot trim new fillet surfaces."""
import json
from pathlib import Path
from build123d import import_step, Face
from body_fillets import build_fillet

from reference.wheel import load_wheel_cutter

folder = Path(__file__).resolve().parents[1]
body = import_step(folder/'exports/adapter-body-pre-imprint.step')
cutter = load_wheel_cutter()
builder, selected = build_fillet(body)
# Include corner blends generated from vertices as well as edge blends.
faces = {}
for edge in selected:
    for source in [edge, *edge.vertices()]:
        for shape in builder.Generated(source.wrapped):
            face = Face(shape)
            faces[hash(face)] = face
minimum = min(face.distance_to(cutter) for face in faces.values())
report = dict(selectedEdges=len(selected),generatedFaces=len(faces),
              minimumCutterDistanceMm=minimum,toleranceMm=.001,ok=minimum>.001)
report_path = folder/'logs/fillet-cutter-validation.json'
report_path.parent.mkdir(exist_ok=True)
report_path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
assert report['ok'],report
