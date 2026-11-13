(() => {
  'use strict';
  let nativeStorage;try{nativeStorage=window.localStorage;}catch{}
  const storage=window.TripUtils.createSafeStorage(nativeStorage);
  const trip=window.TRIP;
  document.querySelector('.skip').addEventListener('click',event=>{event.preventDefault();const main=document.querySelector('#main');main.tabIndex=-1;main.focus();});
  const element=(tag,className,text)=>{const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;};
  const dayTabs=element('div','day-tabs');dayTabs.setAttribute('role','tablist');dayTabs.setAttribute('aria-label','選擇旅行日期');document.querySelector('#days').before(dayTabs);
  const panels=[];const tabs=[];const mapLoaders=[];
  trip.days.forEach((day,index)=>{
    const card=element('article','day');const date=element('div','day-date',day.date);date.append(element('small','',day.weekday));const body=element('div');body.append(element('span','proposed','規劃行程'),element('span','day-area',`DAY ${String(index+1).padStart(2,'0')} · ${day.area}`),element('h2','',day.title));
    const tab=element('button','day-tab',day.date);tab.type='button';tab.id=`day-tab-${index+1}`;tab.setAttribute('role','tab');tab.setAttribute('aria-controls',`day-panel-${index+1}`);tab.addEventListener('click',()=>{location.hash=`day-${index+1}`;});tabs.push(tab);dayTabs.append(tab);card.id=`day-panel-${index+1}`;card.setAttribute('role','tabpanel');card.setAttribute('aria-labelledby',tab.id);panels.push(card);
    const maps=element('section','day-maps');const mapSummary=element('h3','','本日地圖與購物攻略');maps.append(mapSummary);
    let mapsLoaded=false;const loadMaps=()=>{if(mapsLoaded)return;mapsLoaded=true;const map=window.TRIP_MAPS[index];const figure=element('figure','day-illustration');const drawing=element('object','map-document');drawing.type='image/svg+xml';drawing.data='assets/'+map.file+'?v=1.76';drawing.setAttribute('aria-label',day.title+'地圖');drawing.style.aspectRatio=window.TRIP_MAPS[index].aspectRatio||'720 / 860';const fullMap=element('a','','開啟完整地圖並放大 ↗');fullMap.href=drawing.data;fullMap.target='_blank';fullMap.rel='noopener noreferrer';drawing.append(fullMap.cloneNode(true));figure.append(drawing,fullMap);maps.append(figure);
      if (index === 2) {
        const shoppingMap = element('figure', 'day-illustration');
        shoppingMap.id = 'harajuku-shibuya-map';
        const shoppingTitle = element('h4', '', '原宿・表參道・澀谷購物地圖');
        const shoppingDrawing = element('object', 'map-document');
        shoppingDrawing.type = 'image/svg+xml';
        shoppingDrawing.data = 'assets/harajuku-shibuya-shopping.svg?v=1.93';
        shoppingDrawing.style.aspectRatio = '680 / 660';
        shoppingDrawing.setAttribute('aria-label', shoppingTitle.textContent);
        const openShoppingMap = element('a', '', '開啟原宿・澀谷完整地圖並放大 ↗');
        openShoppingMap.href = shoppingDrawing.data;
        openShoppingMap.target = '_blank';
        openShoppingMap.rel = 'noopener noreferrer';
        shoppingDrawing.append(openShoppingMap.cloneNode(true));
        shoppingMap.append(shoppingTitle, shoppingDrawing, openShoppingMap);
        figure.before(shoppingMap);
        const shops = [
          {name: 'Nike 原宿', hours: '原宿 Quest 1F・10:00–21:00', x: 236, y: 362, labelX: 45, labelY: 382, query: 'Nike Harajuku Quest'},
          {name: 'On 貓街店', hours: '神宮前 5-17-27・11:00–20:00', x: 394, y: 692, labelX: 65, labelY: 662, query: 'On Store Tokyo Cat Street'}
        ];
        const nearby = element('div', 'map-links');
        shops.forEach(shop => nearby.append(mapLink({
          name: shop.name + '｜' + shop.hours,
          url: 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(shop.query)
        })));
        maps.append(nearby);
        drawing.addEventListener('load', () => {
          const doc = drawing.contentDocument;
          const harajuku = doc?.documentElement.querySelector('svg[y="860"]');
          if (!harajuku || harajuku.querySelector('#harajuku-extra-shops')) return;
          const ns = 'http://www.w3.org/2000/svg';
          const svg = (tag, attributes, value) => {
            const node = doc.createElementNS(ns, tag);
            Object.entries(attributes).forEach(([key, val]) => node.setAttribute(key, val));
            if (value) node.textContent = value;
            return node;
          };
          const group = svg('g', {id: 'harajuku-extra-shops'});
          shops.forEach(shop => {
            const link = svg('a', {
              href: 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(shop.query),
              target: '_blank', rel: 'noopener noreferrer', 'aria-label': shop.name + '：開啟 Google Maps'
            });
            link.append(
              svg('path', {d: 'M' + shop.x + ' ' + shop.y + 'L' + (shop.labelX + 82) + ' ' + (shop.labelY - 5), fill: 'none', stroke: '#536377'}),
              svg('circle', {cx: shop.x, cy: shop.y, r: 5, fill: '#a94732', stroke: '#f8f5ee', 'stroke-width': 2}),
              svg('text', {x: shop.labelX, y: shop.labelY, fill: '#26312e', 'font-family': 'sans-serif', 'font-size': 18, 'font-weight': 600, 'paint-order': 'stroke', stroke: '#f8f5ee', 'stroke-width': 5, 'stroke-linejoin': 'round'}, shop.name)
            );
            group.append(link);
          });
          harajuku.append(group);
        });
      }

      if(index===0){const stay=element('figure','day-illustration');const object=element('object','map-document');object.type='image/svg+xml';object.data='assets/day-1-stay-map.svg?v=1.76&rev=2';object.style.aspectRatio='720 / 1170';object.setAttribute('aria-label','押上回飯店與住宿周邊地圖');const full=element('a','','開啟完整住宿地圖並放大 ↗');full.href=object.data;full.target='_blank';full.rel='noopener noreferrer';stay.append(object,full);maps.append(stay);const floors=element('section','floor-guide');floors.append(element('h3','','晴空街樓層圖'));const image=element('img');image.src='assets/skytree-floors.svg?v=1.76&rev=2';image.alt='晴空街樓層圖：敘敘苑在東館30F；備長鰻魚飯（午餐備選）與利久牛舌（晚餐備選）在東館6F、11番地';image.loading='lazy';floors.append(image);maps.append(floors);}
      if(index===1){const guide=element('a','station-day-link','東京車站購物：地圖＋推薦商品 ↗');guide.href='#station';maps.append(guide);}
      if(index===3){const guide=element('a','station-day-link','退稅攻略：成田 T2 海關確認與領款 ↗');guide.href='#tax-refund';maps.append(guide);}
    };mapLoaders.push(loadMaps);

    const mapLink=item=>{const link=element('a','',item.name+' ↗');link.href=item.url;link.target='_blank';link.rel='noopener noreferrer';return link;};
    const renderStopFloorMap = ({src, width, height, alt, caption}) => {
      const figure = element('figure', 'floor-guide');
      const zoom = mapLink({name: '開啟原圖並放大', url: src});
      const image = element('img');
      image.src = src;
      image.width = width;
      image.height = height;
      image.alt = alt;
      image.loading = 'lazy';
      zoom.prepend(image);
      figure.append(element('figcaption', '', caption), zoom);
      return figure;
    };
    const seenLinks=new Set();const schedule=element('ol','schedule');(day.schedule||[]).forEach(item=>{const row=element('li');row.append(element('span','schedule-time',item.time));const detail=element('div');const title=element('strong');const links=(item.links||[]).filter(link=>{if(window.TripUtils.isNavigationLink(link.url)||seenLinks.has(link.url))return false;seenLinks.add(link.url);return true;});const direct=links.length===1&&links[0].name===item.activity;if(direct)title.append(mapLink(links[0]));else title.textContent=item.activity;detail.append(title);const points=element('ul','schedule-points');(item.points||[item.detail]).filter(Boolean).forEach(point=>points.append(element('li','',point)));detail.append(points);if(/待確認|待核對|尚待|尚需|待上傳/.test(item.detail+' '+item.time))detail.prepend(element('span','pending-badge','待確認'));if(!direct&&links.length){const maps=element('div','map-links');links.forEach(link=>maps.append(mapLink(link)));detail.append(maps);}if(item.floorMap)detail.append(renderStopFloorMap(item.floorMap));row.append(detail);schedule.append(row);});const notes=element('ul','day-note');(day.notes||[day.note]).filter(Boolean).forEach(note=>notes.append(element('li','',note)));body.append(maps,schedule,notes);
    card.append(date,body);document.querySelector('#days').append(card);
  });
  const today=element('button','today-button','今天');today.type='button';const todayStatus=element('span','today-status');todayStatus.setAttribute('role','status');const dateBar=element('div','date-bar');dayTabs.before(dateBar);dateBar.append(dayTabs,today,todayStatus);today.addEventListener('click',()=>{const parts=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Taipei',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());const key=parts.slice(5).replace('-','.');let i=trip.days.findIndex(day=>day.date===key);if(i<0){i=parts<'2026-11-12'?0:3;todayStatus.textContent='目前不在旅期，顯示'+trip.days[i].date;}else todayStatus.textContent='顯示今天行程';location.hash='day-'+(i+1);});
  const pending=document.querySelector('#pending-list');const reminder=element('li');const reminderLink=element('a','','Airporter：待拍攝及上傳2件行李照片');reminderLink.href='#prep';reminder.append(reminderLink);pending.append(reminder);
  const boxes=[];
  const updateProgress=()=>{document.querySelector('#progress').textContent=`${boxes.filter(box=>box.checked).length} / ${boxes.length} 已完成`;};
  trip.checklist.forEach(item=>{const label=element('label','check-item');const input=element('input');input.type='checkbox';input.checked=storage.get('tokyo-2026-check-'+item.id)==='true';input.addEventListener('change',()=>{storage.set('tokyo-2026-check-'+item.id,String(input.checked));updateProgress();});boxes.push(input);label.append(input,element('span','',item.text));if(/待確認|待核對|尚待|待上傳/.test(item.text))label.append(element('span','pending-badge','待確認'));document.querySelector('#checklist').append(label);});
  updateProgress();
  document.querySelector('#reset').addEventListener('click',()=>{if(!window.confirm('清除這個瀏覽器的所有勾選進度？'))return;boxes.forEach((box,index)=>{box.checked=false;storage.set('tokyo-2026-check-'+trip.checklist[index].id,'false');});updateProgress();});
  const themeButton=document.querySelector('#theme');
  const setTheme=dark=>{document.body.classList.toggle('dark',dark);themeButton.setAttribute('aria-pressed',String(dark));themeButton.setAttribute('aria-label',dark?'切換淺色模式':'切換深色模式');themeButton.textContent=dark?'淺色模式':'深色模式';};
  setTheme(storage.get('tokyo-2026-theme')==='dark');themeButton.addEventListener('click',()=>{const dark=!document.body.classList.contains('dark');setTheme(dark);storage.set('tokyo-2026-theme',dark?'dark':'light');});
  dayTabs.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();let day=window.TripUtils.resolveDay(location.hash);day=event.key==='Home'?0:event.key==='End'?3:(day+(event.key==='ArrowRight'?1:3))%4;location.hash=`day-${day+1}`;tabs[day].focus();});
  const renderRoute=(focus=false)=>{const page=window.TripUtils.resolvePage(location.hash);const selected=window.TripUtils.resolveDay(location.hash);if(page==='itinerary')mapLoaders[selected]();panels.forEach((panel,index)=>{panel.hidden=index!==selected;tabs[index].setAttribute('aria-selected',String(index===selected));tabs[index].tabIndex=index===selected?0:-1;});document.querySelectorAll('.page').forEach(section=>{section.hidden=section.id!==page;});document.querySelectorAll('nav a').forEach(link=>{if(link.hash==='#'+page)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');});if(focus){const title=document.querySelector('#'+page+' h1');title.tabIndex=-1;title.focus({preventScroll:true});window.scrollTo(0,0);}};
  window.addEventListener('hashchange',()=>renderRoute(true));renderRoute();
})();
