"""Compare actual exports at the two user-marked regions.

Usage: python preview_shoulders_screen.py PRIOR_STL
"""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
from preview_front_clip import load
from mesh_preview import render

ROOT=Path(__file__).resolve().parent
before=load(Path(sys.argv[1]));after=load(ROOT/'exports/adapter-body.stl')
image=Image.new('RGB',(2200,1700),'#e9eef3')
draw=ImageDraw.Draw(image)
font=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
draw.text((30,20),'IMPLEMENTED / continuous seat shoulders + screen walls 8 mm lower',font=font(32),fill='#183044')
for i,(label,body,color) in enumerate([
    ('BEFORE / prior body',before,(80,139,165)),
    ('AFTER / current manufacturing export',after,(39,154,166))]):
    x=i*1100
    draw.text((x+25,90),label,font=font(28),fill='#183044')
    image.paste(render([(body,color)],(0,1e-9,1),(1080,670),focus=(0,22,42)),(x+10,150))
    image.paste(render([(body,color)],(.75,1,.7),(1080,670),focus=(0,-167,32)),(x+10,915))
    draw=ImageDraw.Draw(image)
    draw.text((x+25,825),'Seat-support shoulders / top view',font=font(25),fill='#183044')
    draw.text((x+25,1590),'Screen sides / front ramp and rounded-cutout junction',font=font(23),fill='#183044')
draw.text((30,1650),'Native shoulder planes extended to body • side tops lowered 8 mm • ramp continues across the full width • no fillets',font=font(23),fill='#405b70')
path=ROOT/'exports/shoulders-and-lowered-screen.png'
image.save(path)
print(path)
