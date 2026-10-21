(() => {
  'use strict';
  let nativeStorage;try{nativeStorage=window.localStorage;}catch{}
  const storage=window.TripUtils.createSafeStorage(nativeStorage);
  const root=document.querySelector('#shopping-categories');
  const inputs=[];
  const progress=()=>{document.querySelector('#shopping-progress').textContent=`${inputs.filter(input=>input.checked).length} / ${inputs.length} 已購買`;};
  for(const group of window.SHOPPING_LIST){
    const section=document.createElement('section');section.className='shopping-category';
    const title=document.createElement('h2');title.textContent=group.category;section.append(title);
    for(const item of group.items){
      const row=document.createElement('article');row.className='shopping-item';row.dataset.item=item.id;
      if(item.image){const image=document.createElement('img');image.src=item.image;image.alt=item.name+' 包裝參考';image.width=180;image.height=180;image.loading='lazy';row.append(image);}else row.classList.add('shopping-item-text');
      const content=document.createElement('div');
      const type=document.createElement('span');type.className='shopping-type';type.textContent=item.type;
      const heading=document.createElement('h3');heading.textContent=item.name;
      const detail=document.createElement('p');detail.textContent=item.detail;
      content.append(type,heading,detail);
      if(item.url){const link=document.createElement('a');link.className='shopping-source';link.href=item.url;link.textContent=(item.linkLabel||'商品資訊')+' ↗';link.target='_blank';link.rel='noopener noreferrer';content.append(link);}
      const label=document.createElement('label');label.className='shopping-purchased';
      const input=document.createElement('input');input.type='checkbox';input.checked=storage.get('tokyo-2026-shopping-'+item.id)==='true';
      row.classList.toggle('is-purchased',input.checked);
      input.addEventListener('change',()=>{storage.set('tokyo-2026-shopping-'+item.id,String(input.checked));row.classList.toggle('is-purchased',input.checked);progress();});
      inputs.push(input);label.append(input,document.createTextNode('已購買'));
      content.append(label);row.append(content);section.append(row);
    }
    root.append(section);
  }
  progress();
})();
