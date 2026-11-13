import fs from 'node:fs';
const dir=new URL('../logs/',import.meta.url);
const read=n=>JSON.parse(fs.readFileSync(new URL(n,dir)));
const unpack=r=>JSON.parse(r.content[0].text);
const before=unpack(read('reorganize-baseline.json')[1]);
const [test,after,design,tree]=read('reorganize-verification.json').map(unpack);
const assert=(v,msg)=>{if(!v)throw new Error(msg);};
for(const b of before.bodies){
 const a=after.bodies.find(x=>x.name===b.name);
 assert(a&&a.closed,'Missing/open manufactured solid '+b.name);
 for(const field of ['volume_mm3','area_mm2','center_of_mass','bbox','faces','edges'])assert(JSON.stringify(a[field])===JSON.stringify(b[field]),'Changed '+field+' '+b.name);
}
const c=name=>tree.components.find(c=>c.name===name);
const root=tree.components.find(c=>c.id===0);
assert(root.bodies.length===0&&root.sketches.length===0,'Root contains geometry');
assert(['AdapterBody','AdapterBodySplit','WheelScanReference'].every(n=>c(n)?.parent===0),'Sibling components');
assert(c('AdapterBody').sketches.length===20&&c('AdapterBodySplit').sketches.length===5,'Sketch ownership');
assert(c('AdapterBody').bodies.length===1&&c('AdapterBodySplit').bodies.length===2,'Body ownership');
assert(test.restored&&test.errors.length===0&&test.parameter_errors.length===0,'Parameter test failed/restoration');
const delta=name=>test.measure.bodies.find(b=>b.name===name).volume_mm3-before.bodies.find(b=>b.name===name).volume_mm3;
assert(delta('AdapterBodyMaster')<0&&Math.abs(delta('AdapterBodyMaster')-delta('AdapterBodyFront')-delta('AdapterBodyRear'))<1e-5,'Inheritance changed');
assert(design.timeline.every(f=>!f.error&&!f.warning),'Feature health');
assert(design.sketches.every(s=>s.dof===0),'Sketch freedom');
const replay=read('reorganization-replay-validation.json');
for(const b of before.bodies){
 const a=replay[1].bodies.find(x=>x.name===b.name);
 assert(a?.closed&&a.volume_mm3===b.volume_mm3,'Independent full replay '+b.name);
}
assert(replay[0].components.find(c=>c.id===0).bodies.length===0,'Replay root contains a body');
console.log(JSON.stringify({ok:true,manufacturedBodiesUnchanged:3,siblingComponents:3,rootBodies:0,rootSketches:0,inheritanceRestored:true,featureCount:design.timeline.length}));
