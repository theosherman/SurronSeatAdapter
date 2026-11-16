"""Render the implemented cavity from current manufacturing STEP exports."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import import_step,Plane,Keep,Compound,ShapeList
from mesh_preview import render
root=Path(__file__).resolve().parent
s=import_step(root/'exports/adapter-body.step')
def mesh(s):
 v,t=s.tessellate(.08,.15)
 return np.array([[tuple(v[i]) for i in row] for row in t])
cut=s.split(Plane((0,0,0),z_dir=(1,0,0)),Keep.BOTTOM)
if isinstance(cut,(list,ShapeList)):cut=Compound(cut)
im=Image.new('RGB',(2200,1550),'#f9fbfd');d=ImageDraw.Draw(im)
f=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
d.text((40,22),'IMPLEMENTED / LONG CAVITY + REAR SIDE CUTOUTS',font=f(36),fill='#203b50')
d.text((40,82),'Actual manufacturing STEP / single cavity roof / separate latch unchanged',font=f(25),fill='#526b7d')
d.text((40,130),'UNDERSIDE',font=f(25),fill='#203b50');d.text((1140,130),'CENTER CUTAWAY',font=f(25),fill='#203b50')
im.paste(render([(mesh(s),(48,152,177))],(.22,-.18,-1),(1080,1200)),(10,150))
im.paste(render([(mesh(cut),(48,152,177))],(1,.3,-.2),(1080,1200)),(1110,150))
d=ImageDraw.Draw(im)
d.text((40,1380),'One controlling pocket; symmetric rear side relief; continuous rear bridge.',font=f(26),fill='#203b50')
d.text((40,1430),'Roof: 18.5 mm offset; 10 mm minimum in interior roof-normal samples.',font=f(26),fill='#203b50')
d.text((40,1480),'Manufacturing validation recorded in logs. Physical fit and strength untested.',font=f(25),fill='#526b7d')
im.save(root/'exports/rear-cavity-implemented.png')
# Publish the same implemented view to the user's live preview browser.
preview=root/'tmp/requested-cavity-preview'
preview.mkdir(parents=True,exist_ok=True)
im.save(preview/'preview.png')
