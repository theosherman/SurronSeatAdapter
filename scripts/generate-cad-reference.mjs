import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=name=>JSON.parse(fs.readFileSync(path.join(root,name),'utf8').replace(/^\uFEFF/,''));
const write=(name,value)=>{fs.mkdirSync(path.dirname(path.join(root,name)),{recursive:true});fs.writeFileSync(path.join(root,name),typeof value==='string'?value:JSON.stringify(value,null,2)+'\n');};
const mm=p=>p.map(v=>v*10);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const fmt=n=>Math.abs(n)<1e-10?'0':Number(n.toFixed(9)).toString();
const vector=p=>'('+p.map(fmt).join(', ')+')';
const extraction=read('reference/fusion/fusion-adapter-extraction.json');
const timeline=read('reference/fusion/fusion-timeline-and-user-parameters.json');
const profileSource=read('reference/fusion/fusion-selected-profile-loops.json');
const connectorSource=read('reference/fusion/fusion-connector-source.json');
const extrusions=read('reference/fusion/fusion-adapter-extrusions.json');

function geometry(c){
  const out={type:c.type.split('::').at(-1),construction:c.construction??false};
  for(const k of ['start','mid','end','center'])if(c[k])out[k+'Mm']=mm(c[k]);
  if(c.radius!==undefined)out.radiusMm=c.radius*10;
  if(c.points){out.sampledPointsMm=c.points.map(mm);out.approximate=true;out.samplingToleranceMm=(c.approximationToleranceCm??0.0001)*10;}
  return out;
}
const sketches=extraction.components.flatMap(c=>c.sketches.map(s=>({
  name:s.name,sourceComponent:c.name,sourceTimelineIndex:s.index,
  originMm:mm(s.origin),xAxis:s.x,yAxis:s.y,normal:cross(s.x,s.y),
  curves:s.curves.map(geometry),
  dimensions:s.dimensions.map(d=>({name:d.name,sourceExpression:d.expression,fusionNativeValue:d.value})),
})));
// The first extraction sampled this one ellipse. Replace it with the exact
// subsequently inspected Fusion ellipse, in the original Fusion sketch frame.
const notch=sketches.find(s=>s.name==='RearSeatNotchSketch');
const ellipse=notch.curves.find(c=>c.type==='SketchEllipse');
Object.assign(ellipse,{centerMm:[-14.500000000000004,196.70896933768436,8.881784197001252e-15],majorAxis:[1,0,0],majorRadiusMm:3.500000000000001,minorRadiusMm:3.4895137853640384,approximate:false});
delete ellipse.sampledPointsMm;delete ellipse.samplingToleranceMm;

const selectedProfiles=profileSource.features.map(f=>({sourceTimelineIndex:f.index,timelineName:f.timelineName,featureName:f.featureName,profiles:f.profiles.map(p=>({sketch:p.sketch,areaMm2:p.areaCm2*100,centroidMm:mm(p.centroid),loops:p.loops.map(l=>({outer:l.outer,curves:l.curves.map(geometry)}))}))}));
const drafts=profileSource.datums.map(d=>({sourceTimelineIndex:d.index,name:d.name,angleDegrees:d.angleRadians*180/Math.PI,isDirectionFlipped:d.isDirectionFlipped,neutralPlane:{originMm:mm(d.neutralPlaneOrigin),normal:d.neutralPlaneNormal},selectedFaces:d.faces.map(f=>({pointMm:mm(f.point),type:f.type,normal:f.normal}))}));

