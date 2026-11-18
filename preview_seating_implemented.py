"""Render the implemented 8 mm deeper seating from manufacturing STL exports."""
from PIL import Image, ImageDraw, ImageFont
from preview_front_clip import load, ROOT
from mesh_preview import render

out=ROOT/'exports'
body=load(out/'adapter-body.stl')
wheel=[load(out/'sherman-p-prepared'/f'{name}.stl') for name in ('body-scaled','front-handle','rear-handle')]
meshes=[(m,(207,168,91)) for m in wheel]+[(body,(43,151,174))]
image=Image.new('RGB',(1900,1260),'#eef2f6');d=ImageDraw.Draw(image)
font=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
d.text((35,20),'IMPLEMENTED / 8 mm deeper seating',font=font(34),fill='#183044')
d.text((35,72),'Actual manufacturing STL geometry; wheel and front grip raised 8 mm relative to the adapter.',font=font(23),fill='#40566a')
image.paste(render(meshes,(1,0,0),(1840,450)),(30,115))
image.paste(render(meshes,(1,0,0),(1050,550),focus=(0,-195,40)),(30,600))
image.paste(render([(body,(43,151,174))],(1,-.6,.7),(760,550),focus=(0,-190,40)),(1110,600))
d=ImageDraw.Draw(image)
d.text((55,575),'Front grip / circular opening continued through the taller ramp',font=font(23),fill='#183044')
d.text((1140,575),'Adapter only / front connection',font=font(23),fill='#183044')
d.text((35,1180),'Teal: adapter    Gold: EUC references    Grip bore: 30.2 mm    Body-only fit scale: 1.003',font=font(24),fill='#40566a')
path=out/'deeper-seating-8mm-implemented.png';image.save(path);print(path)
