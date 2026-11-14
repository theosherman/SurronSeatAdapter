"""Build123d's permanent frame: source (x,y,z) maps to (-x,-y,z).

This is a proper Z-axis half-turn, not a reflection. Convert source datums before
constructing faces/solids; sketch-local coordinates and dimensions stay untouched.
The authoritative cross-engine recipe and original scan remain unchanged.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import struct


def source_to_model(xyz):
    return [-xyz[0], -xyz[1], xyz[2]]


def model_recipe(source):
    recipe = deepcopy(source)
    recipe['globalAxes'] = dict(x='width; reversed from source', y='physical front is negative Y', z='up')
    for sketch in recipe['sketches']:
        for key in ('originMm','xAxis','yAxis','normal'):
            sketch[key] = source_to_model(sketch[key])
    for step in recipe['masterSteps']:
        for key in ('direction','finalRoofPlanePointMm','finalRoofPlaneNormal'):
            if isinstance(step.get(key),list): step[key] = source_to_model(step[key])
        for key in ('plane','targetPlane','mirrorPlane','sourceStartPlane'):
            if key in step:
                for field in ('originMm','normal'):
                    step[key][field] = source_to_model(step[key][field])
    for draft in recipe['drafts']:
        for key in ('originMm','normal'):
            draft['neutralPlane'][key] = source_to_model(draft['neutralPlane'][key])
        for face in draft['selectedFaces']:
            for key in ('pointMm','normal'):
                face[key] = source_to_model(face[key])
    # Child data is not consumed here; it remains in the original source frame.
    return recipe


def prepare_scan(source, destination):
    """Convert every scan vertex and normal before importing a faceted BREP."""
    source, destination = Path(source), Path(destination)
    raw = source.read_bytes()
    count = struct.unpack_from('<I',raw,80)[0]
    if len(raw)!=84+count*50: raise ValueError('Expected a binary STL')
    data = bytearray(raw)
    for i in range(count):
        for j in range(4):  # normal followed by three vertices
            offset = 84+i*50+j*12
            struct.pack_into('<3f',data,offset,*source_to_model(struct.unpack_from('<3f',raw,offset)))
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_bytes(data)
    report = dict(source=source.name, output=destination.name, triangles=count,
                  transform='(x, y, z) -> (-x, -y, z)', clearanceMm=0,
                  sourceSha256=hashlib.sha256(raw).hexdigest(), outputSha256=hashlib.sha256(data).hexdigest())
    destination.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    return destination
