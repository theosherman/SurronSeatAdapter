"""Additional views of the unchanged parallel-screen proposal."""
from pathlib import Path
(Path(__file__).resolve().parents[1]/'tmp').mkdir(parents=True,exist_ok=True)
import sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import import_step,GeomType,Plane,Keep
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mesh_preview import render
s=import_step((Path(__file__).resolve().parents[1]/'tmp')/'concepts/parallel-screen-proposed.step')
display=s.split(Plane((0,-123,0),z_dir=(0,1,0)),Keep.BOTTOM)
v,t=display.tessellate(.025,.07);m=np.array([list(p) for p in v])[np.array(t)]
# Crop only the view to remove the rear body that would hide the junction.
# No edges or faces are changed in the actual proposal.
visible=np.max(abs(m[:,:,1]+123),axis=1)>1e-5
m=m[visible]
normal=np.cross(m[:,1]-m[:,0],m[:,2]-m[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
newtop=(abs(normal[:,1]-.1184039683)<1e-5)&(abs(normal[:,2]-.9929655081)<1e-5)
ramp=(abs(normal[:,1]-.8191520443)<1e-5)&(abs(normal[:,2]-.5735764364)<1e-5)
# The retained screen front wall and added extension have different normals.
wall=(abs(normal[:,1]-1)<1e-6)&(m[:,:,1].mean(axis=1)<-175)&(m[:,:,1].mean(axis=1)>-181)
meshes=[(m[~(newtop|ramp|wall)],(66,128,150)),(m[newtop],(65,183,168)),
        (m[ramp],(112,157,198)),(m[wall],(224,154,77))]
image=Image.new('RGB',(2400,1490),'#e9eef3');d=ImageDraw.Draw(image)
f=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
d.text((38,25),'SCREEN-TO-CLIP JOIN / additional inspection angles',font=f(37),fill='#183044')
d.text((38,82),'Same proposed solid • rear body hidden in these views to expose the junction • no geometry changes',font=f(23),fill='#4c6074')
for k,(title,eye) in enumerate([('From the screen opening, looking toward the clip',(.65,1,.78)),('Close side view of the clip transition',(1,.22,.18))]):
 x=20+k*1190
 d.text((x+20,151),title,font=f(25),fill='#183044')
 image.paste(render(meshes,eye,(1170,1040),focus=(0,-191,31)),(x,196))
 d=ImageDraw.Draw(image)
d.text((40,1285),'Green: parallel top     Blue: retained uphill ramp     Orange: added upright extension at the screen edge',font=f(24),fill='#183044')
d.text((40,1340),'The orange face is a real extra wall in this proposal. These views make it visible for review.',font=f(24),fill='#405b70')
d.text((40,1410),'PREVIEW ONLY • manufacturing model untouched • reference scan hidden so it cannot obscure the join',font=f(23),fill='#405b70')
image.save((Path(__file__).resolve().parents[1]/'tmp')/'parallel-screen-join-angles.png')
print('Orange wall triangles:',int(wall.sum()))
for face in s.faces():
 if face.geom_type==GeomType.PLANE and face.normal_at().Y>.999 and -181<face.center().Y<-175:
  print('Upright screen-front extension:',face.area,tuple(face.center()),tuple(face.bounding_box().min),tuple(face.bounding_box().max))
