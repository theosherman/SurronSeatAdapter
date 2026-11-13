import fs from 'node:fs';
const recipe=JSON.parse(fs.readFileSync(new URL('../inputs/recipe.json',import.meta.url)));
const commands=[];
const add=(command,params)=>commands.push({command,params});
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function profileSketch(index,name,mirrorX=false){
 const selected=recipe.selectedProfiles.find(p=>p.sourceTimelineIndex===index);
 const sk=recipe.sketches.find(s=>s.name===selected.profiles[0].sketch);
 const z=selected.profiles[0].centroidMm[2]??0;
 const normal=cross(sk.xAxis,sk.yAxis);
 const reflect=v=>v.map((n,i)=>mirrorX&&i===0?-n:n);
 add('sketch.create',{name,plane:{origin:reflect(sk.originMm.map((v,i)=>v+normal[i]*z)),x_dir:reflect(sk.xAxis),y_dir:reflect(sk.yAxis)}});
 const seen=new Set();const ids=[];let lines=0,arcs=0,circles=0;
 for(const p of selected.profiles)for(const loop of p.loops)for(const c of loop.curves){
  const xy=v=>v.slice(0,2).map(n=>Math.abs(n)<1e-9?0:n);
  const key=JSON.stringify([c.type,...[c.startMm,c.endMm,c.centerMm].filter(Boolean).map(xy)].sort());
  if(seen.has(key))continue;seen.add(key);
  if(c.type==='Line3D'){add('sketch.line',{points:[xy(c.startMm),xy(c.endMm)],infer:false});ids.push('l'+ ++lines);}
  else if(c.type==='Arc3D'){add('sketch.arc.three_point',{start:xy(c.startMm),end:xy(c.endMm),through:xy(c.midMm)});ids.push('a'+ ++arcs);}
  else if(c.type==='Circle3D'){
   const referenceOnly=index===97&&!mirrorX;
   add('sketch.circle.center',{center:xy(c.centerMm),radius:c.radiusMm,...(referenceOnly?{construction:true}:{})});ids.push('c'+ ++circles);
  }
  else throw new Error('Unsupported exact curve '+c.type);
 }
 add('sketch.constraint.fix',{entities:ids,fixed:true});add('sketch.finish',{});
 return name;
}
add('parameters.add',{name:'airtagPocketDepth',expression:'8.5 mm',comment:'AirTag pocket depth; verified locally at 8.5 and 8.6 mm only.'});
profileSketch(9,'M01_BottomProfile');
add('solid.extrude',{sketch:'M01_BottomProfile',distance:150,distance2:50,operation:'new',name:'M01_BottomExtrusion',body_name:'AdapterBody'});
add('solid.mirror',{bodies:['AdapterBody'],plane:'YZ',combine:true,name:'M02_BaseMirror'});
profileSketch(12,'M03_SideProfiles');
add('solid.extrude',{sketch:'M03_SideProfiles',distance:120,operation:'intersect',targets:['AdapterBody'],name:'M03_SideIntersection'});
profileSketch(14,'M04_RearProfile');
add('solid.extrude',{sketch:'M04_RearProfile',distance:490,operation:'intersect',targets:['AdapterBody'],name:'M04_RearIntersection'});
add('solid.mirror',{bodies:['AdapterBody'],plane:'YZ',combine:true,name:'M05_ShellMirror'});
fs.writeFileSync(new URL('../scripts/adapter-stage1.json',import.meta.url),JSON.stringify({commands},null,2));
console.log(JSON.stringify({commands:commands.length,sourceSteps:'M01-M05'}));
commands.length=0;
for(const [sketch,count] of [['M01_BottomProfile',17],['M03_SideProfiles',14],['M04_RearProfile',7]]){add('sketch.edit',{sketch});add('sketch.constraint.fix',{entities:Array.from({length:count},(_,i)=>'l'+(i+1)),fixed:true});add('sketch.finish',{});}
profileSketch(18,'M06_RearDovetailProfile');
add('solid.extrude',{sketch:'M06_RearDovetailProfile',distance:300,operation:'join',targets:['AdapterBody'],name:'M06_RearDovetail'});
add('solid.split_body',{body:'AdapterBody',plane:{origin:[0,-263.445982162752,109.10684591063722],normal:[0,-1,0]},name:'M06_RearDovetailEndPlane'});
fs.writeFileSync(new URL('../scripts/adapter-stage2a.json',import.meta.url),JSON.stringify({commands},null,2));
commands.length=0;
add('solid.remove',{bodies:['AdapterBody']});
add('body.rename',{body:'AdapterBody (1)',name:'AdapterBodyMaster'});
profileSketch(75,'M07_BoltProfiles');
add('solid.extrude',{sketch:'M07_BoltProfiles',distance:1000,direction:'symmetric',operation:'cut',targets:['AdapterBody'],name:'M07_BoltThroughHoles'});
profileSketch(76,'M08_RearAccessProfiles');
add('solid.extrude',{sketch:'M08_RearAccessProfiles',distance:500,direction:'negative',start_offset:-3,operation:'cut',targets:['AdapterBody'],name:'M08_RearAccessCavities'});
const bolt=recipe.sketches.find(s=>s.name==='BoltHolesSketch');
const roof=recipe.masterSteps.find(s=>s.id==='M09');
for(const [i,u] of [-23,23].entries()){
 const sk='M09_FrontAccessProfile'+i,tool='FrontAccessTool'+i;
 add('sketch.create',{name:sk,plane:{origin:bolt.originMm,x_dir:bolt.xAxis,y_dir:bolt.yAxis}});
 add('sketch.circle.center',{center:[u,-64.05715581262262],radius:8.5});
 add('sketch.constraint.fix',{entities:['c1'],fixed:true});add('sketch.finish',{});
 add('solid.extrude',{sketch:sk,distance:400,direction:'symmetric',operation:'new',name:'M09_AccessTool'+i,body_name:tool});
 add('solid.split_body',{body:tool,plane:{origin:roof.finalRoofPlanePointMm,normal:roof.finalRoofPlaneNormal},name:'M09_CeilingPlane'+i});
 add('solid.remove',{bodies:[tool]});
 add('solid.combine',{target:'AdapterBody',tools:[tool+' (1)'],operation:'cut',name:'M09_FrontAccessCavity'+i});
}
for(const c of commands.slice(2)){if(c.params.targets)c.params.targets=c.params.targets.map(x=>x==='AdapterBody'?'AdapterBodyMaster':x);if(c.params.target==='AdapterBody')c.params.target='AdapterBodyMaster';}
fs.writeFileSync(new URL('../scripts/adapter-stage2b.json',import.meta.url),JSON.stringify({commands},null,2));
commands.length=0;
profileSketch(79,'M10_HangerProfile');
add('solid.extrude',{sketch:'M10_HangerProfile',distance:1,direction:'negative',operation:'new',body_name:'SeatHanger',name:'M10_SeatHanger'});
const d1=recipe.drafts.find(d=>d.sourceTimelineIndex===80);
add('solid.draft',{body:'SeatHanger',faces:d1.selectedFaces.map(f=>f.pointMm),neutral:{origin:d1.neutralPlane.originMm,normal:d1.neutralPlane.normal},angle:'45 deg',name:'M11_HangerDraft'});
add('solid.mirror',{bodies:['SeatHanger'],plane:'YZ',name:'M11_HangerMirror'});
add('solid.combine',{target:'AdapterBodyMaster',tools:['SeatHanger','SeatHanger (2)'],operation:'join',name:'M11_JoinHangers'});
profileSketch(84,'M12_HandleProfile');
add('solid.extrude',{sketch:'M12_HandleProfile',distance:98,direction:'symmetric',operation:'join',targets:['AdapterBodyMaster'],name:'M12_HandleMount'});
profileSketch(86,'M13_FrontCutProfile');
add('solid.extrude',{sketch:'M13_FrontCutProfile',through_all:true,operation:'cut',targets:['AdapterBodyMaster'],name:'M13_FrontCut'});
fs.writeFileSync(new URL('../scripts/adapter-stage3a.json',import.meta.url),JSON.stringify({commands},null,2));
commands.length=0;
const d4=recipe.drafts.find(d=>d.sourceTimelineIndex===87);
// Native draft87 is unsupported for the body geometry in 0.40.1. Exact
// planar wedge equivalent uses the source's fixed lower edge and final plane.
add('sketch.create',{name:'M14_FrontDraftWedgeProfile',plane:{origin:[-43,0,0],x_dir:[0,1,0],y_dir:[0,0,1]}});
add('sketch.line',{points:[[159.1595320874856,11.33586233574399],[159.1595320874856,34.33586233574536],[176.73146895659514,36.4311889499611]],closed:true,infer:false});
add('sketch.constraint.fix',{entities:['l1','l2','l3'],fixed:true});add('sketch.finish',{});
add('solid.extrude',{sketch:'M14_FrontDraftWedgeProfile',distance:86,operation:'cut',targets:['AdapterBodyMaster'],name:'M14_FrontDraftEquivalent'});
profileSketch(89,'M15_SeatNotches');
add('solid.extrude',{sketch:'M15_SeatNotches',distance:8,direction:'negative',operation:'cut',targets:['AdapterBodyMaster'],name:'M15_RearSeatNotches'});
profileSketch(91,'M16_FrontDovetailProfile');
add('solid.extrude',{sketch:'M16_FrontDovetailProfile',distance:80,direction:'symmetric',operation:'join',targets:['AdapterBodyMaster'],name:'M16_FrontDovetail'});
profileSketch(97,'M17_SeatSideProfile');
profileSketch(97,'M17_SeatSideReflectedProfile',true);
add('solid.extrude',{sketch:'M17_SeatSideReflectedProfile',distance:1000,direction:'symmetric',operation:'cut',targets:['AdapterBodyMaster'],name:'M17_SeatSideCutMirrored'});
// Cut the positive-X half analytically, then mirror that half to avoid the
// kernel's ineffective negative-X cylinder Boolean. All upstream geometry
// is symmetric here; the asymmetric wheel imprint is applied afterwards.
add('solid.split_body',{body:'AdapterBodyMaster',plane:'YZ',name:'M17_KeepSmoothHalf'});
add('solid.remove',{bodies:['AdapterBodyMaster (1)'],name:'M17_RemoveOppositeHalf'});
add('solid.mirror',{bodies:['AdapterBodyMaster'],plane:'YZ',combine:true,name:'M17_MirrorSmoothHalf'});
profileSketch(121,'M18_RearCutProfiles');
add('solid.extrude',{sketch:'M18_RearCutProfiles',distance:1000,direction:'symmetric',operation:'cut',targets:['AdapterBodyMaster'],name:'M18_RearCut'});
profileSketch(121,'M18_RearCutReflectedProfiles',true);
add('solid.extrude',{sketch:'M18_RearCutReflectedProfiles',distance:1000,direction:'symmetric',operation:'cut',targets:['AdapterBodyMaster'],name:'M18_RearCutMirrored'});
fs.writeFileSync(new URL('../scripts/adapter-stage3b.json',import.meta.url),JSON.stringify({commands},null,2));
commands.length=0;
profileSketch(124,'M19_BodyCavityProfile');
add('solid.extrude',{sketch:'M19_BodyCavityProfile',through_all:true,direction:'negative',start_offset:-12,taper:'15 deg',operation:'cut',targets:['AdapterBodyMaster'],name:'M19_DraftedUndersideCavity'});
profileSketch(126,'M20_AirTagProfile');
add('solid.extrude',{sketch:'M20_AirTagProfile',distance:'airtagPocketDepth',direction:'negative',operation:'cut',targets:['AdapterBodyMaster'],name:'M20_AirTagPocket'});
fs.writeFileSync(new URL('../scripts/adapter-stage3c.json',import.meta.url),JSON.stringify({commands},null,2));
const stages=['stage1','stage2a','stage2b','stage3a','stage3b','stage3c'];
fs.writeFileSync(new URL('../scripts/adapter-master-pre-imprint.json',import.meta.url),JSON.stringify({commands:stages.flatMap(s=>JSON.parse(fs.readFileSync(new URL('../scripts/adapter-'+s+'.json',import.meta.url))).commands)},null,2));
const full=['adapter-master-pre-imprint','adapter-imprint','adapter-child',...(fs.existsSync(new URL('../scripts/reorganize-components.json',import.meta.url))?['reorganize-components']:[])];
if(full.every(n=>fs.existsSync(new URL('../scripts/'+n+'.json',import.meta.url))))fs.writeFileSync(new URL('../scripts/seat-adapter-build.json',import.meta.url),JSON.stringify({commands:full.flatMap(n=>JSON.parse(fs.readFileSync(new URL('../scripts/'+n+'.json',import.meta.url))).commands)},null,2));
