"""One finishing fillet on the adapter; the running dovetail is excluded.

Geometric selectors refer to the sharp, placed body before wheel subtraction.
Fail explicitly on changed geometry rather than silently losing selected edges.
"""
import json
from pathlib import Path
from build123d import Vector

SPEC = json.loads(Path(__file__).with_name('body-fillets.json').read_text())


def require_mirrored_selection(rows):
    """Reject a one-sided selection before asking OCCT to build any blends."""
    for row in rows:
        lo = [-row['maximum'][0], *row['minimum'][1:]]
        hi = [-row['minimum'][0], *row['maximum'][1:]]
        if not any(abs(other['length']-row['length']) < .001
                   and all(abs(a-b)<.001 for a,b in zip(lo,other['minimum']))
                   and all(abs(a-b)<.001 for a,b in zip(hi,other['maximum']))
                   for other in rows):
            raise ValueError(f'Fillet has no mirrored partner: {row}')


def fillet_body(body):
    require_mirrored_selection(SPEC['edges'])
    edges = list(body.edges())
    selected = []
    for row in SPEC['edges']:
        matches = [e for e in edges
                   if abs(e.length-row['length']) < .001
                   and (e.bounding_box().min-Vector(row['minimum'])).length < .001
                   and (e.bounding_box().max-Vector(row['maximum'])).length < .001]
        if len(matches) != 1:
            raise ValueError(f'Fillet edge changed or ambiguous: {row}')
        selected.append(matches[0])
    result = body.fillet(SPEC['radiusMm'], selected)
    if not result.is_valid or len(result.solids()) != 1:
        raise ValueError('Adapter fillet did not produce one valid solid')
    return result
