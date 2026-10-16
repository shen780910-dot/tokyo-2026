"""Record confirmed Airporter payment without exposing private order details."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent.parent
def load(name):return json.loads((R/name).read_text(encoding='utf-8').split(' = ',1)[1].strip().removesuffix(';'))
def save(name,key,data): (R/name).write_text(key+' = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
d=load('assets/trip-data.js'); day=d['days'][0]
day['schedule'][0]['activity']='IT200 桃園 → 成田第2航廈'
row=day['schedule'][1]
row.update(time='出關後｜12:30前交件',activity='Airporter已預約付款・行李寄送飯店',detail='成田第2航廈國際線抵達層1F JALABC櫃檯交件，訂單截止12:30。已付¥5,225（約NT$1,045），訂單領取時間20:00，依實際配送通知取件。飯店代收已確認；行李件數／尺寸級距及訂單地址區名仍須核對，詳見Notion。推車及當日必需品隨身帶。')
day['schedule'][-1]['detail']=day['schedule'][-1]['detail'].replace('Airporter通常20:00後送達','Airporter訂單領取時間20:00')
day['note']='Airporter已預約付款，11/12成田T2抵達層1F JALABC，12:30前交件、20:00領取。配送實付¥5,225＋兩成人Access特急暫估¥2,400，去程約NT$1,525；加回程青鳥NT$5,780，合計約NT$7,305。不含晴空塔至飯店車資；青鳥預訂、行李規格及配送地址區名待核對。'
replacements={'booked-20261011-6':'確認11/12 Access特急經押上直通班次；Airporter交件截止12:30','airporter-booking':'保存已付款的Airporter訂單，12:30前至成田T2抵達層1F JALABC交件；確認延誤處理','airporter-receipt':'飯店代收已確認；核對Airporter地址區名與20:00取件安排','airporter-luggage':'核對訂單行李件數／尺寸級距；兩箱裝滿後各不超過160cm／30kg，推車隨身帶'}
for item in d['checklist']:item['text']=replacements.get(item['id'],item['text'])
save('assets/trip-data.js','window.TRIP',d)
m=load('assets/trip-maps.js');m[0]['note']=day['note']
(R/'assets/trip-maps.js').write_text('window.TRIP_MAPS = '+json.dumps(m,ensure_ascii=False)+';\n',encoding='utf-8')
(R/'VERSION').write_text('v1.14\n',encoding='utf-8')
p=R/'CHANGELOG.md';s=p.read_text(encoding='utf-8');pos=s.index('## ')
p.write_text(s[:pos]+'## v1.14\n\n- Airporter更新為已預約付款，實付¥5,225；訂單詳細資料保留於Notion。\n- 交件明確標為成田T2抵達層1F JALABC，11/12截止12:30，領取時間20:00。\n- 交通總預算更新約NT$7,305，同步行前核對清單及配送地址待確認事項。\n\n'+s[pos:],encoding='utf-8')
