"""Verify the original eleven-edge body/dovetail junction stays sharp and mirrored."""
import json
from pathlib import Path
from build123d import import_step, Compound, Vertex
from body_fillets import require_mirrored_selection

folder = Path(__file__).resolve().parents[1]
sharp = import_step(folder/'exports/adapter-body-pre-imprint.step')
finished = import_step(folder/'exports/adapter-body.step')
# This is the body junction, not the remote terminal at Y=261 mm.
def is_root(edge):
    lo,hi=edge.bounding_box().min,edge.bounding_box().max
    shoulder = 147<lo.Y<152 and 147<hi.Y<152 and 24<lo.Z<32 and 24<hi.Z<32
    side_return = (147<lo.Y and hi.Y<179 and 24<lo.Z and hi.Z<50
                   and max(abs(lo.X),abs(hi.X))<15)
    return shoulder or side_return

root = [edge for edge in sharp.edges() if is_root(edge)]
assert len(root) == 11, len(root)
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
report = dict(rootEdges=11,mirrored=True,toleranceMm=.001,checks=checks,
              ok=all(row['maxSharpBoundaryDistanceMm']<.001 for row in checks))
report_path = folder/'logs/dovetail-root-validation.json'
report_path.parent.mkdir(exist_ok=True)
report_path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
assert report['ok'], report
