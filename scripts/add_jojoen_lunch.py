"""Add flexible arrival-day lunch and a geographic restaurant label."""
from pathlib import Path
import json, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent.parent
def load(name):return json.loads((R/name).read_text(encoding='utf-8').split(' = ',1)[1].strip().removesuffix(';'))
d=load('assets/trip-data.js'); day=d['days'][0]
row=next(row for row in day['schedule'] if row['activity']=='晴空街午餐・休息')
row.update(activity='午餐首選｜敘敘苑 晴空街30F',detail='抵達後直接到30F詢問，不預約固定時間；現場候位超過30分鐘就改吃館內其他餐廳。週四午餐目前至16:00最後點餐，滿座可能無法入店。綜合午餐每人¥4,700，兩成人約NT$1,880，孩子餐費另計；兒童椅與分食規則現場確認。',links=[{'name':'敘敘苑 晴空街店｜官方菜單','url':'https://www.jojoen.co.jp/shop/jojoen/soramachi/'}])
for row in day['schedule']:
 if row['activity']=='利久牛舌｜晴空街6F':row.update(activity='晚餐備選｜利久牛舌 晴空街6F',detail='依午餐份量與孩子體力決定；若午餐吃敘敘苑，晚餐可改清淡或簡單用餐。候位依現場狀況調整。')
day['note']+=' 午餐首選敘敘苑，現場候位上限30分鐘；利久牛舌保留為晚餐備選。'
for item in d['checklist']:
 if item['id']=='shopping-skytree':item['text']='晴空街敘敘苑午餐現場候位，超過30分鐘換店；TOMICA、Pokémon Center與LIFE，利久晚餐備選'
(R/'assets/trip-data.js').write_text('window.TRIP = '+json.dumps(d,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
ns={'__file__':str(R/'scripts/build_geo_maps.py')}
exec((R/'scripts/build_geo_maps.py').read_text(encoding='utf-8').split('output=[]')[0],ns)
maps=load('assets/trip-maps.js');root=ET.fromstring(maps[0]['svg']); tag=lambda name:'{http://www.w3.org/2000/svg}'+name
if not any('敘敘苑' in a.get('aria-label','') for a in root.iter(tag('a'))):
 fragment='''<svg xmlns="http://www.w3.org/2000/svg"><a href="https://www.google.com/maps/search/?api=1&amp;query=Jojoen+Tokyo+Skytree+Town+Solamachi" target="_blank" rel="noopener noreferrer" aria-label="敘敘苑：開啟Google Maps"><title>敘敘苑 晴空街30F・午餐首選</title><path class="leader" d="M424.2 424.5L418 155" style="stroke:#536377;stroke-width:1.1;fill:none"/><circle cx="424.2" cy="424.5" r="3.5" fill="#a94732"/><g class="icon" transform="translate(418 155) scale(0.66)">'''+ns['ICONS']['food']+'''</g><rect class="hit" x="435" y="132" width="235" height="75"/><text class="name" x="445" y="155" font-size="23">敘敘苑</text><text class="sub" x="445" y="176" font-size="13">30F・午餐現場候位</text><text class="sub" x="445" y="194" font-size="13" data-hours="true">週四10:30–16:00 午餐</text></a></svg>'''
 outlined=ET.fromstring(ns['outline_text'](fragment))
 root.append(outlined[0])
maps[0]['svg']=ET.tostring(root,encoding='unicode');maps[0]['note']=day['note']
(R/'assets/trip-maps.js').write_text('window.TRIP_MAPS = '+json.dumps(maps,ensure_ascii=False)+';\n',encoding='utf-8')
(R/'assets/day-1-map.svg').write_text(maps[0]['svg'],encoding='utf-8')
(R/'VERSION').write_text('v1.15\n',encoding='utf-8')
p=R/'CHANGELOG.md';s=p.read_text(encoding='utf-8');i=s.index('## ')
p.write_text(s[:i]+'## v1.15\n\n- 11/12午餐首選加入敘敘苑晴空街30F，不預約、現場候位超過30分鐘換店。\n- 晴空塔地圖補上午餐位置、午餐時段與Google Maps連結；行程提供官方菜單。\n- 利久牛舌改為晚餐備選，依午餐份量與孩子體力調整。\n\n'+s[i:],encoding='utf-8')
