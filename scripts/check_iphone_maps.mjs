import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const profile=path.join(root,'.chrome-preview','iphone-check-'+process.pid);
await fs.mkdir(profile,{recursive:true});
const chrome=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',[
 '--headless=new','--disable-gpu','--no-sandbox','--remote-debugging-port=0',
 '--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
const delay=ms=>new Promise(r=>setTimeout(r,ms));
let ws;
try{
 let port;
 for(let i=0;i<60;i++){
  try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}catch{}
  await delay(100);
 }
 if(!port)throw Error('Chrome debugging port unavailable');
 const targets=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
 ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 let id=0;const pending=new Map();
 ws.onmessage=e=>{const r=JSON.parse(e.data);const p=pending.get(r.id);if(p){pending.delete(r.id);r.error?p.reject(Error(JSON.stringify(r.error))):p.resolve(r.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{pending.set(++id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 await send('Page.enable');
 await send('Emulation.setTouchEmulationEnabled',{enabled:true});
 const evaluate=async expression=>(await send('Runtime.evaluate',{expression,returnByValue:true})).result.value;
 const results=[];
 for(const device of [{name:'iphone-15',width:390,height:844},{name:'iphone-16-pro',width:402,height:874},{name:'desktop',width:1440,height:1000}]){
  await send('Emulation.setDeviceMetricsOverride',{width:device.width,height:device.height,deviceScaleFactor:device.name==='desktop'?1:3,mobile:device.name!=='desktop'});
  for(let day=1;day<=4;day++){
   await send('Page.navigate',{url:pathToFileURL(path.join(root,'index.html')).href+'#day-'+day});
   for(let n=0;n<60;n++){if(await evaluate(`document.readyState==='complete'&&document.querySelectorAll('.map-scroll').length===4`))break;await delay(100);}
   const metrics=await evaluate(`(()=>{const panel=document.querySelector('#day-panel-${day}');const frame=panel.querySelector('.map-scroll');const svg=frame.querySelector('svg');const b=svg.getBoundingClientRect();return {viewport:innerWidth,page:document.documentElement.scrollWidth,frameWidth:frame.clientWidth,frameScroll:frame.scrollWidth,svgWidth:b.width,svgLeft:b.left,svgRight:b.right,links:svg.querySelectorAll('a').length,hours:svg.querySelectorAll('[data-hours]').length,viewBox:svg.getAttribute('viewBox')};})()`);
   if(metrics.viewport!==device.width||metrics.page>device.width||metrics.frameScroll>metrics.frameWidth+1||metrics.svgLeft<0||metrics.svgRight>device.width+1||metrics.svgWidth>metrics.frameWidth+1)throw Error(JSON.stringify({device,day,metrics}));
   if(day<=3&&metrics.hours===0)throw Error('Missing shop hours');
   const overlaps=await evaluate(`(()=>{const svg=document.querySelector('#day-panel-${day} .map-scroll svg');const labels=[...svg.querySelectorAll('.text-shape.name,.text-shape.sub')];const markers=[...svg.querySelectorAll('a > ellipse,a > circle[r="13"],a > .icon')];const hits=[];for(const text of labels){const a=text.closest('a');if(!a)continue;const b=text.getBoundingClientRect();for(const marker of markers){if(marker.closest('a')===a)continue;const m=marker.getBoundingClientRect();if(Math.min(b.right,m.right)-Math.max(b.left,m.left)>1&&Math.min(b.bottom,m.bottom)-Math.max(b.top,m.top)>1)hits.push({text:text.getAttribute('aria-label'),marker:marker.closest('a').getAttribute('aria-label')});}}return hits;})()`);
   if(overlaps.length)throw Error(JSON.stringify({device:device.name,day,overlaps}));
   results.push({device:device.name,day,...metrics});
   if(device.name==='iphone-15'||device.name==='desktop'){
    const clip=await evaluate(`(()=>{const b=document.querySelector('#day-panel-${day} .map-scroll').getBoundingClientRect();return {x:b.left+scrollX,y:b.top+scrollY,width:b.width,height:b.height,scale:1};})()`);
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip});
    await fs.writeFile(path.join(root,'previews',device.name+'-day-'+day+'.png'),Buffer.from(shot.data,'base64'));
   }
  }
 }
 await fs.writeFile(path.join(root,'previews','iphone-map-checks.json'),JSON.stringify(results,null,2));
 console.log(JSON.stringify(results.map(r=>({device:r.device,day:r.day,viewport:r.viewport,map:Math.round(r.svgWidth),hours:r.hours,horizontalOverflow:false})),null,2));
 await send('Browser.close');
}finally{ws?.close();chrome.kill();}
