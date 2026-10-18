"""Apply the confirmed Tokyo/Yurakucho and Ginza/Harajuku split.

Reads the current plan; preserves shop links and unrelated days. Map helpers are
loaded without executing historical generators' mutation sections.
"""
from pathlib import Path
import copy,json,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent.parent
def read(name):return json.loads((R/'assets'/name).read_text(encoding='utf-8').split(' = ',1)[1].strip().removesuffix(';'))
def write(name,prefix,data):(R/'assets'/name).write_text(prefix+' = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
d=read('trip-data.js');day2,day3=d['days'][1:3]
existing=day2['schedule']+day3['schedule']
def row(prefix,**changes):
 item=copy.deepcopy(next(x for x in existing if x['activity'].startswith(prefix)));item.update(changes);return item
hotel={'name':'住宿資訊・入住核對（Notion）','url':'https://app.notion.com/p/shen0910/a1d400d1c43e8384944e0151ccee1361'}
day2.update(title='東京站・emmi・有樂町',area='新御徒町 → 東京站・大丸 → KITTE → 有樂町',schedule=[
 row('飯店 → 東京站',time='09:00–09:30｜移動估算'),
 row('JR改札內',time='上午｜東京站區含emmi預留約4～4.5小時'),
 row('大丸東京',detail='八重洲北口出站後，先逛1F TRIPLE DECKER LONDON、N.Y.C.SAND，再下B1找PRESS BUTTER SAND。候選全部保留，排隊太久可跳過；接著上4F逛emmi，再回1F往Gift Palette。'),
 {'time':'大丸採買後｜必逛・預留45～60分鐘','activity':'emmi｜大丸東京店4F','detail':'從大丸B1搭館內電梯上4F，逛完再搭電梯回1F接Gift Palette。營業10:00～20:00；指定款式與尺寸依當日庫存。','links':[{'name':'emmi 大丸東京｜官方店舖資訊','url':'https://emmi.jp/Page/shoplist/detail/daimarutokyo.aspx'}]},
 row('PISTA・',time='上午～午餐前｜Gift Palette 1F',detail='都在JR改札外，四間現場選。G32＝PISTA、G9＝BRULEE MERIZE、G8＝VANILLABEANS、G3＝Butter Butler。冷藏甜點優先現吃或確認保冷；若孩子餓了，先吃午餐再繼續採買。'),
 row('東京動漫街',time='午餐前後｜Tomica／Plarail預留45～60分鐘',detail='Gift Palette旁H下B1，到いちばんプラザ附近。主逛Tomica／Plarail東京站專賣店C7，先看專賣店原創款與現場活動；一般款記下型號與價格，到有樂町BC再比價。JUMP C6、龍貓C12、吉伊卡哇C21列自由候選。寶可夢C34在1F，可跳過；活動及整理券依當日公告。逛完沿北通り接南通り，往（12）Calbee＋。'),
 row('東京おかしランド'),
 row('東京站周邊午餐',time='中午｜可提前插入',detail='以孩子食慾為優先，尚未採買完也可先用餐，午餐後再補逛東京站；不必等全部店家逛完。'),
 row('GOOD DESIGN',time='午餐後｜預留20～30分鐘'),
 row('BicCamera 有樂町',time='下午｜預留60～90分鐘',detail='從KITTE步行往有樂町，直上4F玩具區，主買Tomica一般車款、Plarail列車、軌道與套組；比較東京站專賣店記下的型號與價格。特定款先查分店庫存或預留；營業10:00～22:00。',links=[{'name':'BicCamera 有樂町｜樓層與預留服務','url':'https://www.biccamera.com/bc/i/shop/shoplist/shop014.jsp'}]),
 row('GODIVA Bakery'),
 row('3COINS＋plus 西銀座店',time='傍晚｜視採買進度',detail='西銀座百貨2F，營業11:00～20:00；接在有樂町一起逛。博品館、MUJI與LOFT移到隔天，不再當天往銀座南端折返。'),
 row('札幌 DOMINICA',time='18:30～19:30｜暫定',detail='保留原定湯咖哩晚餐：京橋3-4-1 TM銀座大樓2F；從有樂町／西銀座步行前往。週五晚餐17:30～21:00、最後點餐20:30；孩子餐點先確認不辣口味，2F留意樓梯與推車。Gurgaon銀座仍為備案，兩間擇一。'),
 row('回飯店整理戰利品')])
day2['note']='東京站採買與大丸4F emmi → 午餐 → KITTE → 有樂町BC（Tomica／Plarail）→ GODIVA → 西銀座3COINS → DOMINICA晚餐（Gurgaon備案）。東京站限定款先看、一般款到BC比價；依孩子食慾提前休息。'
day3.update(title='銀座購物・原宿試鞋',area='新御徒町 → 新橋・銀座 → 明治神宮前・原宿',schedule=[
 {'time':'10:00–11:00｜含移動緩衝','activity':'飯店 → 新橋 → 博品館','detail':'步行至御徒町站，搭JR山手線或京濱東北線往新橋；出站後步行到博品館。以11:00開門開始逛銀座。'},
 row('博品館玩具公園',time='11:00–11:45｜主要購物點',detail='先從銀座南端逛博品館，再一路往北。營業11:00～20:00；以孩子喜歡的玩具及試玩為主，賽車體驗依當日現場資訊。Tomica／Plarail已在前一天安排兩間，可避免重複採買。'),
 row('Dover Street Market',time='11:45–12:15｜彈性候選',detail='從博品館往北到銀座小松西館，營業11:00～20:00。時間不足時縮短或跳過，優先保留MUJI、LOFT與下午試鞋。'),
 row('銀座木村家',time='中午順路｜預留10～15分鐘',detail='經過木村屋總本店銀座本店1F時買酒種紅豆麵包；營業10:00～20:00，口味與售完狀況依現場，可視午餐時間跳過。'),
 {'time':'12:30–13:15｜估算','activity':'銀座周邊午餐','detail':'安排坐下用餐與休息；候位太久改找附近可立即入座的餐廳，避免壓縮下午試鞋時間。'},
 row('SABON 銀座',time='午餐後｜彈性候選',detail='松屋通り店營業11:30～20:00；有明確品項再短暫停留，時間不足可跳過。'),
 row('MUJI 銀座',time='13:15–14:15｜主要購物點',detail='無印良品銀座，營業11:00～21:00。與LOFT接續安排；包含步行緩衝，依前面購物進度調整。'),
 row('銀座 LOFT',time='14:15–15:15｜主要購物點',detail='MUJI後逛銀座LOFT，週六營業11:00～21:00。15:15開始結帳，最晚15:30離開銀座往原宿，保留完整試鞋時間。'),
 {'time':'15:30–16:15｜含步行、轉乘估算','activity':'銀座 → 明治神宮前（原宿）','detail':'從銀座站搭銀座線往澀谷方向，在表參道轉千代田線往代代木上原方向，一站到明治神宮前。帶推車依現場電梯指標，移動預留45分鐘。'},
 {'time':'16:15–17:15｜主要購物點','activity':'HOKA 原宿｜試鞋','detail':'明治神宮前站出站後步行到HOKA，營業11:00～20:00。預留試穿、找尺寸與結帳；若候位較久，避免延誤後面的NB。'},
 {'time':'17:15–18:30｜主要購物點','activity':'New Balance 原宿｜試鞋','detail':'從HOKA步行前往，官方營業11:00～19:00。預留量腳、試穿與結帳；若HOKA超時，優先確保18:00前到NB。','links':[{'name':'New Balance 原宿｜官方店舖資訊','url':'https://stores.newbalance.jp/tokyo/shibuya/4-32-16-jingumae'}]},
 {'time':'18:30後','activity':'原宿晚餐 → 回飯店整理行李','detail':'用餐後從JR原宿站搭山手線往新宿、池袋方向回御徒町，再步行回飯店。3COINS原宿僅在需要補買且時間足夠時順逛，前一天已安排西銀座店。隔天07:30接送，晚上以休息與整理行李為主。','links':[hotel]},
 ])
day3['note']='銀座先南後北：博品館 → Dover Street Market（彈性）→ 木村家（順路）→ 午餐 → SABON（彈性）→ MUJI → LOFT。15:30離開銀座 → 原宿HOKA → NB。澀谷PARCO、Nintendo與澀谷寶可夢取消；emmi已改到前一天大丸4F。'
for item in d['checklist']:
 if item['id']=='shopping-tokyo-ginza':item['text']='11/13：東京站Tomica／Plarail限定商品、有樂町BC一般款；西銀座3COINS'
 if item['id']=='shopping-parco':item['text']='11/13：大丸東京4F emmi，預留45～60分鐘'
 if item['id']=='shopping-harajuku':item['text']='11/14：銀座LOFT、MUJI、博品館；15:30出發原宿HOKA與NB（19:00關門）'
write('trip-data.js','window.TRIP',d)
p=R/'index.html';s=p.read_text(encoding='utf-8').replace('澀谷・銀座','東京站・銀座・原宿').replace('週五東京站、西銀座3COINS與銀座LOFT、MUJI；週六澀谷PARCO、emmi與原宿購物。','週五東京站、大丸emmi與有樂町玩具採買；週六銀座LOFT、MUJI、博品館，再到原宿逛HOKA與NB。').replace('晴空塔、東京站與銀座、澀谷與原宿','晴空塔、東京站與有樂町、銀座與原宿').replace('11/13東京站與銀座；11/14澀谷與原宿','11/13東京站、emmi與有樂町；11/14銀座與原宿');p.write_text(s,encoding='utf-8')

ns={'__file__':str(R/'scripts/build_geo_maps.py')}
exec((R/'scripts/build_geo_maps.py').read_text(encoding='utf-8').split('output=[]')[0],ns)
polisher={'__file__':str(R/'scripts/polish_map_markers.py')}
exec((R/'scripts/polish_map_markers.py').read_text(encoding='utf-8').split("path = R / 'assets/trip-maps.js'")[0],polisher)
point=ns['point'];make=ns['make'];polish=polisher['polish'];ns['SUB_SIZE']=13
ns['HOURS'].update({'大丸東京・emmi':'4F emmi 10:00–20:00','Gurgaon 銀座':'晚餐17:00–22:00'})
tokyo=dict(title='東京站・有樂町採買地圖',date='11/13・Tomica／Plarail與emmi',source='ginza',bounds=(35.6708,139.7585,35.683,139.773),scale=200,
 points=[point('東京車站',35.681236,139.767125,'station',(450,170),'伴手禮・動漫街看下方分層圖','Tokyo Station'),point('大丸東京・emmi',35.6811,139.7691,label=(450,275),sub='食品1F／B1・emmi 4F',query='emmi 大丸東京店'),point('GOOD DESIGN',35.6798,139.7648,label=(100,350),sub='KITTE 3F',query='GOOD DESIGN STORE TOKYO by NOHARA KITTE'),point('BicCamera 有樂町',35.6755023,139.7630127,label=(100,465),sub='4F Tomica／Plarail',query='Bic Camera Yurakucho'),point('GODIVA Bakery',35.67465,139.7639,'food',(450,485),'東京交通會館1F','GODIVA Bakery ゴディパン 本店'),point('3COINS＋plus',35.67281,139.76235,label=(100,605),sub='西銀座2F',query='3COINS+plus 西銀座店'),point('札幌DOMINICA',35.6754976,139.7679071,'food',(450,365),'週五晚餐・TM銀座2F','札幌ドミニカ 銀座店'),point('Gurgaon 銀座',35.67452773,139.76735782,'food',(450,655),'晚餐備案・B1','グルガオン 銀座1-6-13')],route=[0,1,2,3,4,5,6],left_labels={2,3,5},extra=day2['note'])
ginza=dict(title='銀座・先南後北購物地圖',date='11/14・11:00開始／15:30出發原宿',source='ginza',bounds=(35.6655,139.757,35.6755,139.7698),scale=200,
 points=[point('新橋站',35.66622,139.75858,'station',(100,740),'JR御徒町搭車抵達','Shimbashi Station'),point('博品館TOY PARK',35.6678843,139.7609706,label=(100,650),sub='玩具・主要購物點',query='博品館TOY PARK 銀座本店'),point('Dover Street Market',35.67015,139.7636,label=(450,580),sub='彈性候選・銀座小松西館',query='DOVER STREET MARKET GINZA'),point('銀座木村家',35.67203,139.76482,'food',(450,485),'順路買紅豆麵包','木村屋總本店 銀座本店'),point('SABON 銀座',35.67163646,139.76667272,label=(450,390),sub='松屋通り店・彈性候選',query='SABON 銀座松屋通り店'),point('MUJI 銀座',35.6733818,139.7655211,label=(100,310),sub='主要購物點',query='MUJI Ginza'),point('銀座 LOFT',35.674097,139.7662311,label=(450,235),sub='15:15開始結帳',query='Ginza Loft'),point('銀座站C8',35.67375,139.76435,'station',(100,205),'銀座線往表參道轉千代田線','Ginza Station C8')],route=[0,1,2,3,4,5,6,7],left_labels={0,1,5,7},extra='15:30銀座站搭銀座線→表參道轉千代田線→明治神宮前；推車依現場電梯指標。')
ginza['points'][1]['label']=(100,615)
ginza['points'][6]['label']=(450,165)
ginza['left_labels']={1,5}
harajuku=dict(title='原宿・HOKA與NB試鞋地圖',date='11/14・16:15後／NB 19:00關門',source='harajuku',bounds=(35.6655,139.7005,35.672,139.7086),scale=100,
 points=[point('明治神宮前站',35.66887,139.70553,'station',(450,650),'銀座經表參道轉乘抵達','Meiji Jingumae Station'),point('HOKA 原宿',35.6688185,139.70525,label=(90,545),sub='16:15–17:15 試鞋',query='HOKA Harajuku'),point('New Balance 原宿',35.66994944,139.70684928,label=(450,300),sub='17:15–18:30 試鞋',query='New Balance Harajuku'),point('原宿站',35.67017,139.70269,'station',(90,230),'JR山手線回御徒町','Harajuku Station'),point('3COINS 原宿',35.6669017,139.7045081,label=(450,740),sub='有需要再補買・不列主路線',query='3COINS Harajuku')],route=[0,1,2,3],left_labels={1,3},extra='銀座購物後直接到原宿，不再安排澀谷PARCO。')
def render(m,index):
 m['display']={i:(p['label'][0]-30,p['label'][1]-5) for i,p in enumerate(m['points'])}
 return polish(make(m,index))
harajuku['points'][0]['label']=(450,535)
tokyo_svg=render(tokyo,52);ginza_svg=render(ginza,53);harajuku_svg=render(harajuku,54)
root=ET.fromstring(ginza_svg);inset=ET.fromstring(harajuku_svg);root.set('viewBox','0 0 720 1720');inset.set('x','0');inset.set('y','860');inset.set('width','720');inset.set('height','860');root.append(inset);day3_svg=ET.tostring(root,encoding='unicode')
maps=read('trip-maps.js')
for day,svg in [(2,tokyo_svg),(3,day3_svg)]:
 (R/'assets'/f'day-{day}-map.svg').write_text(svg,encoding='utf-8')
 maps[day-1].update(svg=svg,note=d['days'][day-1]['note'],links=[])
write('trip-maps.js','window.TRIP_MAPS',maps)
print('Updated days 2 and 3, overview, checklist and geographic maps; preserved days 1 and 4')
