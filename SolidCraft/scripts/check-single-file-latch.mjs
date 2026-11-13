import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readNative,writeNative,sha256,compareStageGeometry} from './modular-native-history.mjs';
import {write,command as c} from './modular-cad.mjs';
const source=path.resolve('SolidCraft/models/seat-adapter.sc');
const resume=process.argv[2];
const runDir=resume?path.resolve(resume):fs.mkdtempSync(path.resolve('SolidCraft/models/experiments/single-file-latch/check-'));
const log=path.resolve('SolidCraft/logs/single-file-latch');
const sourceHash=sha256(fs.readFileSync(source));
const document=resume?JSON.parse(fs.readFileSync(path.join(runDir,'document.json'))):readNative(source,path.join(runDir,'document.json')).document;
if(resume)assert.equal(sha256(fs.readFileSync(source)),JSON.parse(fs.readFileSync(path.join(runDir,'source-hash.json'))).sourceHash,'Resume source drift');
else write(path.join(runDir,'source-hash.json'),{sourceHash});
const cli='C:/Program Files/SolidCraft/solidcraft-cli.exe';
function run(args,label){
 console.log('Checking '+label);
 const r=spawnSync(cli,args,{encoding:'utf8',windowsHide:true,timeout:240000});
 fs.writeFileSync(path.join(log,label+'.txt'),r.stderr+'\n'+r.stdout);
 assert.equal(r.status,0,r.stderr||r.stdout||r.error?.message);
}
function variant(label,edit){
 if(resume&&label!=='zero-clearance')return JSON.parse(fs.readFileSync(path.join(runDir,label+'-results.json')));
 const d=structuredClone(document);edit(d);
 const native=path.join(runDir,label+'-'+Date.now()+'.sc'), script=path.join(runDir,label+'.json'),report=path.join(log,label+'.json');
 writeNative({sourcePath:source,outputPath:native,document:d,expectedSha256:sourceHash});
 const commands=[c('document.inspect',{timeline:true,measure:true}),c('model.faces',{body:'Latch'})];
 if(label==='rebuilt')commands.push(c('model.faces',{body:'AdapterBodyMaster'}),c('file.export',{path:path.join(runDir,'master.stl'),bodies:['AdapterBodyMaster'],quality:'fine'}),...['step','stl'].map(ext=>c('file.export',{path:path.resolve('SolidCraft/exports/latch.'+ext),bodies:['Latch'],quality:'fine'})));
 write(script,{commands});run(['run',script,'--in',native,'--results','--json-out',report],label);
 const results=JSON.parse(fs.readFileSync(report));write(path.join(runDir,label+'-results.json'),results);assert(results[0].timeline.every(f=>!f.error&&!f.warning),label+' history');
 return results;
}
const rebuilt=variant('rebuilt',()=>{});
const widened=variant('widened',d=>{const sketch=d.features.find(f=>f.name==='M06_RearDovetailProfile').sketch;for(const p of sketch.points)if(p.pos[0])p.pos[0]+=Math.sign(p.pos[0])*.25;});
const restored=variant('restored',()=>{});
const zero=variant('zero-clearance',d=>{d.params.find(p=>p.name==='latchClearance').expr='0 mm';d.features.find(f=>f.name==='L06_MatingClearance').suppressed=true;});
const body=(r,n)=>r[0].bodies.find(b=>b.name===n);
const baseline=JSON.parse(fs.readFileSync(path.join(log,'geometry.json')));
for(const b of baseline[0].bodies){assert(compareStageGeometry(b,body(rebuilt,b.name)).ok,'rebuild '+b.name);assert(compareStageGeometry(b,body(restored,b.name)).ok,'restore '+b.name);}
const masterDelta=body(widened,'AdapterBodyMaster').volume_mm3-body(rebuilt,'AdapterBodyMaster').volume_mm3;
const latchDelta=body(widened,'Latch').volume_mm3-body(rebuilt,'Latch').volume_mm3;
assert(masterDelta>1&&latchDelta< -1,'Shared sketch must grow master and cut wider slot');
for(const name of ['F91:side:l1','F91:side:l3']){
 const a=rebuilt[1].faces.find(f=>f.name===name),b=widened[1].faces.find(f=>f.name===name);
 const delta=a.plane_normal.reduce((s,n,i)=>s+n*(b.point[i]-a.point[i]),0);
 assert(Math.abs(Math.abs(delta)-.25*Math.abs(a.plane_normal[0]))<1e-5,'Slot flank widens by 0.25 mm in X');
}
const planes=r=>r[1].faces.filter(f=>f.plane_normal);
const match=(face,candidates)=>candidates.find(f=>f.name===face.name);
const displacements=planes(zero).map(f=>{const n=match(f,planes(rebuilt));return n?{name:f.name,normal:f.plane_normal,delta:f.plane_normal.reduce((s,v,i)=>s+v*(n.point[i]-f.point[i]),0)}:null;}).filter(Boolean);
const moved=displacements.filter(f=>Math.abs(f.delta)>.001);
assert.equal(moved.length,3,'Exactly three mating planes offset');assert(moved.every(f=>Math.abs(Math.abs(f.delta)-.2)<1e-5),'0.2 mm offsets');
assert(body(zero,'Latch').volume_mm3>body(rebuilt,'Latch').volume_mm3,'Clearance removes material');
assert.equal(rebuilt[2].faces.filter(f=>f.cylinder&&Math.abs(f.cylinder.radius-20)<1e-6).length,2,'R20 cylinders');
const ceilings=spawnSync(process.execPath,['SolidCraft/scripts/validate-mounting-ceilings.mjs',path.join(runDir,'master.stl'),path.join(log,'ceilings.json')],{encoding:'utf8',windowsHide:true});assert.equal(ceilings.status,0,ceilings.stderr||ceilings.stdout);
for(const ext of ['step','stl']){
 run(['run',path.resolve('SolidCraft/exports/latch.'+ext),'--json-out',path.join(log,'export-'+ext+'.json')],'export-'+ext);
 const out=JSON.parse(fs.readFileSync(path.join(log,'export-'+ext+'.json')));
 assert.equal(out.bodies.length,1,'Latch-only export '+ext);const b=out.bodies[0],nominal=body(rebuilt,'Latch');
 assert(b.closed&&Math.abs(b.volume_mm3-nominal.volume_mm3)<nominal.volume_mm3*.0001,'Export volume '+ext);
 assert(['min','max'].every(side=>b.bbox[side].every((n,i)=>Math.abs(n-nominal.bbox[side][i])<.05)),'Export bounds '+ext);
}
const evidenceHashes=Object.fromEntries(['rebuilt','widened','restored','zero-clearance'].map(label=>[label,sha256(fs.readFileSync(path.join(runDir,label+'-results.json')))]));
const evidenceDir=path.join(log,'runs',path.basename(runDir));fs.mkdirSync(evidenceDir,{recursive:true});
for(const label of Object.keys(evidenceHashes))fs.copyFileSync(path.join(runDir,label+'-results.json'),path.join(evidenceDir,label+'-results.json'));
const exportHashes=Object.fromEntries(['step','stl'].map(ext=>[ext,sha256(fs.readFileSync(path.resolve('SolidCraft/exports/latch.'+ext)))]));
const report={ok:true,sourceHash,runDir,evidenceDir,evidenceHashes,exportHashes,rebuild:true,dependency:{masterDelta,latchDelta},clearance:{moved,zeroMethod:'Offset feature suppressed; kernel rejects a zero-distance offset.'},exports:true};
assert.equal(sha256(fs.readFileSync(source)),sourceHash,'Authoritative source changed during checks');
write(path.join(log,'integration.json'),report);console.log(JSON.stringify(report));

