"""Verify that the asymmetric wheel cutter cannot trim new fillet surfaces."""
import json
from pathlib import Path
from build123d import import_brep, import_step, Face, Vector
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from body_fillets import SPEC, require_mirrored_selection

folder = Path(__file__).resolve().parent
require_mirrored_selection(SPEC['edges'])
body = import_step(folder/'exports/adapter-body-pre-imprint.step')
cutter = import_brep(folder/'reference/wheel/body-scaled.brep')
edges = list(body.edges())
selected = []
for row in SPEC['edges']:
    matches = [e for e in edges if abs(e.length-row['length'])<.001
               and (e.bounding_box().min-Vector(row['minimum'])).length<.001
               and (e.bounding_box().max-Vector(row['maximum'])).length<.001]
    assert len(matches)==1, row
    selected.append(matches[0])
builder = BRepFilletAPI_MakeFillet(body.wrapped)
for edge in selected:
    builder.Add(SPEC['radiusMm'],edge.wrapped)
builder.Build()
assert builder.IsDone()
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
(folder/'logs/fillet-cutter-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
assert report['ok'],report
