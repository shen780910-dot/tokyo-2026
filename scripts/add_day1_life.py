"""Add LIFE after day-one dinner, preserving current itinerary and map panels."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

R=Path(__file__).resolve().parent.parent
data_path=R/'assets/trip-data.js'
data=json.loads(data_path.read_text(encoding='utf-8').split(' = ',1)[1].strip().removesuffix(';'))
day=data['days'][0]
day['schedule']=[row for row in day['schedule'] if 'LIFE' not in row['activity']]
index=next(i for i,row in enumerate(day['schedule']) if row['activity']=='電車回飯店')
day['schedule'].insert(index,{
 'time':'晚餐後｜預留20～30分鐘',
 'activity':'LIFE 超市｜Central Square 押上站前店',
 'detail':'晴空街晚餐後，前往晴空塔對面的 LIFE 採買飲料、水果與隔天早餐，再從押上站搭電車回飯店。地址：押上1-10-3，押上站B3出口旁；營業09:30～24:00，藥妝區至21:00。依孩子體力調整停留時間。',
 'links':[{'name':'LIFE 押上站前店｜官方資訊','url':'https://store.lifecorp.jp/detail/east621/'}]
})
day['note']='午餐暫定やよい軒；晴空塔以電車往返，利久牛舌晚餐後逛LIFE超市再回飯店；抵達日依孩子體力調整，不另排錦糸町採買。'
data_path.write_text('window.TRIP = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')

namespace={'__file__':str(R/'scripts/build_geo_maps.py')}
exec((R/'scripts/build_geo_maps.py').read_text(encoding='utf-8').split('output=[]')[0],namespace)
model=dict(namespace['maps'][0])
model['points']=[dict(p) for p in model['points'] if p['kind']!='stay']
model.update(title='晴空塔・晴空街購物',route=[0,1,2,3,5])
model['points'].append(namespace['point']('LIFE 超市',35.7101890480642,139.813749747037,
 label=(500,580),sub='押上站前店・B3出口旁',query='ライフ セントラルスクエア押上駅前店 押上1-10-3'))
namespace['HOURS']['LIFE 超市']='09:30–24:00'
model['display']={i:(p['label'][0]-30,p['label'][1]-5) for i,p in enumerate(model['points'])}
svg=namespace['make'](model,31)

maps_path=R/'assets/trip-maps.js'
maps=json.loads(maps_path.read_text(encoding='utf-8').split(' = ',1)[1].strip().removesuffix(';'))
root=ET.fromstring(maps[0]['svg'])
for old in list(root):
 if old.tag=='{http://www.w3.org/2000/svg}svg':root.remove(old)
panel=ET.fromstring(svg)
panel.set('x','0');panel.set('y','860');panel.set('width','720');panel.set('height','860')
root.append(panel)
maps[0]['svg']=ET.tostring(root,encoding='unicode')
maps[0]['note']=day['note']
maps_path.write_text('window.TRIP_MAPS = '+json.dumps(maps,ensure_ascii=False)+';\n',encoding='utf-8')
(R/'assets/day-1-map.svg').write_text(maps[0]['svg'],encoding='utf-8')
print('Added LIFE after dinner and as stop 5 on the Skytree map')
