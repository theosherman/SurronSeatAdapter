"""Build123d's permanent frame: source (x,y,z) maps to (-x,-y,z).

This is a proper Z-axis half-turn, not a reflection. Convert source datums before
constructing faces/solids; sketch-local coordinates and dimensions stay untouched.
The authoritative cross-engine recipe and original scan remain unchanged.
"""
from copy import deepcopy
from pathlib import Path
import json


# User-approved front-clip / stationary front-handle vertical alignment.
# Applied to finished adapter and separate latch, never to wheel references.
ADAPTER_TRANSLATION_MM = tuple(json.loads(
    (Path(__file__).parent/'adapter-placement.json').read_text())['translationMm'])


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
