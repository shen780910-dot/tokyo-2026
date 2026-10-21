import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const profile=path.join(root,'.chrome-preview','station-check-'+process.pid);await fs.mkdir(profile,{recursive:true});
const chrome=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
const delay=ms=>new Promise(r=>setTimeout(r,ms));let ws;
try{
 let port;for(let i=0;i<60;i++){try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}catch{}await delay(100);}if(!port)throw Error('Chrome unavailable');
 const targets=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 let id=0;const pending=new Map();ws.onmessage=e=>{const r=JSON.parse(e.data),p=pending.get(r.id);if(p){pending.delete(r.id);r.error?p.reject(Error(JSON.stringify(r.error))):p.resolve(r.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{pending.set(++id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>(await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true})).result.value;

 await send('Page.enable');
 for(const device of [{name:'iphone-15',width:390,height:844},{name:'iphone-16-pro',width:402,height:874},{name:'desktop',width:1440,height:1000}]){
  await send('Emulation.setDeviceMetricsOverride',{width:device.width,height:device.height,deviceScaleFactor:1,mobile:device.name!=='desktop'});
  const url=pathToFileURL(path.join(root,'index.html')).href+'#shopping';
  await send('Page.navigate',{url});
  for(let i=0;i<100;i++){if(await evaluate(`document.readyState==='complete'&&document.querySelector('.shopping-purchased input')!==null`))break;await delay(100);}
  await evaluate('document.fonts.ready.then(()=>true)');
  const metrics=await evaluate(`(()=>{const p=document.querySelector('#shopping'),img=p.querySelector('img');return {visible:!p.hidden,width:document.documentElement.scrollWidth,category:p.querySelector('h2').textContent,image:img.complete&&img.naturalWidth>0,nav:document.querySelector('nav [aria-current="page"]').hash};})()`);
  const clothing=await evaluate(`(()=>{const row=document.querySelector('[data-item="instagram-DeUHZBjjUhR"]');return row?.closest('.shopping-category').querySelector('h2').textContent==='衣著'&&row.querySelector('a').href==='https://www.instagram.com/p/DeUHZBjjUhR/'&&row.querySelector('img')?.getAttribute('src')==='assets/shopping/hoka-clifton-11-gtx-glm.jpg'&&row.textContent.includes('HK1183115-AKP');})()`);if(!clothing)throw Error('Clothing link or category missing');
  if(!metrics.visible||metrics.width>device.width||metrics.category!=='3C 用品'||!metrics.image||metrics.nav!=='#shopping')throw Error(JSON.stringify({device,metrics}));
  await evaluate(`(()=>{const input=document.querySelector('.shopping-purchased input');if(input.checked)input.click();input.click();})()`);
  if(!await evaluate(`document.querySelector('#shopping-progress').textContent==='1 / 2 已購買'`))throw Error('Shopping progress did not update');
  await send('Page.navigate',{url});
  for(let i=0;i<100;i++){if(await evaluate(`document.readyState==='complete'&&document.querySelector('.shopping-purchased input')?.checked===true`))break;await delay(100);}
  if(!await evaluate(`document.querySelector('.shopping-purchased input')?.checked===true`))throw Error('Shopping state lost on reload');
  await evaluate(`document.querySelector('.shopping-purchased input').click()`);
  for(const dark of [false,true]){
   await evaluate(`if(document.body.classList.contains('dark')!==${dark})document.querySelector('#theme').click()`);
   const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});await fs.writeFile(path.join(root,'previews',device.name+'-shopping-'+(dark?'dark':'light')+'.png'),Buffer.from(shot.data,'base64'));
  }
  await evaluate(`location.hash='prep'`);await delay(100);
  if(!await evaluate(`!document.querySelector('#prep').hidden&&document.querySelector('#shopping').hidden`))throw Error('Prep route regressed');
  console.log(device.name+': shopping route, image, category, persistence, progress, dark mode and width passed');
 }
 await send('Browser.close');
}finally{ws?.close();chrome.kill();}
