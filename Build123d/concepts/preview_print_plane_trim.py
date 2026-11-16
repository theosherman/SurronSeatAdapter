"""Native cutting-plane proposal only; never overwrites manufacturing CAD."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import import_step,GeomType,Plane,Keep,export_step,export_stl
Path('/tmp/surron-seat-adapter-previews/Build123d/exports').mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from mesh_preview import render
OUT=Path('/tmp/surron-seat-adapter-previews/Build123d/exports/concepts')
OUT.mkdir(parents=True,exist_ok=True)
body=import_step(ROOT/'exports/adapter-body.step')
faces=[f for f in body.faces() if f.geom_type==GeomType.PLANE and f.area>5000
       and abs(f.normal_at().X)>.85 and f.center().Y>0]
assert len(faces)==2
if max(max((v.center()-f.center()).dot(f.normal_at()) for v in body.vertices()) for f in faces)<1e-3:
 raise ValueError('Historical preview requires the untrimmed raised-front-clip checkpoint; current exports are already trimmed')
trimmed=body
report={'previewOnly':True,'authoritativeExportsChanged':False,'planes':[]}
for face in sorted(faces,key=lambda f:f.normal_at().X):
 p,n=face.center(),face.normal_at()
 report['planes'].append({'pointMm':list(p),'outwardNormal':list(n),
    'maxOriginalProtrusionMm':max((v.center()-p).dot(n) for v in body.vertices())})
 trimmed=trimmed.split(Plane(p,z_dir=n),Keep.BOTTOM).clean()
assert trimmed.is_valid and len(trimmed.solids())==1
removed=body.cut(trimmed)
report.update(originalVolumeMm3=body.volume,proposedVolumeMm3=trimmed.volume,
 removedVolumeMm3=removed.volume,proposedValid=trimmed.is_valid,proposedSolids=len(trimmed.solids()))
for face,entry in zip(sorted(faces,key=lambda f:f.normal_at().X),report['planes']):
 p,n=face.center(),face.normal_at()
 entry['maxProposedProtrusionMm']=max((v.center()-p).dot(n) for v in trimmed.vertices())
assert max(e['maxProposedProtrusionMm'] for e in report['planes'])<1e-5
export_step(trimmed,OUT/'print-plane-trim-proposed.step')
export_stl(trimmed,OUT/'print-plane-trim-proposed.stl',tolerance=.02,angular_tolerance=.08)

def mesh(shape):
 v,t=shape.tessellate(.04,.10)
 return np.array([list(p) for p in v])[np.array(t)]
retained=mesh(trimmed);scrap=mesh(removed)
# Highlight the exact planar patches produced by the two proposed cuts.
normals=np.cross(retained[:,1]-retained[:,0],retained[:,2]-retained[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
cut=np.zeros(len(retained),dtype=bool)
for entry in report['planes']:
 p=np.array(entry['pointMm']);n=np.array(entry['outwardNormal'])
 cut |= (abs(normals@n)>.999999)&(np.max(abs((retained-p)@n),axis=1)<1e-5)&(retained[:,:,1].mean(axis=1)<-165)
front=retained[:,:,1].min(axis=1)<-179.157
unchanged=[(retained[~front],(86,119,145)),(retained[front&~cut],(39,154,166))]
after=unchanged+[(retained[cut],(93,194,158))]
before=[(retained,(69,132,151)),(scrap,(236,115,60))]
# Include handle in close-up only, for context.
dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
handle=np.frombuffer((ROOT/'exports/sherman-p-prepared/front-handle.stl').read_bytes(),dtype=dtype,offset=84)['v'].astype(float)
image=Image.new('RGB',(2400,1580),'#e9eef3');draw=ImageDraw.Draw(image)
font=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
draw.text((42,24),'RESTORE THE PRINT-BED PLANES / proposed trim',font=font(39),fill='#183044')
draw.text((42,83),'Extend the existing rear side planes through the entire adapter • mirror trim on both sides • no change to body placement',font=font(23),fill='#4c6074')
for k,(title,items) in enumerate([('BEFORE / orange material sits beyond the rear planes',before),('PROPOSED / green faces share the rear printing planes',after)]):
 x=20+k*1190
 draw.text((x+18,150),title,font=font(25),fill='#183044')
 image.paste(render([(handle,(197,161,88))]+items,(1,-.55,.68),(1170,800),focus=(0,-173,25)),(x,196))
# Lay the actual right-hand plane flat on an illustrative bed, using a rigid
# display transform only. The original/proposed source solids keep their frame.
entry=report['planes'][1];p=np.array(entry['pointMm']);n=np.array(entry['outwardNormal'])
def onbed(m):
 q=m-p
 return np.stack([q[:,:,0]*n[2]-q[:,:,2]*n[0],q[:,:,1],-(q@n)],axis=-1)
for k,items in enumerate([before,after]):
 x=20+k*1190
 image.paste(render([(onbed(m),col) for m,col in items],(0,-1,0),(1170,340),focus=(-65,0,45)),(x,1040))
 draw=ImageDraw.Draw(image)
 # Same projection extents as renderer focus: 210 x 164 mm.
 scale=min((1170-65)/210,(340-55)/164)
 bed=1040+170+45*scale
 draw.line((x+25,bed,x+1145,bed),fill='#4b5e71',width=3)
 draw.text((x+35,bed+12),'PRINT BED / existing right rear face aligned flat',font=font(18),fill='#4c6074')
 draw.text((x+20,1008),'End view / displayed in print orientation',font=font(23),fill='#183044')
draw=ImageDraw.Draw(image)
draw.text((42,1415),f'Maximum protrusion: {report["planes"][0]["maxOriginalProtrusionMm"]:.2f} mm   •   Proposed total removal: {removed.volume:,.0f} mm³   •   Result: one valid native solid',font=font(24),fill='#183044')
draw.text((42,1460),'Orange: proposed removal   •   Green: new coplanar contact faces   •   Gold: front-handle reference',font=font(23),fill='#405b70')
draw.text((42,1520),'PREVIEW ONLY • authoritative adapter untouched • both cuts use the exact rear-face planes, with no offset',font=font(23),fill='#405b70')
image.save(Path('/tmp/surron-seat-adapter-previews/Build123d/exports')/'print-plane-trim-preview.png')
(OUT/'print-plane-trim-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