function reflectVector(v,n){const d=v.reduce((a,x,i)=>a+x*n[i],0);return v.map((x,i)=>x-2*d*n[i]);}
function reflectPoint(v,o,n){return reflectVector(v.map((x,i)=>x-o[i]),n).map((x,i)=>x+o[i]);}
const mirrors=connectorSource.filter(d=>d.mirrorNormal).map(d=>({sourceTimelineIndex:d.index,originMm:mm(d.mirrorOrigin),normal:d.mirrorNormal}));
function connectorInstance(source,order){
  const p=source.profiles[0];let o=mm(p.origin),x=[...p.x],y=[...p.y],direction=cross(x,y).map(v=>-v);
  for(const index of order){const m=mirrors.find(m=>m.sourceTimelineIndex===index);o=reflectPoint(o,m.originMm,m.normal);x=reflectVector(x,m.normal);y=reflectVector(y,m.normal);direction=reflectVector(direction,m.normal);}
  const seen=new Set(),curves=[];
  for(const pr of source.profiles)for(const l of pr.loops)for(const c of l.curves){
    const key=[c.start,c.end].map(p=>p.map(v=>Math.round(v*1e10)/1e10).join(',')).sort().join('|');
    if(!seen.has(key)){seen.add(key);curves.push(geometry(c));}
  }
  return {name:source.index===186?'top':'side'+(order.length?'-mirrored-'+order.join('-'):'-original'),sourceTimelineIndex:source.index,mirrorOrder:order,originMm:o,xAxis:x,yAxis:y,normal:cross(x,y),extrusionDirection:direction,depthMm:8,curves};
}
const top=connectorSource.find(s=>s.index===186),side=connectorSource.find(s=>s.index===188);
const connectors=[connectorInstance(top,[]),connectorInstance(side,[]),connectorInstance(side,[192]),connectorInstance(side,[193]),connectorInstance(side,[192,193])];
const splitA=[0,-92.88539833894989,63.05711325274752],splitB=[0,-109.93653499568712,-20.751900973452995];
const delta=splitB.map((v,i)=>v-splitA[i]),splitN=cross([1,0,0],delta),norm=Math.hypot(...splitN);

const steps=[
  {id:'M01',source:[8,9],operation:'NEW',sketch:'BottomSketch',positiveDepthMm:150,negativeDepthMm:50,direction:[0,0,1]},
  {id:'M02',source:[10],operation:'MIRROR_AND_UNION',plane:{originMm:[0,0,0],normal:[1,0,0]}},
  {id:'M03',source:[11,12],operation:'INTERSECT',sketch:'SideSketch',profileSource:12,depthMm:120,direction:[1,0,0],note:'Depth confirmed by source parameter d16. Some direct operation getters fail for this linked feature.'},
  {id:'M04',source:[13,14],operation:'INTERSECT',sketch:'RearSketch',profileSource:14,depthMm:490,direction:[0,1,0],note:'Retain sketch-space Z=-263.445982162752 mm; its plane is offset in global Y.'},
  {id:'M05',source:[15],operation:'MIRROR_AND_UNION',plane:{originMm:[0,0,0],normal:[1,0,0]}},
  {id:'M06',source:[17,18],operation:'ADD_UP_TO_PLANE',sketch:'TrunkDovetailSketch',profileSource:18,targetPlane:{originMm:[0,-263.44598216275198,109.10684591063722],normal:[0,-1,0]}},
  {id:'M07',source:[74,75],operation:'REMOVE_THROUGH_ALL_BOTH_DIRECTIONS',sketch:'BoltHolesSketch',profileSource:75,diameterMm:7},
  {id:'M08',source:[76],operation:'REMOVE_DOWNWARD_FROM_OFFSET_PLANE',sketch:'BoltHolesSketch',profileSource:76,diameterMm:17,roofOffsetMm:3,note:'Start 3 mm below the top sketch plane, then cut toward underside through all. Preserve the small through-hole and roof.'},
  {id:'M09',source:[77],operation:'REMOVE_BOUNDED_ABOVE_AND_THROUGH_ALL_BELOW',sketch:'BoltHolesSketch',profileSource:77,diameterMm:17,nominalRoofOffsetMm:3,finalRoofPlaneNormal:[0,0.26418906967888117,0.964470909598733],finalRoofPlanePointMm:[23,73.86340632647599,41.74904474222621],note:'Use the exact as-built plane for an Onshape match. Offset is nominally 3 mm; the extrusion axis and sloped roof normal differ. Final Onshape offsetOppositeDirection=false.'},
  {id:'M10',source:[78,79],operation:'NEW',sketch:'SeatHangerSketch',profileSource:79,depthMm:1,direction:'negative sketch normal'},
  {id:'M11',source:[80,81,82],operation:'DRAFT_MIRROR_UNION',draftSource:80,angleDegrees:45,mirrorPlane:{originMm:[0,0,0],normal:[1,0,0]},note:'Draft the hanger, mirror it, and join both hangers to the master.'},
  {id:'M12',source:[83,84],operation:'ADD_SYMMETRIC',sketch:'HandleMountSketch',profileSource:84,totalDepthMm:98,direction:[1,0,0]},
  {id:'M13',source:[85,86],operation:'REMOVE_THROUGH_ALL',sketch:'FrontCutSketch',profileSource:86,direction:[0,0,1]},
  {id:'M14',source:[87],operation:'DRAFT',draftSource:87,angleDegrees:-35},
  {id:'M15',source:[88,89],operation:'REMOVE',sketch:'RearSeatNotchSketch',profileSource:89,depthMm:8,direction:'negative sketch normal'},
  {id:'M16',source:[90,91],operation:'ADD_SYMMETRIC',sketch:'FrontDovetailSketch',profileSource:91,totalDepthMm:80,direction:[1,0,0]},
  {id:'M17',source:[94,95,96,97,98],operation:'REMOVE_CYLINDER_AND_MIRROR',sketch:'SeatCutoutSketch',profileSource:97,mirrorPlane:{originMm:[0,0,0],normal:[1,0,0]},asBuilt:'Through-all in both directions instead of a nonparallel from-face start.',sourceStartPlane:{originMm:[-64.68750101999127,-79.96131101324718,0],normal:[-0.8229961558022109,0.5680469413127609,0]},note:'HingeTrajectorySketch is retained reference geometry. This start-bound adaptation is not a proven exact topology match to Fusion.'},
  {id:'M18',source:[119,120,121,122],operation:'REMOVE_THROUGH_ALL_BOTH_DIRECTIONS_AND_MIRROR',sketch:'RearCutSketch',profileSource:121,mirrorPlane:{originMm:[0,0,0],normal:[1,0,0]}},
  {id:'M19',source:[123,124],operation:'REMOVE_DRAFTED_THROUGH_ALL',sketch:'BodyCutSketch',profileSource:124,startOffsetMm:-12,draftDegrees:15,direction:'negative sketch normal',note:'Taper expands the underside cavity. Specify start-offset bound type explicitly.'},
  {id:'M20',source:[125,126],operation:'REMOVE',sketch:'AirtagCutSketch',profileSource:126,depthMm:8.5,direction:'negative sketch normal'},
  {id:'M21',source:[199],operation:'SUBTRACT_ALIGNED_WHEEL_SCAN',alignment:'wheel-scan-alignment.json',clearanceMm:0,note:'Explicit later user authorization. Use the Sherman P scan, not the old Veteran Sherman L reference asset.'},
];

