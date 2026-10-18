(() => {
  'use strict';
  let nativeStorage;try{nativeStorage=window.localStorage;}catch{}
  const storage=window.TripUtils.createSafeStorage(nativeStorage);
  const trip=window.TRIP;
  document.querySelector('.skip').addEventListener('click',event=>{event.preventDefault();const main=document.querySelector('#main');main.tabIndex=-1;main.focus();});
  const element=(tag,className,text)=>{const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;};
  const dayTabs=element('div','day-tabs');dayTabs.setAttribute('role','tablist');dayTabs.setAttribute('aria-label','選擇旅行日期');document.querySelector('#days').before(dayTabs);
  const panels=[];const tabs=[];
  trip.days.forEach((day,index)=>{
    const card=element('article','day');const date=element('div','day-date',day.date);date.append(element('small','',day.weekday));const body=element('div');body.append(element('span','proposed','規劃行程'),element('span','day-area',`DAY ${String(index+1).padStart(2,'0')} · ${day.area}`),element('h2','',day.title));
    const tab=element('button','day-tab',day.date);tab.type='button';tab.id=`day-tab-${index+1}`;tab.setAttribute('role','tab');tab.setAttribute('aria-controls',`day-panel-${index+1}`);tab.addEventListener('click',()=>{location.hash=`day-${index+1}`;});tabs.push(tab);dayTabs.append(tab);card.id=`day-panel-${index+1}`;card.setAttribute('role','tabpanel');card.setAttribute('aria-labelledby',tab.id);panels.push(card);
    const figure=element('figure','day-illustration');const drawing=element('div','map-scroll');drawing.innerHTML=window.TRIP_MAPS[index].svg;figure.append(drawing);const caption=element('figcaption','map-caption');const fullMap=element('a','', '開啟完整地圖 ↗');fullMap.href=`assets/day-${index+1}-map.svg`;fullMap.target='_blank';fullMap.rel='noopener noreferrer';caption.append(fullMap);figure.append(caption);body.append(figure);
    if(index===0){const floors=element('figure','floor-guide');const image=element('img');image.src='assets/skytree-floors.svg';image.alt='晴空街樓層：30F敘敘苑、6F利久牛舌、4F Pokémon Center、3F TOMICA・PLARAIL';image.width=720;image.height=1000;floors.append(image);const guide=element('figcaption','map-caption');const article=element('a','','晴空塔購物攻略｜來一球叭噗 ↗');article.href='https://gototravel.tw/tokyo-skytree-shopping/';article.target='_blank';article.rel='noopener noreferrer';guide.append(article);floors.append(guide);body.append(floors);}
    if(index===1)body.append(window.renderTokyoStationGuide());
    const mapLink=item=>{const link=element('a','',item.name+' ↗');link.href=item.url;link.target='_blank';link.rel='noopener noreferrer';return link;};
    const seenLinks=new Set();const schedule=element('ol','schedule');(day.schedule||[]).forEach(item=>{const row=element('li');row.append(element('span','schedule-time',item.time));const detail=element('div');const title=element('strong');const links=(item.links||[]).filter(link=>{if(window.TripUtils.isNavigationLink(link.url)||seenLinks.has(link.url))return false;seenLinks.add(link.url);return true;});const direct=links.length===1&&links[0].name===item.activity;if(direct)title.append(mapLink(links[0]));else title.textContent=item.activity;detail.append(title,element('p','',item.detail));if(!direct&&links.length){const maps=element('div','map-links');links.forEach(link=>maps.append(mapLink(link)));detail.append(maps);}row.append(detail);schedule.append(row);});body.append(schedule,element('p','',day.note));
    card.append(date,body);document.querySelector('#days').append(card);
  });
  const boxes=[];
  const updateProgress=()=>{document.querySelector('#progress').textContent=`${boxes.filter(box=>box.checked).length} / ${boxes.length} 已完成`;};
  trip.checklist.forEach(item=>{const label=element('label','check-item');const input=element('input');input.type='checkbox';input.checked=storage.get('tokyo-2026-check-'+item.id)==='true';input.addEventListener('change',()=>{storage.set('tokyo-2026-check-'+item.id,String(input.checked));updateProgress();});boxes.push(input);label.append(input,element('span','',item.text));document.querySelector('#checklist').append(label);});
  updateProgress();
  document.querySelector('#reset').addEventListener('click',()=>{if(!window.confirm('清除這個瀏覽器的所有勾選進度？'))return;boxes.forEach((box,index)=>{box.checked=false;storage.set('tokyo-2026-check-'+trip.checklist[index].id,'false');});updateProgress();});
  const themeButton=document.querySelector('#theme');
  const setTheme=dark=>{document.body.classList.toggle('dark',dark);themeButton.setAttribute('aria-pressed',String(dark));themeButton.setAttribute('aria-label',dark?'切換淺色模式':'切換深色模式');themeButton.textContent=dark?'淺色模式':'深色模式';};
  setTheme(storage.get('tokyo-2026-theme')==='dark');themeButton.addEventListener('click',()=>{const dark=!document.body.classList.contains('dark');setTheme(dark);storage.set('tokyo-2026-theme',dark?'dark':'light');});
  dayTabs.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();let day=window.TripUtils.resolveDay(location.hash);day=event.key==='Home'?0:event.key==='End'?3:(day+(event.key==='ArrowRight'?1:3))%4;location.hash=`day-${day+1}`;tabs[day].focus();});
  const renderRoute=(focus=false)=>{const page=window.TripUtils.resolvePage(location.hash);const selected=window.TripUtils.resolveDay(location.hash);panels.forEach((panel,index)=>{panel.hidden=index!==selected;tabs[index].setAttribute('aria-selected',String(index===selected));tabs[index].tabIndex=index===selected?0:-1;});document.querySelectorAll('.page').forEach(section=>{section.hidden=section.id!==page;});document.querySelectorAll('nav a').forEach(link=>{if(link.hash==='#'+page)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');});if(focus){const title=document.querySelector('#'+page+' h1');title.tabIndex=-1;title.focus({preventScroll:true});window.scrollTo(0,0);}};
  window.addEventListener('hashchange',()=>renderRoute(true));renderRoute();
})();
