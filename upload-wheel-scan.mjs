import fs from 'node:fs';
import { pathToFileURL } from 'node:url';

// Reuse the connected Onshape MCP's auth provider; never log or persist credentials.
const root='C:/Users/theoa/AppData/Local/npm-cache/_npx/24b6afb7e47c0d78/node_modules/@gpambrozio/onshape-mcp/dist/';
const {CredentialStore}=await import(pathToFileURL(root+'auth/store.js').href);
const {createAuthProvider}=await import(pathToFileURL(root+'auth/provider.js').href);
const {OnshapeClient}=await import(pathToFileURL(root+'api/client.js').href);
const store=new CredentialStore();
const creds=store.resolve();
if(!creds)throw new Error('The connected Onshape credential is unavailable');
const client=new OnshapeClient(createAuthProvider(creds,store));
const file='Sherman_P_Scan_Aligned_To_Adapter_mm.stl';
const form=new FormData();
form.append('file',new Blob([fs.readFileSync(file)],{type:'application/sla'}),file);
form.append('storeInDocument','true');
form.append('flattenAssemblies','true');
form.append('translate','true');
form.append('unit','millimeter');
form.append('locationElementId','69186d95d4c9dc45ec42f803');
const url=client.url('/api/v6/translations/d/b1a1f737761c2581236d5ec3/w/eb902961c90530f7f212e211');
const response=await client.fetchWithAuth(url,{Accept:'application/json'},'POST',form);
const detail=await response.json();
if(!response.ok)throw new Error('Upload failed: '+response.status+' '+JSON.stringify(detail));
fs.writeFileSync('wheel-scan-upload.json',JSON.stringify(detail,null,2)+'\n');
console.log(JSON.stringify({status:response.status,id:detail.id,requestState:detail.requestState,resultElementIds:detail.resultElementIds}));
