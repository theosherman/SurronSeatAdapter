"""Render the implemented manufacturing STL with stationary wheel references."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from preview_front_clip import load
from mesh_preview import render

ROOT = Path(__file__).resolve().parent
body = load(ROOT/'exports/adapter-body.stl')
scan = np.concatenate([load(ROOT/'exports/sherman-p-prepared'/f'{p}.stl')
                       for p in ('body-original','front-handle','rear-handle')])
image = Image.new('RGB',(2000,1450),'#e9eef3')
draw = ImageDraw.Draw(image)
font = lambda n: ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
draw.text((30,25),'IMPLEMENTED / Sherman P suspension-access outline',font=font(34),fill='#183044')
draw.text((30,80),'Actual manufacturing export • mirrored outline • enlarged screen opening • unsplit master',font=font(24),fill='#405b70')
items = [(scan,(177,191,202)),(body,(39,154,166))]
image.paste(render(items,(0,1e-9,1),(900,1190)),(15,175))
image.paste(render([(body,(39,154,166))],(1,-.9,.9),(1050,1000)),(930,240))
draw = ImageDraw.Draw(image)
draw.text((30,140),'Top view / front at top',font=font(25),fill='#183044')
draw.text((970,140),'Oblique view / native adapter body',font=font(25),fill='#183044')
draw.text((30,1385),'Teal: rebuilt adapter     Gray: aligned wheel scan     Physical fit remains untested',font=font(24),fill='#405b70')
path = ROOT/'exports/suspension-outline-implemented.png'
image.save(path)
print(path)
