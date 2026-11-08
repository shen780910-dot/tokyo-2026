(() => {
  'use strict';
  const make=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text)e.textContent=text;return e;};
  const items=window.SHOPPING_LIST.flatMap(g=>g.items).filter(x=>x.routeFloor&&x.decision!=='不買');
  const host=document.querySelector('#station-shopping-guide');let initialized=false,state={items:{},unlocked:false,connected:false,writingIds:[]};
  function build(){if(initialized)return;initialized=true;host.append(window.renderTokyoStationGuide());}
  function activate(){if(location.hash==='#station')build();}window.addEventListener('hashchange',activate);
  window.addEventListener('shopping-state',event=>{state=event.detail;update();});
  function update(){for(const label of host.querySelectorAll('.station-buy')){const input=label.querySelector('input');const id=input.dataset.item;input.checked=state.items[id]?.purchased===true;input.disabled=!state.unlocked||!state.connected||state.writingIds.includes(id);label.classList.toggle('is-purchased',input.checked);}const status=host.querySelector('.station-sync-note');if(status)status.textContent=state.unlocked?'已解鎖，購買狀態與待購清單同步。':'圖片與推薦可直接查看；到待購清單解鎖後，可在此勾選已購買。';}
  window.renderStationProducts=(floor,container)=>{
    container.replaceChildren();const chosen=items.filter(x=>floor==='overview'||x.routeFloor===floor);
    const heading=make('h3','','本層推薦商品');container.append(heading);
    const note=make('p','station-sync-note','圖片與推薦可直接查看；到待購清單解鎖後，可在此勾選已購買。');container.append(note);const unlock=make('a','station-unlock','到待購清單解鎖共同勾選 ↗');unlock.href='#shopping';container.append(unlock);
    if(!chosen.length){container.append(make('p','','此層以逛街為主，沒有另列伴手禮；採買請切換其他樓層。'));return;}
    const grid=make('div','station-product-grid');const shops=Map.groupBy?Map.groupBy(chosen,x=>x.routeOrder):chosen.reduce((m,x)=>m.set(x.routeOrder,[...(m.get(x.routeOrder)||[]),x]),new Map());
    for(const [order,products] of shops){const shop=make('article','station-shop');shop.id='station-shop-'+order;shop.append(make('p','station-shop-number',String(order).padStart(2,'0')+'｜'+products[0].store));
      for(const item of products){const block=make('section','station-product');block.id='station-product-'+item.id;const img=make('img');img.src=item.image;img.alt=item.recommendation||item.name;img.loading='lazy';img.width=640;img.height=440;block.append(img,make('h4','',item.recommendation||item.name),make('p','station-product-hint',item.selectionNote||item.detail));
        if(item.imageNote)block.append(make('p','station-image-note',item.imageNote));
        const links=make('div','station-product-links');const used=new Set();for(const [name,url] of [['商品／Notion',item.url],['推薦來源',item.sourceUrl],['圖片來源',item.imageSource]]){if(!url||used.has(url))continue;used.add(url);const a=make('a','',name+' ↗');a.href=url;a.target='_blank';a.rel='noopener noreferrer';links.append(a);}block.append(links);
        const label=make('label','station-buy');const input=make('input');input.type='checkbox';input.dataset.item=item.id;input.disabled=true;input.addEventListener('change',()=>{void window.familyShoppingSync.setPurchased(item.id,input.checked).catch(()=>update());});label.append(input,document.createTextNode('已購買'));block.append(label);shop.append(block);
      }
      const next=make('p','station-next',products.at(-1).nextStop);shop.append(next);grid.append(shop);
    }container.append(grid);update();
  };
  activate();
})();
