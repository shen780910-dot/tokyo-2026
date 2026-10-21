(() => {
  'use strict';
  let nativeStorage;try{nativeStorage=window.localStorage;}catch{}
  const storage=window.TripUtils.createSafeStorage(nativeStorage);
  const root=document.querySelector('#shopping-categories');
  const make=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text)e.textContent=text;return e;};
  const controls=make('section','family-sync-controls');controls.setAttribute('aria-label','家庭共用購買狀態');
  const status=make('p','family-sync-status','正在讀取共用清單…');status.id='shopping-sync-status';status.setAttribute('role','status');
  const form=make('form','family-unlock');const field=make('label');field.append(document.createTextNode('共用密碼'));
  const password=make('input');password.type='password';password.inputMode='numeric';password.autocomplete='current-password';password.maxLength=64;password.required=true;password.placeholder='解鎖後可共同勾選';field.append(password);
  const unlock=make('button','','解鎖');unlock.type='submit';form.append(field,unlock);
  const logout=make('button','family-logout','退出共用修改');logout.type='button';logout.hidden=true;
  const retry=make('button','family-retry','重新同步');retry.type='button';retry.hidden=true;
  controls.append(status,form,logout,retry);document.querySelector('.shopping-status').append(controls);
  document.querySelector('.shopping-status .muted').textContent='所有人都能查看；輸入共用密碼後，家人可一起勾選。';
  const rows=new Map();let current={items:{},writingIds:[],unlocked:false,connected:false};let unlocking=false;
  function render(state){
    current=state;let purchased=0;
    for(const [id,{row,input}] of rows){const checked=state.items[id]?.purchased===true;input.checked=checked;row.classList.toggle('is-purchased',checked);input.disabled=!state.unlocked||!state.connected||state.writingIds.includes(id);if(checked)purchased++;}
    document.querySelector('#shopping-progress').textContent=`${purchased} / ${rows.size} 已購買`;
    form.hidden=state.unlocked;logout.hidden=!state.unlocked;retry.hidden=state.connected||state.loading;
    status.classList.toggle('has-error',Boolean(state.error));
    status.textContent=state.error||(state.writingIds.length?'正在儲存購買狀態…':state.loading&&!state.lastSyncedAt?'正在讀取共用清單…':state.unlocked?'已解鎖・家人共用，約每5秒同步':'家庭共用・目前唯讀，解鎖後可勾選');
  }
  const sync=window.ShoppingSync.create({...window.SHOPPING_SYNC_CONFIG,storage,onState:render});
  window.familyShoppingSync=sync;
  for(const group of window.SHOPPING_LIST){
    const section=make('section','shopping-category');section.append(make('h2','',group.category));
    for(const item of group.items){
      const row=make('article','shopping-item');row.dataset.item=item.id;
      if(item.image){const image=make('img');image.src=item.image;image.alt=item.name+' 商品參考';image.width=180;image.height=180;image.loading='lazy';row.append(image);}else row.classList.add('shopping-item-text');
      const content=make('div');content.append(make('span','shopping-type',item.type),make('h3','',item.name),make('p','',item.detail));
      if(item.url){const link=make('a','shopping-source',(item.linkLabel||'商品資訊')+' ↗');link.href=item.url;link.target='_blank';link.rel='noopener noreferrer';content.append(link);}
      const label=make('label','shopping-purchased');const input=make('input');input.type='checkbox';input.disabled=true;
      input.addEventListener('change',()=>{void sync.setPurchased(item.id,input.checked).catch(()=>render(current));});
      label.append(input,document.createTextNode('已購買'));content.append(label);row.append(content);section.append(row);rows.set(item.id,{row,input});
    }
    root.append(section);
  }
  form.addEventListener('submit',async event=>{event.preventDefault();if(unlocking)return;unlocking=true;unlock.disabled=true;const value=password.value;password.value='';try{await sync.unlock(value);}catch{}finally{unlocking=false;unlock.disabled=false;}});
  logout.addEventListener('click',()=>{void sync.logout().catch(()=>{});});retry.addEventListener('click',()=>{void sync.refresh();});
  const activate=()=>{if(location.hash==='#shopping')void sync.start();else sync.stop();};
  window.addEventListener('hashchange',activate);render(current);activate();
})();
