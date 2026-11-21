import fs from 'node:fs';
import { basename } from 'node:path';

const input = new URL('../fusion/Sherman_P_Flush_Screen_Fusion_Default.stl', import.meta.url);
const output = process.argv[2];
if (!output) throw new Error('Pass the output STL path');
const raw = fs.readFileSync(input);
const count = raw.readUInt32LE(80);
if (raw.length !== 84 + count * 50) throw new Error('Unexpected binary STL layout');
const localShift = [-215.88780212402347, -82.9285278320313, -387.6817016601563];
const occurrenceTranslation = [-0.29169701859548116, 222.19752512903554, 15];
const rotation = [-1, -1, 1];
const translation = localShift.map((v,i) => rotation[i]*v + occurrenceTranslation[i]);
const aligned = Buffer.from(raw);
const vertices = new Map();
const edges = new Map();
const min = [Infinity,Infinity,Infinity], max = [-Infinity,-Infinity,-Infinity];
let volume = 0;
for (let t=0;t<count;t++) {
  const at=84+50*t;
  for(let k=0;k<3;k++) aligned.writeFloatLE(raw.readFloatLE(at+4*k)*rotation[k],at+4*k);
  const tri=[];
  for(let v=0;v<3;v++) {
    const p=[];
    for(let k=0;k<3;k++) {
      const x=raw.readFloatLE(at+12+v*12+k*4)*rotation[k]+translation[k];
      aligned.writeFloatLE(x,at+12+v*12+k*4);
      p.push(x); min[k]=Math.min(min[k],x); max[k]=Math.max(max[k],x);
    }
    tri.push(p);
  }
  const [a,b,c]=tri;
  volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;
  const keys=tri.map(p=>p.map(v=>Math.round(v*10000)).join(','));
  keys.forEach(k=>vertices.set(k,true));
  for(let e=0;e<3;e++) {const key=[keys[e],keys[(e+1)%3]].sort().join('|');edges.set(key,(edges.get(key)||0)+1);}
}
const badEdges=[...edges.values()].filter(n=>n!==2).length;
if(badEdges) throw new Error(`Scan is not closed: ${badEdges} non-manifold/boundary edges`);
const sourceSample=[5.593046569824217,-0.8041748046875057,1.7643463134765618];
const expectedRaw=sourceSample.map((v,i)=>v*10-localShift[i]);
let sampleError=Infinity;
for(let t=0;t<count;t++)for(let v=0;v<3;v++) {
  let error=0;for(let k=0;k<3;k++)error+=Math.pow(raw.readFloatLE(84+t*50+12+v*12+k*4)-expectedRaw[k],2);
  sampleError=Math.min(sampleError,Math.sqrt(error));
}
if(sampleError>0.001) throw new Error('STL did not match the Fusion scan sample');
fs.writeFileSync(output,aligned);
const report={input:basename(input.pathname),output:basename(output),units:'millimeter',triangles:count,uniqueVertices:vertices.size,badEdges,rotationDiagonal:rotation,translationMillimeters:translation,boundsMillimeters:{min,max},volumeMillimetersCubed:Math.abs(volume),fusionReferenceVolumeMillimetersCubed:4221287.871964949,sampleMatchErrorMillimeters:sampleError,alignmentSource:'Existing Sherman P Body Top Refined v4 component geometry and occurrence transform in Fusion'};
console.log(JSON.stringify(report));
