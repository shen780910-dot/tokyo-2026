"""Traditional Chinese vector wayfinding, traced against the official plans.

Source-coordinate footprints and fixture locations are preserved. Small counters
outside the shopping list are grouped into labelled retail zones, not invented
as individually surveyed units. Original official plans remain linked.
"""
from html import escape
from urllib.parse import quote
import json,math

PAPER='#eeeade';WALK='#faf8f1';SHOP='#d8e3df';ALT='#e8dfce';INK='#26312e';MUTED='#536377'

def render_all(c):
 R=c['R'];n=c['namespace'];start,text,system,finish=(c[k] for k in ['start','text','system','finish'])
 specs={s['id']:s for s in c['specs']};out=c['out'];routes=c['wayfinding']
 # Entry on the official food-hall facade, rather than an arbitrary interior dot.
 routes['daimaru1f']['points']=[(870,100),(845,165),(845,620),(925,620),(985,620),(985,455),(1050,455)]
 routes['daimaru1f']['nodes'].append(('入口',870,100,-30,-20))
 routes['daimaru1f']['steps'][0]='八重洲北口出JR改札後就是大丸旁；循大丸食品區「正面入口」進1F，再依序逛（3）TRIPLE DECKER、（4）N.Y.C.SAND。圖上入口是建議進店起點，不代表改札就在櫃位內。'
 routes['1f']['steps'][-1]='B八重洲北口出站後，循大丸食品區「正面入口」進1F；下一張從入口接（3）→（4）→B1的（5）。'
 routes['daimarub1']['extra']=[[(969,380),(1040,380),(1040,555),(1200,555),(1200,735),(1078,778)]]

 class V:
  def __init__(self,item,crop,title=None,subtitle=None):
   self.item=item;self.spec=specs[item['id']];self.cx,self.cy,self.cw,self.ch=crop;self.scale=650/self.cw
   self.top=220;self.height=self.ch*self.scale;self.legend=self.top+self.height+70
   self.total=math.ceil(self.legend+len(item['shops'])*91+185)
   start(title or self.spec['title'],subtitle or '依官方配置重繪・繁中店名／入口／上下樓',self.total)
   self.p=n['parts'];self.p.append('<style>.chinese-plan .text-shape{stroke:none;fill:#26312e}.chinese-plan .text-shape.sub{fill:#536377}</style><g class="chinese-plan" data-language="zh-Hant" data-source="'+escape(self.spec['url'],quote=True)+'">')
   self.rect(self.cx,self.cy,self.cw,self.ch,'',WALK,False)
  def xy(self,x,y):return 35+(x-self.cx)*self.scale,self.top+(y-self.cy)*self.scale
  def poly(self,points,label='',fill=SHOP):
   pts=[self.xy(x,y) for x,y in points];self.p.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="{fill}" stroke="#b8c2ba" stroke-width="1.1"/>')
  def rect(self,x,y,w,h,label='',fill=SHOP,border=True,size=17):
   px,py=self.xy(x,y);self.p.append(f'<rect x="{px:.2f}" y="{py:.2f}" width="{w*self.scale:.2f}" height="{h*self.scale:.2f}" fill="{fill}" stroke="'+('#b8c2ba' if border else fill)+'" stroke-width="1"/>')
   if label:self.label(label,x+w/2,y+h/2,size,'middle',w*self.scale-10)
  def label(self,value,x,y,size=18,anchor='middle',maxwidth=None,color=INK):
   px,py=self.xy(x,y);lines=value.split('|')
   for i,line in enumerate(lines):
    length=sum((.55 if ord(ch)<128 else 1) for ch in line)
    actual=min(size,maxwidth/max(1,length)) if maxwidth else size
    text(line,px,py+(i-(len(lines)-1)/2)*(actual+4)+actual*.32,actual,True,color,anchor)
  def fixture(self,code,x,y,label,kind='lift'):
   px,py=self.xy(x,y);self.p.append(f'<g class="floor-connection" data-connection="{code}"><rect x="{px-15}" y="{py-15}" width="30" height="30" rx="4" fill="{MUTED}"/>')
   system(code,px,py+6,16,'#fff','middle');self.p.append('</g>')
   # Facility labels are in a legend, keeping the symbol's exact location clear.
  def segment(self,points,color,label):
   if not points:return
   d='M'+' L'.join(f'{x:.2f} {y:.2f}' for x,y in [self.xy(x,y) for x,y in points])
   key='zh-arrow-'+str(len(self.p));self.p.append(f'<defs><marker id="{key}" markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="{color}" stroke-width="1.6"/></marker></defs><path d="{d}" fill="none" stroke="#fff" stroke-width="7"/><path class="walking-route" aria-label="{escape(label)}" d="{d}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="9 6" stroke-linejoin="round" marker-end="url(#{key})"/>')
  def pin(self,num,x,y,dx=0,dy=-28):
   px,py=self.xy(x,y);bx,by=px+dx,py+dy
   self.p.append(f'<g class="official-shop-pin" data-shop="{num}"><path d="M{px} {py}L{bx} {by}" stroke="#a94732" stroke-width="1.2"/><circle cx="{px}" cy="{py}" r="4" fill="#a94732" stroke="#fff"/><circle cx="{bx}" cy="{by}" r="12" fill="#a94732" stroke="#fff"/></g>');system(str(num),bx,by+5,16,'#fff','middle')
  def end(self,facility_note='字母為上下樓點；紅色數字為採買順序。'):
   self.p.append('</g>')
   for i,num in enumerate(self.item['shops']):
    y=self.legend+i*91;c['shop'](num,65,y,26,info=n['shops'][num-1][2])
    if num in c['notion_pages']:href='https://app.notion.com/p/'+c['notion_pages'][num];kind='notion';label='Notion ↗'
    else:href='https://emmi.jp/Page/shoplist/detail/daimarutokyo.aspx' if num==6 else 'https://www.tokyoeki-1bangai.co.jp/shop/detail/?cd=000196';kind='official';label='官方資訊 ↗'
    self.p.append(f'<a class="shop-detail-link" data-kind="{kind}" data-shop="{num}" href="{href}" target="_blank" rel="noopener noreferrer"><rect x="526" y="{y-28}" width="147" height="62" rx="6" fill="{PAPER}" stroke="{MUTED}"/>');system(label,599,y+10,21,MUTED,'middle');self.p.append('</a>')
   y=self.legend+len(self.item['shops'])*91+8
   for line in [facility_note,'依官方配置重繪；小櫃位合併為區域，非精密測量。','原始官方圖可由網頁下方「底圖來源」開啟。']:
    text(line,43,y,17,True,MUTED);y+=29
   svg=finish();self.item['svg']=svg;self.item['steps']=routes[self.item['id']]['steps'];self.item['source']='繁中重繪｜'+self.spec['source']
   (R/'assets'/self.spec['file']).write_text(svg,encoding='utf-8')

 def overlay(v):
  key=v.item['id'];r=routes[key]
  for i,points in enumerate([r['points'],*r.get('extra',[])]):
   if points:v.segment(points,*reversed(c['route_styles'][key][i]))
  for code,x,y,*_ in r['nodes']:
   if code!='入口':v.fixture(code,x,y,'')
  for num,x,y,dx,dy in v.spec['pins']:v.pin(num,x,y,-26,-25) if num==3 else v.pin(num,x,y,dx,dy)

 for item in out:
  key=item['id']
  if key=='daimaru1f':item['walk']='八重洲北口出改札 → 食品區正面入口 → 3 → 4 → C下B1'
  if key in ['daimaru1f','daimarub1','daimaru4f']:
   is1=key=='daimaru1f';isb=key=='daimarub1'
   v=V(item,(675,45,840,850 if is1 else 1030 if not isb else 780),subtitle='JR側在上・八重洲側在下・沿採買編號走')
   if is1:
    v.poly([(820,110),(1480,110),(1480,870),(820,870)],'',WALK)
    v.label('JR東京站側',1110,65,21)
    v.label('食品區正面入口',880,115,18)
    v.label('JR側連通通道',735,500,17)
    v.label('八重洲側',1130,900,20)
    for box in [(915,120,395,68,'洋菓子・烘焙'),(1385,120,90,185,'年輪家|奶油餅乾'),(855,235,115,75,'Mont Blanc|Gallet'),(990,235,185,75,'TOKYO TULIP|甜點櫃位'),(1190,235,185,75,'麻布花林糖'),(855,340,115,80,'期間限定|甜點展區'),(1030,440,100,62,'N.Y.C.SAND'),(1140,440,200,62,'巧克力・洋菓子'),(855,465,115,72,'餅乾・蛋捲'),(1030,520,310,68,'東京香蕉・蛋糕'),(855,555,115,60,'銀座甜點櫃'),(855,615,115,55,'TRIPLE|DECKER'),(990,615,160,55,'日式和菓子'),(1170,615,200,55,'東京伴手禮'),(1030,690,340,75,'奶油夾心・和菓子'),(1385,440,90,325,'虎屋|豐島屋|和菓子')]:v.rect(*box)
    v.rect(1030,325,290,95,'',ALT);v.label('中央電扶梯',1210,415,17)
    v.fixture('F',1010,800,'');v.label('F 八重洲側電梯',1185,805,18)
    v.segment([(870,70),(870,110)],'#62713c','八重洲北口出站後往食品正面入口')
    v.label('← 八重洲北口出改札後，循大丸食品入口',1080,180,16)
    overlay(v);v.end('C＝中央電扶梯下B1；F＝八重洲側館內電梯。')
   elif isb:
    v.rect(890,65,565,745,'',WALK)
    for box in [(990,125,240,86,'紅酒・洋酒'),(925,255,95,60,'麵包'),(1080,255,245,58,'紅酒・起司'),(925,355,95,150,'PRESS|BUTTER|SAND'),(1090,420,255,45,'食品雜貨'),(1090,500,150,52,'明治屋'),(925,565,105,55,'新鮮蔬果'),(1070,565,120,55,'醃漬食品'),(1210,565,90,55,'魚板'),(1310,555,130,100,'肉品・火腿'),(925,660,250,55,'蔬果・果汁'),(1210,660,230,90,'鮮魚'),(1340,245,90,265,'烘焙|銀座木村家')]:v.rect(*box)
    v.rect(1090,320,235,80,'',ALT);v.label('中央電扶梯',1210,385,17)
    v.label('JR側／北自由通道',1150,90,18);v.label('八重洲側',1220,820,20)
    v.label('便當・熟食區',765,350,18);v.label('和洋甜點區',765,540,18)
    overlay(v);v.end('C＝從1F下樓；F＝上4F逛（6）emmi。')
   else:
    for box in [(685,55,770,980,''),(685,55,770,980,'')][:1]:v.rect(*box,fill=WALK)
    for box in [(685,70,180,90,'精品女裝'),(870,70,180,90,'時尚服務'),(1055,70,200,90,'活動區'),(1260,70,180,90,'ROPE'),(685,220,160,130,'休閒女裝'),(915,210,130,285,'emmi'),(1100,210,220,100,'SNIDEL'),(1100,380,220,130,'EPOCA|女裝'),(1340,210,100,300,'女裝專櫃'),(685,590,100,170,'女裝'),(835,550,210,210,'女性內著'),(1100,550,340,110,'女裝・選品'),(725,870,300,65,'咖啡・休息')]:v.rect(*box)
    v.rect(1100,320,220,45,'中央電扶梯',ALT);v.label('JR側',1100,30,22);v.label('八重洲側',1190,1010,20)
    overlay(v);v.label('F 八重洲側電梯',1235,785,18);v.end('F＝與B1相同電梯；逛完回1F接（7）PISTA。')
  elif key in ['b1','1f']:
   b1=key=='b1';v=V(item,(120,120,1300,1180) if b1 else (270,50,760,1250),subtitle='改札內採買・先不要出站・字母接下一層')
   if b1:
    v.poly([(250,790),(460,335),(840,335),(840,355),(1000,355),(1000,550),(995,805),(1080,780),(1080,750),(1310,750),(1310,790),(1380,790),(1380,955),(940,955),(940,1275),(875,1275),(875,945),(720,945),(720,860),(520,860),(440,1100),(205,1160)],'',WALK)
    v.poly([(170,850),(285,790),(435,825),(520,860),(440,1100),(205,1160)],'',SHOP)
    v.rect(690,420,345,405,'中央廣場|便當・熟食',ALT)
    v.poly([(990,800),(1080,780),(1080,750),(1305,750),(1305,790),(1380,790),(1380,955),(990,955)],'',SHOP)
    v.label('銀之鈴甜點區',1180,865,22);v.label('丸之內地下購物區',390,1050,20)
    v.label('丸之內坡道',540,795,19);v.label('丸之內地下中央口',265,740,18)
    v.label('八重洲地下中央口',1220,1030,20);v.label('丸之內地下北口',440,450,18)
    v.label('地下北口',910,330,20);v.label('SQUARE ZERO',840,730,19)
    v.label('月台電梯不可當上1F電梯',820,560,17)
   else:
    v.poly([(345,95),(880,95),(880,225),(700,225),(680,355),(855,450),(900,630),(715,650),(715,950),(1010,985),(1010,1020),(920,1020),(920,1100),(860,1100),(860,1255),(600,1255),(600,960),(350,990),(315,915),(315,325)],'',WALK)
    v.rect(350,100,470,95,'北通道・餐飲區',SHOP)
    v.rect(350,225,260,120,'吹拔區・伴手禮',ALT)
    v.rect(350,380,280,115,'中央通道購物區',SHOP)
    v.rect(350,620,260,310,'站內月台連通區',ALT)
    v.poly([(890,1010),(960,1050),(950,1250),(820,1250),(820,1130)],'',SHOP)
    v.label('北自由通道（改札外）',570,65,18)
    v.label('丸之內北口',340,205,18);v.label('八重洲北口',870,175,20)
    v.label('中央通道',520,550,22);v.label('丸之內中央口',365,585,18)
    v.label('八重洲中央口',830,620,18);v.label('新幹線北轉乘口',810,325,17)
    v.label('不是本次出站口',810,355,16,color='#a94732')
    v.label('京葉通道商店區',800,1190,18)
   overlay(v);v.end('A＝電扶梯；E＝電梯；B＝八重洲北口出JR。')
  elif key=='gift':
   v=V(item,(185,100,420,230),subtitle='1F改札外・依7→8→9→10採買，再從H下B1')
   v.rect(265,170,75,90,'',SHOP);v.rect(370,155,110,105,'',SHOP)
   for box in [(267,171,70,34,'便利熟食'),(267,211,70,18,'星巴克'),(267,246,20,20,'G3'),(294,236,17,31,'G4'),(318,236,20,13,'G8'),(335,235,15,14,'G9'),(370,155,55,35,'東京香蕉'),(426,155,54,35,'甜點櫃'),(370,195,38,32,'洋菓子'),(415,195,65,32,'伴手禮'),(370,236,30,16,'G31'),(395,244,30,18,'G32'),(429,244,48,18,'烘焙')]:v.rect(*box,size=12)
   v.rect(490,126,65,106,'1F角色店|寶可夢等',ALT,size=15)
   v.label('大丸東京1F',455,300,18);v.label('八重洲北口',230,195,18)
   v.label('往北自由通道',415,125,17)
   overlay(v);v.end('G是官方櫃位碼；H＝下B1動漫街的階梯／電扶梯。')
  elif key=='okashi':
   v=V(item,(160,80,520,250),subtitle='B1改札外・從（11）動漫街接過來，不進JR')
   v.rect(180,164,260,32,'餐飲與其他店家',ALT)
   v.rect(180,218,210,54,'便當・伴手禮櫃位',ALT)
   v.rect(548,216,22,32,'44',SHOP,size=14);v.rect(572,216,23,32,'45',SHOP,size=14);v.rect(598,216,25,32,'46',SHOP,size=14)
   v.poly([(625,216),(642,216),(642,272),(548,272),(548,250),(625,250)],'',SHOP)
   v.label('南通道',425,207,22);v.label('銀之鈴廣場（JR內）',555,105,18)
   v.label('八重洲地下中央口',580,140,17);v.label('往八重洲地下街',450,310,18)
   overlay(v);v.end('G44奶油夾心・G45杏仁・G46森林點心・G47 Calbee＋。')
  elif key=='character':
   # Preserve the accepted callout composition, replace only the Japanese base.
   svg=c['character_callouts'](specs[key]);import xml.etree.ElementTree as ET
   root=ET.fromstring(svg);tag=lambda name:'{http://www.w3.org/2000/svg}'+name
   plan=root.find('.//'+tag('svg')+'[@class="official-plan"]');plan.clear();plan.set('class','chinese-plan');plan.set('data-language','zh-Hant');plan.set('x','35');plan.set('y','280');plan.set('width','650');plan.set('height',str(245*650/841.89));plan.set('viewBox','0 80 841.89 245')
   ET.SubElement(plan,tag('polygon'),{'points':'135,170 455,170 455,120 600,120 600,170 675,170 675,205 688,205 688,280 700,280 700,295 350,295 350,285 135,285','fill':'#e9e7dd','stroke':'#b8c2ba','stroke-width':'1'})
   # Floor geometry and C-codes follow the current official PDF.
   for x,y,w,h,code in [(155,215,22,58,'1'),(177,215,22,58,'2'),(199,215,22,58,'3'),(221,215,22,58,'4'),(292,215,28,27,'5'),(320,215,30,27,'6'),(320,242,30,30,'7'),(365,215,24,27,'19'),(386,260,16,25,'10'),(402,260,16,25,'11'),(418,260,28,25,'12'),(446,260,24,25,'13'),(470,260,24,25,'14'),(494,260,24,25,'15'),(518,260,24,25,'16'),(542,260,24,25,'17'),(566,260,25,15,'18'),(488,215,52,27,'20'),(540,215,30,27,'21'),(565,230,25,12,'22'),(590,215,14,27,'23'),(604,230,35,12,'24'),(657,276,30,10,'25'),(657,246,20,25,'26'),(657,195,20,51,'27'),(610,174,24,21,'29'),(506,144,33,17,'37'),(506,161,33,17,'38'),(539,144,31,52,'31'),(506,178,17,18,'33'),(523,178,16,18,'32')]:
    ET.SubElement(plan,tag('rect'),{'x':str(x),'y':str(y),'width':str(w),'height':str(h),'fill':'#d8e3df','stroke':'#faf8f1','stroke-width':'1'})
    t=ET.SubElement(plan,tag('text'),{'x':str(x+w/2),'y':str(y+h/2+3),'font-family':'Arial','font-size':'8','text-anchor':'middle','fill':INK});t.text=code
   # Chinese base labels are rendered by the same outline helper in a temporary SVG.
   start('','',500);n['parts']=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 80 841.89 245">']
   for label,x,y in [('北通道',270,207),('往零食區',85,207),('大丸東京側',400,302),('活動廣場',466,229),('北自由通道',475,123),('八重洲地下中央口',65,130)]:text(label,x,y,12,True,MUTED)
   translated=ET.fromstring(finish())
   for child in translated:plan.append(child)
   item['svg']=ET.tostring(root,encoding='unicode');item['source']='繁中重繪｜東京站一番街動漫街官方圖';item['steps']=routes[key]['steps'];(R/'assets'/specs[key]['file']).write_text(item['svg'],encoding='utf-8')
  else:
   v=V(item,(0,0,1044,724),subtitle='上方八重洲・下方丸之內・本站體相對位置')
   v.rect(340,210,690,445,'JR改札內|一般列車月台連通區',ALT,size=24)
   v.rect(398,0,155,100,'大丸東京',SHOP,size=22);v.rect(205,0,145,70,'大丸東京',SHOP,size=20)
   v.rect(145,115,72,105,'Gift|Palette',SHOP,size=17)
   v.rect(285,115,63,90,'Gift|Palette',SHOP,size=15)
   v.label('八重洲側',880,70,24);v.label('丸之內側',150,680,24)
   v.label('北自由通道',245,450,19);v.label('八重洲北口',390,220,21)
   v.label('八重洲中央口',670,230,20);v.label('八重洲南口',940,195,20)
   v.label('丸之內北口',350,630,18);v.label('丸之內中央口',600,630,18);v.label('丸之內南口',930,630,18)
   v.segment([(380,300),(330,230),(350,110),(400,80)],'#62713c','八重洲北口出站後往大丸食品入口')
   v.end('總覽為區域相對位置；進店後切到大丸1F詳圖。')
 (R/'assets/tokyo-station-guide.js').write_text('window.TOKYO_STATION_GUIDE = '+json.dumps(out,ensure_ascii=False)+';\n',encoding='utf-8')
 print('Rebuilt all nine floor guides in Traditional Chinese with native SVG geometry')
