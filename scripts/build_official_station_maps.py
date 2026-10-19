"""Official floor-plan bases with SVG pins and matching shop-name annotations.

GRANSTA/Daimaru publish JPEG maps; those originals are embedded without tracing
or inventing corridors. Gift Palette's official PDF is converted to vector SVG.
"""
from pathlib import Path
from html import escape
import base64,json,math,re,xml.etree.ElementTree as ET
import pymupdf
from station_map_translations import overlay as translate_map
R=Path(__file__).resolve().parent.parent
sources=R/'previews/official-floor-sources'
namespace={'__file__':str(R/'scripts/build_tokyo_station_guide.py')}
exec((R/'scripts/build_tokyo_station_guide.py').read_text(encoding='utf-8').split('# Regional diagram:')[0],namespace)
namespace['shops'][3]=(4,'TRIPLE DECKER LONDON',*namespace['shops'][3][2:])
namespace['shops'].append((11,'東京動漫街','B1 改札外・角色商品街','角色商店現場自由選','Tokyo Character Street'))
namespace['shops'].append((12,'emmi 大丸東京','大丸4F・10:00–20:00','預留45～60分鐘','emmi 大丸東京店'))
start,text,system,shop,finish=(namespace[n] for n in ['start','text','system','shop','finish'])
notion_pages={
 1:'3fc400d1c43e8130bdf7f5c1b010fc37',2:'3c8400d1c43e81a985a9c845bfa52374',
 3:'3c7400d1c43e81488678d4e80adca25a',4:'3fc400d1c43e816c9f57fe3a3ac985fa',
 5:'3fc400d1c43e8102b256e78387891620',6:'3fc400d1c43e8124a778d8226edc756b',
 7:'3fc400d1c43e814d9f05c5fc431d8ec0',8:'3fc400d1c43e8190842fd262f79cd702',
 10:'3c8400d1c43e815d9915c9c8631d6d0d',
 11:'3c8400d1c43e816584cad44baa840f92',
}
def data_url(path):
 if path.suffix=='.pdf':
  doc=pymupdf.open(path);page=doc[0];payload=page.get_svg_image().encode();mime='image/svg+xml';width,height=page.rect.width,page.rect.height
 else:
  payload=path.read_bytes();mime='image/png' if path.suffix=='.png' else 'image/jpeg';pix=pymupdf.Pixmap(path);width,height=pix.width,pix.height
 return 'data:'+mime+';base64,'+base64.b64encode(payload).decode(),width,height
