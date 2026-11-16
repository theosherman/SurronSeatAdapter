"""Verify the original five-edge body/dovetail junction stays sharp and mirrored."""
import json
from pathlib import Path
from build123d import import_step, Compound, Vertex
from body_fillets import require_mirrored_selection

folder = Path(__file__).resolve().parent
sharp = import_step(folder/'exports/adapter-body-pre-imprint.step')
finished = import_step(folder/'exports/adapter-body.step')
# This is the body junction, not the remote terminal at Y=261 mm.
root = [edge for edge in sharp.edges()
        if 147 < edge.bounding_box().min.Y < 152
        and 147 < edge.bounding_box().max.Y < 152
        and 24 < edge.bounding_box().min.Z < 32
        and 24 < edge.bounding_box().max.Z < 32]
assert len(root) == 5, len(root)
rows = [dict(length=e.length,minimum=list(e.bounding_box().min),
             maximum=list(e.bounding_box().max)) for e in root]
require_mirrored_selection(rows)
boundary = Compound(finished.faces())
checks = []
for edge in root:
    # Interior samples avoid the unchanged neighboring corner blends.
    points = [edge.position_at(t) for t in (.25, .5, .75)]
    distances = [boundary.distance_to(Vertex(p)) for p in points]
    checks.append(dict(midpointMm=list(points[1]),
                       maxSharpBoundaryDistanceMm=max(distances)))
report = dict(rootEdges=5,mirrored=True,toleranceMm=.001,checks=checks,
              ok=all(row['maxSharpBoundaryDistanceMm']<.001 for row in checks))
(folder/'logs/dovetail-root-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
assert report['ok'], report
