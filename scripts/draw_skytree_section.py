"""Draw an original hand-drawn building section inspired by the supplied guide."""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent.parent
ns={'__file__':str(R/'scripts/build_geo_maps.py')}
exec((R/'scripts/build_geo_maps.py').read_text(encoding='utf-8').split('output=[]')[0],ns)
parts=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1000" role="img" aria-labelledby="section-title section-desc"><title id="section-title">晴空塔與晴空街手繪樓層剖面</title><desc id="section-desc">西館在左，晴空塔在中央，東館在右。30樓敘敘苑、6樓利久、4樓Pokémon Center均在東館，3樓TOMICA在西館。樓層高度非比例，展望台未列入本次行程。</desc><defs><filter id="section-paper"><feTurbulence baseFrequency=".65" numOctaves="2" seed="8" type="fractalNoise"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".035"/></feComponentTransfer><feBlend in="SourceGraphic" mode="multiply"/></filter></defs><rect width="720" height="1000" fill="#eeeade"/><rect width="720" height="1000" filter="url(#section-paper)" fill="#eeeade"/><path d="M20 25Q355 20 700 26L697 976Q365 981 22 975Z" stroke="#536377" stroke-width="1.4" fill="none"/><path d="M21 30L103 18" stroke="#c8937e" stroke-width="20" opacity=".4"/><path d="M620 18L699 34" stroke="#a6b79c" stroke-width="20" opacity=".4"/>''']
def text(content,x,y,size=23,sub=False,color='#26312e'):
 parts.append(f'<text class="{"sub" if sub else "name"}" x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(content)}</text>')
def numeral(content,x,y,size=23):
 parts.append(f'<text data-numeral="true" x="{x}" y="{y}" font-size="{size}" font-family="Arial,Helvetica,sans-serif" fill="#536377">{content}</text>')
text('晴空街・想去的店',45,75,30)
text('從西館走到東館，再上樓吃飯',45,110,18,True,'#536377')
# Tower outline: deliberately irregular pen strokes, a separate landmark from the mall.
parts.append('''<g stroke="#536377" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"><path d="M279 186L280 144L287 143L288 185M277 151L291 151M278 161L290 161M280 186L270 257L294 257L287 186M274 208L291 229M290 208L273 230M271 244L294 244M262 258L303 258L294 278L273 279ZM274 280L267 325L299 325L291 280M271 289L296 315M293 290L269 315M255 327L310 328L309 345L300 363L265 362L255 345ZM266 364L251 612L318 612L300 364M265 383L304 423L260 467L309 509L255 553L316 602M301 383L263 425L307 468L257 510L313 552L252 602M269 364L266 611M297 364L302 611M260 439L307 439M257 501L312 501M254 560L315 560M250 614L319 614"/><path d="M278 146L278 187M252 331L311 331M253 614L320 614" stroke-width=".8" opacity=".6"/></g>''')
text('東京晴空塔',66,220,23)
parts.append('<path d="M187 220L250 326" stroke="#536377" stroke-width="1" fill="none"/>')
text('展望台非本次必排行程',45,250,16,True,'#536377')
text('西館',76,590,23);text('塔區',262,650,22);text('東館',455,228,23)
def band(x,y,w,h,fill):
 parts.append(f'<path d="M{x} {y}Q{x+w/2} {y-2} {x+w} {y+1}L{x+w-1} {y+h}Q{x+w/2} {y+h+2} {x} {y+h-1}Z" fill="{fill}" stroke="#a89c7c" stroke-width="1"/>')
def stop(x,y,name,sub,hours):
 parts.append(f'<circle cx="{x}" cy="{y-8}" r="4" fill="#a94732"/>')
 text(name,x+13,y,24);text(sub,x+13,y+25,16,True,'#536377');text(hours,x+13,y+48,16,True,'#536377')