specs=[
 dict(id='b1',label='JR B1',file='tokyo-station-b1.svg',title='JR B1・Ivorish MAISON',subtitle='先留在JR改札內；官方HERE指店家，不是你的位置',source='GRANSTA 官方店家定位圖',url='https://www.gransta.jp/mall/gransta_tokyo/ivorish_maison/',base='gransta-ivorish.jpg',crop=(0,0,1500,1500),pins=[(1,350,950,24,-36)],shops=[1],notes=['認「丸の内地下中央口」與「丸の内坂」找位置。','買完跟站內指標回1F，接著逛The Maple Mania。']),
 dict(id='1f',label='JR 1F',file='tokyo-station-1f.svg',title='JR 1F・The Maple Mania',subtitle='紅色2是店家；買完從八重洲北口出JR',source='GRANSTA 官方店家定位圖',url='https://www.gransta.jp/mall/gransta_tokyo/themaplemania/',base='gransta-maple.jpg',crop=(0,0,1500,1500),pins=[(2,540,335,32,-36)],shops=[2],notes=['右上「八重洲北口」才是本次出站方向。','不要進「北のりかえ口」等新幹線轉乘閘門。']),
 dict(id='gift',label='Gift 1F',file='tokyo-station-gift.svg',title='Gift Palette・官方櫃位圖',subtitle='1F改札外｜紅色6至9對照下方店名',source='東京站一番街 官方樓層圖（PDF轉SVG）',url='https://www.tokyoeki-1bangai.co.jp/assets/pdf/floorMap_giftpalette.pdf',base='gift.pdf',crop=(180,110,410,215),pins=[(9,273,258,-19,-37),(8,326,237,-18,-48),(7,335,238,26,-24),(6,399,248,15,24)],shops=[6,7,8,9],notes=['G32＝PISTA；G9＝布蕾塔；G8＝VANILLABEANS；G3＝Butter Butler。','H樓梯／電扶梯下B1，到「いちばんプラザ」前；推車找電梯。']),
 dict(id='daimaru1f',label='大丸1F',file='tokyo-station-daimaru-1f.svg',title='大丸東京・1F 食品區',subtitle='紅色4與5為本次採買；保留官方通道與電梯',source='大丸東京 官方1F樓層圖',url='https://www.daimaru.co.jp/tokyo/floor/1f.html',base='daimaru-1f.jpg',crop=(805,85,705,810),pins=[(4,925,620,-35,20),(5,1050,455,-27,-30)],shops=[4,5],notes=['圖上方是JR側，下方是八重洲側；不要套用其他圖的方向。','逛完在大丸館內下B1，找PRESS BUTTER SAND。']),
 dict(id='daimarub1',label='大丸B1',file='tokyo-station-daimaru-b1.svg',title='大丸東京・B1 食品區',subtitle='紅色3是PRESS；保留官方電扶梯與電梯位置',source='大丸東京 官方B1樓層圖',url='https://www.daimaru.co.jp/tokyo/floor/b1f.html',base='daimaru-b1.jpg',crop=(885,75,580,735),pins=[(3,969,380,-27,-30)],shops=[3],notes=['對照原圖「プレスバターサンド」就是PRESS BUTTER SAND。','買完回1F Gift Palette；大丸一般10:00開門。']),
 dict(id='okashi',label='零食B1',file='tokyo-station-okashi.svg',title='東京おかしランド・B1',subtitle='紅色10是Calbee＋；在八重洲地下中央口外',source='東京站一番街 官方零食區樓層圖（PDF轉SVG）',url='https://www.tokyoeki-1bangai.co.jp/assets/pdf/floorMap_okashi.pdf',base='okashi.pdf',crop=(160,80,520,250),pins=[(10,620,252,18,24)],shops=[10],notes=['Calbee＋對應官方G47，圖右側綠色區域。','從H下B1後，沿一番街通路找「東京おかしランド」。']),
 dict(id='overview',label='站區總覽',file='tokyo-station-overview.svg',title='東京站・1F 站區總覽',subtitle='保留官方JR閘門、大丸與Gift Palette的實際關係',source='東京站一番街 官方1F周邊圖',url='https://www.tokyoeki-1bangai.co.jp/tokyogiftpalette/',base='station-1f.png',crop=(0,0,1044,724),pins=[],shops=[],notes=['先在JR內買完兩間，再找「八重洲北口」。','大丸與Gift Palette都在改札外；往丸之內找北自由通路。']),
]
specs.append(dict(id='character',label='動漫B1',file='tokyo-station-character.svg',title='東京動漫街・B1 改札外',subtitle='10動漫街｜H下樓先逛這區，再往11零食區',source='東京站一番街 官方動漫街樓層圖（PDF轉SVG）',url='https://www.tokyoeki-1bangai.co.jp/assets/pdf/floorMap_chara.pdf',base='character.pdf',crop=(105,105,620,205),pins=[(11,466,228,0,30)],shops=[11],notes=['C7 Tomica・C6 JUMP・C12龍貓・C21吉伊卡哇。','寶可夢C34在1F，不在這張B1圖；可現場跳過。']))
specs.append(dict(id='daimaru4f',label='大丸4F',file='tokyo-station-daimaru-4f.svg',title='大丸東京・4F emmi',subtitle='6 emmi｜F電梯上樓，逛完回1F接7',source='大丸東京 官方4F樓層圖',url='https://www.daimaru.co.jp/tokyo/floor/4f.html',base='daimaru-4f.jpg',crop=(0,0,1514,1100),pins=[(12,987,430,28,-25)],shops=[12],notes=['F是八重洲側電梯；6是原圖「エミ」。','逛完搭F電梯回1F，往JR側離開大丸接7。']))
out=[]
route_styles={
 'b1':[('1→2','#b44732')],
 '1f':[('1→2','#b44732'),('2→八重洲北口→4','#62713c')],
 'daimaru1f':[('4→5','#536377'),('5→大丸B1→3','#94621c')],
 'daimarub1':[('5→大丸B1→3','#94621c')],
 'gift':[('6→7→8→9','#805276'),('9→H下樓→10','#26716b')],
 'okashi':[('9→H下樓→10','#26716b')],
 'overview':[],
}
wayfinding={
 'b1':dict(points=[(350,950),(320,930),(340,842),(550,842),(850,842),(860,862)],nodes=[('A',860,862,30,26),('E',1038,862,24,28)],steps=[
  '（1）Ivorish買完，沿「丸の内坂」往八重洲／銀の鈴方向走；不要穿出丸之內地下改札。',
  '走到銀の鈴區西側、靠SQUARE ZERO的A點，搭連通B1與1F的電扶梯上1F。不要搭往列車月台的樓梯。',
  '帶推車請走地圖E電梯上1F；不要搭標示「3・4番線」的月台專用電梯。',
  '切到「JR 1F」：從同樣的A點（或E點）接續，前往（2）The Maple Mania。']),
 '1f':dict(points=[(483,387),(483,365),(540,365),(540,335)],extra=[[(540,335),(615,335),(615,210),(879,205)]],nodes=[('A',483,387,-30,15),('E',643,404,30,18),('B',879,205,28,-25)],steps=[
  'A是從B1上來的電扶梯出口；上到1F後，往吹き抜けエリア的（2）The Maple Mania。',
  '推車從E電梯出來，沿站內通道往（2）走；A與E都在1F改札內。',
  '（2）買完往「八重洲北口」B點走，從一般JR改札出站；不要進旁邊「北のりかえ口」新幹線轉乘口。',
  '出站後往大丸東京食品區，切到「大丸1F」；下一段採買順序是（4）→（5）→（3）。']),
 'daimaru1f':dict(points=[(845,280),(865,280),(865,620),(925,620),(985,620),(985,455),(1050,455)],extra=[[(1050,455),(990,420),(990,375),(1155,375)]],nodes=[('C',1155,375,20,35)],steps=[
  '從JR八重洲北口出站後進大丸1F食品區，先（4）TRIPLE DECKER LONDON，再（5）N.Y.C.SAND。',
  '買完往和洋菓子區中央C電扶梯，確認「下り」及B1方向，下一層就是大丸B1。',
  '推車改用食品區八重洲側電梯（官方圖下方）；選B1。',
  '切到「大丸B1」：C是同一組館內電扶梯，接續前往（3）PRESS BUTTER SAND。']),
 'daimarub1':dict(points=[(1195,345),(1100,345),(1100,350),(1010,350),(969,380)],nodes=[('C',1195,345,28,-24)],steps=[
  '從1F的C電扶梯下B1後，往「プレスバターサンド」櫃位走，即（3）PRESS BUTTER SAND。',
  '買完回C電扶梯，找「上り」回1F；推車則原路回八重洲側電梯上1F。',
  '回到1F後往JR側離開大丸，找「東京ギフトパレット」；全程留在改札外，不用再進JR。',
  '切到「Gift 1F」，接續（6）到（9）；店家編號就是採買順序。']),
 'gift':dict(points=[(399,248),(400,225),(350,225),(350,238),(335,238),(326,238),(314,238),(314,235),(290,235),(290,258),(273,258)],extra=[[(273,258),(265,258),(265,243),(290,245)]],nodes=[('H',290,245,-24,-22)],steps=[
  '在1F改札外依序逛（6）PISTA G32→（7）BRULEE MERIZE G9→（8）VANILLABEANS G8→（9）Butter Butler G3。',
  '（9）買完，找星巴克G2旁的H階梯／電扶梯，下到B1「いちばんプラザ」附近。H是官方階梯代號。',
  '帶推車先找Gift Palette的電梯下B1，避免搬推車走H階梯；依現場無障礙指標繞行。',
  'B1沿「東京おかしランド／八重洲地下中央口」指標走到南通り，切到「零食B1」接續（10）。']),
 'okashi':dict(points=[(470,207),(520,207),(587,207),(648,207),(648,250),(620,252)],nodes=[('D',580,174,27,25)],steps=[
  '從Gift Palette下B1後，沿一番街通路往「東京おかしランド」，找到「南通り」。兩張局部圖之間依現場指標銜接。',
  '到D階梯附近、八重洲地下中央改札外側，沿南通り走到綠色零食區；不用進JR改札。',
  '（10）Calbee＋是G47，位在零食區右側；G44～G46可依現場狀況一起逛。',
  'D是附近的官方階梯地標，不是H的同一組樓梯；後續依行程往KITTE／丸之內方向走。']),
 'overview':dict(points=[],nodes=[],steps=['本次樓層順序：JR B1→JR 1F→大丸1F→大丸B1→Gift 1F→零食B1。','A＝JR B1／1F電扶梯；E＝同區電梯；B＝八重洲北口。','C＝大丸食品區中央電扶梯；H＝Gift Palette旁下B1的官方階梯代號。','彩色虛線是依官方圖判讀的步行方向；遇單向電扶梯、管制或施工，依現場標示調整。']),
}
# Numbers follow the walk, rather than the historical order of shop records.
renumber={3:5,4:3,5:4,10:11,11:10}
namespace['shops']=sorted([(renumber.get(n,n),*row) for n,*row in namespace['shops']])
notion_pages={renumber.get(n,n):page for n,page in notion_pages.items()}
for floor,route in wayfinding.items():
 route['steps']=[re.sub(r'（(3|4|5|10)）',lambda m:f'（{renumber[int(m[1])]}）',step).replace('採買順序為4→5→3→6','採買順序為3→4→5→6') for step in route['steps']]
