"""Remove only the proposal's new front ledge; retain original continuous ramp."""
from pathlib import Path
Path('/tmp/surron-seat-adapter-previews/Build123d/exports').mkdir(parents=True,exist_ok=True)
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import import_step,GeomType,Face,Wire,Solid,Plane,Keep,export_step,export_stl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mesh_preview import render
OUT=Path('/tmp/surron-seat-adapter-previews/Build123d/exports/concepts')
OUT.mkdir(parents=True,exist_ok=True)
original=import_step(ROOT/'exports/adapter-body.step')
previous=import_step(OUT/'parallel-screen-proposed.step')
ramp=next(f for f in original.faces() if f.geom_type==GeomType.PLANE and f.area>3000
          and .81<f.normal_at().Y<.83 and .57<f.normal_at().Z<.58)
p,n=ramp.center(),ramp.normal_at();slope=-n.Y/n.Z
z=lambda y:p.Z+slope*(y-p.Y)
ymin=ramp.bounding_box().min.Y;ymax=ramp.bounding_box().max.Y
# Only the central 86 mm screen/front-ramp band: added sidewalls remain.
points=[(-43,ymin,z(ymin)),(-43,ymax,z(ymax)),(-43,ymax,150),(-43,ymin,150)]
tool=Solid.extrude(Face(Wire.make_polygon(points,close=True)),(86,0,0))
proposed=previous.cut(tool).clean()
assert proposed.is_valid and len(proposed.solids())==1
missing=original.cut(proposed)
assert missing.volume<.001,missing.volume
upright=[f for f in proposed.faces() if f.geom_type==GeomType.PLANE and f.normal_at().Y>.999
         and -181<f.center().Y<-175 and f.area>1]
assert not upright,'Added front ledge remains'
newramp=next(f for f in proposed.faces() if f.geom_type==GeomType.PLANE
            and f.normal_at().dot(n)>.999999 and f.area>3000)
export_step(proposed,OUT/'continuous-screen-ramp-proposed.step')
export_stl(proposed,OUT/'continuous-screen-ramp-proposed.stl',tolerance=.02,angular_tolerance=.08)
report=dict(previewOnly=True,authoritativeExportsChanged=False,valid=proposed.is_valid,
 solids=len(proposed.solids()),addedVolumeMm3=proposed.volume-original.volume,
 removedFromPriorProposalMm3=previous.volume-proposed.volume,originalMaterialRemovedMm3=missing.volume,
 addedFrontUprightFaces=len(upright),continuousRampNormal=list(newramp.normal_at()),
 rampYBoundsMm=[newramp.bounding_box().min.Y,newramp.bounding_box().max.Y],
 interpretation='Retain the parallel reinforced sidewalls; remove only added material above the original central screen-front ramp so its incline is uninterrupted into the clip. No fillets.')
(OUT/'continuous-screen-ramp-report.json').write_text(json.dumps(report,indent=2)+'\n')

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
d.text((40,25),'REVISED JOIN / parallel sidewalls + uninterrupted front slope',font=f(35),fill='#183044')
d.text((40,82),'The added upright ledge is removed; the original screen-front incline continues directly into the clip',font=f(23),fill='#4c6074')
for k,(title,items,eye,focus) in enumerate([
 ('From the screen opening toward the clip',detail,(.65,1,.78),(0,-191,31)),
 ('Side view / reinforced walls, continuous front ramp',full,(1,.22,.18),(0,-172,31))]):
 x=20+k*1190;d.text((x+20,150),title,font=f(25),fill='#183044')
 image.paste(render(items,eye,(1170,1050),focus=focus),(x,195));d=ImageDraw.Draw(image)
d.text((40,1300),'Green: reinforced top parallel to underside     Blue: one continuous existing incline into the clip',font=f(25),fill='#183044')
d.text((40,1360),'Added height remains at the sides • no extra front ledge • no fillets • underside, clip bore and printing planes retained',font=f(23),fill='#405b70')
d.text((40,1440),'PREVIEW ONLY • manufacturing geometry unchanged • rear hidden in the left inspection view',font=f(23),fill='#405b70')
image.save(Path('/tmp/surron-seat-adapter-previews/Build123d/exports')/'continuous-screen-ramp-preview.png');print(json.dumps(report))
