"""Render the implemented outward offsets from the manufacturing STL."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from preview_front_clip import load
from mesh_preview import render
from coordinates import ADAPTER_TRANSLATION_MM

ROOT = Path(__file__).resolve().parent

def main():
    mesh = load(ROOT/'exports/adapter-body.stl')
    source = (mesh-np.array(ADAPTER_TRANSLATION_MM))*[-1,-1,1]
    normal = np.array([29.84830397955,31.])
    normal /= np.linalg.norm(normal)
    front = np.zeros(len(mesh),dtype=bool)
    for side in (-1,1):
        distance = (side*source[:,:,0]*normal[0]+source[:,:,1]*normal[1]
                    -(49*normal[0]+193.15953208748562*normal[1])-3)
        front |= np.max(abs(distance),axis=1)<.002
    planes = json.loads((ROOT/'tests/fixtures/accepted-dimensions.json').read_text())['printingPlanes']
    printing = np.zeros(len(mesh),dtype=bool)
    for plane in planes:
        distance = (mesh-np.array(plane['pointMm']))@np.array(plane['outwardNormal'])-1
        printing |= np.max(abs(distance),axis=1)<.002
    assert front.any() and printing.any()
    meshes = [(mesh[~front & ~printing],(98,155,199)),
              (mesh[printing],(58,182,156)),(mesh[front],(250,171,46))]
    image = Image.new('RGB',(2100,1400),'#e9eef3')
    draw = ImageDraw.Draw(image)
    font = lambda n: ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
    draw.text((35,25),'IMPLEMENTED / printing planes +1 mm / front corner cuts +3 mm',font=font(32),fill='#183044')
    draw.text((35,80),'Teal: printing planes (1 + 2). Orange: triangular front corner cuts (3), mirrored on both sides.',font=font(23),fill='#405b70')
    image.paste(render(meshes,(1,-.65,.75),(1020,1050)),(20,150))
    image.paste(render(meshes,(1,-.65,.75),(1020,1050),focus=(0,-182,28)),(1060,150))
    draw=ImageDraw.Draw(image)
    draw.text((45,125),'Whole adapter',font=font(24),fill='#183044')
    draw.text((1080,125),'Front close-up / same angle',font=font(24),fill='#183044')
    draw.text((40,1240),'All offsets measured normal to the original faces; original angles and extrusion directions preserved.',font=font(23),fill='#183044')
    draw.text((40,1290),'Original rear profile and triangular cut profiles edited. More material retained; no body patches.',font=font(23),fill='#405b70')
    draw.text((40,1340),'Rendered from the rebuilt manufacturing STL. Opposite faces may be hidden by the body.',font=font(23),fill='#405b70')
    image.save(ROOT/'exports/face-offsets-implemented.png')
    image.save(ROOT/'tmp/face-offsets-implemented.png')

if __name__=='__main__':main()
