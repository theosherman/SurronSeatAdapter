import fs from 'node:fs';
import {cad,command as c,write} from './modular-cad.mjs';
const recipe=JSON.parse(fs.readFileSync(new URL('../../cad-rebuild/accessories/latch-recipe.json',import.meta.url)));
const stage=process.argv[2];
const feature=i=>recipe.features.find(f=>f.index===i);
function sketch(index,name){
 const f=feature(index), frame=recipe.sketches.find(s=>s.name===f.profiles[0].sketch);
 const cmds=[c('sketch.create',{name,plane:{origin:frame.origin,x_dir:frame.xAxis,y_dir:frame.yAxis}})];
 const seen=new Map(), profiles=[];let lines=0,arcs=0;
 for(const p of f.profiles){const ids=[];for(const loop of p.loops)for(const curve of loop.curves){
  const xy=p=>p.slice(0,2);const ends=[xy(curve.start),xy(curve.end)].sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
  const key=JSON.stringify([curve.type,ends.map(p=>p.map(n=>+n.toFixed(8))),curve.mid?.map(n=>+n.toFixed(8))]);
  let id=seen.get(key);if(!id){
   if(curve.type.endsWith('Line3D')){id='l'+ ++lines;cmds.push(c('sketch.line',{points:[xy(curve.start),xy(curve.end)],infer:false}));}
   else if(curve.type.endsWith('Arc3D')){id='a'+ ++arcs;cmds.push(c('sketch.arc.three_point',{start:xy(curve.start),end:xy(curve.end),through:xy(curve.mid)}));}
   else throw Error('Unsupported curve '+curve.type);
   seen.set(key,id);
  }ids.push(id);
 }profiles.push({curves:ids});}
 cmds.push(c('sketch.constraint.fix',{entities:[...seen.values()],fixed:true}),c('sketch.finish'));
 return {cmds,profiles};
}
let cmds=[];
if(stage==='half'){
 const existing=cad([c('component.list')],'single-component-guard');
 if(JSON.stringify(existing).includes('"Latch"'))throw Error('Latch already exists; resume a later stage');
 const s=sketch(102,'L01_SideProfile');
 cmds=[c('component.create',{name:'Latch',parent:0,activate:true}),...s.cmds,
 c('solid.extrude',{sketch:'L01_SideProfile',profiles:s.profiles,distance:120,operation:'new',body_name:'Latch',name:'L01_SideExtrusion'}),
 c('solid.split_body',{body:'Latch',plane:{origin:feature(102).extentOne.entity.geometry.origin,normal:feature(102).extentOne.entity.geometry.normal.map(n=>-n)},name:'L02_ExactObliqueCap'})];
}else if(stage==='blank')cmds=[c('solid.remove',{bodies:['Latch (1)'],name:'L02_RemoveBeyondCap'}),c('solid.mirror',{bodies:['Latch'],plane:'YZ',combine:true,name:'L03_MirrorHalf'})];
else if(stage==='top'){
 const s=sketch(104,'L04_TopProfile');cmds=[...s.cmds,c('solid.extrude',{sketch:'L04_TopProfile',profiles:s.profiles,distance:300,direction:'symmetric',operation:'intersect',targets:['Latch'],name:'L04_TopIntersection'})];
}else if(stage==='slot')cmds=[c('solid.extrude',{sketch:'M06_RearDovetailProfile',profiles:[0],distance:300,operation:'cut',targets:['Latch'],name:'L05_DependentDovetailSlot'})];
else if(stage==='clearance')cmds=[c('parameters.add',{name:'latchClearance',expression:'0.2 mm',comment:'Three mating faces; signed offset removes material.'}),c('solid.offset_face',{body:'Latch',faces:feature(106).inputFaces.map(f=>f.point),distance:'-latchClearance',name:'L06_MatingClearance'})];
else if(stage==='show')cmds=[c('browser.visibility',{items:['Latch'],visible:true,isolate:true}),c('view.fit'),c('file.save')];
else throw Error('Stage required: half, blank, top, slot, clearance, show');
const results=cad([...cmds,c('inspect.measure',{bodies:stage==='half'?['Latch','Latch (1)']:['Latch']})],`single-build-${stage}`);
write(`SolidCraft/logs/single-file-latch/${stage}.json`,results);
console.log(JSON.stringify(results.slice(-2)));


