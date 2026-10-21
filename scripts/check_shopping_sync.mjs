import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const origin='https://shen780910-dot.github.io',site=origin+'/tokyo-2026/';
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const password=await new Promise(resolve=>{process.stdin.setRawMode(true);process.stdin.resume();process.stdout.write('Ready for shared password on hidden stdin.\n');let v='';process.stdin.on('data',function read(chunk){for(const c of chunk.toString()){if(c==='\r'||c==='\n'){process.stdin.setRawMode(false);process.stdin.pause();process.stdin.removeListener('data',read);resolve(v);return;}v+=c;}});});
const clients=[];
async function launch(name,width,height){
 const profile=path.join(root,'.chrome-preview','shared-'+process.pid+'-'+name);await fs.mkdir(profile,{recursive:true});
 const chrome=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
 let port;for(let i=0;i<100;i++){try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}catch{}await delay(100);}if(!port)throw Error('Chrome unavailable');
 const targets=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();const ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});let id=0;const pending=new Map();
 const send=(method,params={})=>new Promise((resolve,reject)=>{pending.set(++id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 const errors=[];
 ws.onmessage=async e=>{const r=JSON.parse(e.data);if(r.id){const p=pending.get(r.id);if(p){pending.delete(r.id);r.error?p.reject(Error(JSON.stringify(r.error))):p.resolve(r.result);}return;}if(r.method==='Runtime.exceptionThrown')errors.push(r.params.exceptionDetails.text);if(r.method==='Fetch.requestPaused'){const {requestId,request}=r.params;try{let relative=decodeURIComponent(new URL(request.url).pathname).replace(/^\/tokyo-2026\//,'');if(!relative)relative='index.html';const file=path.resolve(root,relative);if(!file.startsWith(root+path.sep))throw Error('Invalid local path');const body=await fs.readFile(file);const type={'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.jpg':'image/jpeg','.ttf':'font/ttf','.woff2':'font/woff2'}[path.extname(file)]||'application/octet-stream';await send('Fetch.fulfillRequest',{requestId,responseCode:200,responseHeaders:[{name:'Content-Type',value:type}],body:body.toString('base64')});}catch{await send('Fetch.continueRequest',{requestId});}}};
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value;};
 await send('Page.enable');await send('Runtime.enable');await send('Network.enable');
 await send('Fetch.enable',{patterns:[{urlPattern:site+'*',requestStage:'Request'}]});
 await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<700});
 const client={name,width,height,chrome,ws,send,evaluate,errors};clients.push(client);
 await send('Page.navigate',{url:site+'#shopping'});
 await until(client,`document.querySelector('.shopping-purchased input')&&document.querySelector('#shopping-sync-status').textContent.includes('唯讀')`);
 return client;
}
async function until(c,expression,timeout=18000){const end=Date.now()+timeout;while(Date.now()<end){if(await c.evaluate(expression))return;await delay(300);}throw Error(c.name+': condition timed out '+expression);}
const checkbox=`document.querySelector('[data-item="instax-mini-film-20"] input')`;
async function unlock(c){await c.evaluate(`(()=>{const input=document.querySelector('.family-unlock input');input.value=${JSON.stringify(password)};document.querySelector('.family-unlock').requestSubmit();})()`);await until(c,`!${checkbox}.disabled`);}
try{
 const a=await launch('iphone-15',390,844),b=await launch('iphone-16-pro',402,874),c=await launch('desktop',1440,1000);
 for(const client of clients){if(!await client.evaluate(`${checkbox}.disabled&&!document.querySelector('#shopping').hidden`))throw Error('Anonymous must be read-only');}
 await unlock(a);await unlock(b);
 const original=await a.evaluate(`${checkbox}.checked`);
 await a.evaluate(`${checkbox}.click()`);await until(a,`!${checkbox}.disabled&&${checkbox}.checked===${!original}`);
 await until(b,`${checkbox}.checked===${!original}`);await until(c,`${checkbox}.checked===${!original}&&${checkbox}.disabled`);
 await b.evaluate(`${checkbox}.click()`);await until(a,`${checkbox}.checked===${original}`);await until(c,`${checkbox}.checked===${original}`);
 await a.send('Page.reload');await until(a,`document.querySelector('.shopping-purchased input')&&!${checkbox}.disabled`);
 await a.send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
 await until(a,`${checkbox}.disabled&&document.querySelector('#shopping-sync-status').textContent.includes('離線')`);
 await a.send('Network.emulateNetworkConditions',{offline:false,latency:0,downloadThroughput:-1,uploadThroughput:-1});await until(a,`!${checkbox}.disabled`);
 for(const client of clients){
  if(await client.evaluate('document.documentElement.scrollWidth')>client.width)throw Error('Horizontal overflow: '+client.name);
  for(const dark of [false,true]){await client.evaluate(`if(document.body.classList.contains('dark')!==${dark})document.querySelector('#theme').click()`);await client.evaluate('window.scrollTo(0,0)');const shot=await client.send('Page.captureScreenshot',{format:'png'});await fs.writeFile(path.join(root,'previews',client.name+'-family-shopping-'+(dark?'dark':'light')+'.png'),Buffer.from(shot.data,'base64'));}
  if(client.errors.length)throw Error(JSON.stringify(client.errors));
 }
 await a.evaluate(`document.querySelector('.family-logout').click()`);await until(a,`${checkbox}.disabled&&!document.querySelector('.family-unlock').hidden`);
 if(!await b.evaluate(`!${checkbox}.disabled`))throw Error('Logout affected another device');
 await b.evaluate(`document.querySelector('.family-logout').click()`);await until(b,`${checkbox}.disabled`);
 console.log('PASS: public read-only; independent family unlock; A→B and B→A automatic sync; anonymous live read; refresh persistence; offline recovery; per-device logout; 390/402/1440px light/dark layouts.');
}finally{for(const c of clients){try{await c.send('Browser.close');}catch{}c.ws.close();c.chrome.kill();}}
