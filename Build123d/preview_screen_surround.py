"""Inspection views rendered from the implemented manufacturing STEP."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import import_step,GeomType,Plane,Keep
from mesh_preview import render
ROOT=Path(__file__).resolve().parent
proposed=import_step(ROOT/'exports/adapter-body.step')
ramp=next(f for f in proposed.faces() if f.geom_type==GeomType.PLANE and f.area>3000
          and .81<f.normal_at().Y<.83 and .57<f.normal_at().Z<.58)
n=ramp.normal_at()
def mesh(shape,cutaway=False):
 if cutaway:shape=shape.split(Plane((0,-123,0),z_dir=(0,1,0)),Keep.BOTTOM)
 v,t=shape.tessellate(.025,.07);a=np.array([list(p) for p in v])[np.array(t)]
 if cutaway:a=a[np.max(abs(a[:,:,1]+123),axis=1)>1e-5]
 return a

def colors(a):
 normals=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
 rampmask=(normals@np.array(list(n))>.999999)
 parallel=(abs(normals[:,1]-.1184039683)<1e-5)&(abs(normals[:,2]-.9929655081)<1e-5)
 return [(a[~(rampmask|parallel)],(66,128,150)),(a[parallel],(65,183,168)),(a[rampmask],(112,157,198))]
full=colors(mesh(proposed));detail=colors(mesh(proposed,True))
image=Image.new('RGB',(2400,1500),'#e9eef3');d=ImageDraw.Draw(image)
f=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
d.text((40,25),'IMPLEMENTED / parallel sides + uninterrupted front slope',font=f(35),fill='#183044')
d.text((40,82),'The added upright ledge is removed; the original screen-front incline continues directly into the clip',font=f(23),fill='#4c6074')
for k,(title,items,eye,focus) in enumerate([
 ('From the screen opening toward the clip',detail,(.65,1,.78),(0,-191,31)),
 ('Side view / reinforced walls, continuous front ramp',full,(1,.22,.18),(0,-172,31))]):
 x=20+k*1190;d.text((x+20,150),title,font=f(25),fill='#183044')
 image.paste(render(items,eye,(1170,1050),focus=focus),(x,195));d=ImageDraw.Draw(image)
d.text((40,1300),'Green: reinforced top parallel to underside     Blue: one continuous existing incline into the clip',font=f(25),fill='#183044')
d.text((40,1360),'Added height remains at the sides • no extra front ledge • no fillets • underside, clip bore and printing planes retained',font=f(23),fill='#405b70')
d.text((40,1440),'Actual manufacturing STEP • rear hidden only in the left inspection view',font=f(23),fill='#405b70')
image.save(ROOT/'exports/screen-surround-implemented.png');print(ROOT/'exports/screen-surround-implemented.png')
