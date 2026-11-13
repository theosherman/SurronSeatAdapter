import fs from 'node:fs';
import assert from 'node:assert/strict';
import {compareStageGeometry} from './modular-native-history.mjs';
const dir=process.argv[2];
assert(dir,'Supply wheel-imprint evidence directory');
const nominal=JSON.parse(fs.readFileSync(dir+'/nominal.json'));
const moved=JSON.parse(fs.readFileSync(dir+'/propagation.json'));
const design=r=>r.find(x=>Array.isArray(x.timeline)&&Array.isArray(x.bodies));
const before=design(nominal),raised=moved[1],restored=moved[4];
for(const d of [before,raised,restored]){
 assert(d.timeline.length>0&&d.timeline.every(f=>!f.error&&!f.warning),'Healthy history');
 for(const name of ['AdapterBodyMaster','AdapterBodyFront','AdapterBodyRear','Latch'])assert(d.bodies.find(b=>b.name===name)?.closed,'Closed '+name);
}
const body=(d,name)=>d.bodies.find(b=>b.name===name);
const masterDelta=body(raised,'AdapterBodyMaster').volume_mm3-body(before,'AdapterBodyMaster').volume_mm3;
const childDelta=['AdapterBodyFront','AdapterBodyRear'].reduce((v,n)=>v+body(raised,n).volume_mm3-body(before,n).volume_mm3,0);
assert(Math.abs(masterDelta)>.01&&Math.abs(childDelta)>.01,'Wheel move must change master and printing child');
for(const n of ['AdapterBodyMaster','AdapterBodyFront','AdapterBodyRear','Latch'])assert(compareStageGeometry(body(before,n),body(restored,n)).ok,'Restore '+n);
for(const p of moved[2].points){const q=moved[5].points.find(q=>q.id===p.id);assert(p.world.every((v,i)=>Math.abs(v-q.world[i]-(i===2?1:0))<1e-7),'Handle sketch follows wheel');}
console.log(JSON.stringify({ok:true,masterDelta,childDelta,restored:true,handleSketchFollows:true}));
