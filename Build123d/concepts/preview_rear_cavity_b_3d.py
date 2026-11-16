"""Option B mesh proportion study, separate from manufacturing geometry."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build123d import Face,Wire,Solid,import_step,GeomType
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from preview_front_clip import load
from mesh_preview import render
(Path(__file__).resolve().parents[1]/'tmp').mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[1];OUT=(Path(__file__).resolve().parents[1]/'tmp/concepts/rear-cavity/option-b-3d')
OUT.mkdir(parents=True,exist_ok=True)
font=lambda n:ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
BLUE=(87,148,187);TEAL=(36,163,173);GREEN=(70,166,113);DARKGREEN=(35,119,82);GOLD=(220,171,73)
SHIFT=25.0
original=load(ROOT/'exports/adapter-body.stl'); latch=load(ROOT/'exports/latch.stl')
wheel=load(ROOT/'exports/sherman-p-prepared/body-scaled.stl');handle=load(ROOT/'exports/sherman-p-prepared/rear-handle.stl')
# This continuous mesh map illustrates proportions only. Production changes must
# instead rebuild the pocket, wall, and dovetail and reapply the approved cutter.
a=original.copy();y=a[:,:,1];z=a[:,:,2]
weight=np.clip((y-90)/25,0,1)*np.clip((82-z)/17,0,1)
a[:,:,1]-=SHIFT*weight
# Extend the actual adapter-facing front/top planes, preserving the original
# hook/contact geometry. This fills the top transition rather than warping it.
native_latch=import_step(ROOT/'exports/latch.step')
mating=[f for f in native_latch.faces() if f.geom_type==GeomType.PLANE
        and f.normal_at().Y < -.3 and f.center().Z > 0]
extensions=[Solid.extrude(f,(0,-SHIFT,0)) for f in mating]
latch_study=native_latch.fuse(*extensions).clean()
assert latch_study.is_valid and len(latch_study.solids())==1
vs,ts=latch_study.tessellate(.025,.08)
l=np.array([[tuple(vs[i]) for i in t] for t in ts])
changed_a=weight.max(1)>1e-7

def write_stl(path,mesh):
    dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);data=np.zeros(len(mesh),dtype=dt)
    data['v']=mesh;n=np.cross(mesh[:,1]-mesh[:,0],mesh[:,2]-mesh[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12);data['n']=n
    path.write_bytes(b'OPTION B CONCEPT ONLY'.ljust(80,b' ')+len(mesh).to_bytes(4,'little')+data.tobytes())
write_stl(OUT/'adapter-concept.stl',a);write_stl(OUT/'latch-concept.stl',l)

def cut(mesh,x=.1):
    result=[];segments=[]
    for tri in mesh:
        pts=[];hits=[]
        for i in range(3):
            p=tri[i];q=tri[(i+1)%3];ip=p[0]<=x;iq=q[0]<=x
            if ip:pts.append(p)
            if ip!=iq:
                hit=p+(q-p)*((x-p[0])/(q[0]-p[0]));pts.append(hit);hits.append(hit)
        if len(hits)==2:segments.append(hits)
        for i in range(1,len(pts)-1):result.append([pts[0],pts[i],pts[i+1]])
    # Cap section loops for readable solid cut faces, not manufacturing exports.
    edges={};adj={}
    for i,seg in enumerate(segments):
        pair=tuple(tuple(np.round(p,4)) for p in seg);edges[i]=pair
        for p in pair:adj.setdefault(p,set()).add(i)
    caps=[]
    while edges:
        idx=next(iter(edges));p,q=edges.pop(idx);chain=[p,q]
        while chain[-1]!=chain[0]:
            ids=[i for i in adj[chain[-1]] if i in edges]
            if not ids:break
            p,q=edges.pop(ids[0]);chain.append(q if p==chain[-1] else p)
        if chain[-1]==chain[0] and len(chain)>3:
            try:
                f=Face(Wire.make_polygon(chain[:-1],close=True));vs,ts=f.tessellate(.08)
                caps.extend([[tuple(vs[i]) for i in t] for t in ts])
            except Exception as exc:print('Uncapped display loop:',exc)
    return np.array(result),np.array(caps).reshape(-1,3,3)

def colored(adapter,latch,cutaway=False,explode=False):
    changed_l=np.zeros(len(latch),dtype=bool) if latch is globals()['latch'] else (latch[:,:,1]+.65*latch[:,:,2]).mean(1)<195
    groups=[(adapter[~changed_a],BLUE),(adapter[changed_a],TEAL),
            (latch[~changed_l]+([0,48,-10] if explode else [0,0,0]),GREEN),
            (latch[changed_l]+([0,48,-10] if explode else [0,0,0]),DARKGREEN)]
    if cutaway:
        gs=[]
        for m,c in groups:
            if not len(m):continue
            shell,cap=cut(m);gs.append((shell,c))
            # Groups split by color are open; separately cap the complete part.
        for m,c in [(adapter,(119,198,205)),(latch,(118,203,153))]:
            shell,cap=cut(m)
            if len(cap):gs.append((cap,c))
        for m in [wheel,handle]:
            shell,cap=cut(m);gs.extend([(shell,GOLD),(cap,(243,207,126))])
        return [(m,c) for m,c in gs if len(m)]
    return groups+([] if explode else [(wheel,GOLD),(handle,GOLD)])

pages=[('01-assembled-comparison','Option B / assembled rear underside',False,False,(1,1,-.5),[
'LEFT: current assembly. RIGHT: concept wall moves inward; latch reaches forward.',
'Teal: changed adapter region. Dark green: extended latch. Gold: stationary wheel.']),
('02-cutaway-comparison','Option B / 3D cutaway through the cavity',True,False,(1,.35,.2),[
'Half the assembly is removed to expose the cavity, rear wall and latch.',
'Provisional 25 mm wall shift; hook and wheel-contact geometry stay fixed.']),
('03-exploded-comparison','Option B / separate adapter and latch',False,True,(1,.65,-.2),[
'Wheel hidden and latch pulled rearward/down for illustration only.',
'This is an exploded display offset, not the latch installation path.'])]
for filename,title,cutaway,explode,eye,notes in pages:
    im=Image.new('RGB',(2400,1410),'#e9eef3');d=ImageDraw.Draw(im)
    d.text((35,23),title,font=font(39),fill='#203b50')
    d.text((35,85),'CURRENT',font=font(27),fill='#203b50');d.text((1235,85),'OPTION B / PROPORTION STUDY',font=font(27),fill='#203b50')
    for i,(aa,ll) in enumerate([(original,latch),(a,l)]):
        # Original shares triangle ordering and masks with the concept.
        groups=colored(aa,ll,cutaway,explode)
        if i==0:
            groups=[(m,BLUE if c in [BLUE,TEAL,(119,198,205)] else GREEN if c in [GREEN,DARKGREEN,(118,203,153)] else c) for m,c in groups]
        im.paste(render(groups,eye,(1170,1070),focus=(0,166,25)),(15+i*1200,135))
    d=ImageDraw.Draw(im)
    for j,note in enumerate(notes):d.text((35,1235+43*j),note,font=font(25),fill='#203b50')
    d.text((35,1350),'CONCEPT MESH DEFORMATION • no manufacturing CAD changed • dovetail / wheel interference / strength not validated',font=font(23),fill='#677988')
    im.save(OUT/f'{filename}.png');print(filename,flush=True)

# Self-contained canvas viewer: local file, no CDN or dependencies.
# Crop front triangles from the display to keep the rear detail responsive.
def packed(m):return np.round(m[m[:,:,1].max(1)>65],3).reshape(-1).tolist()
data={'current':{'adapter':packed(original),'latch':packed(latch)},'concept':{'adapter':packed(a),'latch':packed(l)},'wheel':packed(wheel),'handle':packed(handle)}
html='''<!doctype html><meta charset="utf-8"><title>Option B — rear cavity concept</title>
<style>body{margin:0;background:#edf2f6;color:#203b50;font:16px system-ui}header{padding:16px 24px;background:white}h2{margin:0 0 8px}button,label{margin-right:18px}button{padding:8px 14px}canvas{display:block;width:100vw;height:75vh;touch-action:none}p{margin:8px 24px}</style>
<header><h2>Option B / rotatable 3D concept</h2><button id="toggle">Showing option B — switch to current</button><label><input id="wheel" type="checkbox" checked>Wheel reference</label><label><input id="half" type="checkbox">Half cutaway</label><label><input id="explode" type="checkbox">Explode latch</label><button id="reset">Reset view</button></header><canvas></canvas>
<p>Drag to rotate · Scroll to zoom. Blue: adapter · Green: separate latch · Gold: wheel.</p><p>25 mm provisional inward shift. Mesh study only; production geometry unchanged. Interference and dovetail fit not validated.</p>
<script>const DATA=__DATA__;const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');let concept=true,az=.7,el=.3,zoom=3.3,drag=null;
const controls=['wheel','half','explode'].map(x=>document.getElementById(x));controls.forEach(e=>e.onchange=draw);
document.getElementById('toggle').onclick=()=>{concept=!concept;document.getElementById('toggle').textContent=concept?'Showing option B — switch to current':'Showing current — switch to option B';draw()};
document.getElementById('reset').onclick=()=>{az=.7;el=.3;zoom=3.3;draw()};
canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)};canvas.onpointerup=()=>drag=null;canvas.onpointermove=e=>{if(!drag)return;az+=(e.clientX-drag[0])*.008;el=Math.max(-1.4,Math.min(1.4,el+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];draw()};canvas.onwheel=e=>{e.preventDefault();zoom*=Math.exp(-e.deltaY*.001);zoom=Math.max(.7,Math.min(12,zoom));draw()};
function draw(){canvas.width=innerWidth;canvas.height=innerHeight*.75;let W=canvas.width,H=canvas.height;ctx.fillStyle='#f9fbfd';ctx.fillRect(0,0,W,H);let ca=Math.cos(az),sa=Math.sin(az),ce=Math.cos(el),se=Math.sin(el),triangles=[];
function add(arr,color,latch=false){for(let i=0;i<arr.length;i+=9){let raw=[];for(let j=0;j<3;j++)raw.push([arr[i+j*3],arr[i+j*3+1]+(latch&&controls[2].checked?48:0),arr[i+j*3+2]+(latch&&controls[2].checked?-10:0)]);if(controls[1].checked){let clipped=[];for(let j=0;j<raw.length;j++){let p=raw[j],q=raw[(j+1)%raw.length],ip=p[0]<=.1,iq=q[0]<=.1;if(ip)clipped.push(p);if(ip!==iq){let t=(.1-p[0])/(q[0]-p[0]);clipped.push(p.map((v,k)=>v+t*(q[k]-v)))}}raw=clipped;if(raw.length<3)continue}
let pts=raw.map(p=>{let x=p[0],y=p[1]-165,z=p[2]-20,r=x*ca+y*sa,dep=x*sa-y*ca;return [W/2+r*zoom,H/2-(z*ce-dep*se)*zoom,dep*ce+z*se]});let p=raw[0],q=raw[1],r=raw[2],u=q.map((v,k)=>v-p[k]),v=r.map((v,k)=>v-p[k]),n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],len=Math.hypot(...n)||1;let shade=.45+.55*Math.abs((n[0]*.5+n[1]*-.3+n[2]*.8)/len);triangles.push({pts,depth:pts.reduce((s,p)=>s+p[2],0)/pts.length,color:color.map(c=>Math.round(c*shade))})}}
let m=DATA[concept?'concept':'current'];add(m.adapter,concept?[36,163,173]:[87,148,187]);add(m.latch,[70,166,113],true);if(controls[0].checked){add(DATA.wheel,[220,171,73]);add(DATA.handle,[220,171,73])}triangles.sort((a,b)=>a.depth-b.depth);for(let t of triangles){ctx.beginPath();t.pts.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fillStyle=`rgb(${t.color})`;ctx.fill()}}
window.onresize=draw;draw();</script>'''
(OUT/'option-b-interactive.html').write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
(OUT/'study.json').write_text(json.dumps(dict(previewOnly=True,wallShiftMm=SHIFT,method='adapter mesh proportion map; native planar-face extrusions extend the separate latch; not a production CAD rebuild',productionGeometryChanged=False,cutawayCaps='display only; individual loops filled',interactiveCutaway='uncapped clipped triangles',wheelContactPreservedBy='original latch retained; only adapter-facing front and top planes extruded toward negative Y',latchStudyValid=latch_study.is_valid,latchStudySolids=len(latch_study.solids()),validation='visual proportion study only'),indent=2)+'\n')
print(OUT)
