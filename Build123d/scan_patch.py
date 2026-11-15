"""Reconnect a defective source screen patch without moving scan vertices."""
from pathlib import Path
import hashlib
import json
import math
import struct

PATCH = json.loads(Path(__file__).with_name('scan-screen-patch.json').read_text())


def repair_screen_patch(data):
    """Apply the audited connectivity correction only to the exact source mesh."""
    if hashlib.sha256(data).hexdigest() != PATCH['inputModelFrameSha256']:
        raise ValueError('Screen patch recipe does not match this scan')
    result = bytearray(data)
    for index, points in zip(PATCH['replaceTriangleIndices'], PATCH['replacementTriangleVerticesMm'], strict=True):
        a, b, c = points
        u, v = [b[i]-a[i] for i in range(3)], [c[i]-a[i] for i in range(3)]
        normal = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        length = math.sqrt(sum(x*x for x in normal))
        struct.pack_into('<12fH', result, 84+index*50,
                         *(x/length for x in normal), *(x for p in points for x in p), 0)
    return bytes(result)
