"""Verify mirrored fillet boundaries before the asymmetric scan subtraction."""
import json
from pathlib import Path
from build123d import Compound, Vertex
from adapter import build_master
from body_fillets import fillet_body


def check_symmetry(body):
    boundary = Compound(body.faces())
    worst = 0
    samples = 0
    for edge in body.edges():
        for t in (0, .5, 1):
            p = edge.position_at(t)
            distance = boundary.distance_to(Vertex(-p.X, p.Y, p.Z))
            worst = max(worst, distance)
            samples += 1
    report = dict(samples=samples, maxMirrorBoundaryDistanceMm=worst,
                  toleranceMm=.001, valid=body.is_valid, solids=len(body.solids()))
    report['ok'] = report['valid'] and report['solids']==1 and worst<.001
    return report


if __name__ == '__main__':
    report = check_symmetry(fillet_body(build_master(imprint=False)))
    path = Path(__file__).resolve().parents[1]/'logs/fillet-symmetry-validation.json'
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))
    assert report['ok'], report
