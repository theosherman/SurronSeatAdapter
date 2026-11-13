import fs from 'node:fs';
import assert from 'node:assert/strict';
import {compareStageGeometry} from './modular-native-history.mjs';
const read=n=>JSON.parse(fs.readFileSync(`SolidCraft/logs/single-file-latch/${n}.json`));
const baseline=read('baseline')[0], geometry=read('geometry')[0];
for(const old of baseline.bodies)assert(compareStageGeometry(old,geometry.bodies.find(b=>b.name===old.name)).ok,`Changed ${old.name}`);
assert.equal(geometry.bodies.length,5,'Four manufactured solids and one reference');
assert(geometry.timeline.length>72&&geometry.timeline.every(f=>!f.error&&!f.warning),'Healthy complete history');
for(const [stage,volume] of [['blank',322840.5208081663],['top',238753.4027211155],['slot',232662.89426460396],['clearance',230819.7862464548]]){
 const b=read(stage).at(-1).bodies[0];assert(b.closed&&Math.abs(b.volume_mm3-volume)<volume*.0001,stage);
}
const b=geometry.bodies.find(b=>b.name==='Latch');
for(const [side,expected] of Object.entries({min:[-60.865103223,-222.424548470,-45.662921353],max:[60.865103223,-150.227353849,47.321249211]}))assert(b.bbox[side].every((n,i)=>Math.abs(n-expected[i])<.05),'Latch bounds');
const slot=read('geometry')[2];assert.equal(slot.definition.sketch,read('geometry')[3].id,'Direct shared sketch');
assert(!geometry.timeline.some(f=>f.name.startsWith('L')&&f.type.includes('Fillet')));
if(process.argv[2]!=='geometry'){
 const r=read('integration');assert(r.ok&&r.dependency&&r.clearance&&r.rebuild&&r.exports,'Complete integration evidence');
}
console.log('PASS single-file latch '+(process.argv[2]??'integration'));
