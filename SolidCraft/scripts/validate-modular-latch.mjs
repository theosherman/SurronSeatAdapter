import fs from 'node:fs';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';

export function validateMigration(r) {
  assert(r?.baseline && r?.after, 'Missing migration report: baseline and after CAD measurements required');
  for (const name of ['AdapterBodyMaster','AdapterBodyFront','AdapterBodyRear']) {
    const before=r.baseline.bodies.find(b=>b.name===name), after=r.after.bodies.find(b=>b.name===name);
    assert(before?.closed && after?.closed, `Missing/open manufactured solid ${name}`);
    assert(Math.abs(after.volume_mm3-before.volume_mm3)<=Math.max(.001,before.volume_mm3*1e-7), `Volume changed: ${name}`);
    for(const [a,b] of [[before.center_of_mass,after.center_of_mass],[before.bbox.min,after.bbox.min],[before.bbox.max,after.bbox.max]])
      assert(a.every((x,i)=>Math.abs(x-b[i])<=.001),`Placement/bounds changed: ${name}`);
  }
  assert.equal(r.ceilingChecks?.length,12,'Require twelve fresh ceiling checks');
  assert(r.ceilingChecks.every(c=>c.ok),'Mounting ceiling failed');
  assert.equal(r.analyticR20?.master,2,'Master smooth R20 cuts');
  assert.equal(r.analyticR20?.front,2,'Front smooth R20 cuts');
  assert(r.health?.every(f=>!f.error&&!f.warning),'Feature health');
  assert(r.inheritance?.restored && r.inheritance.masterDelta<0 && Math.abs(r.inheritance.masterDelta-r.inheritance.childDelta)<1e-5,'Master inheritance/restoration');
  return {ok:true,stage:'migration'};
}

export function validateGeometry(r) {
  assert(r?.latch,'Missing geometry report: fresh latch measurements required');
  const b=r.latch;
  assert(b.closed && r.manufacturedBodies===1,'Require one closed manufactured latch');
  assert(Math.abs(b.volume_mm3-230819.7862464548)<=230819.7862464548*.0001,'Latch volume');
  for(const [actual,want] of [[b.bbox.min,[-60.865103223,-222.424548470,-45.662921353]],[b.bbox.max,[60.865103223,-150.227353849,47.321249211]]])
    assert(actual.every((x,i)=>Math.abs(x-want[i])<=.05),'Latch bounds');
  assert.equal(r.signedOffsets?.length,3,'Three mating offsets required');
  assert(r.signedOffsets.every(x=>Math.abs(x+.2)<1e-8),'Offset must remove material by 0.2 mm');
  assert.equal(r.filletFeatures,0,'No fillets');
  return {ok:true,stage:'geometry'};
}

export function validateRecovery(r) {
  assert(r?.ok===false && r.stage==='master-extraction','Expected a failed extraction attempt');
  assert(r.restored && !r.design.dirty,'Recovery must restore saved work');
  assert(r.design.path.replaceAll('\\','/').endsWith('/models/seat-adapter.sc'),'Original assembly must be active');
  assert.equal(r.design.timeline.length,72,'Original feature history');
  assert(r.design.timeline.every(f=>!f.error&&!f.warning),'Restored feature health');
  assert(r.design.sketches.every(s=>s.dof===0),'Restored sketches');
  for(const [name,volume] of [['AdapterBodyMaster',1507476.065203498],['AdapterBodyFront',853718.2229182002],['AdapterBodyRear',636139.6010199692]]) {
    const b=r.design.bodies.find(b=>b.name===name);
    assert(b?.closed && Math.abs(b.volume_mm3-volume)<.001,`Recovery geometry ${name}`);
  }
  assert(['AdapterBody','AdapterBodySplit','WheelScanReference'].every(name=>r.tree.components.some(c=>c.name===name&&c.parent===0)),'Restored hierarchy');
  return {ok:true,stage:'recovery',manufacturedSolids:3,features:72};
}

if(process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href){
  const stage=process.argv[2]??'migration';
  const path=process.argv[3]??new URL(`../logs/modular-latch/${stage==='recovery'?'migration-attempt':stage}.json`,import.meta.url);
  assert(fs.existsSync(path),`Missing ${stage} report: ${path}`);
  const validate={migration:validateMigration,geometry:validateGeometry,recovery:validateRecovery}[stage];
  assert(validate,`Unknown stage ${stage}`);
  console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(path,'utf8')))));
}
