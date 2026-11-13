import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
export const root=fileURLToPath(new URL('../',import.meta.url));
export const log=path.join(root,'logs/modular-latch');
export const model=n=>path.join(root,'models',n).replaceAll('\\','/');
export const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
export function cad(commands,label,{rollback=true}={}) {
  const input=path.join(log,`${label}-request.json`), output=path.join(log,`${label}-response.json`);
  write(input,{name:'batch',arguments:{commands,verbose:false,rollback}});
  const result=spawnSync(process.execPath,[path.join(root,'scripts/mcp-call.mjs'),input,output],{encoding:'utf8',windowsHide:true,timeout:240000});
  if(result.status!==0)throw new Error(`Desktop RPC ${label}: ${result.stderr||result.error}`);
  const outer=JSON.parse(fs.readFileSync(output,'utf8'))[0];
  const content=outer.content?.find(c=>c.type==='text')?.text;
  let response;try{response=JSON.parse(content);}catch{throw new Error(content??JSON.stringify(outer));}
  if(outer.isError||!response.ok)throw new Error(`${label}: ${JSON.stringify(response)}`);
  return response.results;
}
export const command=(command,params={})=>({command,params});
export const inspect=label=>cad([command('document.inspect',{timeline:'summary',measure:true}),command('component.list')],label);
