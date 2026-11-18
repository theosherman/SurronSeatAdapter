import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=name=>JSON.parse(fs.readFileSync(path.join(root,name),'utf8').replace(/^\uFEFF/,''));
const assert=(ok,message)=>{if(!ok)throw new Error(message);};
const dot=(a,b)=>a.reduce((n,v,i)=>n+v*b[i],0);
const norm=a=>Math.hypot(...a);
const recipe=read('cad-rebuild/recipe.json');
const timeline=read('reference/fusion/fusion-timeline-and-user-parameters.json');
const parameters=read('reference/fusion/fusion-adapter-parameters.json');
const manifest=read('cad-rebuild/onshape-current-manifest.json');

function finite(value,where='recipe'){
 if(typeof value==='number')assert(Number.isFinite(value),`Non-finite number at ${where}`);
 else if(value&&typeof value==='object')for(const [key,v] of Object.entries(value))finite(v,where+'.'+key);
}
finite(recipe);
assert(recipe.canonicalLengthUnit==='millimeter','Canonical unit is wrong');
assert(timeline.timeline.length===200,'Expected 200 source markers');
assert(timeline.timeline.every((t,i)=>t.index===i),'Timeline indices are discontinuous');
assert(parameters.length===149,'Expected 149 recorded model parameters');
assert(recipe.sketches.length===18,'Expected 18 source sketches');
assert(recipe.selectedProfiles.reduce((n,f)=>n+f.profiles.length,0)===37,'Expected 37 exact selected profiles');
assert(recipe.child.connectorInstances.length===5,'Expected five connector locations');
assert(recipe.scope.fillets===false,'Fillets must stay excluded');
assert(recipe.sourceUserParameters.find(p=>p.name==='Gap')?.valueMm===-0.20000000000000004,'Gap conversion changed');

for(const s of [...recipe.sketches,...recipe.child.connectorInstances]){
 assert(Math.abs(norm(s.xAxis)-1)<1e-9,`${s.name}: non-unit X`);
 assert(Math.abs(norm(s.yAxis)-1)<1e-9,`${s.name}: non-unit Y`);
 assert(Math.abs(dot(s.xAxis,s.yAxis))<1e-9,`${s.name}: non-orthogonal frame`);
 assert(Math.abs(norm(s.normal)-1)<1e-9,`${s.name}: non-unit normal`);
 if(s.extrusionDirection)assert(Math.abs(Math.abs(dot(s.normal,s.extrusionDirection))-1)<1e-9,`${s.name}: cut direction is not normal to profile`);
 for(const c of s.curves){
  if(c.radiusMm!==undefined)assert(c.radiusMm>0,`${s.name}: non-positive radius`);
  assert(c.approximate!==true,`${s.name}: undocumented sampled geometry remains`);
 }
}
for(const f of recipe.selectedProfiles)for(const p of f.profiles){
 assert(p.areaMm2>0,`${f.sourceTimelineIndex}: non-positive selected area`);
 assert(recipe.sketches.some(s=>s.name===p.sketch),`Missing parent sketch ${p.sketch}`);
 for(const loop of p.loops)for(const curve of loop.curves)assert(!curve.approximate,`${f.sourceTimelineIndex}: approximate selected loop`);
}
for(const step of recipe.masterSteps){
 if(step.profileSource!==undefined)assert(recipe.selectedProfiles.some(f=>f.sourceTimelineIndex===step.profileSource),`Missing profile source ${step.profileSource}`);
 if(step.sketch)assert(recipe.sketches.some(s=>s.name===step.sketch),`Missing sketch ${step.sketch}`);
}
const rear=recipe.sketches.find(s=>s.name==='RearSketch');
assert(rear.curves.some(c=>c.startMm&&Math.abs(c.startMm[2]+263.44598216275198)<1e-7),'Rear sketch local-Z offset was dropped');
const split=recipe.child.splitPlane;
for(const p of split.lineEndpointsMm)assert(Math.abs(dot(p.map((v,i)=>v-split.originMm[i]),split.normal))<1e-8,'Split endpoint is off its plane');
assert(manifest.validation.masterValidation.bodyCount===1,'Final master count is wrong');
assert(manifest.validation.childValidation.bodyCount===2,'Final child count is wrong');
assert(manifest.validation.masterValidation.volume>manifest.validation.childValidation.volume,'Connector cuts must reduce child volume');
for(const removed of ['SplitBodySketch','TopJointSketch','SideJointSketch'])assert(!manifest.masterSketches[removed],`Deleted master sketch ${removed} is still in the current manifest`);

const docs=['README.md','AGENTS.md','BUILD-SEQUENCE.md',...fs.readdirSync(path.join(root,'docs')).filter(n=>n.endsWith('.md')).map(n=>'docs/'+n)];
let links=0;
for(const file of docs){
 const content=fs.readFileSync(path.join(root,file),'utf8');
 for(const match of content.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)){
  const target=match[1].split('#')[0];
  if(!target||/^[a-z]+:/i.test(target))continue;
  assert(fs.existsSync(path.resolve(root,path.dirname(file),decodeURIComponent(target))),`${file}: broken link ${target}`);links++;
 }
}
console.log(JSON.stringify({ok:true,timelineMarkers:200,sourceSketches:18,modelParameters:149,selectedProfiles:37,connectorInstances:5,localLinksChecked:links,onshapeApiCalls:0}));