# East tower upper floors and the break for office levels.
band(350,258,294,86,'#e4d1af');numeral('30–31F',545,248,19)
stop(364,285,'敘敘苑','30F・12番地｜午餐首選','10:30–16:00 午餐')
text('現場候位，超過30分鐘換店',365,366,16,True,'#536377')
parts.append('<path d="M351 383L374 377L397 383L420 377L443 383L466 377L489 383L512 377L535 383L558 377L581 383L604 377L644 383" stroke="#a89c7c" fill="none"/>')
band(350,400,294,33,'#d7ddcb');numeral('8–10F',653,423,17);text('其他樓層',367,422,16,True,'#536377')
band(350,441,294,29,'#e4d1af');numeral('7F',653,463,20)
band(330,478,314,83,'#e4d1af');numeral('6F',653,508,22)
stop(346,506,'利久牛舌','6F・11番地｜晚餐備選','11:00–23:00')
band(330,569,314,30,'#c9d8d3');numeral('5F',653,591,20)
# Shared podium: the west/east distinction stays visible across the lower floors.
band(45,612,205,81,'#d8dfdf');band(253,661,74,32,'#dfd4af');band(330,612,314,81,'#cfd8df');numeral('4F',653,646,22)
stop(346,640,'Pokémon Center','4F・11番地｜角色商品','10:00–21:00')
text('塔區入口',65,659,18,True,'#536377')
band(45,703,282,83,'#cfd8df');band(330,703,314,83,'#cfd8df');numeral('3F',653,737,22)
stop(60,731,'TOMICA・PLARAIL','西館・4番地','10:00–21:00')
text('東館購物樓層',367,750,18,True,'#536377')
band(45,796,282,35,'#dfc8c5');band(330,796,314,35,'#cfd8df');numeral('2F',653,821,20)
text('食品・伴手禮',65,820,17,True,'#536377');text('服飾・雜貨',367,820,17,True,'#536377')
band(45,841,282,37,'#cfd8df');band(330,841,314,37,'#cfd8df');numeral('1F',653,868,20)
text('東京晴空塔站側',65,867,17,True,'#536377');text('押上站側',367,867,17,True,'#536377')
parts.append('<path d="M48 902H644M48 897V907M644 897V907" stroke="#536377" fill="none"/>')
text('West Yard',68,931,20);text('Tower Yard',259,931,18);text('East Yard',473,931,20)
text('樓層與館別示意・高度非比例，移動依現場電梯指引',45,961,16,True,'#536377')
parts.append('</svg>')
# Outline the authored lettering, keeping floor numerals in a clear system font.
raw=ET.fromstring(''.join(parts));tag=lambda n:'{http://www.w3.org/2000/svg}'+n
digits=[]
for parent in raw.iter():
 for n in list(parent):
  if n.get('data-numeral'):digits.append(n);parent.remove(n)
outlined=ET.fromstring(ns['outline_text'](ET.tostring(raw,encoding='unicode')))
for n in digits:outlined.append(n)
(R/'assets/skytree-floors.svg').write_text(ET.tostring(outlined,encoding='unicode'),encoding='utf-8')
p=R/'assets/app.js';s=p.read_text(encoding='utf-8').replace('image.height=730','image.height=1000')
s=s.replace("floors.append(image);body.append(floors);", "floors.append(image);const guide=element('figcaption','map-caption');const article=element('a','','晴空塔購物攻略｜來一球叭噗 ↗');article.href='https://gototravel.tw/tokyo-skytree-shopping/';article.target='_blank';article.rel='noopener noreferrer';guide.append(article);floors.append(guide);body.append(floors);")
p.write_text(s,encoding='utf-8')
(R/'VERSION').write_text('v1.17\n',encoding='utf-8')
p=R/'CHANGELOG.md';s=p.read_text(encoding='utf-8');i=s.index('## ');p.write_text(s[:i]+'## v1.17\n\n- 參考使用者提供的樓層導覽構圖，重繪原創紙色手繪SVG剖面，呈現晴空塔、西館與東館。\n- 將敘敘苑、利久、Pokémon Center與TOMICA標示在對應館別及樓層。\n- 樓層圖下加入「來一球叭噗」晴空塔購物攻略連結，保留清楚的系統樓層數字。\n\n'+s[i:],encoding='utf-8')
