(() => {
  'use strict';
  window.renderTokyoStationGuide = () => {
    const section=document.createElement('section');section.className='station-guide';section.setAttribute('aria-labelledby','station-guide-title');
    section.innerHTML='<h3 id="station-guide-title">東京站・伴手禮分層導覽</h3><p class="station-guide-intro">先逛JR閘門內兩間，再從1F八重洲北口出站。全部都是候選，現場自由跳過。</p><ol class="station-route"><li><strong>JR內</strong><span>B1 Ivorish → 1F Maple Mania</span></li><li><strong>大丸</strong><span>1F TRIPLE DECKER・N.Y.C.SAND → B1 PRESS</span></li><li><strong>Gift Palette</strong><span>回1F，逛PISTA・布蕾塔・巧克力・費南雪</span></li><li><strong>おかしランド</strong><span>再下B1，Calbee＋等零食現場選</span></li></ol>';
    const tabs=document.createElement('div');tabs.className='station-floor-tabs';tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','東京站採買樓層');section.append(tabs);
    const panel=document.createElement('div');panel.id='station-floor-panel';panel.className='station-guide-canvas';panel.setAttribute('role','tabpanel');section.append(panel);
    const caption=document.createElement('p');caption.className='station-guide-caption';const full=document.createElement('a');full.target='_blank';full.rel='noopener noreferrer';full.textContent='開啟完整樓層圖 ↗';caption.append(full);section.append(caption);
    const buttons=[];let active=0;
    const choose=(index,focus=false)=>{active=index;const item=window.TOKYO_STATION_GUIDE[index];buttons.forEach((button,i)=>{button.setAttribute('aria-selected',String(i===index));button.tabIndex=i===index?0:-1;});panel.innerHTML=item.svg;panel.setAttribute('aria-labelledby',buttons[index].id);full.href='assets/'+item.file;if(focus)buttons[index].focus();};
    window.TOKYO_STATION_GUIDE.forEach((item,index)=>{const button=document.createElement('button');button.type='button';button.id='station-floor-'+item.id;button.textContent=item.label;button.setAttribute('role','tab');button.setAttribute('aria-controls',panel.id);button.addEventListener('click',()=>choose(index));tabs.append(button);buttons.push(button);});
    tabs.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();choose(event.key==='Home'?0:event.key==='End'?buttons.length-1:(active+(event.key==='ArrowRight'?1:-1)+buttons.length)%buttons.length,true);});
    const note=document.createElement('p');note.className='station-guide-note';note.textContent='改札內＝需車票的JR付費區。出站後找自由通路往丸之內，不要為了穿越車站再刷進JR；推車依現場電梯指標。圖為區域示意，非精密櫃位平面。';section.append(note);
    const details=document.createElement('details');details.className='station-official-maps';const summary=document.createElement('summary');summary.textContent='找不到店？開啟官方樓層圖';details.append(summary);
    const links=[['GRANSTA 官方樓層圖','https://www.gransta.jp/'],['Gift Palette 官方櫃位圖','https://www.tokyoeki-1bangai.co.jp/assets/pdf/floorMap_giftpalette.pdf'],['東京站一番街官方導覽','https://www.tokyoeki-1bangai.co.jp/'],['大丸官方樓層圖','https://www.daimaru.co.jp/tokyo/floor/']];
    links.forEach(([name,url])=>{const a=document.createElement('a');a.href=url;a.textContent=name+' ↗';a.target='_blank';a.rel='noopener noreferrer';details.append(a);});section.append(details);
    choose(0);return section;
  };
})();