const recipe={schemaVersion:'1.0',canonicalLengthUnit:'millimeter',angleUnit:'degree',status:'Portable specification of the accepted Onshape rebuild; not a tested SolidCraft or Zoo implementation',sourceDocument:timeline.document,sourceTimelineIndices:'zero-based',globalAxes:{x:'left/right width',y:'front toward screen cutout is positive',z:'up'},positionFormula:'globalMm = originMm + xAxis*uMm + yAxis*vMm + normal*wMm; normal = cross(xAxis,yAxis). Do not drop nonzero sketch-space w.',scope:{master:'one unsplit solid with wheel imprint',child:'associative master copy split into two solids, five 8 mm connector recesses',fillets:false,separateConnectorInserts:false},sourceUserParameters:timeline.userParameters.map(p=>({...p,valueMm:p.unit==='mm'?p.value*10:null})),sketches,selectedProfiles,drafts,masterSteps:steps,child:{relationship:'live/associative link to completed master',splitPlane:{originMm:splitA,normal:splitN.map(v=>v/norm),lineEndpointsMm:[splitA,splitB],extrusionDirectionAcrossWidth:[1,0,0],keepBothSides:true},connectorMirrors:mirrors,connectorInstances:connectors,depthMm:8,notImplementedFromSource:[191,194,195,196,197,198],note:'No source fillets, loose connector inserts, or Gap-based insert offsets were reproduced.'},scan:read('wheel-scan-alignment.json'),finalValidation:read('wheel-imprint-state.json')};
write('cad-rebuild/recipe.json',recipe);

let catalog='# Fusion sketch catalog\n\nGenerated from the saved extraction. All positions and radii below are millimeters; direction vectors are unitless. Full exact geometry is in [recipe.json](../cad-rebuild/recipe.json). Original dimension expressions are preserved there without guessing their units.\n\n';
for(const s of sketches){
 catalog+=`## ${s.name} (timeline ${s.sourceTimelineIndex})\n\nComponent: \`${s.sourceComponent}\`. Curves: ${s.curves.length}.\n\n- Origin: \`${vector(s.originMm)}\`\n- X axis: \`${vector(s.xAxis)}\`\n- Y axis: \`${vector(s.yAxis)}\`\n- Normal: \`${vector(s.normal)}\`\n\n`;
 const zs=s.curves.flatMap(c=>['startMm','endMm','centerMm'].filter(k=>c[k]).map(k=>c[k][2]));
 if(zs.some(z=>Math.abs(z)>1e-7))catalog+='Some curve points have nonzero sketch-space Z. Apply the full 3D frame transform before flattening to a target sketch plane.\n\n';
 catalog+='| Parameter | Original expression |\n|---|---|\n';
 for(const d of s.dimensions)catalog+=`| ${d.name} | ${d.sourceExpression.replaceAll('|','\\|')} |\n`;
 catalog+='\n';
}
write('docs/SKETCH-CATALOG.md',catalog);

