import assert from 'node:assert/strict';
import path from 'node:path';
export function assertBuildContext(doc,tree,stage){
 assert.equal(path.resolve(doc.path??'').toLowerCase(),path.resolve('SolidCraft/models/seat-adapter.sc').toLowerCase(),'Wrong live document; open the authoritative seat-adapter.sc');
 for(const name of ['AdapterBody','AdapterBodySplit','WheelScanReference'])assert(tree.components.some(c=>c.name===name),'Missing component '+name);
 assert(doc.sketches.some(s=>s.name==='M06_RearDovetailProfile'),'Missing driving dovetail sketch');
 const latch=tree.components.find(c=>c.name==='Latch');
 if(stage==='half')assert(!latch,'Latch already exists; resume a later stage');
 else assert(latch,'Latch component missing');
 return latch;
}
