import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {validatePrinting} from './validate-modular-latch.mjs';
const modulePath=new URL('./modular-native-history.mjs',import.meta.url);
const h=fs.existsSync(modulePath)?await import(modulePath):null;
const api=()=>{assert(h,'Native history migration is not implemented');return h;};
const fixture=()=>JSON.parse(fs.readFileSync(new URL('../logs/modular-latch/source-document.json',import.meta.url)));
test('preserves complete master feature definitions, IDs and signed zeros without mutating input',()=>{
 const {partitionCurrentDocument,serializeNative}=api(), d=fixture(), original=serializeNative(d);
 const result=partitionCurrentDocument(d,{masterComponentId:74});
 assert.equal(result.masterDocument.name,'Adapter Body');
 assert.equal(result.masterDocument.features.length,58);
 assert.deepEqual(result.masterDocument.features,d.features.filter(f=>f.component===74).map(f=>({...f,component:0})));
 assert.deepEqual(JSON.parse(serializeNative(result.masterDocument)).features,result.masterDocument.features);
 assert.equal(serializeNative(d),original);
 assert.equal(result.printingFeatures.length,13);
 assert.equal(result.masterDocument.components.length,0);
 assert.equal(result.masterDocument.occurrences.length,0);
});
test('refuses nonidentity, multiple or absent master occurrences and unowned master',()=>{
 const {partitionCurrentDocument:p}=api();
 let d=fixture();d.occurrences.find(o=>o.component===74).transform[0][3]=1;assert.throws(()=>p(d,{masterComponentId:74}),/identity/);
 d=fixture();d.occurrences.push({...d.occurrences.find(o=>o.component===74),id:1000});assert.throws(()=>p(d,{masterComponentId:74}),/exactly one/);
 d=fixture();d.occurrences=d.occurrences.filter(o=>o.component!==74);assert.throws(()=>p(d,{masterComponentId:74}),/exactly one/);
 assert.throws(()=>p(fixture(),{masterComponentId:999}),/master component/);
});
test('rejects source drift and occupied destinations before writing',()=>{
 const {assertSourceHash,assertNewDestination,sha256}=api(), source=new URL('../models/seat-adapter.sc',import.meta.url);
 assert.throws(()=>assertSourceHash(source,'stale'),/changed/);
 assert.doesNotThrow(()=>assertSourceHash(source,sha256(fs.readFileSync(source))));
 assert.throws(()=>assertNewDestination(source),/exists/);
});
test('requires independent fresh master measurements and rejects a changed replay',()=>{
 const {validateStandalone}=api();assert.throws(()=>validateStandalone({}),/Missing/);
 const baseline=JSON.parse(fs.readFileSync(new URL('../logs/modular-latch/history-spike-rebuild.json',import.meta.url)));
 assert.equal(validateStandalone({baseline,rebuilt:baseline,replayed:baseline,features:58,healthy:true,assetsMatch:true}).ok,true);
 const changed=structuredClone(baseline);changed.bodies[0].volume_mm3+=1;
 assert.throws(()=>validateStandalone({baseline,rebuilt:baseline,replayed:changed,features:58,healthy:true,assetsMatch:true}),/volume/);
});
test('container roundtrip preserves embedded assets and removes caches without touching source',()=>{
 const {readNative,writeNative,sha256,partitionCurrentDocument}=api();
 const base=path.resolve('SolidCraft/models/seat-adapter.sc'), before=sha256(fs.readFileSync(base));
 const dir=fs.mkdtempSync(path.resolve('SolidCraft/models/experiments/history-test-'));
 const source=readNative(base,path.join(dir,'source.json'));
 const output=path.join(dir,'master.sc');
 writeNative({sourcePath:base,outputPath:output,document:partitionCurrentDocument(source.document,{masterComponentId:74}).masterDocument,expectedSha256:before});
 const rebuilt=readNative(output,path.join(dir,'master.json'));
 assert.deepEqual(rebuilt.inventory.assets,source.inventory.assets);
 assert.equal(rebuilt.inventory.cacheEntries,0);
 assert.equal(sha256(fs.readFileSync(base)),before);
 assert.throws(()=>writeNative({sourcePath:base,outputPath:output,document:source.document,expectedSha256:before}),/exists/);
});
test('printing acceptance rejects empty health and extra solids',()=>{
 const d=JSON.parse(fs.readFileSync(new URL('../logs/modular-latch/baseline.json',import.meta.url))).design;
 const r={baseline:d,after:structuredClone(d),health:d.timeline,manufacturedBodies:3,referenceBodies:['wheel_scan_mm'],definitionsPreserved:true,placementsPreserved:true,inheritance:{restored:true,masterDelta:-1,childDelta:-1}};
 assert.equal(validatePrinting(r).ok,true);
 assert.throws(()=>validatePrinting({...r,health:[]}),/history|features/);
 r.after.bodies.push({...d.bodies[0],name:'UnexpectedSolid'});
 assert.throws(()=>validatePrinting(r),/Unexpected|count|roles/);
});
test('requires provenance of both prepared snapshot and native master',()=>{
 const {assertPreparedRun,sha256}=api();assert.equal(typeof assertPreparedRun,'function');
 const dir=fs.mkdtempSync(path.resolve('SolidCraft/models/experiments/provenance-test-'));
 const sourcePath=path.join(dir,'source.sc'),master=path.join(dir,'master.sc');
 fs.writeFileSync(sourcePath,'source');fs.writeFileSync(master,'master');fs.writeFileSync(path.join(dir,'current-document.json'),'snapshot');
 const r={runDir:dir,sourcePath,master,sourceHash:sha256(Buffer.from('source')),masterHash:sha256(Buffer.from('master')),documentHash:sha256(Buffer.from('snapshot'))};
 assert.doesNotThrow(()=>assertPreparedRun(r));
 fs.writeFileSync(master,'changed');assert.throws(()=>assertPreparedRun(r),/changed/);
 fs.writeFileSync(master,'master');fs.writeFileSync(path.join(dir,'current-document.json'),'changed');assert.throws(()=>assertPreparedRun(r),/changed/);
});
test('rejects ambiguous ownership and unsupported dependent data, resolves changed component IDs',()=>{
 const {partitionCurrentDocument:p}=api();let d=fixture();d.components.push({...d.components.find(c=>c.name==='AdapterBody'),id:999});
 assert.throws(()=>p(d,{masterComponentId:74}),/ambiguous/);
 d=fixture();d.future_component_dependencies={component:60};assert.throws(()=>p(d,{masterComponentId:74}),/Unsupported/);
 d=fixture();for(const x of d.components){if(x.id===74)x.id=1074;if(x.id===60)x.id=1060;}
 for(const x of d.occurrences){if(x.component===74)x.component=1074;if(x.component===60)x.component=1060;}
 for(const f of d.features){if(f.component===74)f.component=1074;if(f.component===60)f.component=1060;if(f.id===59)f.id=1059;if(f.type==='body_transfer'&&f.to===60)f.to=1060;}
 const result=p(d,{masterComponentId:1074});assert.equal(result.printingFeatures.length,13);assert.equal(result.printingFeatures[0].id,1059);assert.equal(result.printingComponents[0].id,1060);
});
test('manufacturing comparison rejects successful import with changed volume',()=>{
 const {compareStageGeometry}=api();assert.equal(typeof compareStageGeometry,'function');
 const b=JSON.parse(fs.readFileSync(new URL('../logs/modular-latch/history-spike-rebuild.json',import.meta.url))).bodies[0];
 assert.equal(compareStageGeometry(b,b).ok,true);
 assert.equal(compareStageGeometry(b,{...b,volume_mm3:b.volume_mm3-.5458307993}).ok,false);
});
test('failed or in-progress attempts cannot validate old successful evidence',()=>{
 const {assertEvidenceCurrent}=api();assert.equal(typeof assertEvidenceCurrent,'function');
 const report={runDir:'new-run'};
 assert.doesNotThrow(()=>assertEvidenceCurrent({status:'complete',runDir:'new-run'},report));
 for(const attempt of [{status:'failed',runDir:'new-run'},{status:'running',runDir:'new-run'},{status:'complete',runDir:'old-run'}])assert.throws(()=>assertEvidenceCurrent(attempt,report),/evidence|attempt/);
});