const masterUsed=new Set(steps.flatMap(s=>s.source));
const childUsed=new Set([183,184,185,186,187,188,189,190,192,193]);
function disposition(t){
 if(t.index===131||t.index===132)return 'Excluded old Veteran Sherman L asset cut/removal; replaced by later Sherman P scan imprint';
 if(t.index===93)return 'Skipped: zero produced faces/bodies and unchanged body volume before/after';
 if(t.index===199)return 'Reference source for later authorized Sherman P scan imprint';
 if(t.entityType?.includes('Fillet'))return 'Excluded: all fillets cancelled by user';
 if([194,195,196].includes(t.index))return 'Excluded: separate inserts/Gap offsets not recreated';
 if(childUsed.has(t.index))return 'Child split/connectors; construction reorganized in Onshape';
 if(masterUsed.has(t.index))return 'Master geometry or its reference sketch/datum';
 if([179,180,181,182].includes(t.index))return 'Fusion copy/move/component setup replaced with live child derivation';
 if(t.suppressed)return 'Suppressed source branch; not recreated';
 return 'Other source component/reference; not part of requested adapter rebuild';
}
let table='# Fusion timeline map\n\nAll 200 source markers are listed with zero-based indices. Disposition describes the accepted rebuild, not an instruction to replay unrelated assembly branches. The Fusion entityComponent field is preserved in the JSON but can be misleading for linked/reparented features (notably index 12); use selected profiles and the feature recipe.\n\n| Index | Source marker | Entity type | Suppressed | Rebuild disposition |\n|---:|---|---|:---:|---|\n';
for(const t of timeline.timeline)table+=`| ${t.index} | ${t.name.trim().replaceAll('|','\\|')} | ${(t.entityType??'').split('::').at(-1)} | ${t.suppressed?'yes':'no'} | ${disposition(t)} |\n`;
table+='\n## Source warnings\n\nWarnings were captured before rebuilding. They are evidence about source references, not current Onshape failures. See the JSON for full messages.\n\n';
for(const t of timeline.timeline.filter(t=>t.message))table+=`- ${t.index}: \`${t.name.trim()}\` - ${t.message.replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').slice(0,500)}\n`;
write('docs/FUSION-TIMELINE.md',table);

let features='# Portable master feature sequence\n\nUse this with [the rebuild guide](CAD-REBUILD.md), [sketch catalog](SKETCH-CATALOG.md), and [recipe.json](../cad-rebuild/recipe.json). Exact selected profile loops, areas, and centroids are in the recipe. Do not extrude every region of a sketch indiscriminately.\n\n| Step | Fusion indices | Operation | Sketch / datum | Main dimensions |\n|---|---|---|---|---|\n';
for(const s of steps){const dims=Object.entries(s).filter(([k])=>/Mm$|Degrees$/.test(k)&&typeof s[k]==='number').map(([k,v])=>`${k}: ${fmt(v)}`).join('; ');features+=`| ${s.id} | ${s.source.join(', ')} | ${s.operation} | ${s.sketch??(s.draftSource?'draft '+s.draftSource:'')} | ${dims} |\n`;}
features+='\n## Draft datums\n\n';
for(const d of drafts)features+=`- ${d.sourceTimelineIndex} ${d.name}: ${fmt(d.angleDegrees)} degrees; neutral origin \`${vector(d.neutralPlane.originMm)}\`, normal \`${vector(d.neutralPlane.normal)}\`. Selected face points and normals are in the recipe.\n`;
features+='\n## Selected profile evidence\n\n| Fusion feature index | Marker | Sketch | Area (mm²) | Centroid in sketch coordinates (mm) |\n|---:|---|---|---:|---|\n';
for(const f of selectedProfiles)for(const p of f.profiles)features+=`| ${f.sourceTimelineIndex} | ${f.timelineName} | ${p.sketch} | ${fmt(p.areaMm2)} | ${vector(p.centroidMm)} |\n`;
write('docs/FEATURE-RECIPE.md',features);

