// Local-only conversion of saved Fusion evidence. No CAD/API calls.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const raw=JSON.parse(fs.readFileSync(path.join(dir,'../../reference/fusion/accessories/fusion-accessories-raw.json'),'utf8'));
const ops={0:'join',1:'cut',2:'intersect',3:'newBody',4:'newComponent'};
const vectors=new Set(['xAxis','yAxis','normal','axis','majorAxis','directionHint']);
const lengths=new Set(['origin','start','mid','end','center','point','centroid','points','boundingBox','radius','majorRadius','minorRadius','length']);
function multiply(v,n){return Array.isArray(v)?v.map(x=>multiply(x,n)):v*n;}
function convert(value,key=''){
  if(value===null||typeof value!=='object')return value;
  if(Array.isArray(value))return value.map(v=>convert(v));
  if('expression'in value&&'value'in value&&'unit'in value){
    const angle=/deg|rad/.test(value.unit);
    return {name:value.name,sourceExpression:value.expression,value:value.value*(angle?180/Math.PI:10),unit:angle?'degree':'millimeter',sourceUnitLabel:value.unit};
  }
  const out={};
  for(const [k,v]of Object.entries(value)){
    if(vectors.has(k))out[k]=v;
    else if(lengths.has(k)&&v!==null)out[k]=multiply(v,10);
    else if(k==='volumeCm3')out.volumeMm3=v*1000;
    else if(k==='areaCm2'||k==='area')out.areaMm2=v*100;
    else if(k==='approximationToleranceCm')out.approximationToleranceMm=v*10;
    else if(k==='startAngle'||k==='endAngle')out[k+'Degrees']=v*180/Math.PI;
    else if(k==='transform'){
      out.transform=[...v];
      // Fusion Matrix3D.asArray uses row-major order, translation entries3,7,11.
      for(const i of [3,7,11])out.transform[i]*=10;
    }else out[k]=convert(v,k);
  }
  return out;
}
const header={schemaVersion:'1.0',canonicalLengthUnit:'millimeter',angleUnit:'degree',sourceDocument:raw.sourceDocument,timelineIndices:'zero-based',status:'Extracted source recipe; not yet built or validated in a target CAD engine',scope:{separatePart:true,fillets:false},coordinateRule:'Profile loop coordinates are in the named parent sketch. global=origin+u*xAxis+v*yAxis+w*cross(xAxis,yAxis). Preserve local w. Frame axes are dimensionless.',startPlaneWarning:'Fusion startExtent.profilePlane is reported in profile-local coordinates. Use the named sketch frame for global sketch planes; FromEntity starts use their explicitly captured global entity plane.',externalDependencies:convert(raw.externalSketches),sourceUserParameters:convert(raw.userParameters)};
const all=[];
for(const source of raw.parts){
  const p=convert(source);
  for(const f of p.features){
    if('operation'in f)f.operationName=ops[f.operation];
    f.rebuildDisposition=f.sourceOnlyDoNotBuild?'omitFillet':'recreate';
    if(f.profiles)for(const profile of f.profiles){
      const s=[...p.sketches,...header.externalDependencies].find(s=>s.name===profile.sketch);
      if(s){
        const [a,b]=[s.xAxis,s.yAxis];
        profile.sketchNormal=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
        profile.coordinateFrame=profile.sketch;
      }
    }
  }
  const last=p.features.filter(f=>f.rebuildDisposition==='recreate').at(-1);
  p.validation={noFilletBodies:last.bodiesAfter,sourceWithFilletBodies:p.finalBodies,comparison:'The no-fillet checkpoint is the correct rebuild target under the user decision. Source final filleted metrics are archival only.'};
  const recipe={...header,...p};
  const filename=p.name==='Latch'?'latch-recipe.json':'saddle-bag-mount-recipe.json';
  fs.writeFileSync(path.join(dir,filename),JSON.stringify(recipe,null,2)+'\n');
  all.push({filename,recipe});
}
fs.writeFileSync(path.join(dir,'../../reference/fusion/accessories/extraction-validation.json'),JSON.stringify({sourceDocument:raw.sourceDocument,markerBefore:raw.markerBefore,markerAfter:raw.markerAfter,errors:raw.errors,parts:all.map(({recipe:r})=>({name:r.name,sketches:r.sketches.length,sketchCurves:r.sketches.reduce((n,s)=>n+s.curves.length,0),dimensions:r.sketches.reduce((n,s)=>n+s.dimensions.length,0),constraints:r.sketches.reduce((n,s)=>n+s.constraints.length,0),features:r.features.length,selectedProfiles:r.features.reduce((n,f)=>n+(f.profiles?.length||0),0),offsetFaceSelections:r.features.reduce((n,f)=>n+(f.inputFaces?.length||0),0),sourceFilletsRecorded:r.features.filter(f=>f.sourceOnlyDoNotBuild).length,noFilletVolumeMm3:r.validation.noFilletBodies.reduce((n,b)=>n+b.volumeMm3,0)})),onshapeApiCalls:0,geometryModified:false,sourceSaved:false},null,2)+'\n');
const fmt=n=>Number(n.toPrecision(10)).toString();
const vec=v=>'('+v.map(fmt).join(', ')+')';
const param=p=>p?`${fmt(p.value)} ${p.unit} (source \`${p.sourceExpression}\`)`:'none';
function description(f){
 if(f.sourceOnlyDoNotBuild)return 'Record source edge selections and radii; omit from this rebuild (no fillets).';
 if(f.type.endsWith('MirrorFeature'))return `Mirror ${f.inputEntities.map(x=>x.name||x.type).join(', ')} about ${f.mirrorPlane.name}; combine = ${f.isCombine}.`;
 if(f.type.endsWith('OffsetFacesFeature'))return `Offset ${f.inputFaces.length} selected faces by ${param(f.distance)}. Select by saved global point, surface normal, area and body/component, not transient IDs.`;
 if(f.type.endsWith('ExtrudeFeature')){
   const e=f.extentOne;
   let extent=e.distance?param(e.distance):e.type.endsWith('ToEntityExtentDefinition')?`up to saved ${e.entity.component}/${e.entity.body} target plane, offset ${param(e.offset)}`:'through all';
   return `${f.operationName}: ${f.profiles.length} selected region(s) from ${[...new Set(f.profiles.map(p=>p.sketch))].join(', ')}; ${extent}${f.extentTwo?'; second extent also recorded':''}${f.startExtent.type.endsWith('FromEntityStartDefinition')?'; start from saved entity plane (not sketch plane)':''}.`;
 }
 return 'See recipe.';
}
let doc=`# Latch and saddle bag mount: Fusion extraction\n\nThese are **separate parts**, extracted from \`${raw.sourceDocument}\` for reference. Build123d provides a [separate editable latch](../README.md#separate-latch). The saddlebag mount remains extracted only. Read the [adapter guide](CAD-REBUILD.md) for the shared assembly coordinate convention. This accessory scope was added after that guide was written.\n\nThe source API uses centimeters and radians; both accessory recipes use **millimeters and degrees**. All timeline indices are zero-based. Extraction temporarily rolled the source timeline and restored marker **${raw.markerAfter}**; no source geometry was edited or document saved. No Onshape API calls were made.\n\n## Files\n\n- [Latch recipe](../cad-rebuild/accessories/latch-recipe.json)\n- [Saddle bag mount recipe](../cad-rebuild/accessories/saddle-bag-mount-recipe.json)\n- [Raw Fusion evidence](../reference/fusion/accessories/fusion-accessories-raw.json)\n- [Extraction verification](../reference/fusion/accessories/extraction-validation.json)\n- [Rerunnable Fusion extraction script](../reference/fusion/accessories/extract-fusion-accessories.py)\n- [Local recipe generator](../cad-rebuild/accessories/generate-accessory-recipes.mjs)\n\n## Shared references and reconstruction rules\n\nBoth parts use the adapter's **TrunkDovetailSketch**, not merely their own sketches. Each standalone recipe includes that external sketch's full frame, curves, dimensions and constraints as a dependency, plus the exact selected loops for the accessory operations. The original parts are nested under AdapterBody in the assembly, but remain separate bodies/components. Their saved occurrence matrices are identity, so component and assembly coordinates coincide. Do not union them into the adapter.\n\nRebuild sketches from exact line, arc, circle and elliptical-arc geometry. Source projected/reference curves have their evaluated geometry saved; they can become explicit target sketch geometry if the target cannot reproduce the original projection relationship. Preserve construction flags, local Z, constraint intent and original expressions. Dimensions are extracted, with source constraint entity references where exposed by the API; this is not a fully serialized Fusion constraint solver. Exact selected loops are authoritative when a sketch contains adjoining regions.\n\nA profile loop is in its **named sketch frame**; transform using origin, X, Y and cross(X,Y). Do not use the source \`startExtent.profilePlane\` as a global plane: Fusion reports that in profile-local coordinates. Explicit FromEntity start and ToEntity end planes are global, with component/body context. The ToEntity \`directionHint\` is dimensionless. Preserve signed blind distances and taper values. For through-all intersection, preserve the two-sided extent arrangement and intersect with the correct current part.\n\nOffset face selectors record the pre-feature global point, geometry, area and \`isParamReversed\`; the actual oriented face normal is the surface normal reversed when that flag is true. Use the signed source distance, including negative \`Gap=-0.2 mm\` and \`Gap*1.5=-0.3 mm\`. These are source functional fit offsets, separate from the adapter wheel-imprint's zero added clearance.\n\nSource fillets are documented with edge geometry and radii, but **must be omitted** under the user's no-fillets instruction. Use the pre-fillet metrics below for a new build.\n`;
for(const {recipe:r}of all){
 const c=r.validation.noFilletBodies[0];
 doc+=`\n## ${r.name}\n\n${r.name==='Latch'?'The latch mates with the rear adapter dovetail.':'The saddle bag mount remains a distinct accessory part.'} ${r.sketches.length} local sketches; ${r.features.length} source features, including one archival fillet.\n\n| Timeline | Sketch | Curves | Dimensions | Constraints | Origin mm | X axis | Y axis |\n|---:|---|---:|---:|---:|---|---|---|\n`;
 for(const s of r.sketches)doc+=`| ${s.index} | ${s.name} | ${s.curves.length} | ${s.dimensions.length} | ${s.constraints.length} | ${vec(s.origin)} | ${vec(s.xAxis)} | ${vec(s.yAxis)} |\n`;
 doc+='\nBuild features in **timeline order**, not the API collection order:\n\n| Timeline | Feature | Action | Volume after, mm^3 |\n|---:|---|---|---:|\n';
 for(const f of r.features)doc+=`| ${f.index} | ${f.name} | ${description(f)} | ${fmt(f.bodiesAfter.reduce((n,b)=>n+b.volumeMm3,0))} |\n`;
 doc+=`\nExpected no-fillet result: **${r.validation.noFilletBodies.length} solid**, volume **${fmt(c.volumeMm3)} mm^3**, bounding box **${vec(c.boundingBox[0])}  to  ${vec(c.boundingBox[1])} mm**. Source final filleted volume (archival): ${fmt(r.finalBodies[0].volumeMm3)} mm^3. Verify each intermediate volume in the recipe as the target features are created.\n`;
}
doc+='\n## Verification and limits\n\nThe saved extraction has zero property-read errors. The timeline marker before/after is 200/200. Both source parts are single solids; all eight extrusions have their selected profile loops, end definitions and start definitions saved. All four offset features have explicit face selectors; the latch mirror includes its global YZ plane and combine flag. No physical print test has been performed. Transient Fusion body names such as Body1 are ambiguous across components; always use the recorded component plus geometry. Use the no-fillet checkpoints, not the source final filleted metrics, when checking the requested rebuild.\n\nRun the local-only generator with `node cad-rebuild/accessories/generate-accessory-recipes.mjs`. The Python extractor requires the original Fusion design open and temporarily changes the timeline marker; do not label that invocation read-only, and do not run it during an unfinished interactive command. It restores the marker in a finally block and never saves the document.\n';
fs.writeFileSync(path.join(dir,'../../docs/ACCESSORY-PARTS.md'),doc);
console.log(JSON.stringify({parts:all.map(({recipe:r})=>r.name),filesWritten:4,propertyReadErrors:raw.errors.length,markerRestored:raw.markerBefore===raw.markerAfter}));

