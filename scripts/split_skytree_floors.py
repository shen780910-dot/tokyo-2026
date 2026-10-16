"""Separate indoor destinations from the outdoor geographic map."""
from pathlib import Path
from html import escape
import json, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent.parent
ns={'__file__':str(R/'scripts/build_geo_maps.py')}
exec((R/'scripts/build_geo_maps.py').read_text(encoding='utf-8').split('output=[]')[0],ns)
p=R/'assets/trip-maps.js';maps=json.loads(p.read_text(encoding='utf-8').split(' = ',1)[1].strip().removesuffix(';'))
root=ET.fromstring(maps[0]['svg']);tag=lambda n:'{http://www.w3.org/2000/svg}'+n
indoor=('TOMICA','Pokémon','利久','敘敘苑')
for parent in list(root.iter()):
 for child in list(parent):
  if child.tag==tag('a') and any(name in child.get('aria-label','') for name in indoor):parent.remove(child)
  elif child.tag==tag('path') and child.get('stroke-dasharray')=='8 7':parent.remove(child)
  elif child.tag==tag('circle') and child.get('r')=='9':parent.remove(child)
  elif child.tag==tag('text') and ''.join(child.itertext()).isdigit():parent.remove(child)
# The map now shows geographic destinations without indoor stop numbering.
maps[0]['svg']=ET.tostring(root,encoding='unicode')
p.write_text('window.TRIP_MAPS = '+json.dumps(maps,ensure_ascii=False)+';\n',encoding='utf-8')
(R/'assets/day-1-map.svg').write_text(maps[0]['svg'],encoding='utf-8')
rows=[('30F','敘敘苑','東館・12番地｜午餐首選','週四午餐10:30–16:00｜候位超過30分鐘換店'),('6F','利久牛舌','東館・11番地｜晚餐備選','11:00–23:00｜依午餐份量彈性安排'),('4F','Pokémon Center','東館・11番地｜角色商品','10:00–21:00'),('3F','TOMICA・PLARAIL','西館・4番地｜角色商品','10:00–21:00')]
parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 730" role="img" aria-labelledby="floor-title floor-desc"><title id="floor-title">晴空街館內樓層圖</title><desc id="floor-desc">30樓敘敘苑，6樓利久，4樓Pokémon Center，3樓TOMICA。依樓層排列，非平面位置圖。</desc><rect width="720" height="730" rx="8" fill="#eeeade"/><path d="M24 25H696V705H24Z" fill="none" stroke="#536377" stroke-width="1.2"/><text class="name" x="48" y="76" font-size="30" fill="#26312e">晴空街・館內樓層</text><text class="sub" x="48" y="109" font-size="18" fill="#536377">依樓層排列，非平面位置與比例</text><path d="M126 145V650" stroke="#c3b38f" stroke-width="2"/>']
for i,(floor,name,sub,hours) in enumerate(rows):
 y=179+i*124
 parts.append(f'<path d="M48 {y+87}H672" stroke="#c3b38f" stroke-width="1"/><text x="64" y="{y+8}" font-family="Arial,sans-serif" font-size="32" fill="#a94732">{floor}</text><text class="name" x="154" y="{y}" font-size="27" fill="#26312e">{escape(name)}</text><text class="sub" x="154" y="{y+31}" font-size="18" fill="#536377">{escape(sub)}</text><text class="sub" x="154" y="{y+59}" font-size="17" fill="#536377">{escape(hours)}</text>')
parts.append('<text class="sub" x="48" y="686" font-size="16" fill="#536377">東、西館之間需步行；高樓層依現場電梯指引</text></svg>')
floor=ET.fromstring(ns['outline_text'](''.join(parts)))
# Restore clear system-font floor numerals instead of outlining with Lihsianti.
for parent in floor.iter():
 for child in list(parent):
  if child.get('aria-label') in [r[0] for r in rows]:
   i=[r[0] for r in rows].index(child.get('aria-label'));n=ET.Element(tag('text'),{'x':'64','y':str(187+i*124),'font-family':'Arial,sans-serif','font-size':'32','fill':'#a94732'});n.text=rows[i][0];parent.insert(list(parent).index(child),n);parent.remove(child)
(R/'assets/skytree-floors.svg').write_text(ET.tostring(floor,encoding='unicode'),encoding='utf-8')
p=R/'assets/app.js';s=p.read_text(encoding='utf-8');needle='    const mapLink=item=>'
addition="    if(index===0){const floors=element('figure','floor-guide');const image=element('img');image.src='assets/skytree-floors.svg';image.alt='晴空街樓層：30F敘敘苑、6F利久牛舌、4F Pokémon Center、3F TOMICA・PLARAIL';image.width=720;image.height=730;floors.append(image);body.append(floors);}\n"
if addition not in s:s=s.replace(needle,addition+needle)
p.write_text(s,encoding='utf-8')
p=R/'assets/style.css';s=p.read_text(encoding='utf-8');s+='\n.floor-guide{margin:24px 0 32px;max-width:100%;min-width:0}.floor-guide img{display:block;width:100%;height:auto;max-width:100%}\n';p.write_text(s,encoding='utf-8')
(R/'VERSION').write_text('v1.16\n',encoding='utf-8')
p=R/'CHANGELOG.md';s=p.read_text(encoding='utf-8');i=s.index('## ');p.write_text(s[:i]+'## v1.16\n\n- 晴空街館內店家改由獨立樓層圖呈現：30F敘敘苑、6F利久、4F寶可夢、3F TOMICA。\n- 地理SVG只保留晴空塔建築地標、押上站與LIFE，移除館內店家紅點與繞行路線。\n- 樓層圖維持粒線體店名、清楚的系統樓層數字，手機完整縮放顯示。\n\n'+s[i:],encoding='utf-8')
