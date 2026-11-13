import fs from 'node:fs';
import path from 'node:path';
import net from 'node:net';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const executable='C:/Program Files/SolidCraft/solidcraft-cli.exe';
const args=['mcp','--connect','127.0.0.1:7878','--allow-path',root,'--compact'];
const desktopListening=await new Promise(resolve=>{
 const socket=net.createConnection({host:'127.0.0.1',port:7878});
 const done=value=>{socket.destroy();resolve(value);};
 socket.once('connect',()=>done(true));socket.once('error',()=>done(false));socket.setTimeout(1500,()=>done(false));
});
const child=spawn(executable,args,{windowsHide:true,stdio:['pipe','pipe','pipe']});
let buffer='',sequence=0,stderr='';const waiting=new Map();
child.stderr.on('data',chunk=>{stderr+=chunk.toString();});
child.stdout.on('data',chunk=>{
 buffer+=chunk.toString();
 while(buffer.includes('\n')){
  const at=buffer.indexOf('\n'),line=buffer.slice(0,at).trim();buffer=buffer.slice(at+1);
  if(!line)continue;
  let message;try{message=JSON.parse(line);}catch{continue;}
  const pending=waiting.get(message.id);if(pending){waiting.delete(message.id);clearTimeout(pending.timer);message.error?pending.reject(new Error(JSON.stringify(message.error))):pending.resolve(message.result);}
 }
});
const send=message=>child.stdin.write(JSON.stringify(message)+'\n');
function request(method,params){return new Promise((resolve,reject)=>{const id=++sequence;const timer=setTimeout(()=>{waiting.delete(id);reject(new Error('Timed out: '+method));},20000);waiting.set(id,{resolve,reject,timer});send({jsonrpc:'2.0',id,method,params});});}
let report;
try{
 const init=await request('initialize',{protocolVersion:'2024-11-05',capabilities:{},clientInfo:{name:'seat-adapter-connection-check',version:'1.0'}});
 send({jsonrpc:'2.0',method:'notifications/initialized'});
 const list=await request('tools/list',{});
 let inspection=null;
 if(desktopListening&&list.tools.some(t=>t.name==='inspect_design'))inspection=await request('tools/call',{name:'inspect_design',arguments:{}});
 report={checkedAt:new Date().toISOString(),executable,args,server:init.serverInfo,protocolVersion:init.protocolVersion,toolCount:list.tools.length,tools:list.tools.map(t=>t.name),desktopListening,inspection,geometryCreated:false};
 fs.mkdirSync(path.join(root,'logs'),{recursive:true});
 fs.writeFileSync(path.join(root,'logs/connection-check.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({mcpHandshake:true,server:report.server,tools:report.toolCount,desktopListening,inspectionPerformed:inspection!==null,geometryCreated:false}));
}catch(error){console.error(error.message);if(stderr)console.error(stderr.slice(-1500));process.exitCode=1;}
finally{child.stdin.end();child.kill();}
