(() => {
  'use strict';
  let nativeStorage;try{nativeStorage=window.localStorage;}catch{}
  const storage=window.TripUtils.createSafeStorage(nativeStorage);
  const trip=window.TRIP;
  document.querySelector('.skip').addEventListener('click',event=>{event.preventDefault();const main=document.querySelector('#main');main.tabIndex=-1;main.focus();});
  const element=(tag,className,text)=>{const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;};
  trip.days.forEach((day,index)=>{
    const card=element('article','day');const date=element('div','day-date',day.date);date.append(element('small','',day.weekday));const body=element('div');body.append(element('span','proposed','建議行程'),element('span','day-area',`DAY ${String(index+1).padStart(2,'0')} · ${day.area}`),element('h2','',day.title));const stops=element('ol','stops');day.stops.forEach(stop=>stops.append(element('li','',stop)));body.append(stops,element('p','',day.note));card.append(date,body);document.querySelector('#days').append(card);
  });
  const boxes=[];
  const updateProgress=()=>{document.querySelector('#progress').textContent=`${boxes.filter(box=>box.checked).length} / ${boxes.length} 已完成`;};
  trip.checklist.forEach(item=>{const label=element('label','check-item');const input=element('input');input.type='checkbox';input.checked=storage.get('yonago-check-'+item.id)==='true';input.addEventListener('change',()=>{storage.set('yonago-check-'+item.id,String(input.checked));updateProgress();});boxes.push(input);label.append(input,element('span','',item.text));document.querySelector('#checklist').append(label);});
  updateProgress();
  document.querySelector('#reset').addEventListener('click',()=>{if(!window.confirm('清除這個瀏覽器的所有勾選進度？'))return;boxes.forEach((box,index)=>{box.checked=false;storage.set('yonago-check-'+trip.checklist[index].id,'false');});updateProgress();});
  const themeButton=document.querySelector('#theme');
  const setTheme=dark=>{document.body.classList.toggle('dark',dark);themeButton.setAttribute('aria-pressed',String(dark));themeButton.setAttribute('aria-label',dark?'切換淺色模式':'切換深色模式');themeButton.textContent=dark?'淺色模式':'深色模式';};
  setTheme(storage.get('yonago-theme')==='dark');themeButton.addEventListener('click',()=>{const dark=!document.body.classList.contains('dark');setTheme(dark);storage.set('yonago-theme',dark?'dark':'light');});
  const renderRoute=(focus=false)=>{const page=window.TripUtils.resolvePage(location.hash);document.querySelectorAll('.page').forEach(section=>{section.hidden=section.id!==page;});document.querySelectorAll('nav a').forEach(link=>{if(link.hash==='#'+page)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');});if(focus){const title=document.querySelector('#'+page+' h1');title.tabIndex=-1;title.focus({preventScroll:true});window.scrollTo(0,0);}};
  window.addEventListener('hashchange',()=>renderRoute(true));renderRoute();
})();