for floor,styles in route_styles.items():
 route_styles[floor]=[(re.sub(r'(?<!\d)[345](?!\d)',lambda m:str(renumber[int(m[0])]),label),color) for label,color in styles]
wayfinding['daimarub1']['extra']=[[(969,380),(969,410),(1010,410),(1010,730),(1078,778)]]
wayfinding['daimarub1']['nodes'].append(('F',1078,778,28,-22))
wayfinding['daimarub1']['steps'][1]='（5）買完往圖下方F「八重洲側エレベーター」，搭館內電梯上4F，逛emmi（預留45～60分鐘）。'
wayfinding['daimarub1']['steps'][2]='emmi逛完搭館內電梯回1F，往JR側離開大丸，再找Gift Palette；全程在改札外。'
route_styles['daimarub1'].append(('5→F電梯4F emmi→1F→6','#7a634b'))
wayfinding['gift']['steps'][-1]='H下到B1後先切「動漫B1」，逛（10）東京動漫街；逛完再沿通路往（11）零食區。'
wayfinding['character']=dict(points=[(400,223),(425,223),(425,208),(466,208),(466,228)],extra=[[(466,228),(466,208),(400,208),(280,208),(140,208)]],nodes=[('H',400,223,-20,-25)],steps=[
 '從Gift Palette的H階梯／電扶梯下到B1，到「いちばんプラザ」附近，即（10）動漫街；不用進JR改札。',
 'Tomica／Plarail C7為主，預留45～60分鐘看原創款、展示及現場活動；JUMP SHOP C6、龍貓C12、吉伊卡哇C21有時間再自由逛。一般款記下型號，到有樂町BC比價。',
 '寶可夢商店C34在1F，並非B1；已安排晴空塔及澀谷寶可夢，可視時間跳過這間。熱門店的整理券或入場規則以當日公告為準。',
 '逛完沿「北通り」往銀の鈴／八重洲地下中央口方向，接「南通り」前往（11）Calbee＋。切到「零食B1」接續；全程在改札外。'])
