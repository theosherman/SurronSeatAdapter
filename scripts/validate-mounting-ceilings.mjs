import fs from 'node:fs';
const root=new URL('../',import.meta.url);
const placement=JSON.parse(fs.readFileSync(new URL('adapter-placement.json',root))).translationMm;
const meshPath=process.argv[2]??new URL('exports/adapter-body.stl',root);
const mesh=fs.readFileSync(meshPath);
const count=mesh.readUInt32LE(80);
if(mesh.length!==84+count*50)throw new Error('Expected binary STL');
const triangles=Array.from({length:count},(_,i)=>Array.from({length:3},(_,v)=>Array.from({length:3},(_,d)=>mesh.readFloatLE(84+i*50+12+v*12+d*4))));
const sub=(a,b)=>a.map((v,i)=>v-b[i]);
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function inside(point,dir){
 const hits=[];
 for(const [a,b,c]of triangles){
  const e1=sub(b,a),e2=sub(c,a),h=cross(dir,e2),det=dot(e1,h);
  if(Math.abs(det)<1e-12)continue;
  const s=sub(point,a),u=dot(s,h)/det;if(u<0||u>1)continue;
  const q=cross(s,e1),v=dot(dir,q)/det;if(v<0||u+v>1)continue;
  const t=dot(e2,q)/det;if(t>1e-7)hits.push(t);
 }
 hits.sort((a,b)=>a-b);
 return hits.filter((t,i)=>i===0||t-hits[i-1]>1e-6).length%2===1;
}
const recipe=JSON.parse(fs.readFileSync(new URL('cad-rebuild/recipe.json',root)));
const bolt=recipe.sketches.find(s=>s.name==='BoltHolesSketch');
const roof=recipe.masterSteps.find(s=>s.id==='M09');
const checks=[];
function check(name,point,expected){
 // Saved source datums become model coordinates before classification.
 point=point.map((v,i)=>(i<2?-v:v)+placement[i]);
 const votes=[[1,.371,.193],[.217,1,.413]].map(dir=>inside(point,dir));
 checks.push({name,pointMm:point,expectedMaterial:expected,material:votes[0],rayAgreement:votes[0]===votes[1],ok:votes.every(v=>v===expected)});
}
function capTests(label,center,normal){
 check(label+' mounting ledge',center.map((v,i)=>v+normal[i]*.5+(i===0?6:0)),true);
 check(label+' access below ledge',center.map((v,i)=>v-normal[i]*.5+(i===0?6:0)),false);
 check(label+' small through hole',center.map((v,i)=>v+normal[i]*.5),false);
}
for(const x of [-23,23])capTests('front '+x,[x,roof.finalRoofPlanePointMm[1],roof.finalRoofPlanePointMm[2]],roof.finalRoofPlaneNormal);
for(const u of [-14.5,14.5]){
 const center=bolt.originMm.map((v,i)=>v+u*bolt.xAxis[i]+193.9428441873774*bolt.yAxis[i]-3*bolt.normal[i]);
 capTests('rear '+u,center,bolt.normal);
}
const report={adapterTranslationMm:placement,ok:checks.every(c=>c.ok),source:String(meshPath),triangles:count,checks,method:'Two independent triangle ray parity tests at 0.5 mm above/below each saved cap plane; annular sample 6 mm off bore axis.'};
const defaultReport = new URL('logs/mounting-ceiling-validation.json', root);
if (!process.argv[3]) fs.mkdirSync(new URL('./', defaultReport), { recursive: true });
fs.writeFileSync(process.argv[3] ?? defaultReport, JSON.stringify(report, null, 2));
console.log(JSON.stringify({ok:report.ok,checks:checks.length,failed:checks.filter(c=>!c.ok)}));
if(!report.ok)process.exitCode=1;
