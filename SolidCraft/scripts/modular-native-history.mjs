import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const container=fileURLToPath(new URL('./native-container.ps1',import.meta.url));
export const sha256=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
export const serializeNative=d=>JSON.stringify(d,(_,v)=>typeof v==='number'&&Object.is(v,-0)?JSON.rawJSON('-0.0'):v);
export function assertSourceHash(source,expected){assert.equal(sha256(fs.readFileSync(source)),expected,'Source changed since capture');}
export function assertNewDestination(output){assert(!fs.existsSync(output),'Output already exists');}
export function assertPreparedRun(r){
 assert(r.sourceHash&&r.documentHash&&r.masterHash,'Prepared run lacks artifact provenance');
 assertSourceHash(r.sourcePath,r.sourceHash);
 assertSourceHash(path.join(r.runDir,'current-document.json'),r.documentHash);
 assertSourceHash(r.master,r.masterHash);
}
export function assertEvidenceCurrent(attempt,report){
 assert(attempt?.status==='complete','Latest attempt has no completed evidence');
 assert.equal(attempt.runDir,report.runDir,'Report evidence belongs to a different attempt');
}
export function compareStageGeometry(before,after){
 const toleranceMm3=Math.max(.001,before.volume_mm3*1e-7),errors=[];
 if(!after?.closed)return {ok:false,errors:['Missing/open body'],toleranceMm3};
 const volumeDeltaMm3=after.volume_mm3-before.volume_mm3;
 if(!Number.isFinite(volumeDeltaMm3)||Math.abs(volumeDeltaMm3)>toleranceMm3)errors.push('volume');
 const bboxDeltaMm={min:after.bbox.min.map((x,i)=>x-before.bbox.min[i]),max:after.bbox.max.map((x,i)=>x-before.bbox.max[i])};
 const comDeltaMm=after.center_of_mass.map((x,i)=>x-before.center_of_mass[i]);
 if([...bboxDeltaMm.min,...bboxDeltaMm.max,...comDeltaMm].some(x=>!Number.isFinite(x)||Math.abs(x)>.001))errors.push('bounds/COM');
 return {ok:errors.length===0,volumeDeltaMm3,toleranceMm3,bboxDeltaMm,comDeltaMm,errors};
}
function zip(args){
 const r=spawnSync('powershell.exe',['-NoProfile','-ExecutionPolicy','Bypass','-File',container,...args],{encoding:'utf8',windowsHide:true,timeout:60000});
 assert.equal(r.status,0,r.stderr||r.error?.message||'Container operation failed');
 return JSON.parse(r.stdout.replace(/^\uFEFF/,''));
}
export function readNative(sourcePath,documentPath){
 assertNewDestination(documentPath);
 const inventory=zip(['-Mode','Read','-InputPath',sourcePath,'-DocumentPath',documentPath]);
 return {document:JSON.parse(fs.readFileSync(documentPath,'utf8')),inventory};
}
export function writeNative({sourcePath,outputPath,document,expectedSha256}){
 assertNewDestination(outputPath);assertSourceHash(sourcePath,expectedSha256);
 const docPath=outputPath+'.document.json';assertNewDestination(docPath);
 fs.writeFileSync(docPath,serializeNative(document));
 return zip(['-Mode','Write','-InputPath',sourcePath,'-DocumentPath',docPath,'-OutputPath',outputPath,'-ExpectedSha256',expectedSha256]);
}
export function partitionCurrentDocument(document,{masterComponentId}){
 const d=structuredClone(document),master=d.components.find(c=>c.id===masterComponentId);
 const supported=new Set(['format','name','features','params','components','occurrences','visibility','appearances','next_id','next_component_color_index','units','joints']);
 assert(Object.keys(d).every(k=>supported.has(k)),'Unsupported native document fields require explicit dependency review');
 assert.equal(d.components.filter(c=>c.name==='AdapterBody').length,1,'Unknown or ambiguous master component');
 assert.equal(new Set(d.components.map(c=>c.id)).size,d.components.length,'Duplicate component IDs');
 assert.equal(new Set(d.features.map(f=>f.id)).size,d.features.length,'Duplicate feature IDs');
 assert(master?.name==='AdapterBody','Unknown or ambiguous master component');
 assert.equal(master.parent,0,'Master must belong to assembly root');
 assert(!d.components.some(c=>c.parent===masterComponentId),'Nested master components require explicit migration');
 const placements=d.occurrences.filter(o=>o.component===masterComponentId);
 assert.equal(placements.length,1,'Expected exactly one master placement');
 const matrix=placements[0].transform;
 assert(matrix.length===4&&matrix.every((r,i)=>r.length===4&&r.every((x,j)=>Math.abs(x-(i===j?1:0))<1e-12)),'Master placement must be identity');
 assert(!d.joints?.length,'Joints require explicit migration');
 const split=d.components.filter(c=>c.name==='AdapterBodySplit');assert.equal(split.length,1,'Expected one printing component');
 const printingFeatures=d.features.filter(f=>f.component===split[0].id||f.name==='C01_DependentMasterCopy');
 assert(printingFeatures.some(f=>f.name==='C01_DependentMasterCopy'),'Missing dependent master copy');
 const masterFeatures=d.features.filter(f=>f.component===masterComponentId);
 assert(masterFeatures.length,'Missing master history');
 const masterDocument=structuredClone(d);
 masterDocument.name='Adapter Body';masterDocument.features=masterFeatures.map(f=>({...f,component:0}));
 masterDocument.components=[];masterDocument.occurrences=[];
 if(masterDocument.visibility)masterDocument.visibility.hidden_occurrences=[];
 return {masterDocument,printingFeatures,printingComponents:split,printingOccurrences:d.occurrences.filter(o=>o.component===split[0].id),inventory:{masterFeatureIds:masterFeatures.map(f=>f.id),sourceFeatureCount:d.features.length}};
}
export function validateStandalone(r){
 assert(r.baseline&&r.rebuilt&&r.replayed,'Missing independent master measurements');
 assert(r.features===58&&r.healthy&&r.assetsMatch,'History/health/assets not verified');
 const before=r.baseline.bodies.find(b=>b.name==='AdapterBodyMaster');assert(before?.closed,'Missing closed baseline');
 for(const data of [r.rebuilt,r.replayed]){
  assert.equal(data.body_count,1,'Standalone manufactured body count');
  const b=data.bodies.find(b=>b.name===before.name);assert(b?.closed,'Standalone master is open/missing');
  assert(Math.abs(b.volume_mm3-before.volume_mm3)<=Math.max(.001,before.volume_mm3*1e-7),'Master volume changed');
  for(const [a,c] of [[before.bbox.min,b.bbox.min],[before.bbox.max,b.bbox.max],[before.center_of_mass,b.center_of_mass]])assert(a.every((x,i)=>Math.abs(x-c[i])<=.001),'Master bounds/COM changed');
 }
 return {ok:true,stage:'standalone',features:r.features};
}
