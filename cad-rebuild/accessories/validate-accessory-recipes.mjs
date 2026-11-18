import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const read=f=>JSON.parse(fs.readFileSync(path.join(dir,f),'utf8'));
const raw=read('../../reference/fusion/accessories/fusion-accessories-raw.json');
assert.equal(raw.markerBefore,raw.markerAfter);
assert.deepEqual(raw.errors,[]);
let profiles=0,curves=0,faceSelectors=0;
for(const name of ['latch-recipe.json','saddle-bag-mount-recipe.json']){
 const r=read(name),source=raw.parts.find(p=>p.name===r.name);
 assert.equal(r.canonicalLengthUnit,'millimeter');
 assert.equal(r.angleUnit,'degree');
 assert.equal(r.scope.fillets,false);
 assert.equal(r.features.length,source.features.length);
 assert.equal(r.validation.noFilletBodies.length,1);
 assert.ok(r.validation.noFilletBodies[0].isSolid);
 for(let i=0;i<r.sketches.length;i++){
   const s=r.sketches[i],rs=source.sketches[i];
   s.origin.forEach((n,j)=>assert.ok(Math.abs(n-rs.origin[j]*10)<1e-10));
   assert.ok(Math.abs(s.xAxis.reduce((n,x)=>n+x*x,0)-1)<1e-10);
   assert.ok(Math.abs(s.yAxis.reduce((n,x)=>n+x*x,0)-1)<1e-10);
   assert.ok(Math.abs(s.xAxis.reduce((n,x,j)=>n+x*s.yAxis[j],0))<1e-10);
   curves+=s.curves.length;
 }
 let lastIndex=-1;
 for(const f of r.features){
   assert.ok(f.index>lastIndex);lastIndex=f.index;
   assert.equal(f.healthState,0);
   if(f.profiles)for(const p of f.profiles){
     profiles++;
     assert.ok(p.loops.length>0);
     assert.ok([...r.sketches,...r.externalDependencies].some(s=>s.name===p.sketch));
     for(const loop of p.loops){
       assert.ok(loop.curves.length>0);
       for(const c of loop.curves)assert.equal(c.points,undefined,'No approximated profile curves expected');
     }
   }
   if(f.inputFaces)for(const face of f.inputFaces){
     faceSelectors++;
     assert.ok(face.component);
     assert.ok(face.point.length===3);
     assert.ok(face.geometry.type.endsWith('Plane'));
   }
   if(f.sourceOnlyDoNotBuild)assert.equal(f.rebuildDisposition,'omitFillet');
 }
 const gap=r.sourceUserParameters.find(p=>p.name==='Gap');
 assert.ok(Math.abs(gap.value-(-0.2))<1e-10);
 const last=r.features.filter(f=>f.rebuildDisposition==='recreate').at(-1);
 assert.equal(last.bodiesAfter[0].volumeMm3,r.validation.noFilletBodies[0].volumeMm3);
}
assert.equal(profiles,34);
assert.equal(curves,84);
assert.equal(faceSelectors,11);
const doc=fs.readFileSync(path.join(dir,'../../docs/ACCESSORY-PARTS.md'),'utf8');
for(const match of doc.matchAll(/\]\(([^)]+)\)/g))assert.ok(fs.existsSync(path.resolve(dir,'../../docs',match[1].split('#')[0])),match[1]);
console.log(JSON.stringify({ok:true,parts:2,sketches:5,curves,selectedProfiles:profiles,offsetFaceSelectors:faceSelectors,sourceReadErrors:0,markerRestored:raw.markerAfter,onshapeApiCalls:0}));
