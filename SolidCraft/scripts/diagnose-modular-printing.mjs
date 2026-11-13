// Isolated native stage reproducer. Never opens or saves the desktop document.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {root,log,write,command as c} from './modular-cad.mjs';
import {writeNative,readNative,sha256,assertPreparedRun,partitionCurrentDocument,compareStageGeometry,assertEvidenceCurrent} from './modular-native-history.mjs';
const dir=fs.mkdtempSync(path.join(root,'models/experiments/printing-stages-'));
const reportDir=path.join(log,path.basename(dir));fs.mkdirSync(reportDir);
const attempt={runDir:dir,reportDir,status:'running',startedAt:new Date().toISOString()};
write(path.join(log,'printing-attempt.json'),attempt);
const results=[];
try {
 const current=JSON.parse(fs.readFileSync(path.join(log,'current-run.json')));
 const validation=JSON.parse(fs.readFileSync(path.join(log,'native-history-validation.json')));
 assertEvidenceCurrent(JSON.parse(fs.readFileSync(path.join(log,'native-attempt.json'))),validation);
 assert.equal(validation.runDir,current.runDir,'Prepared manifest and validation disagree');
 assertPreparedRun(current);
 const source=JSON.parse(fs.readFileSync(path.join(current.runDir,'current-document.json')));
 const masterComponent=source.components.find(c=>c.name==='AdapterBody');
 const partition=partitionCurrentDocument(source,{masterComponentId:masterComponent?.id});
 const copy=partition.printingFeatures.find(f=>f.name==='C01_DependentMasterCopy');
 const transfer=partition.printingFeatures.find(f=>f.type==='body_transfer');
 const split=partition.printingFeatures.find(f=>f.name==='C02_PrintSplit');
 assert(copy&&transfer&&split,'Missing recorded printing definitions');
 assert.equal(transfer.to,partition.printingComponents[0].id,'Transfer target differs from printing component');
 const baseline=validation.baseline.bodies.find(b=>b.name==='AdapterBodyMaster');
 const cli='C:/Program Files/SolidCraft/solidcraft-cli.exe';
 const run=(args,name,targetBody)=>{
   const r=spawnSync(cli,args,{encoding:'utf8',windowsHide:true,timeout:240000});
   fs.writeFileSync(path.join(reportDir,name+'.txt'),r.stderr||r.stdout||'');
   const report=args.includes('--json-out')?args[args.indexOf('--json-out')+1]:null;
   const commandOk=r.status===0;
   const data=commandOk?JSON.parse(fs.readFileSync(report)):null;
   const measurement=data?.bodies.find(b=>b.name===targetBody);
   let geometry=commandOk?compareStageGeometry(baseline,measurement):null;
   if(commandOk&&name==='split'){
     const halves=['AdapterBodyFront','AdapterBodyRear'].map(n=>data.bodies.find(b=>b.name===n));
     if(halves.every(b=>b?.closed)){
       const volume=halves.reduce((s,b)=>s+b.volume_mm3,0);
       const combined={closed:true,volume_mm3:volume,bbox:{min:[0,1,2].map(i=>Math.min(...halves.map(b=>b.bbox.min[i]))),max:[0,1,2].map(i=>Math.max(...halves.map(b=>b.bbox.max[i])))},center_of_mass:[0,1,2].map(i=>halves.reduce((s,b)=>s+b.center_of_mass[i]*b.volume_mm3,0)/volume)};
       geometry=compareStageGeometry(baseline,combined);
     }else geometry={ok:false,errors:['Missing/open printing halves']};
   }
   if(commandOk&&name==='connectors'){
     const checks=['AdapterBodyFront','AdapterBodyRear'].map(n=>compareStageGeometry(validation.baseline.bodies.find(b=>b.name===n),data.bodies.find(b=>b.name===n)));
     geometry={ok:checks.every(c=>c.ok),halves:checks};
   }
   return {commandOk,geometryAccepted:geometry?.ok===true,geometry,status:r.status,error:r.stderr,report};
 };
 const seed=structuredClone(source);seed.name='SeatAdapter';seed.features=[];
 seed.components=seed.components.filter(x=>x.id!==masterComponent.id);
 seed.occurrences=seed.occurrences.filter(x=>x.component!==masterComponent.id);seed.visibility.hidden_occurrences=[];
 const seedPath=path.join(dir,'seed.sc');
 writeNative({sourcePath:current.sourcePath,outputPath:seedPath,document:seed,expectedSha256:current.sourceHash});
 const linkScript=path.join(dir,'link.json'),linked=path.join(dir,'linked.sc');
 write(linkScript,{commands:[c('component.insert_design',{path:current.master,name:'AdapterBody',parent:0})]});
 const link=run(['run',linkScript,'--in',seedPath,'--save',linked,'--json-out',path.join(reportDir,'link.json')],'link','AdapterBodyMaster');
 results.push({name:'link',...link});assert(link.commandOk,link.error);
 const linkNative=readNative(linked,path.join(dir,'linked-document.json')).document;
 assert(!linkNative.features.some(f=>partition.printingFeatures.some(p=>p.id===f.id)),'Linked feature ID collides with preserved printing history');
 // Continue through independent stages to diagnose the later kernel error even
 // when import geometry already fails. That never makes the attempt successful.
 for(const [name,features] of [['copy',[copy]],['transfer',[copy,transfer]],['split',[copy,transfer,split]],['connectors',partition.printingFeatures]]){
   const d=structuredClone(linkNative);d.features.push(...structuredClone(features));
   const input=path.join(dir,name+'.sc'),output=path.join(dir,name+'-built.sc');
   writeNative({sourcePath:linked,outputPath:input,document:d,expectedSha256:sha256(fs.readFileSync(linked))});
   const result=run(['run',input,'--save',output,'--json-out',path.join(reportDir,name+'.json')],name,'AdapterBodyFront');
   results.push({name,input,output,...result});console.log(JSON.stringify({stage:name,commandOk:result.commandOk,geometryAccepted:result.geometryAccepted,error:result.commandOk?null:result.error}));
   if(!result.commandOk)break;
 }
 assertPreparedRun(current);
 const ok=results.length===5&&results.every(r=>r.commandOk&&r.geometryAccepted);
 const summary={ok,stageDiagnosticsOnly:true,printingAcceptancePassed:false,runDir:dir,reportDir,master:current.master,results,firstGeometryMismatch:results.find(r=>r.commandOk&&!r.geometryAccepted)?.name??null};
 write(path.join(reportDir,'summary.json'),summary);write(path.join(log,'printing-stages.json'),summary);
 write(path.join(log,'printing-attempt.json'),{...attempt,status:ok?'complete':'failed',reason:'Full printing acceptance additionally requires the separate inheritance/health validator',finishedAt:new Date().toISOString()});
 if(!ok)process.exitCode=1;
} catch(error){
 const summary={ok:false,runDir:dir,reportDir,error:error.message,results};
 write(path.join(reportDir,'summary.json'),summary);write(path.join(log,'printing-stages.json'),summary);
 write(path.join(log,'printing-attempt.json'),{...attempt,status:'failed',finishedAt:new Date().toISOString(),error:error.message});
 throw error;
}
