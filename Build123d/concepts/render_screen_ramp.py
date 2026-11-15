"""Preview interpretation: continue screen front ramp, thicken above retained underside."""
exec((__import__('pathlib').Path(__file__).parent/'render_front_clip_3d.py').read_text().split('for k,(name,desc,end,kind)')[0])
from build123d import import_step,GeomType
s=import_step(R/'exports/adapter-body.step')
ramp=next(face for face in s.faces() if face.geom_type==GeomType.PLANE and face.area>1500 and -176<face.center().Y<-170 and face.normal_at().Y>.8)
p=ramp.center();n=ramp.normal_at();slope=-n.Y/n.Z
# Refine only the transition so its nonlinear top profile is represented faithfully.
fixed=a[a[:,:,1].min(axis=1)>=-165]
local=a[a[:,:,1].min(axis=1)<-165]
for _ in range(2):
 v0,v1,v2=local[:,0],local[:,1],local[:,2]
 ab=(v0+v1)/2;bc=(v1+v2)/2;ca=(v2+v0)/2
 local=np.concatenate([np.stack(q,axis=1) for q in [(v0,ab,ca),(ab,v1,bc),(ca,bc,v2),(ab,bc,ca)]])
a=np.concatenate([fixed,local])
m=a.copy();y=a[:,:,1];z=a[:,:,2]
bottom=8.88-(.118/.993)*(y+140.99)
top=36.66-(.118/.993)*(y+181.11)
plane=p.Z+slope*(y-p.Y)
# Front-most top edge of the real screen ramp is the fixed starting datum.
y0=-179.2; yjoin=-205.0;lift=18.052632
cliptop=14.821609618179+lift+25.6
raisedtop=np.maximum(top,np.minimum(plane,cliptop))
gain=np.where(y<y0,raisedtop-top,0)
t=np.clip((y0-y)/(y0-yjoin),0,1)
bottomgain=lift*t
weight=np.clip((z-bottom)/(top-bottom),0,1)
delta=bottomgain+(gain-bottomgain)*weight
# Keep the full original jaw profile at its new center.
delta=np.where(y<yjoin,lift,delta)
delta=np.where(y>=y0,0,delta)
m[:,:,2]+=delta
changed=np.max(abs(delta),axis=1)>1e-6
meshes=[(h,(197,161,88)),(m[~changed],(86,119,145)),(m[changed],(39,154,166))]
im=Image.new('RGB',(2200,1490),'#e9eef3');d=ImageDraw.Draw(im)
d.text((40,25),'CONTINUE THE SCREEN RAMP / thicker front connection',font=f(36),fill='#183044')
d.text((40,82),'One concept based on your description • original screen opening retained • clip raised to estimated handle center',font=f(22),fill='#4c6074')
im.paste(render(meshes,(1,-.55,.68),(1250,1000),focus=(0,-166,20)),(20,145))
im.paste(render(meshes,(1,0,.02),(900,660),focus=(0,-178,25)),(1290,170))
d=ImageDraw.Draw(im)
d.text((1320,145),'Side view / thickness and underside',font=f(24),fill='#183044')
d.text((1320,850),'Interpretation shown',font=f(27),fill='#183044')
for j,line in enumerate(['1  Retain the body and underside behind','    the front edge of the screen opening.','2  Continue the existing screen-front incline','    upward into a thicker front bridge.','3  Meet the raised clip at the front; keep','    its existing bore and jaw profile.']):
 d.text((1320,905+37*j),line,font=f(22),fill='#405b70')
d.text((45,1170),'Oblique view / screen opening and raised bridge',font=f(26),fill='#183044')
d.text((45,1220),'Teal: reshaped front     Slate: retained adapter     Gold: actual front-handle scan',font=f(23),fill='#405b70')
d.text((45,1280),f'Existing screen-front ramp measured from CAD: {np.degrees(np.arctan(abs(slope))):.1f}° to horizontal.',font=f(23),fill='#405b70')
d.text((45,1330),'The incline continues toward the clip; extra material builds thickness instead of lifting the whole underside.',font=f(23),fill='#405b70')
d.text((45,1410),'PREVIEW ONLY • mesh shape study, not a validated solid • manufacturing CAD and body placement unchanged',font=f(22),fill='#405b70')
out=R/'exports/front-clip-screen-ramp-preview.png';im.save(out);print(out)
