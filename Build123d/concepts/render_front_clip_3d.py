"""Shaded 3D mesh studies only. No manufacturing exports or CAD source edits."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
(Path(__file__).resolve().parents[1]/'tmp').mkdir(parents=True,exist_ok=True)
R=Path(__file__).resolve().parents[1]
D=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
def read(p):return np.frombuffer(p.read_bytes(),dtype=D,offset=84)['v'].astype(float)
a=read(R/'exports/adapter-body.stl');h=read(R/'exports/sherman-p-prepared/front-handle.stl')
f=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
W,H=2400,1670
im=Image.new('RGB',(W,H),'#e9eef3');d=ImageDraw.Draw(im)
d.text((45,28),'FRONT CLIP / raised transition studies',font=f(40),fill='#183044')
d.text((45,88),'Actual adapter + handle meshes • three provisional front profiles • same camera and scale for comparison',font=f(23),fill='#4c6074')

def render(meshes,eye,size,focus=None):
 w,hh=size;eye=np.array(eye,dtype=float);eye/=np.linalg.norm(eye)
 right=np.cross([0,0,1],eye);right/=np.linalg.norm(right);up=np.cross(eye,right)
 basis=np.array([right,up,eye]).T
 verts=np.concatenate([m.reshape(-1,3) for m,col in meshes]);pr=verts@basis
 if focus is None:lo=pr[:,:2].min(0);hi=pr[:,:2].max(0)
 else:
  q=np.array(focus)@basis;lo=q[:2]-np.array([105,82]);hi=q[:2]+np.array([105,82])
 mid=(hi+lo)/2;scale=min((w-65)/(hi[0]-lo[0]),(hh-55)/(hi[1]-lo[1]))
 pix=np.empty((hh,w,3),dtype=np.uint8);pix[:]=[249,251,253];depth=np.full((hh,w),-np.inf)
 light=eye+up*.8-right*.45;light/=np.linalg.norm(light)
 for mesh,color in meshes:
  normals=np.cross(mesh[:,1]-mesh[:,0],mesh[:,2]-mesh[:,0]);ln=np.linalg.norm(normals,axis=1);normals/=np.maximum(ln[:,None],1e-12)
  proj=mesh@basis;xy=(proj[:,:,:2]-mid)*[scale,-scale]+[w/2,hh/2]
  for j in range(len(mesh)):
   if ln[j]<1e-10:continue
   pp=xy[j];xmin=max(0,int(pp[:,0].min()));xmax=min(w-1,int(pp[:,0].max()+1));ymin=max(0,int(pp[:,1].min()));ymax=min(hh-1,int(pp[:,1].max()+1))
   if xmax<xmin or ymax<ymin:continue
   (ax,ay),(bx,by),(cx,cy)=pp;den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
   if abs(den)<1e-9:continue
   xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
   u=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/den;v=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/den;ww=1-u-v
   z=u*proj[j,0,2]+v*proj[j,1,2]+ww*proj[j,2,2];old=depth[ymin:ymax+1,xmin:xmax+1]
   mask=(u>=0)&(v>=0)&(ww>=0)&(z>old)
   normal=normals[j]
   if normal@eye<0:normal=-normal
   shade=.40+.60*max(0,normal@light)
   col=np.clip(np.array(color)*shade,0,255).astype(np.uint8)
   old[mask]=z[mask];pix[ymin:ymax+1,xmin:xmax+1][mask]=col
 return Image.fromarray(pix)

for k,(name,desc,end,kind) in enumerate([
 ('A / Swept rise','Long, gradual lift into the existing clip',-105,'linear'),
 ('B / Short shoulder','Compact lift concentrated near the clip',-158,'linear'),
 ('C / Sculpted transition','Progressive rise with a gentler root',-128,'smooth')]):
 m=a.copy();t=np.clip((end-m[:,:,1])/(end+194),0,1)
 if kind=='smooth':t=t*t*(3-2*t)
 m[:,:,2]+=18.052632*t
 # Color change marks only the proposed region; no material seam is intended.
 changed=t.max(1)>1e-8
 meshes=[(h,(197,161,88)),(m[~changed],(86,119,145)),(m[changed],(39,154,166))]
 x=20+k*795
 d=ImageDraw.Draw(im);d.rounded_rectangle((x,150,x+775,1570),radius=18,fill='#f9fbfd')
 d.text((x+25,173),name,font=f(31),fill='#183044');d.text((x+25,221),desc,font=f(21),fill='#526577')
 im.paste(render(meshes,(1,-.65,.64),(765,660),focus=(0,-180,15)),(x+5,270))
 d=ImageDraw.Draw(im);d.text((x+25,926),'Front detail / oblique view',font=f(22),fill='#526577')
 im.paste(render(meshes,(1,0,.20),(765,490)),(x+5,967))
 d=ImageDraw.Draw(im);d.text((x+25,1468),'Full adapter / fixed body placement',font=f(22),fill='#526577')
 d.text((x+25,1510),'Teal = proposed rise; slate = retained body',font=f(19),fill='#526577')
d=ImageDraw.Draw(im);d.text((42,1595),'PREVIEW ONLY • approximately 18 mm rise • existing clip bore retained • no manufacturing CAD changed',font=f(23),fill='#344f64')
d.text((42,1630),'Mesh deformation studies show proportions and appearance; jaw engagement, wall thickness and strength still require CAD validation.',font=f(20),fill='#526577')
out=(Path(__file__).resolve().parents[1]/'tmp')/'front-clip-3d-options.png';im.save(out);print(out)