route_styles['character']=[('9→H下樓→10','#26716b'),('10→11','#7a634b')]
route_styles['okashi']=[('10→11','#7a634b')]
wayfinding['okashi']['steps'][0]='從（10）動漫街沿北通り往銀の鈴方向，經八重洲地下中央改札外通路接南通り，找「東京おかしランド」。'
wayfinding['overview']['steps'][0]='樓層順序：JR B1→JR 1F→大丸1F→大丸B1→Gift 1F→動漫B1→零食B1。'
walks={
 'b1':'1 Ivorish → A上1F → 下一張接2（推車走E）',
 '1f':'A／E上樓 → 2 Maple Mania → B出站 → 下一張接3',
 'daimaru1f':'JR側入口 → 3 TRIPLE DECKER → 4 N.Y.C.SAND → C下B1',
 'daimarub1':'C下樓 → 5 PRESS → F電梯上4F emmi → 回1F接6',
 'gift':'6 PISTA → 7 BRULEE → 8 VANILLABEANS → 9 Butter Butler → H下B1逛10動漫街',
 'character':'H下樓 → 10動漫街（自由逛）→ 沿北通り接11零食區',
 'okashi':'從10動漫街過來 → 南通り → 11 Calbee＋ → 午餐',
 'overview':'1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10動漫街 → 11零食區',
}
def with_emmi(n):return 6 if n==12 else n+1 if n>=6 else n
def shifted_refs(value):return re.sub(r'（(6|7|8|9|10|11)）',lambda m:f'（{int(m[1])+1}）',value)
namespace['shops']=sorted([(with_emmi(n),*row) for n,*row in namespace['shops']])
notion_pages={with_emmi(n):page for n,page in notion_pages.items()}
for route in wayfinding.values():route['steps']=[shifted_refs(step) for step in route['steps']]
for floor,styles in route_styles.items():route_styles[floor]=[(re.sub(r'(?<!\d)(6|7|8|9|10|11)(?!\d)',lambda m:str(int(m[1])+1),label),color) for label,color in styles]
route_styles['daimarub1'][-1]=('5→F上4F→6','#7a634b')
wayfinding['daimarub1']['steps'][1]='（5）買完往F八重洲側電梯上4F，切到「大丸4F」接續（6）emmi。'
wayfinding['daimarub1']['steps'][2]='emmi正式列為第6站；逛完回1F，再接第7站Gift Palette，不跳過emmi。'
wayfinding['daimaru4f']=dict(points=[(1095,730),(1070,680),(1070,530),(987,530),(987,430)],extra=[[(987,430),(1000,530),(1055,530),(1055,680),(1095,730)]],nodes=[('F',1095,730,28,25)],steps=[
 '從大丸B1的F八重洲側電梯上4F；本圖F就是同一組電梯的4F出口。',
 '沿通道往原圖標示「エミ」的櫃位，即（6）emmi；營業10:00～20:00，預留45～60分鐘。',
 '逛完原路回F電梯，搭回1F。往JR側離開大丸，找東京ギフトパレット；不用進JR改札。',
 '點「下一段：Gift 1F」，從（7）PISTA接續逛到（10）Butter Butler。'])
