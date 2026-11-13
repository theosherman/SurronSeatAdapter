import fs from 'node:fs';
const recipe=JSON.parse(fs.readFileSync(new URL('../inputs/recipe.json',import.meta.url)));
const commands=[];const add=(command,params)=>commands.push({command,params});
add('solid.move',{bodies:['AdapterBodyMaster'],translate:[0,0,0],copy:true,name:'C01_DependentMasterCopy'});
add('component.create',{name:'AdapterBodySplit',activate:false});
add('component.move_bodies',{bodies:['AdapterBodyMaster (2)'],component:'AdapterBodySplit'});
add('component.activate',{component:'AdapterBodySplit'});
const split=recipe.child.splitPlane;
add('solid.split_body',{body:'AdapterBodyMaster (2)',plane:{origin:split.originMm,normal:split.normal},name:'C02_PrintSplit'});
add('body.rename',{body:'AdapterBodyMaster (2)',name:'AdapterBodyFront'});
add('body.rename',{body:'AdapterBodyMaster (2) (1)',name:'AdapterBodyRear'});
for(const instance of recipe.child.connectorInstances){
 const name='C03_'+instance.name.replaceAll('-','_');
 add('sketch.create',{name:name+'_Profile',plane:{origin:instance.originMm,x_dir:instance.xAxis,y_dir:instance.yAxis}});
 const seen=new Set();let count=0;
 for(const c of instance.curves){
  if(c.type!=='Line3D')throw new Error('Unexpected connector curve '+c.type);
  const a=c.startMm.slice(0,2),b=c.endMm.slice(0,2),key=[a,b].map(v=>v.map(n=>n.toFixed(8)).join(',')).sort().join('|');
  if(seen.has(key))continue;seen.add(key);count++;
  add('sketch.line',{points:[a,b],infer:false});
 }
 add('sketch.constraint.fix',{entities:Array.from({length:count},(_,i)=>'l'+(i+1)),fixed:true});add('sketch.finish',{});
 const x=instance.xAxis,y=instance.yAxis,n=[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]];
 const dot=n.reduce((s,v,i)=>s+v*instance.extrusionDirection[i],0);
 add('solid.extrude',{sketch:name+'_Profile',distance:instance.depthMm,direction:dot>0?'positive':'negative',operation:'cut',targets:['AdapterBodyFront','AdapterBodyRear'],name});
}
add('component.activate',{component:'root'});
add('browser.visibility',{items:['AdapterBodyFront','AdapterBodyRear'],visible:false});
add('browser.visibility',{items:['AdapterBodyMaster'],visible:true});
fs.writeFileSync(new URL('../scripts/adapter-child.json',import.meta.url),JSON.stringify({commands},null,2));
const full=['adapter-master-pre-imprint','adapter-imprint','adapter-child',...(fs.existsSync(new URL('../scripts/reorganize-components.json',import.meta.url))?['reorganize-components']:[])];
if(full.every(n=>fs.existsSync(new URL('../scripts/'+n+'.json',import.meta.url))))fs.writeFileSync(new URL('../scripts/seat-adapter-build.json',import.meta.url),JSON.stringify({commands:full.flatMap(n=>JSON.parse(fs.readFileSync(new URL('../scripts/'+n+'.json',import.meta.url))).commands)},null,2));
console.log(JSON.stringify({commands:commands.length,connectorCutouts:5}));
