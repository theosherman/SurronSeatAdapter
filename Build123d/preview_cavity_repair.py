"""Compare original, defective, and repaired actual exports from below.

Usage: python preview_cavity_repair.py ORIGINAL_STL DEFECTIVE_STL
Use git show to extract historical manufacturing exports to temporary paths.
"""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont
from preview_front_clip import load
from mesh_preview import render

ROOT=Path(__file__).resolve().parent
original=load(Path(sys.argv[1]))
broken=load(Path(sys.argv[2]))
fixed=load(ROOT/'exports/adapter-body.stl')
image=Image.new('RGB',(3000,1550),'#e9eef3')
draw=ImageDraw.Draw(image)
font=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
draw.text((30,20),'UNDERSIDE + CLIP / repaired dependent features',font=font(37),fill='#183044')
for i,(label,body,color) in enumerate([
    ('Original / before outline change',original,(80,139,165)),
    ('Defective outline implementation',broken,(165,106,91)),
    ('Repaired / approved outline retained',fixed,(39,154,166))]):
    x=i*1000
    draw.text((x+20,85),label,font=font(27),fill='#183044')
    image.paste(render([(body,color)],(1,.5,-1),(980,900)),(x+10,140))
    image.paste(render([(body,color)],(1,0,.05),(980,370),focus=(0,-207,25)),(x+10,1120))
    draw=ImageDraw.Draw(image)
    draw.text((x+25,1065),'Front clip / side view',font=font(24),fill='#183044')
draw.text((30,1500),'Actual manufacturing STL exports. Right: enclosed side walls around hollow trunk; complete original grip lifted together.',font=font(26),fill='#405b70')
path=ROOT/'exports/cavity-and-clip-repair.png'
image.save(path)
print(path)
