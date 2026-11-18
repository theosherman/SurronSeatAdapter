"""Render the implemented lower toe and wall from manufacturing STEP."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parent;sys.path.insert(0,str(root))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import *
from mesh_preview import render
from trunk_cavity import REAR_TIP_POINT_MM,REAR_TIP_NORMAL,REAR_TIP_WALL_THICKNESS_MM,rear_cavity_tool
from adapter import SKETCHES
from coordinates import ADAPTER_TRANSLATION_MM
s=import_step(root/'exports/adapter-body.step');l=import_step(root/'exports/latch.step')
p,n=Vector(REAR_TIP_POINT_MM),Vector(REAR_TIP_NORMAL)
a=s.split(Plane(p-n*REAR_TIP_WALL_THICKNESS_MM,z_dir=n),Keep.TOP)
if isinstance(a,(list,ShapeList)):a=Compound(a)
a=a.split(Plane(p,z_dir=(0,0,1)),Keep.BOTTOM)
cavity=rear_cavity_tool(SKETCHES['BodyCutSketch']).translate(ADAPTER_TRANSLATION_MM)
cut_faces=[f for f in s.faces() if f.geom_type==GeomType.PLANE and f.normal_at().dot(n)>.999999]
minimum=min(f.distance_to(cavity) for f in cut_faces)
assert minimum>=REAR_TIP_WALL_THICKNESS_MM-1e-5
im=Image.new('RGB',(1900,1350),'#f9fbfd');d=ImageDraw.Draw(im);font=lambda z:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',z)
def mesh(s):
 v,t=s.tessellate(.1,.2);return np.array([[tuple(v[i]) for i in row] for row in t])
def section_faces(s):
 cut=s.split(Plane.YZ,Keep.BOTTOM)
 if isinstance(cut,(list,ShapeList)):cut=Compound(cut)
 return [f for f in cut.faces() if f.geom_type==GeomType.PLANE and abs(f.center().X)<1e-5 and abs(f.normal_at().X)>.999]
# Highlight retained cavity material in orange in the section views.
def drawsection(shapes,box,limits):
 tile=Image.new('RGB',(box[2],box[3]),'#ffffff');dd=ImageDraw.Draw(tile)
 y0,y1,z0,z1=limits;scale=min((box[2]-40)/(y1-y0),(box[3]-40)/(z1-z0))
 def xy(p):return (20+(p[1]-y0)*scale,box[3]-20-(p[2]-z0)*scale)
 for shape,color in shapes:
  for f in section_faces(shape):
   v,t=f.tessellate(.05,.15)
   for row in t:dd.polygon([xy(tuple(v[i])) for i in row],fill=color)
 im.paste(tile,(box[0],box[1]));return xy

d.text((35,22),f'IMPLEMENTED LOWER CUT + {REAR_TIP_WALL_THICKNESS_MM:g} mm LOCAL CAVITY WALL',font=font(30),fill='#203b50')
d.text((35,78),f'Original cavity cutter limited locally; orange marks the lower {REAR_TIP_WALL_THICKNESS_MM:g} mm wall zone. Seat support and latch preserved.',font=font(21),fill='#526b7d')
im.paste(render([(mesh(s),(48,152,177)),(mesh(l),(58,157,108))],(1,.12,-.1),(950,520)),(15,135))
drawsection([(s,'#3098b1'),(a,'#e99549')],(990,160,880,470),(125,195,-40,25))
d=ImageDraw.Draw(im);d.text((35,130),'COMPLETE ADAPTER',font=font(23),fill='#203b50');d.text((1015,125),'CENTER SECTION / REAR WALL CLOSE-UP',font=font(23),fill='#203b50')
drawsection([(s,'#3098b1'),(a,'#e99549')],(30,730,1830,410),(-250,270,-50,115))
d=ImageDraw.Draw(im);d.text((35,680),'COMPLETE CENTER SECTION / WHITE IS OPEN CAVITY',font=font(24),fill='#203b50')
d.text((40,1180),f'New diagonal cut to adjusted cavity: {minimum:.3f} mm minimum measured distance.',font=font(24),fill='#203b50')
d.text((40,1230),'Approved exterior cut and remaining cavity preserved.',font=font(23),fill='#203b50')
d.text((40,1280),'Actual manufacturing STEP / validated geometry',font=font(22),fill='#526b7d')
im.save(root/'exports/rear-tip-implemented.png')
(root/'tmp').mkdir(exist_ok=True)
im.save(root/'tmp/rear-tip-implemented.png')
