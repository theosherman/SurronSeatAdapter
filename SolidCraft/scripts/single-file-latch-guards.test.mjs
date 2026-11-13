import test from 'node:test';
import assert from 'node:assert/strict';
import {assertBuildContext} from './single-file-latch-guards.mjs';
const doc={path:'SolidCraft/models/seat-adapter.sc',sketches:[{name:'M06_RearDovetailProfile'}]};
const tree={components:['AdapterBody','AdapterBodySplit','WheelScanReference'].map(name=>({name}))};
test('refuses wrong live document before any latch mutation',()=>assert.throws(()=>assertBuildContext({...doc,path:'other.sc'},tree,'half'),/Wrong live document/));
test('requires existing adapter and shared sketch',()=>{
 assert.throws(()=>assertBuildContext({...doc,sketches:[]},tree,'half'),/dovetail/);
 assert.throws(()=>assertBuildContext(doc,{components:[]},'half'),/Missing component/);
});
test('resumes only existing latch and refuses duplicate construction',()=>{
 assert.throws(()=>assertBuildContext(doc,tree,'top'),/Latch component missing/);
 const t={components:[...tree.components,{name:'Latch',id:82}]};
 assert.equal(assertBuildContext(doc,t,'top').id,82);
 assert.throws(()=>assertBuildContext(doc,t,'half'),/already exists/);
});
