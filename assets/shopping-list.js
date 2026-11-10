(() => {
  'use strict';
  let nativeStorage;try{nativeStorage=window.localStorage;}catch{}
  const storage=window.TripUtils.createSafeStorage(nativeStorage);
  const root=document.querySelector('#shopping-categories');
  const make=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text)e.textContent=text;return e;};

  const staffDialog=make('dialog','staff-dialog');
  staffDialog.setAttribute('aria-labelledby','staff-dialog-title');
  const staffTitle=make('h2','','給店員看・日本語');
  staffTitle.id='staff-dialog-title';
  const staffCloseForm=make('form');
  staffCloseForm.method='dialog';
  staffCloseForm.append(make('button','staff-close','關閉'));
  const staffImage=make('img','staff-image');
  const staffName=make('p','staff-product-name');
  staffName.lang='ja';
  const staffRequest=make('p','','こちらの商品を探しています。');
  staffRequest.lang='ja';
  staffDialog.append(staffTitle,staffCloseForm,staffName,staffRequest,staffImage);
  root.after(staffDialog);

  function showStaffCard(item, imageSrc=item.image){
    staffName.textContent=item.jpName||item.name;
    staffName.lang=item.jpName?'ja':'zh-Hant';
    staffImage.hidden=!imageSrc;
    if(imageSrc){
      staffImage.src=imageSrc;
      staffImage.alt=item.name+' 商品參考';
    }else{
      staffImage.removeAttribute('src');
      staffImage.alt='';
    }
    staffDialog.showModal();
  }
  const controls=make('section','family-sync-controls');controls.setAttribute('aria-label','家庭共用購買狀態');
  const status=make('p','family-sync-status','正在讀取共用清單…');status.id='shopping-sync-status';status.setAttribute('role','status');
  const form=make('form','family-unlock');const field=make('label');field.append(document.createTextNode('共用密碼'));
  const password=make('input');password.type='password';password.inputMode='numeric';password.autocomplete='current-password';password.maxLength=64;password.required=true;password.placeholder='解鎖後可共同勾選';field.append(password);
  const unlock=make('button','','解鎖');unlock.type='submit';form.append(field,unlock);
  const logout=make('button','family-logout','退出共用修改');logout.type='button';logout.hidden=true;
  const retry=make('button','family-retry','重新同步');retry.type='button';retry.hidden=true;
  controls.append(status,form,logout,retry);document.querySelector('.shopping-status').append(controls);
  document.querySelector('.shopping-status .muted').textContent='所有人都能查看；輸入共用密碼後，家人可一起勾選。';
  let hidePurchased=false,activeCategory=-1;
  const categoryTabs=make('div','shopping-category-tabs');categoryTabs.setAttribute('role','tablist');categoryTabs.setAttribute('aria-label','待購商品類別');root.before(categoryTabs);
  const categoryPanels=[],categoryButtons=[];
  const allTab=make('button','shopping-category-tab','全部');allTab.type='button';allTab.setAttribute('role','tab');allTab.setAttribute('aria-selected','true');allTab.addEventListener('click',()=>selectCategory(-1));categoryTabs.append(allTab);
  const visitFilters=make('div','shopping-visit-filters');
  function addSelect(labelText,values){const label=make('label','',labelText);const select=make('select');select.setAttribute('aria-label',labelText);const all=make('option','','全部');all.value='';select.append(all);for(const value of values){const option=make('option','',value);option.value=value;select.append(option);}select.addEventListener('change',()=>{selectCategory(-1);});label.append(select);visitFilters.append(label);return select;}
  const items=window.SHOPPING_LIST.filter(g=>g.category!=='已取消／不前往').flatMap(g=>g.items);
  const storeSelect=addSelect('店家',[...new Set(items.map(x=>x.store))].sort());categoryTabs.after(visitFilters);

  function selectCategory(index,focus=false){
    activeCategory=index;allTab.setAttribute('aria-selected',String(index===-1));allTab.tabIndex=index===-1?0:-1;
    categoryButtons.forEach((button,i)=>{button.setAttribute('aria-selected',String(i===index));button.tabIndex=i===index?0:-1;});
    applyFilter();
    if(focus)categoryButtons[index].focus();
  }
  const filter=make('button','shopping-filter','隱藏已購買');filter.type='button';filter.setAttribute('aria-pressed','false');filter.setAttribute('aria-controls','shopping-categories');
  document.querySelector('.shopping-status').insertBefore(filter,controls);
  const empty=make('p','shopping-filter-empty','目前沒有未購買的商品。');empty.hidden=true;root.after(empty);
  function applyFilter(){
    let visible=0;for(const row of root.querySelectorAll('[data-cancelled]'))row.hidden=Boolean(storeSelect.value);
    for(const {row,item} of rows.values()){row.hidden=(hidePurchased&&row.classList.contains('is-purchased'))||(storeSelect.value&&item.store!==storeSelect.value);if(!row.hidden)visible++;}
    categoryPanels.forEach((section,i)=>{section.hidden=activeCategory===-1?section.dataset.cancelledCategory==='true':i!==activeCategory;});
    const selected=categoryPanels[activeCategory];
    visible=selected?[...selected.querySelectorAll('.shopping-item')].filter(row=>!row.hidden).length:[...rows.values()].filter(({row})=>!row.hidden).length;
    empty.textContent=hidePurchased?'此類別目前沒有未購買的商品。':'此類別目前沒有商品。';
    empty.hidden=visible>0;
    filter.textContent=hidePurchased?'顯示全部商品':'隱藏已購買';filter.setAttribute('aria-pressed',String(hidePurchased));
  }
  filter.addEventListener('click',()=>{hidePurchased=!hidePurchased;applyFilter();});
  const rows=new Map();let current={items:{},writingIds:[],unlocked:false,connected:false};let unlocking=false;
  function render(state){
    current=state;
    window.dispatchEvent(new CustomEvent('shopping-state',{detail:state}));
    const changedRows=new Set();
    let purchased=0;
    for(const [id,{row,input,expander}] of rows){
      const checked=state.items[id]?.purchased===true;
      if(row.classList.contains('is-purchased')!==checked){
        changedRows.add(row);
        row.classList.toggle('is-purchased',checked);
        expander.hidden=!checked;
      }
      if(input.checked!==checked)input.checked=checked;
      const disabled=!state.unlocked||!state.connected||state.writingIds.includes(id);
      if(input.disabled!==disabled)input.disabled=disabled;
      if(checked)purchased++;
    }
    if(changedRows.size){
      for(const section of categoryPanels){
        const children=[...section.querySelectorAll('.shopping-item')];
        if(!children.some(row=>changedRows.has(row)))continue;
        children.sort((a,b)=>Number(a.classList.contains('is-purchased'))-Number(b.classList.contains('is-purchased'))||Number(a.dataset.order)-Number(b.dataset.order));
        let nextRow=null;
        for(const row of children.reverse()){
          if(changedRows.has(row)&&row.nextElementSibling!==nextRow)section.insertBefore(row,nextRow);
          nextRow=row;
        }
      }
      applyFilter();
    }
    const progress=document.querySelector('#shopping-progress');
    const progressText=`${purchased} / ${rows.size} 已購買`;
    if(progress.textContent!==progressText)progress.textContent=progressText;
    form.hidden=state.unlocked;logout.hidden=!state.unlocked;
    status.classList.toggle('has-error',Boolean(state.error));
    retry.hidden=state.connected||(!state.error&&state.loading);
    const statusText=state.error||(state.writingIds.length?'正在儲存購買狀態…':state.loading&&!state.lastSyncedAt?'正在讀取共用清單…':state.unlocked?'已解鎖・家人共用，約每5秒同步':'家庭共用・目前唯讀，解鎖後可勾選');
    if(status.textContent!==statusText)status.textContent=statusText;
  }
  const sync=window.ShoppingSync.create({...window.SHOPPING_SYNC_CONFIG,storage,onState:render});
  window.familyShoppingSync=sync;
  for(const [index,group] of window.SHOPPING_LIST.entries()){
    const section=make('section','shopping-category');section.id='shopping-category-'+index;if(group.category==='已取消／不前往')section.dataset.cancelledCategory='true';section.setAttribute('role','tabpanel');section.setAttribute('aria-labelledby','shopping-category-tab-'+index);section.tabIndex=0;
    const tab=make('button','shopping-category-tab',group.category+' · '+group.items.length);tab.id='shopping-category-tab-'+index;tab.type='button';tab.setAttribute('role','tab');tab.setAttribute('aria-controls',section.id);tab.setAttribute('aria-selected',String(index===activeCategory));tab.tabIndex=index===activeCategory?0:-1;
    tab.addEventListener('click',()=>selectCategory(index));
    tab.addEventListener('keydown',event=>{let next=index;if(event.key==='ArrowRight')next=(index+1)%window.SHOPPING_LIST.length;else if(event.key==='ArrowLeft')next=(index-1+window.SHOPPING_LIST.length)%window.SHOPPING_LIST.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=window.SHOPPING_LIST.length-1;else return;event.preventDefault();selectCategory(next,true);});
    categoryTabs.append(tab);categoryButtons.push(tab);categoryPanels.push(section);
    section.append(make('h2','',group.category));
    for(const item of group.items){
      const row=make('article','shopping-item');row.dataset.item=item.id;row.dataset.order=group.items.indexOf(item);
      const content=make('div','shopping-item-body');
      const heading=make('h3','',item.name);
      const thumbnailNotice=make('span','shopping-thumbnail-notice','待補縮圖');
      thumbnailNotice.hidden=true;
      function showMissingThumbnail(){
        row.classList.add('shopping-item-text');
        thumbnailNotice.hidden=item.decision==='不買';
        if(item.jpName){
          const titleButton=make('button','shopping-name-button',item.name);
          titleButton.type='button';
          titleButton.setAttribute('aria-haspopup','dialog');
          titleButton.addEventListener('click',()=>showStaffCard(item,''));
          heading.replaceChildren(titleButton);
        }
      }
      if(item.image){
        const photo=make('button','shopping-photo');
        photo.type='button';
        photo.setAttribute('aria-label','查看商品大圖和日文品名：'+item.name);
        photo.setAttribute('aria-haspopup','dialog');
        const image=make('img');
        image.src=item.image;
        image.alt='';
        image.width=180;
        image.height=180;
        image.loading='lazy';
        photo.append(image);
        photo.addEventListener('click',()=>showStaffCard(item));
        image.addEventListener('error',()=>{
          photo.hidden=true;
          showMissingThumbnail();
        },{once:true});
        row.append(photo);
      }else showMissingThumbnail();
      content.append(heading);
      const meta=make('p','shopping-visit',(item.purchaseDate||'日期待確認')+' · '+(item.store||'店家待確認'));
      if(item.decision!=='不買' && item.pendingSummary)meta.append(' ',make('span','pending-badge','待確認'));
      meta.append(' ',thumbnailNotice);
      content.append(meta);
      if(item.detail)content.append(make('p','shopping-excerpt',item.detail));
      const label=make('label','shopping-purchased');const input=make('input');input.type='checkbox';input.disabled=true;
      input.addEventListener('change',()=>{void sync.setPurchased(item.id,input.checked).catch(()=>render(current));});
      label.append(input,document.createTextNode('已購買'));if(item.decision!=='不買')content.append(label);
      const expander=make('button','purchase-expander','展開商品資料');expander.type='button';expander.hidden=true;expander.setAttribute('aria-expanded','false');expander.addEventListener('click',()=>{const expanded=row.classList.toggle('is-expanded');expander.setAttribute('aria-expanded',String(expanded));expander.textContent=expanded?'收合商品資料':'展開商品資料';});content.append(expander);
      const details=make('details','shopping-details');
      details.append(make('summary','','商品詳情'));
      const notes=make('div','shopping-detail-body');
      if(item.type)notes.append(make('p','shopping-type',item.type));
      if(item.detail)notes.append(make('p','',item.detail));
      if(item.positionNote)notes.append(make('p','',item.positionNote));
      if(item.usage||item.caution){
        notes.append(make('h4','',item.usage?'使用方法':'注意事項'));
        if(item.usage)notes.append(make('p','shopping-usage',item.usage));
        if(item.caution)notes.append(make('p','shopping-caution','注意：'+item.caution));
      }
      if(item.id==='escura-instantsnap-white'){
        const template=document.querySelector('#camera-comparison-template');
        if(template){const comparison=make('details','shopping-instructions shopping-camera-comparison');comparison.append(make('summary','','三款相機比較與購買資訊'));comparison.append(template.content.cloneNode(true));notes.append(comparison);}
      }
      const links=make('div','shopping-detail-links');
      for(const [url,label] of [
        [item.availabilityUrl,'官方實體通路查核'],
        [item.positionMapUrl,'已核對的官方櫃位圖'],
        [item.notionUrl,item.notionLabel||'Notion'],
        [item.sourceUrl!==item.url?item.sourceUrl:null,item.sourceLabel||'原始來源'],
        [item.url,item.sourceUrl===item.url?(item.sourceLabel||'原始來源'):(item.linkLabel||'商品資訊')]
      ]){
        if(!url)continue;
        const link=make('a','shopping-source',label+' ↗');
        link.href=url;link.target='_blank';link.rel='noopener noreferrer';links.append(link);
      }
      if(item.routeFloor){
        const map=make('a','shopping-source','看本層地圖與下一站 ↗');
        map.href='?floor='+encodeURIComponent(item.routeFloor)+'#station';links.append(map);
      }
      if(links.childElementCount)notes.append(links);
      if(notes.childElementCount){details.append(notes);content.append(details);}
      row.append(content);section.append(row);if(item.decision!=='不買')rows.set(item.id,{row,input,item,expander});else row.dataset.cancelled='true';
    }
    root.append(section);
  }
  const requestedItem=new URLSearchParams(location.search).get('item');
  if(requestedItem&&rows.has(requestedItem)){const index=window.SHOPPING_LIST.findIndex(group=>group.items.some(item=>item.id===requestedItem));selectCategory(index);const row=rows.get(requestedItem).row;row.tabIndex=-1;requestAnimationFrame(()=>{row.scrollIntoView({block:'center'});row.focus({preventScroll:true});});}
  form.addEventListener('submit',async event=>{event.preventDefault();if(unlocking)return;unlocking=true;unlock.disabled=true;const value=password.value;password.value='';try{await sync.unlock(value);}catch{}finally{unlocking=false;unlock.disabled=false;}});
  logout.addEventListener('click',()=>{void sync.logout().catch(()=>{});});retry.addEventListener('click',()=>{void sync.refresh();});
  const activate=()=>{if(['#shopping','#station'].includes(location.hash))void sync.start();else sync.stop();};
  window.addEventListener('hashchange',activate);applyFilter();render(current);activate();
})();
