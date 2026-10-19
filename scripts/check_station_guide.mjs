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
 await send('Page.enable');const results=[];
 for(const device of [{name:'iphone-15',width:390,height:844},{name:'iphone-16-pro',width:402,height:874},{name:'desktop',width:1440,height:1000}]){
  await send('Emulation.setDeviceMetricsOverride',{width:device.width,height:device.height,deviceScaleFactor:device.name==='desktop'?1:3,mobile:device.name!=='desktop'});
  await send('Page.navigate',{url:pathToFileURL(path.join(root,'index.html')).href+'#day-2'});
  for(let i=0;i<60;i++){if(await evaluate(`document.querySelectorAll('.station-floor-tabs button').length===9 && document.readyState==='complete'`))break;await delay(100);}
  await evaluate(`document.fonts.ready.then(()=>true)`);
  const allStops=await evaluate(`JSON.stringify(window.TOKYO_STATION_GUIDE.flatMap(item=>item.shops).sort((a,b)=>a-b))`);
  if(allStops!==JSON.stringify([1,2,3,4,5,6,7,8,9,10,11,12]))throw Error('Shopping stops incomplete or duplicated');
  const sequence=await evaluate(`JSON.stringify(window.TOKYO_STATION_GUIDE.flatMap(item=>item.shops))`);if(sequence!==JSON.stringify([1,2,3,4,5,6,7,8,9,10,11,12]))throw Error('Tab order is not walking order');
  if(device.name==='iphone-15'){
   const clip=await evaluate(`(()=>{const b=document.querySelector('#station-guide-title').getBoundingClientRect();return {x:b.left+scrollX,y:b.top+scrollY,width:b.width,height:b.height,scale:1};})()`);
   const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip});await fs.writeFile(path.join(root,'previews','iphone-15-station-heading.png'),Buffer.from(shot.data,'base64'));
  }
  for(const [index,floor,links,notionCount] of [[0,'b1',2,1],[1,'1f',2,1],[2,'daimaru1f',4,2],[3,'daimarub1',2,1],[4,'daimaru4f',2,0],[5,'gift',8,3],[6,'character',10,1],[7,'okashi',2,1],[8,'overview',0,0]]){
   await evaluate(`document.querySelectorAll('.station-floor-tabs button')[${index}].click()`);
   const basesLoaded=await evaluate(`Promise.all([...document.querySelectorAll('.station-guide-canvas image')].map(image=>new Promise(resolve=>{const img=new Image();img.onload=()=>resolve(img.naturalWidth>0);img.onerror=()=>resolve(false);img.src=image.getAttribute('href');}))).then(values=>values.every(Boolean))`);
   if(!basesLoaded)throw Error('Official floor-plan base failed to load');
   const metrics=await evaluate(`(()=>{const panel=document.querySelector('.station-guide-canvas');const svg=panel.querySelector('svg');const b=svg.getBoundingClientRect();return {hash:location.hash,active:document.querySelector('.station-floor-tabs [aria-selected="true"]').id,pageWidth:document.documentElement.scrollWidth,left:b.left,right:b.right,links:svg.querySelectorAll('a').length,width:panel.clientWidth,official:svg.querySelectorAll('.official-plan').length,images:svg.querySelectorAll('image').length};})()`);
   if(metrics.hash!=='#day-2'||metrics.pageWidth>device.width||metrics.left<0||metrics.right>device.width+1||metrics.links!==links+1||metrics.active!=='station-floor-'+floor||metrics.official!==1||metrics.images!==1)throw Error(JSON.stringify({device,floor,metrics}));
   const sourceValid=await evaluate(`(()=>{const a=document.querySelector('.station-guide-canvas .map-source-link');return a?.getAttribute('href')===window.TOKYO_STATION_GUIDE[${index}].url&&a.getAttribute('target')==='_blank';})()`);if(!sourceValid)throw Error('Missing direct source link');
   const details=await evaluate(`(()=>{const svg=document.querySelector('.station-guide-canvas svg');const links=[...svg.querySelectorAll('a.shop-detail-link')];return {notion:links.filter(a=>a.getAttribute('href').startsWith('https://app.notion.com/p/')).length,valid:links.every(a=>a.getAttribute('target')==='_blank'&&a.getAttribute('rel').includes('noopener')),butter:links.find(a=>a.getAttribute('data-shop')==='10')?.getAttribute('data-kind')};})()`);
   if(details.notion!==notionCount||!details.valid||(floor==='gift'&&details.butter!=='official'))throw Error(JSON.stringify({floor,details}));
   const route=await evaluate(`(()=>{const svg=document.querySelector('.station-guide-canvas svg');return {steps:document.querySelectorAll('.station-directions li').length,paths:svg.querySelectorAll('.walking-route').length,nodes:[...svg.querySelectorAll('.floor-connection')].map(n=>n.dataset.connection)};})()`);
   if(route.steps!==4||(!['overview','character'].includes(floor)&&route.paths<1)||(['b1','1f'].includes(floor)&&(!route.nodes.includes('A')||!route.nodes.includes('E'))))throw Error(JSON.stringify({floor,route}));
   if(floor==='character'){const original=await evaluate(`(()=>{const svg=document.querySelector('.station-guide-canvas svg');return {callouts:svg.querySelectorAll('.character-callout').length,box:svg.querySelector('.official-plan').getAttribute('viewBox'),overlays:svg.querySelectorAll('.walking-route,.official-shop-pin,.floor-connection').length};})()`);if(original.box!=='0 80 841.89 245'||original.overlays!==0||original.callouts!==8)throw Error('Character annotations do not match official-base callout layout');}
   const geometry=await evaluate(`(()=>{const svg=document.querySelector('.station-guide-canvas svg');const shapes=[...svg.querySelectorAll('.text-shape')];const bounds=svg.getBoundingClientRect();const issues=[];for(let i=0;i<shapes.length;i++){const a=shapes[i],b=a.getBoundingClientRect();if(b.right>bounds.right-3||b.left<bounds.left+3)issues.push({overflow:a.getAttribute('aria-label')});for(const c of shapes.slice(i+1)){const d=c.getBoundingClientRect();if(Math.min(b.right,d.right)-Math.max(b.left,d.left)>1&&Math.min(b.bottom,d.bottom)-Math.max(b.top,d.top)>1)issues.push({overlap:[a.getAttribute('aria-label'),c.getAttribute('aria-label')]});}}return issues;})()`);
   if(geometry.length)throw Error(JSON.stringify({device:device.name,floor,geometry}));
   if(device.name==='iphone-15'||device.name==='desktop'){
    const clip=await evaluate(`(()=>{const b=document.querySelector('.station-guide-canvas').getBoundingClientRect();return {x:b.left+scrollX,y:b.top+scrollY,width:b.width,height:b.height,scale:1};})()`);
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip});await fs.writeFile(path.join(root,'previews',device.name+'-station-'+floor+'.png'),Buffer.from(shot.data,'base64'));
   }
   results.push({device:device.name,floor,links,overflow:false});
  }
  const keyboard=await evaluate(`(()=>{const tab=document.querySelector('#station-floor-gift');tab.dispatchEvent(new KeyboardEvent('keydown',{key:'Home',bubbles:true}));return document.activeElement.id==='station-floor-b1'&&document.querySelector('#station-floor-b1').getAttribute('aria-selected')==='true'&&location.hash==='#day-2';})()`);if(!keyboard)throw Error('Keyboard navigation failed');
  const ordered=await evaluate(`(()=>{const order=['1f','daimaru1f','daimarub1','daimaru4f','gift','character','okashi'];for(const floor of order){document.querySelector('.station-next-floor').click();if(document.querySelector('.station-floor-tabs [aria-selected="true"]').id!=='station-floor-'+floor)return false;}return !document.querySelector('.station-next-floor')&&location.hash==='#day-2';})()`);if(!ordered)throw Error('Next-floor walking sequence failed');
 }
 console.log(JSON.stringify(results,null,2));await send('Browser.close');
}finally{ws?.close();chrome.kill();}