const currentSketches=read('onshape-current-sketch-ids.json');
for(const s of ['SplitBodySketch','TopJointSketch','SideJointSketch'])delete currentSketches[s];
const imprint=read('wheel-imprint-state.json'),child=read('child-split-state.json'),connectorsState=read('connector-cutouts-state.json');
const manifest={status:'Final accepted state, documented 2026-11-12; not a live API inventory',document:imprint.master.doc,workspace:imprint.master.ws,master:imprint.master,child:imprint.child,scan:imprint.scanPartStudio,masterSketches:currentSketches,features:{childDerived:child.derivedFeature,childSplitPlane:child.planeFeature,childSplit:child.splitFeature,childConnectors:connectorsState.featureId,rearScrewAccess:'F9orq0gyXHsXnGW_1',frontScrewAccess:'FXQWXmmJub3ISHs_1',scanDerived:imprint.scanDerivedFeature,scanScale:imprint.scanUnitScaleFeature,wheelImprint:imprint.booleanFeature},versions:{preImprint:imprint.preImprintVersion,historicalUnsplitWithFillets:'6fc7581e82a4b84cb8cd893f'},authoritativeFrontScrewPayload:'../front-screw-ceiling-correction.json',validation:imprint};
write('cad-rebuild/onshape-current-manifest.json',manifest);
write('BUILD-SEQUENCE.md',`# Current build sequence and handoff

This is the current handoff for the completed Fusion-to-Onshape rebuild. The old incremental notes are preserved at [docs/history/BUILD-SEQUENCE-session-log.md](docs/history/BUILD-SEQUENCE-session-log.md). They contain superseded instructions and stale IDs.

## Read first

1. [Onshape reconstruction notes](docs/ONSHAPE-RECONSTRUCTION.md): captured Onshape model structure and file map.
2. [CAD rebuild guide](docs/CAD-REBUILD.md): source geometry, corrections and datums.
3. [Portable recipe](cad-rebuild/recipe.json): millimeter geometry and selected loops for another CAD engine.
4. [Porting and validation](docs/PORTING-AND-VALIDATION.md): implementation and verification checklist.
5. [Current manifest](cad-rebuild/onshape-current-manifest.json): saved final IDs and measured state.

## Accepted sequence

1. Rebuild the unsplit master using the bottom, side and rear profiles, signed extrusions, intersections, mirrors and unions.
2. Add dovetails, drafted hangers, handle mount, relief cuts, underside tapered cavity and AirTag recess.
3. Preserve four 7 mm through-holes and four larger 17 mm downward screwdriver-access recesses with retained mounting ceilings. Apply the final front ceiling correction, not the earlier reversed offset.
4. Align the supplied Sherman P scan using the saved exact transform, check units, and subtract the zero-clearance underside imprint from the master.
5. Reference the completed master associatively in a separate printing child. Keep the master unsplit.
6. Split the child into two solids on the plane from the first Fusion SplitBodySketch line.
7. Add five 8 mm-deep connector recesses to the child: one top and four side locations using the saved mirror planes.
8. Verify one master solid, two child solids, retained screw ceilings, open small holes and access cavities, and healthy inherited/connector features.

No fillets or separate loose inserts are included. The old Veteran Sherman L cut is excluded; the later explicitly authorized Sherman P scan imprint is included. The source Gap parameter is recorded, but its insert offsets were not applied.

## Current status

The sequence above was completed and checked in Onshape. The user visually reviewed the close reconstruction and requested the documented corrections. The complete Fusion constraint graph and an exhaustive whole-assembly equality comparison were not captured.

Saved evidence includes all 200 source timeline markers, 18 sketches, 37 exact selected profiles, 149 model parameters, the Gap user parameter, exact scan placement, source scripts, final FeatureScript and validation.

Conserve future Onshape API calls. Run node scripts/generate-cad-reference.mjs to regenerate local tables and recipe files. Do not automatically replay live upload scripts or historical transient IDs.
`);
console.log(JSON.stringify({timeline:timeline.timeline.length,sketches:sketches.length,selectedProfiles:selectedProfiles.reduce((n,f)=>n+f.profiles.length,0),masterSteps:steps.length,connectorInstances:connectors.length,canonicalUnit:recipe.canonicalLengthUnit}));
