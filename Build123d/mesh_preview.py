"""Deterministic orthographic depth-buffer rendering for CAD mesh previews."""
import numpy as np
from PIL import Image

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