route_styles['daimaru4f']=[('5→F上4F→6','#7a634b'),('6→回1F→7','#62713c')]
wayfinding['character']['points']=[];wayfinding['character']['extra']=[];wayfinding['character']['nodes']=[];route_styles['character']=[]
wayfinding['character']['steps'][2]='繁中店名透過細引線直接連到店家圓點，位置依最新官方櫃位；完整原始PDF仍可從下方底圖來源開啟。寶可夢C34在1F，並未誤標在B1。'
walks.update(daimarub1='C下樓 → 5 PRESS → F電梯上4F，下一張接6 emmi',daimaru4f='F上4F → 6 emmi → F回1F → 下一張接7',gift='7 PISTA → 8 BRULEE → 9 VANILLABEANS → 10 Butter Butler → H下B1',character='H下樓 → 11動漫街（原圖）→ 沿北通り接12零食區',okashi='從11動漫街過來 → 南通り → 12 Calbee＋ → 午餐',overview='1→2→3→4→5→6 emmi→7→8→9→10→11動漫街→12零食區')
wayfinding['overview']['steps'][0]='依序：JR B1→JR 1F→大丸1F→大丸B1→大丸4F emmi→Gift 1F→動漫B1→零食B1。'
specs=sorted(specs,key=lambda s:['b1','1f','daimaru1f','daimarub1','daimaru4f','gift','character','okashi','overview'].index(s['id']))
def map_navigation(spec,height):
 parts=namespace['parts'];index=specs.index(spec);site='https://shen780910-dot.github.io/tokyo-2026/'
 parts.append('<g class="map-floor-navigation" role="navigation" aria-label="樓層地圖切換">')
 for delta,x,label in [(-1,100,'← 前一張'),(1,620,'後一張 →')]:
  target=index+delta
  if 0<=target<len(specs):
   floor=specs[target]
   parts.append(f'<a class="map-floor-switch" data-floor="{floor["id"]}" href="{site}?floor={floor["id"]}#day-2" aria-label="{label}：{floor["label"]}"><rect x="{x-62}" y="{height-80}" width="124" height="56" fill="transparent"/>')
   system(label,x,height-44,18,'#536377','middle');parts.append('</a>')
  else:system(label,x,height-44,18,'#a5aaa5','middle')
 parts.append(f'<a class="map-full-floor" href="{site}assets/{spec["file"]}" target="_blank" rel="noopener noreferrer"><rect x="230" y="{height-80}" width="260" height="56" fill="transparent"/>')
 system('開啟完整樓層圖 ↗',360,height-44,18,'#536377','middle');parts.append('</a></g>')

