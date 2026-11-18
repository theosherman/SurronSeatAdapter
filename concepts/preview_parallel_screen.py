"""Review-only native screen-surround reinforcement; no manufacturing changes."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import import_step,GeomType,Plane,Keep,Solid,Compound,ShapeList,export_step,export_stl
(Path(__file__).resolve().parents[1]/'tmp').mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mesh_preview import render
from print_planes import trim_to_rear_print_planes
OUT=(Path(__file__).resolve().parents[1]/'tmp/concepts')
OUT.mkdir(parents=True,exist_ok=True)
body=import_step(ROOT/'exports/adapter-body.step')
planes=[f for f in body.faces() if f.geom_type==GeomType.PLANE]
rear=next(f for f in planes if f.area>2000 and -103<f.center().Y<-100 and f.normal_at().Y<-.99)
cliptop=next(f for f in planes if f.area>2000 and f.center().Y<-200 and f.normal_at().Z>.99)
y0=rear.center().Y;z0=rear.bounding_box().max.Z
y1=cliptop.bounding_box().max.Y
p,n=cliptop.center(),cliptop.normal_at();z1=p.Z-n.Y/n.Z*(y1-p.Y)
bottom=next(f for f in planes if f.area>4000 and abs(f.normal_at().X)<1e-6
            and f.normal_at().Z<-.99 and f.normal_at().Y<-.1)
slope=-bottom.normal_at().Y/bottom.normal_at().Z
z1=z0+slope*(y1-y0)
target=Plane((0,y0,z0),x_dir=(1,0,0),z_dir=(0,-slope,1))
slab=Solid.make_box(200,y0-y1,200,Plane((-100,y1,-50)))
# Keep the plan aperture exactly open. Existing lower sloped screen wall stays.
rails=[f for f in planes if f.area>800 and -160<f.center().Y<-145 and f.normal_at().Z>.99]
yfront=min(f.bounding_box().min.Y for f in rails)
aperture=Solid.make_box(86,y0-yfront,200,Plane((-43,yfront,-50)))
def shape(value):return Compound(value) if isinstance(value,(list,ShapeList)) else value
pieces=[]
for face in planes:
 normal=face.normal_at()
 if abs(normal.X)>1e-6 or normal.Z<.55 or face.area<500:continue
 if face.bounding_box().min.Y>=y0 or face.bounding_box().max.Y<=y1:continue
 candidate=shape(Solid.extrude(face,(0,0,100)).intersect(slab))
 if not candidate.solids():continue
 candidate=candidate.split(target,Keep.BOTTOM)
 if candidate is None:continue
 candidate=shape(shape(candidate).cut(aperture))
 if candidate.volume>1e-6:pieces.append(candidate)
proposed=trim_to_rear_print_planes(body.fuse(*pieces).clean())
assert proposed.is_valid and len(proposed.solids())==1
added=proposed.cut(body)
# No subtraction was intended: existing solid and all its functional surfaces stay.
missing=body.cut(proposed)
assert missing.volume<.001,missing.volume
export_step(proposed,OUT/'parallel-screen-proposed.step')
export_stl(proposed,OUT/'parallel-screen-proposed.stl',tolerance=.02,angular_tolerance=.08)
report=dict(previewOnly=True,authoritativeExportsChanged=False,startYZmm=[y0,z0],endYZmm=[y1,z1],
 topRiseAngleDegrees=float(np.degrees(np.arctan(abs(slope)))),addedVolumeMm3=added.volume,
 originalMaterialRemovedMm3=missing.volume,valid=proposed.is_valid,solids=len(proposed.solids()),
 screenPlanAperture=dict(widthMm=86,rearYmm=y0,frontYmm=yfront),
 bottomPlaneNormal=list(bottom.normal_at()), remainingRiseToClipMm=p.Z-n.Y/n.Z*(y1-p.Y)-z1, interpretation='At the same rear screen edge, run the new top parallel to the existing underside plane. Keep the remaining original uphill wall into the taller clip. Preserve all existing material and the aperture, underside, bore and printing planes.')
(OUT/'parallel-screen-report.json').write_text(json.dumps(report,indent=2)+'\n')
def mesh(s):
 v,t=s.tessellate(.04,.10)
 return np.array([list(p) for p in v])[np.array(t)]
old=mesh(body);new=mesh(proposed)
# New top is a single plane; highlight only added region's exterior faces.
normal=np.array([0,-slope,1]);normal/=np.linalg.norm(normal)
newtop=(np.max(abs((new-np.array([0,y0,z0]))@normal),axis=1)<1e-5)
oldfront=old[:,:,1].min(axis=1)<-179.157
before=[(old[~oldfront],(86,119,145)),(old[oldfront],(39,154,166))]
after=[(new[~newtop],(69,132,151)),(new[newtop],(64,184,169))]
dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
handle=np.frombuffer((ROOT/'exports/sherman-p-prepared/front-handle.stl').read_bytes(),dtype=dtype,offset=84)['v'].astype(float)
image=Image.new('RGB',(2400,1550),'#e9eef3');draw=ImageDraw.Draw(image)
font=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
draw.text((40,25),'SCREEN SURROUND / top parallel to the underside',font=font(37),fill='#183044')
draw.text((40,84),'Corrected interpretation: same starting point; follow the underside slope and retain the remaining rise into the clip',font=font(23),fill='#4c6074')
for k,(label,items) in enumerate([('CURRENT / top dips beside the screen',before),('PROPOSED / parallel top, remaining rise at clip',after)]):
 x=20+k*1190
 draw.text((x+18,150),label,font=font(27),fill='#183044')
 image.paste(render([(handle,(197,161,88))]+items,(1,-.45,.85),(1170,790),focus=(0,-150,27)),(x,195))
 image.paste(render([(handle,(197,161,88))]+items,(1,0,.01),(1170,355),focus=(0,-151,34)),(x,1015))
 draw=ImageDraw.Draw(image);draw.text((x+18,985),'Side profile / same underside and clip position',font=font(22),fill='#4c6074')
draw=ImageDraw.Draw(image)
draw.text((40,1390),f'Green: top parallel to underside ({report["topRiseAngleDegrees"]:.1f}° rise)   •   Screen aperture stays open   •   Added material: {added.volume:,.0f} mm³',font=font(24),fill='#183044')
draw.text((40,1440),'Short uphill wall into clip retained • underside and bore unchanged • both printing planes maintained',font=font(23),fill='#405b70')
draw.text((40,1500),'PREVIEW ONLY • current manufacturing model and exports unchanged',font=font(23),fill='#405b70')
image.save((Path(__file__).resolve().parents[1]/'tmp')/'parallel-screen-preview.png')
print(json.dumps(report))
