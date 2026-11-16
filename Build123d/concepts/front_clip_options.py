"""Throwaway side-profile concepts; reads exports, never modifies manufacturing CAD."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.optimize import least_squares
from build123d import import_step, GeomType
(Path(__file__).resolve().parents[1]/'tmp').mkdir(parents=True,exist_ok=True)
R=Path(__file__).resolve().parents[1]
D=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
def mesh(p): return np.frombuffer(p.read_bytes(),dtype=D,offset=84)['v'].astype(float)
a=mesh(R/'exports/adapter-body.stl'); h=mesh(R/'exports/sherman-p-prepared/front-handle.stl')
s=import_step(R/'exports/adapter-body.step')
e=next(e for e in s.edges() if e.geom_type==GeomType.CIRCLE and e.arc_center.Y < -200 and 14<e.radius<16)
c=np.array([e.arc_center.Y,e.arc_center.Z]); r=e.radius
# Crown of the center section, with fixed known clip bore radius.
pts=[]
for tri in h:
 for i,j in ((0,1),(1,2),(2,0)):
  p,q=tri[i],tri[j]
  if p[0]*q[0]<0: pts.append((p+(q-p)*(-p[0]/(q[0]-p[0])))[1:])
pts=np.array(pts); crown=pts[pts[:,1]>pts[:,1].max()-3]
fit=least_squares(lambda p:np.linalg.norm(crown-p,axis=1)-r,[c[0],pts[:,1].max()-r],loss='soft_l1').x
dz=fit[1]-c[1]
W,H=1800,1080; im=Image.new('RGB',(W,H),'#f2f5f9');d=ImageDraw.Draw(im)
f=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
d.text((36,25),'Raised front clip / three profile concepts',font=f(34),fill='#183044')
d.text((36,78),'Existing adapter placement held fixed • gold: handle scan • blue: existing body • teal: proposed front',font=f(20),fill='#4c6074')
for k,(title,note,start,style) in enumerate([('A / Long rising transition','Cleanest continuous silhouette',-132,'ramp'),('B / Compact shoulder','Keeps the raised region short',-174,'step'),('C / Tapered rise + rib','More visual structure at the root',-151,'rib')]):
 left=22+k*594; top=135
 d.rounded_rectangle((left,top,left+572,1005),radius=15,fill='white')
 d.text((left+22,top+23),title,font=f(24),fill='#183044')
 d.text((left+22,top+62),note,font=f(18),fill='#4c6074')
 scale=3.65
 def xy(p):return(left+163+(p[0]-c[0])*scale,top+365-(p[1]-c[1])*scale)
 # Handle and current unaltered remaining body, projected from true meshes.
 for tri in h[np.argsort(h[:,:,0].mean(axis=1))]:d.polygon([xy(p[1:]) for p in tri],fill='#c7a14a')
 # Crop only for concept presentation, not a CAD operation.
 for tri in a[np.argsort(a[:,:,0].mean(axis=1))]:
  if tri[:,1].min()<c[0]+29:continue
  if tri[:,1].min()>-110:continue
  d.polygon([xy(p[1:]) for p in tri],fill='#4788b1')
 outer=r+10.5; end=c[0]+23
 base=c[1]+7; upper=base+22
 # Proposed raised root joins the fixed body at start and rises into clip shoulder.
 if style=='step': poly=[(start,base),(start,upper),(start-7,upper+dz),(end,fit[1]+outer-2),(end,fit[1]-1),(start-7,base+dz)]
 else: poly=[(start,base),(start,upper),(end,fit[1]+outer-2),(end,fit[1]-1)]
 d.polygon([xy(p) for p in poly],fill='#218f98')
 if style=='rib':
  p=[(start+7,base-8),(start+7,base),(end,fit[1]-1),(end+4,fit[1]-12)]
  d.polygon([xy(v) for v in p],fill='#166c79')
 # Preserve bore diameter and downward-open horseshoe character.
 ang=np.linspace(np.deg2rad(-23),np.deg2rad(203),150)
 ring=[fit+outer*np.array([np.cos(t),np.sin(t)]) for t in ang]
 ring += [fit+r*np.array([np.cos(t),np.sin(t)]) for t in ang[::-1]]
 d.polygon([xy(p) for p in ring],fill='#218f98')
 cx,cy=xy(fit)
 d.line((cx-21,cy,cx+21,cy),fill='#822b50',width=2);d.line((cx,cy-21,cx,cy+21),fill='#822b50',width=2)
 d.text((left+22,top+620),'Clip centered on inferred handle axis',font=f(18),fill='#183044')
 d.text((left+22,top+654),f'Concept rise: {dz:.1f} mm • bore: {2*r:.1f} mm',font=f(18),fill='#183044')
 d.text((left+22,top+711),'Side-profile study / front at left',font=f(18),fill='#4c6074')
 d.text((left+22,top+745),'Root thickness and jaw ends provisional',font=f(17),fill='#4c6074')
d.text((36,1030),'CONCEPTS ONLY • scan crown estimates handle axis • no fillets added • CAD unchanged • snap fit / strength not validated',font=f(19),fill='#4c6074')
out=(Path(__file__).resolve().parents[1]/'tmp')/'front-clip-raised-options.png';im.save(out)
print({'preview':str(out),'clipCenterYZ':c.tolist(),'estimatedHandleCenterYZ':fit.tolist(),'riseMm':dz})