def character_callouts(spec):
 """Keep official floor geometry, label shops in the surrounding whitespace."""
 uri,source_w,source_h=data_url(sources/'character.pdf')
 start(spec['title'],'圓點對應店家・圖外店名可開啟Google Maps',940)
 parts=namespace['parts'];cx,cy,cw,ch=0,80,841.89,245;scale=650/cw;map_y=280
 parts.append(f'<svg class="official-plan" x="35" y="{map_y}" width="650" height="{ch*scale}" viewBox="{cx} {cy} {cw} {ch}"><image href="{uri}" width="{source_w}" height="{source_h}"/>')
 translate_map(parts,system,spec['id'],source_w);parts.append('</svg>')
 # Official C-codes identify shops; itinerary stop 11 denotes the whole area.
 labels=[
  ('C6',['JUMP SHOP'],335,228,250,225,'JUMP SHOP 東京駅店'),
  ('C31',['拉拉熊／角落生物'],552,174,450,164,'リラックマストア すみっコぐらしshop 東京駅店'),
  ('C21',['吉伊卡哇'],554,228,620,225,'ちいかわらんど TOKYO Station'),
  ('C3',['蠟筆小新'],210,244,100,620,'クレヨンしんちゃん アクションデパート東京駅店'),
  ('C7',['Tomica／Plarail'],335,263,235,535,'トミカ プラレールショップ 東京店'),
  ('C10',['史努比'],387,274,355,620,'スヌーピータウンミニ 東京駅店'),
  ('C12',['橡子共和國'],427,274,435,535,'どんぐり共和国 東京駅店'),
  ('C17',['朝日電視台'],550,274,620,620,'テレアサショップ 東京駅店'),
 ]
 from urllib.parse import quote
 # Leaders are drawn first so they cannot cover another shop's name.
 for code,names,x,y,lx,ly,query in labels:
  px,py=35+x*scale,map_y+(y-cy)*scale
  elbow=ly+27 if ly<map_y else ly-32
  d=f'M{px:.2f} {py:.2f}V{elbow}H{lx}'
  if code in ['C3','C17']:d=f'M{px:.2f} {py:.2f}V480H{lx}V{elbow}'
  elif code=='C31':d=f'M{px:.2f} {py:.2f}H440V{elbow}H{lx}'
  parts.append(f'<path class="character-leader" d="{d}" fill="none" stroke="#fff" stroke-width="3.6"/><path d="{d}" fill="none" stroke="#ae4666" stroke-width="1.5"/>')
 for code,names,x,y,lx,ly,query in labels:
  px,py=35+x*scale,map_y+(y-cy)*scale
  href='https://www.google.com/maps/search/?api=1&query='+quote(query)
  parts.append(f'<a class="character-callout" data-code="{code}" href="{escape(href,quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="{escape(names[0])}：Google Maps"><title>{escape(names[0])}｜官方{code}</title><circle cx="{px:.2f}" cy="{py:.2f}" r="5" fill="#bd426a" stroke="#fff" stroke-width="1.6"/><rect x="{lx-98}" y="{ly-26}" width="196" height="54" fill="transparent"/><g stroke="#eeeade" stroke-width="3" stroke-linejoin="round" paint-order="stroke fill">')
  for i,name in enumerate(names):text(name,lx,ly+i*27,24,False,'#9d3656','middle')
  parts.append('</g>');system(code,lx,ly+23,16,'#536377','middle');parts.append('</a>')
 text('Tomica／Plarail先逛；其他店現場自由選。',43,690,19,True,'#536377')
 text('寶可夢C34在1F；櫃位以最新版官方圖為準。',43,720,18,True,'#536377')
 shop(11,65,790,26,info='B1改札外・圓點與繁中店名直接對照')
 parts.append('<a class="shop-detail-link" data-kind="notion" data-shop="11" href="https://app.notion.com/p/3c8400d1c43e816584cad44baa840f92" target="_blank" rel="noopener noreferrer" aria-label="東京站・動漫街資料 Notion"><rect x="526" y="762" width="147" height="62" rx="6" fill="#eeeade" stroke="#536377" stroke-width="1.1"/>')
 system('Notion ↗',599,800,21,'#536377','middle');parts.append('</a>')
 namespace['parts'].append(f'<a class="map-source-link" href="{spec["url"]}" target="_blank" rel="noopener noreferrer"><rect x="526" y="830" width="147" height="44" fill="transparent"/>')
 text('底圖來源 ↗',599,854,17,True,'#536377','middle')
 namespace['parts'].append('</a>')
 map_navigation(spec,940)
 return finish()
