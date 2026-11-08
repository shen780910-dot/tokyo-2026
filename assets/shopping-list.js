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
  let hidePurchased=false,activeCategory=0;
  const categoryTabs=make('div','shopping-category-tabs');categoryTabs.setAttribute('role','tablist');categoryTabs.setAttribute('aria-label','待購商品類別');root.before(categoryTabs);
  const categoryPanels=[],categoryButtons=[];
  function selectCategory(index,focus=false){
    activeCategory=index;
    categoryButtons.forEach((button,i)=>{button.setAttribute('aria-selected',String(i===index));button.tabIndex=i===index?0:-1;});
    applyFilter();
    if(focus)categoryButtons[index].focus();
  }
  const filter=make('button','shopping-filter','隱藏已購買');filter.type='button';filter.setAttribute('aria-pressed','false');filter.setAttribute('aria-controls','shopping-categories');
  document.querySelector('.shopping-status').insertBefore(filter,controls);
  const empty=make('p','shopping-filter-empty','目前沒有未購買的商品。');empty.hidden=true;root.after(empty);
  function applyFilter(){
    let visible=0;
    for(const {row} of rows.values()){row.hidden=hidePurchased&&row.classList.contains('is-purchased');if(!row.hidden)visible++;}
    categoryPanels.forEach((section,i)=>{section.hidden=i!==activeCategory;});
    const selected=categoryPanels[activeCategory];
    visible=selected?[...selected.querySelectorAll('.shopping-item')].filter(row=>!row.hidden).length:0;
    empty.textContent=hidePurchased?'此類別目前沒有未購買的商品。':'此類別目前沒有商品。';
    empty.hidden=visible>0;
    filter.textContent=hidePurchased?'顯示全部商品':'隱藏已購買';filter.setAttribute('aria-pressed',String(hidePurchased));
  }
  filter.addEventListener('click',()=>{hidePurchased=!hidePurchased;applyFilter();});
  const rows=new Map();let current={items:{},writingIds:[],unlocked:false,connected:false};let unlocking=false;
  function render(state){
    current=state;let purchased=0;
    for(const [id,{row,input}] of rows){const checked=state.items[id]?.purchased===true;input.checked=checked;row.classList.toggle('is-purchased',checked);input.disabled=!state.unlocked||!state.connected||state.writingIds.includes(id);if(checked)purchased++;}
    document.querySelector('#shopping-progress').textContent=`${purchased} / ${rows.size} 已購買`;
    applyFilter();
    form.hidden=state.unlocked;logout.hidden=!state.unlocked;retry.hidden=state.connected||state.loading;
    status.classList.toggle('has-error',Boolean(state.error));
    status.textContent=state.error||(state.writingIds.length?'正在儲存購買狀態…':state.loading&&!state.lastSyncedAt?'正在讀取共用清單…':state.unlocked?'已解鎖・家人共用，約每5秒同步':'家庭共用・目前唯讀，解鎖後可勾選');
  }
  const sync=window.ShoppingSync.create({...window.SHOPPING_SYNC_CONFIG,storage,onState:render});
  window.familyShoppingSync=sync;
  for(const [index,group] of window.SHOPPING_LIST.entries()){
    const section=make('section','shopping-category');section.id='shopping-category-'+index;section.setAttribute('role','tabpanel');section.setAttribute('aria-labelledby','shopping-category-tab-'+index);section.tabIndex=0;
    const tab=make('button','shopping-category-tab',group.category+' · '+group.items.length);tab.id='shopping-category-tab-'+index;tab.type='button';tab.setAttribute('role','tab');tab.setAttribute('aria-controls',section.id);tab.setAttribute('aria-selected',String(index===0));tab.tabIndex=index===0?0:-1;
    tab.addEventListener('click',()=>selectCategory(index));
    tab.addEventListener('keydown',event=>{let next=index;if(event.key==='ArrowRight')next=(index+1)%window.SHOPPING_LIST.length;else if(event.key==='ArrowLeft')next=(index-1+window.SHOPPING_LIST.length)%window.SHOPPING_LIST.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=window.SHOPPING_LIST.length-1;else return;event.preventDefault();selectCategory(next,true);});
    categoryTabs.append(tab);categoryButtons.push(tab);categoryPanels.push(section);
    section.append(make('h2','',group.category));
    for(const item of group.items){
      const row=make('article','shopping-item');row.dataset.item=item.id;
      if(item.image){const image=make('img');image.src=item.image;image.alt=item.name+' 商品參考';image.width=180;image.height=180;image.loading='lazy';row.append(image);}else row.classList.add('shopping-item-text');
      const content=make('div');content.append(make('span','shopping-type',item.type),make('h3','',item.name),make('p','',item.detail));
      if(item.positionNote)content.append(make('p','',item.positionNote));
      if(item.positionMapUrl){const officialMap=make('a','shopping-source','已核對的官方櫃位圖 ↗');officialMap.href=item.positionMapUrl;officialMap.target='_blank';officialMap.rel='noopener noreferrer';content.append(officialMap);}
      if(item.routeFloor){const map=make('a','shopping-source','看本層地圖與下一站 ↗');map.href='?floor='+encodeURIComponent(item.routeFloor)+'#day-2';content.append(map);}
      if(item.nextStop){const next=make('details','shopping-instructions');next.append(make('summary','','下一家怎麼走'),make('p','',item.nextStop));content.append(next);}
      if(item.usage||item.caution){
        const instructions=make('details','shopping-instructions');
        instructions.append(make('summary','',item.usage?'使用方法':'注意事項'));
        if(item.usage)instructions.append(make('p','shopping-usage',item.usage));
        if(item.caution)instructions.append(make('p','shopping-caution','注意：'+item.caution));
        content.append(instructions);
      }
      if(item.id==='escura-instantsnap-white'){
        const template=document.querySelector('#camera-comparison-template');
        if(template){const comparison=make('details','shopping-instructions shopping-camera-comparison');comparison.append(make('summary','','三款相機比較與購買資訊'));comparison.append(template.content.cloneNode(true));content.append(comparison);}
      }
      if(item.sourceUrl&&item.sourceUrl!==item.url){const source=make('a','shopping-source',(item.sourceLabel||'原始來源')+' ↗');source.href=item.sourceUrl;source.target='_blank';source.rel='noopener noreferrer';content.append(source);}
      if(item.url){const link=make('a','shopping-source',(item.sourceUrl===item.url?(item.sourceLabel||'原始來源'):(item.linkLabel||'商品資訊'))+' ↗');link.href=item.url;link.target='_blank';link.rel='noopener noreferrer';content.append(link);}
      const label=make('label','shopping-purchased');const input=make('input');input.type='checkbox';input.disabled=true;
      input.addEventListener('change',()=>{void sync.setPurchased(item.id,input.checked).catch(()=>render(current));});
      label.append(input,document.createTextNode('已購買'));content.append(label);row.append(content);section.append(row);rows.set(item.id,{row,input});
    }
    root.append(section);
  }
  const requestedItem=new URLSearchParams(location.search).get('item');
  if(requestedItem&&rows.has(requestedItem)){const index=window.SHOPPING_LIST.findIndex(group=>group.items.some(item=>item.id===requestedItem));selectCategory(index);const row=rows.get(requestedItem).row;row.tabIndex=-1;requestAnimationFrame(()=>{row.scrollIntoView({block:'center'});row.focus({preventScroll:true});});}
  form.addEventListener('submit',async event=>{event.preventDefault();if(unlocking)return;unlocking=true;unlock.disabled=true;const value=password.value;password.value='';try{await sync.unlock(value);}catch{}finally{unlocking=false;unlock.disabled=false;}});
  logout.addEventListener('click',()=>{void sync.logout().catch(()=>{});});retry.addEventListener('click',()=>{void sync.refresh();});
  const activate=()=>{if(location.hash==='#shopping')void sync.start();else sync.stop();};
  window.addEventListener('hashchange',activate);render(current);activate();
})();
