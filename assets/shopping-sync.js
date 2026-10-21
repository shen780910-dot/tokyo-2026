(() => {
 'use strict';
 const SESSION_KEY='tokyo-2026-family-session';
 const CACHE_KEY='tokyo-2026-family-cache';
 globalThis.ShoppingSync={create(options){
  const storage=options.storage,request=options.fetch||globalThis.fetch;
  const doc=options.document||globalThis.document,win=options.window||globalThis.window;
  const timers=options.scheduler||globalThis;
  let state={items:{},unlocked:false,loading:false,writingIds:[],connected:false,error:'',lastSyncedAt:null};
  let token='',interval=null,sequence=0,stopped=false,started=false;
  try{const session=JSON.parse(storage.get(SESSION_KEY)||'null');if(session?.token&&Date.parse(session.expiresAt)>Date.now()){token=session.token;state.unlocked=true;}const cache=JSON.parse(storage.get(CACHE_KEY)||'null');if(cache?.items)state.items=cache.items;}catch{}
  const emit=()=>options.onState?.({...state,items:{...state.items},writingIds:[...state.writingIds]});
  const save=(key,value)=>{try{storage.set(key,value);}catch{}};
  const lock=()=>{token='';state.unlocked=false;save(SESSION_KEY,'');};
  const online=()=>win?.navigator?.onLine!==false;
  async function api(path,init={}){
   if(!online())throw Error('目前離線，恢復網路後會自動同步');
   const controller=new AbortController();let timer;
   const perform=async()=>{const response=await request(options.baseUrl.replace(/\/$/,'')+'/api/'+path,{cache:'no-store',...init,signal:controller.signal,headers:{...(init.body?{'Content-Type':'application/json'}:{}),...(token?{Authorization:'Bearer '+token}:{}),...init.headers}});
    let data;try{data=await response.json();}catch{throw Error('暫時無法同步，請稍後重試');}
    if(!response.ok){if(response.status===401)lock();const error=Error(data.error||'暫時無法同步，請稍後重試');error.status=response.status;throw error;}return data;};
   const timeout=new Promise((resolve,reject)=>{timer=setTimeout(()=>{reject(Error('同步逾時，請檢查網路後重試'));controller.abort();},options.requestTimeoutMs||12000);});
   try{return await Promise.race([perform(),timeout]);}finally{clearTimeout(timer);}
  }
  function merge(items){for(const [id,value] of Object.entries(items)){if(typeof value.purchased!=='boolean'||!Number.isInteger(value.revision))continue;const old=state.items[id];if(!old||value.revision>=old.revision)state.items[id]=value;}save(CACHE_KEY,JSON.stringify({items:state.items}));}
  async function refresh(){
   const current=++sequence;if(stopped)return;
   state.loading=true;emit();
   try{const data=await api('shopping');if(current!==sequence||stopped)return;merge(data.items);state.connected=true;state.error='';state.lastSyncedAt=new Date().toISOString();}
   catch(error){if(current!==sequence||stopped)return;state.connected=false;state.error=error.message;}
   finally{if(current===sequence&&!stopped){state.loading=false;emit();}}
  }
  async function unlock(password){
   try{const session=await api('unlock',{method:'POST',body:JSON.stringify({password})});token=session.token;state.unlocked=true;state.error='';save(SESSION_KEY,JSON.stringify(session));emit();await refresh();}
   catch(error){state.error=error.message;emit();throw error;}
  }
  async function setPurchased(id,purchased){
   if(!state.unlocked||!state.connected||!online()||state.writingIds.includes(id))throw Error('請先解鎖並確認網路連線');
   if(typeof purchased!=='boolean')throw Error('購買狀態格式錯誤');
   ++sequence;state.loading=false;state.writingIds.push(id);state.error='';emit();
   try{const data=await api('shopping/'+encodeURIComponent(id),{method:'PUT',body:JSON.stringify({purchased})});merge({[data.itemId]:{purchased:data.purchased,revision:data.revision}});state.connected=true;state.lastSyncedAt=new Date().toISOString();}
   catch(error){state.connected=false;state.error=error.message;throw error;}
   finally{state.writingIds=state.writingIds.filter(value=>value!==id);emit();}
  }
  async function logout(){try{await api('logout',{method:'POST',body:'{}'});lock();state.error='';emit();}catch(error){state.error='暫時無法退出，請恢復連線後重試';emit();throw error;}}
  function poll(){if(interval!==null){timers.clearInterval(interval);interval=null;}if(!stopped&&!doc?.hidden){interval=timers.setInterval(()=>{if(!state.loading&&!state.writingIds.length)void refresh();},5000);}}
  const visibility=()=>{poll();if(!doc?.hidden)void refresh();};
  const focus=()=>{if(!doc?.hidden)void refresh();};
  const offline=()=>{++sequence;state.loading=false;state.connected=false;state.error='目前離線，恢復網路後會自動同步';emit();};
  async function start(){if(started)return;started=true;stopped=false;doc?.addEventListener?.('visibilitychange',visibility);win?.addEventListener?.('focus',focus);win?.addEventListener?.('online',focus);win?.addEventListener?.('offline',offline);poll();await refresh();}
  function stop(){stopped=true;started=false;++sequence;if(interval!==null)timers.clearInterval(interval);interval=null;doc?.removeEventListener?.('visibilitychange',visibility);win?.removeEventListener?.('focus',focus);win?.removeEventListener?.('online',focus);win?.removeEventListener?.('offline',offline);}
  return {start,unlock,setPurchased,logout,refresh,stop};
 }};
})();
