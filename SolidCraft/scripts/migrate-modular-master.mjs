import fs from 'node:fs';
import path from 'node:path';
import {cad,command as c,inspect,root,log,model,write} from './modular-cad.mjs';

if(!process.argv.includes('--apply'))throw new Error('One-time native migration: supply --apply after preserving the current desktop document');
const [before,tree]=inspect('migration-start');
if(before.dirty)throw new Error('Save current desktop work before migration');
if(before.path?.replaceAll('\\','/').toLowerCase()!==model('seat-adapter.sc').toLowerCase())throw new Error('Expected saved migration input seat-adapter.sc');
if(fs.existsSync(model('adapter-body.sc')))throw new Error('Source destination already exists; inspect rather than overwriting');
write(path.join(log,'baseline.json'),{capturedAt:new Date().toISOString(),design:before,tree});
// Definitions were read from the saved current native document, not a historical generator.
const native=JSON.parse(fs.readFileSync(path.join(log,'source-document.json'),'utf8'));
const branch=native.features.filter(f=>f.id===59||f.component===60);
write(path.join(log,'printing-branch.json'),{commands:branch.map(feature=>c('timeline.add',{feature})),components:native.components.filter(x=>x.id===60),occurrences:native.occurrences.filter(x=>x.component===60)});
fs.mkdirSync(path.join(root,'models/experiments'),{recursive:true});
try {
  cad([c('file.save',{path:model('experiments/modular-extraction-input.sc')})],'preserve-extraction-copy');
  cad([c('timeline.delete',{features:branch.map(f=>f.id)})],'remove-print-branch');
  const [extraction]=cad([c('component.extract',{component:'AdapterBody',path:model('adapter-body.sc')})],'extract-master');
  write(path.join(log,'extraction.json'),extraction);
  // This stage is intentionally not a successful migration claim; subsequent
  // parameterization, rewiring and geometric validation must pass first.
  console.log(JSON.stringify({ok:true,stage:'source-extracted',extraction}));
} catch(error) {
  // Only this controller's temporary native copy was changed. Reopen the
  // committed original rather than saving partial geometry to a live target.
  cad([c('doc.open',{path:before.path})],'restore-recovery-checkpoint');
  const [restored,restoredTree]=inspect('restored-checkpoint');
  const manufactured=['AdapterBodyMaster','AdapterBodyFront','AdapterBodyRear'];
  const equal=manufactured.every(name=>{
    const a=before.bodies.find(b=>b.name===name),b=restored.bodies.find(b=>b.name===name);
    return b?.closed && ['volume_mm3','bbox','center_of_mass'].every(k=>JSON.stringify(a[k])===JSON.stringify(b[k]));
  });
  write(path.join(log,'migration-attempt.json'),{ok:false,stage:'master-extraction',error:error.message,recoveryCommit:'e56b2ce',restored:equal&&!restored.dirty,design:restored,tree:restoredTree});
  throw new Error(`${error.message}; recovery ${equal&&!restored.dirty?'verified':'FAILED: inspect desktop'}`);
}