for spec in specs:
 spec['shops']=[with_emmi(renumber.get(n,n)) for n in spec['shops']]
 spec['pins']=[(with_emmi(renumber.get(n,n)),*coords) for n,*coords in spec['pins']]
 if spec['id']=='character':spec.update(crop=(0,0,841.89,595.28),pins=[],subtitle='11動漫街｜完整官方原圖，保留全部店名對照')
 if spec['id']=='daimaru1f':spec['subtitle']='依序3→4→C下B1；圖下接下一段'
 elif spec['id']=='daimarub1':spec['subtitle']='C下樓→5→F電梯上4F emmi，再回1F接6'
 if spec['id']=='b1':spec['notes']=['（1）→丸の内坂→銀の鈴側A電扶梯，上1F。','推車走E電梯；切JR 1F，從同樣的A／E接續。']
 elif spec['id']=='1f':spec['notes']=['A／E上樓→（2）→B八重洲北口，才出JR。','出站後走大丸1F；不要進新幹線轉乘口。']
 elif spec['id']=='daimaru1f':spec['notes']=['（3）→（4）→C中央電扶梯，往下到B1。','推車走官方圖下方八重洲側電梯，選B1。']
 elif spec['id']=='daimarub1':spec['notes']=['C下樓→（5）→F電梯上4F逛emmi。','逛完搭電梯回1F，再離開大丸接（6）。']
 elif spec['id']=='gift':spec['notes']=['（6）G32→（7）G9→（8）G8→（9）G3。','H在星巴克G2旁，下B1先逛（10）動漫街。']
 elif spec['id']=='okashi':spec['subtitle']='11 Calbee＋｜從10動漫街過來，全程改札外';spec['notes']=['從（10）動漫街往南通り，到（11）G47。','D是附近階梯地標；與Gift的H不同一組。']
 if spec['id']=='gift':spec['subtitle']='1F改札外｜7至10對照下方店名'
 if spec['id'] not in ['daimaru4f','character']:
  spec['notes']=[shifted_refs(note) for note in spec['notes']]
 if spec['id']=='daimarub1':spec['subtitle']='C下樓→5→F上4F，下一張接6 emmi';spec['notes']=['C下樓→（5）→F電梯上4F，接（6）emmi。','點下一段「大丸4F」，再回1F接（7）。']
 if spec['id']=='okashi':spec['subtitle']='12 Calbee＋｜從11動漫街過來，全程改札外'
 if spec['id']=='character':
  svg=character_callouts(spec);(R/'assets'/spec['file']).write_text(svg,encoding='utf-8')
  out.append({k:spec[k] for k in ['id','label','file','source','url']}|{'svg':svg,'shops':spec['shops'],'steps':wayfinding['character']['steps'],'walk':walks['character'],'routes':[]})
  continue
 uri,source_w,source_h=data_url(sources/spec['base']);cx,cy,cw,ch=spec['crop'];scale=650/cw;map_y=160;map_h=ch*scale;legend_y=map_y+map_h+56
 height=math.ceil(legend_y+len(spec['shops'])*91+140)
 start(spec['title'],spec['subtitle'],height)
 parts=namespace['parts']
 parts.append(f'<svg class="official-plan" x="35" y="{map_y}" width="650" height="{map_h}" viewBox="{cx} {cy} {cw} {ch}" overflow="hidden"><image href="{uri}" width="{source_w}" height="{source_h}"/>')
 translate_map(parts,system,spec['id'],source_w);parts.append('</svg>')
 route=wayfinding[spec['id']]
 route_points=[point for segment in [route['points'],*route.get('extra',[])] for point in segment]
 for number,x,y,*_ in spec['pins']:
  assert any(math.hypot(x-px,y-py)<=2 for px,py in route_points),f'Shop {number} is disconnected from walking route'
 def xy(x,y):return 35+(x-cx)*scale,map_y+(y-cy)*scale
 for segment,points in enumerate([route['points'],*route.get('extra',[])]):
  if not points:continue
  label,color=route_styles[spec['id']][segment]
  marker_id=f'walking-arrow-{segment}'
  parts.append(f'<defs><marker id="{marker_id}" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M1 1L8 5L1 9" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>')
  d='M'+' L'.join(f'{px:.2f} {py:.2f}' for px,py in [xy(x,y) for x,y in points])
  parts.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/><path class="walking-route" aria-label="{escape(label)}" d="{d}" fill="none" stroke="{color}" stroke-width="4" stroke-dasharray="10 7" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#{marker_id})"/>')
 for letter,x,y,dx,dy in route['nodes']:
  px,py=xy(x,y);bx,by=px+dx,py+dy
  if spec['id']=='b1' and letter=='E':bx,by=px+24,py-30
  parts.append(f'<g class="floor-connection" data-connection="{letter}"><title>{letter}：對照下方逐段路線</title><path d="M{px} {py}L{bx} {by}" stroke="#536377" stroke-width="1.5"/><circle cx="{px}" cy="{py}" r="11" fill="none" stroke="#536377" stroke-width="2"/><rect x="{bx-13}" y="{by-13}" width="26" height="26" rx="4" fill="#536377" stroke="#fff" stroke-width="1.5"/>')
  system(letter,bx,by+7,20,'#fff','middle');parts.append('</g>')
 for number,x,y,dx,dy in spec['pins']:
  px,py=35+(x-cx)*scale,map_y+(y-cy)*scale;bx,by=px+dx,py+dy
  parts.append(f'<g class="official-shop-pin" data-shop="{number}"><path d="M{bx} {by}L{px} {py}" stroke="#a94732" stroke-width="1.7" fill="none"/><circle cx="{px}" cy="{py}" r="4" fill="#a94732" stroke="#fff" stroke-width="1.2"/><circle cx="{bx}" cy="{by}" r="14" fill="#a94732" stroke="#fff" stroke-width="2"/>')
  system(str(number),bx,by+6,20,'#fff','middle');parts.append('</g>')
 labels={1:'法式吐司',2:'楓糖伴手禮',3:'三層夾心餅',4:'紐約焦糖餅',5:'奶油夾心餅',6:'女裝',7:'開心果餅乾',8:'布蕾奶油塔',9:'巧克力夾心餅',10:'奶油費南雪',12:'現炸薯條'}
 for i,n in enumerate(spec['shops']):
  info=labels.get(n,'')+'・'+namespace['shops'][n-1][2].replace('吹拔區','挑高空間旁')
  if spec['id']=='gift':info={7:'官方 G32・開心果餅乾',8:'官方 G9・布蕾奶油塔',9:'官方 G8・巧克力夾心餅',10:'官方 G3・奶油費南雪'}[n]
  shop(n,65,legend_y+i*91,26,info=info)
  link_y=legend_y+i*91
  if n in notion_pages:
   href='https://app.notion.com/p/'+notion_pages[n];label='Notion ↗';kind='notion'
  elif n==6:
   href='https://emmi.jp/Page/shoplist/detail/daimarutokyo.aspx';label='官方資訊 ↗';kind='official'
  else:
   href='https://www.tokyoeki-1bangai.co.jp/shop/detail/?cd=000196';label='官方資訊 ↗';kind='official'
  brand=escape(namespace['shops'][n-1][1],quote=True)
  parts.append(f'<a class="shop-detail-link" data-kind="{kind}" data-shop="{n}" href="{escape(href,quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="{brand} {label}"><title>{brand}｜{label}</title><rect x="526" y="{link_y-28}" width="147" height="62" rx="6" fill="#eeeade" stroke="#536377" stroke-width="1.1"/>')
  system(label,599,link_y+10,21,'#536377','middle');parts.append('</a>')
 y=legend_y+len(spec['shops'])*91+8
 for note in spec['notes']:
  # Two lines avoid reducing the text to an unreadable size on phones.
  chunks=[note] if len(note)<=35 else [note[:32],note[32:]]
  for chunk in chunks:text(chunk,43,y,18,True,'#536377');y+=28
 source_y=legend_y+max(0,len(spec['shops'])-1)*91+64
 parts.append(f'<a class="map-source-link" href="{spec["url"]}" target="_blank" rel="noopener noreferrer"><rect x="526" y="{source_y-24}" width="147" height="44" fill="transparent"/>')
 text('底圖來源 ↗',599,source_y,17,True,'#536377','middle');parts.append('</a>')
 map_navigation(spec,height)
 svg=finish();(R/'assets'/spec['file']).write_text(svg,encoding='utf-8')
 out.append({k:spec[k] for k in ['id','label','file','source','url']}|{'svg':svg,'shops':spec['shops'],'steps':route['steps'],'walk':walks[spec['id']],'routes':[{'label':label,'color':color} for label,color in route_styles[spec['id']]]})
(R/'assets/tokyo-station-guide.js').write_text('window.TOKYO_STATION_GUIDE = '+json.dumps(out,ensure_ascii=False)+';\n',encoding='utf-8')
print('Built nine official-base SVG guides including full Character Street and Daimaru 4F')
