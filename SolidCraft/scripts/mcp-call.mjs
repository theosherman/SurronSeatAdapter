import fs from 'node:fs';
import {spawn} from 'node:child_process';
const child=spawn('C:/Program Files/SolidCraft/solidcraft-cli.exe',['mcp','--connect','127.0.0.1:7878','--allow-path','C:/Projects/Suron Seat Adapter/SolidCraft','--compact'],{windowsHide:true});
let buffer='',id=0;const pending=new Map();
child.stdout.on('data',chunk=>{buffer+=chunk;while(buffer.includes('\n')){const n=buffer.indexOf('\n'),line=buffer.slice(0,n);buffer=buffer.slice(n+1);let m;try{m=JSON.parse(line);}catch{continue;}const p=pending.get(m.id);if(p){pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(m.error):p.resolve(m.result);}}});
child.stderr.on('data',c=>process.stderr.write(c));
const send=m=>child.stdin.write(JSON.stringify(m)+'\n');
function request(method,params){return new Promise((resolve,reject)=>{const n=++id;const timer=setTimeout(()=>reject(new Error('RPC timeout '+method)),180000);pending.set(n,{resolve,reject,timer});send({jsonrpc:'2.0',id:n,method,params});});}
try{
 await request('initialize',{protocolVersion:'2024-11-05',capabilities:{},clientInfo:{name:'adapter-builder',version:'1'}});send({jsonrpc:'2.0',method:'notifications/initialized'});
 const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8').replace(/^\uFEFF/,''));
 const results=[];for(const call of (Array.isArray(input)?input:[input]))results.push(await request(call.method??'tools/call',call.params??call));
 const output=JSON.stringify(results,null,2);if(process.argv[3])fs.writeFileSync(process.argv[3],output);else console.log(output);
}finally{child.stdin.end();child.kill();}
