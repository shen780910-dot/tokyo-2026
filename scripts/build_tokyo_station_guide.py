"""Build original floor/paid-area wayfinding SVGs from verified facility maps."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json, xml.etree.ElementTree as ET

R=Path(__file__).resolve().parent.parent
ns={'__file__':str(R/'scripts/build_geo_maps.py')}
exec((R/'scripts/build_geo_maps.py').read_text(encoding='utf-8').split('output=[]')[0],ns)
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
fallback_font=TTFont('C:/Windows/Fonts/msjh.ttc',fontNumber=0)
shops=[
 (1,'Ivorish MAISON','B1 丸之內改札內','夾心餅乾・費南雪','Ivorish MAISON Gransta Tokyo'),
 (2,'The Maple Mania','1F 吹拔區・改札內','楓糖奶油餅乾','The Maple Mania Gransta Tokyo'),
 (3,'PRESS BUTTER SAND','大丸 B1・改札外','奶油焦糖夾心餅','PRESS BUTTER SAND Daimaru Tokyo'),
 (4,'TRIPLE DECKER','大丸 1F・改札外','三層酥餅','TRIPLE DECKER LONDON Daimaru Tokyo'),
 (5,'N.Y.C.SAND','大丸 1F・改札外','焦糖巧克力夾心餅','N Y C SAND Daimaru Tokyo'),
 (6,'PISTA & TOKYO','Gift Palette 1F・改札外','開心果餅乾','PISTA TOKYO Tokyo Gift Palette'),
 (7,'BRULEE MERIZE','Gift Palette 1F・改札外','布蕾奶油塔','BRULEE MERIZE Tokyo Gift Palette'),
 (8,'VANILLABEANS','Gift Palette 1F・改札外','巧克力夾心餅','VANILLABEANS Tokyo Gift Palette'),
 (9,'Butter Butler','Gift Palette 1F・改札外','奶油費南雪','Butter Butler Tokyo Gift Palette'),
 (10,'Calbee＋','東京おかしランド B1・改札外','零食・現做點心','Calbee Plus Tokyo Station'),
]
parts=[]
def text(value,x,y,size=24,sub=False,color='#26312e',anchor='start'):
 parts.append(f'<text class="{"sub" if sub else "name"}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{escape(value)}</text>')
def system(value,x,y,size=23,color='#536377',anchor='start'):
 parts.append(f'<text data-system="true" x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{color}">{escape(value)}</text>')
def box(x,y,w,h,fill,stroke='#b3a98f'):
 parts.append(f'<path d="M{x} {y}Q{x+w/2} {y-2} {x+w} {y+1}L{x+w-1} {y+h}Q{x+w/2} {y+h+1} {x} {y+h-1}Z" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
def line(points,color='#536377',width=1.4,arrow=False):
 parts.append(f'<path d="{points}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"'+(' marker-end="url(#guide-arrow)"' if arrow else '')+'/>')
def marker(n,x,y,size=21):
 parts.append(f'<circle cx="{x}" cy="{y-7}" r="15" fill="#a94732"/>');system(str(n),x,y,size,'#fff','middle')
def shop(n,x,y,size=22,info=None):
 _,name,loc,item,query=shops[n-1]
 parts.append(f'<a href="https://www.google.com/maps/search/?api=1&amp;query={quote(query)}" target="_blank" rel="noopener noreferrer" aria-label="{escape(name)}：Google Maps"><title>{escape(name+"｜"+loc)}</title><rect x="{x-19}" y="{y-26}" width="270" height="56" fill="transparent"/>')
 marker(n,x,y);text(name,x+25,y,size);text(info or item,x+25,y+25,17,True,'#536377');parts.append('</a>')
def start(title,subtitle,h=1100):
 global parts
 parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 {h}" role="img" aria-labelledby="guide-title guide-desc"><title id="guide-title">{title}</title><desc id="guide-desc">{escape(subtitle)}。依官方館別與出口關係重繪，非店內精密平面；箭頭為區域移動順序，不指定未查證的電梯。</desc><defs><marker id="guide-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="none" stroke="#a94732" stroke-width="1.3"/></marker></defs><rect width="720" height="{h}" fill="#eeeade"/><path d="M20 24Q360 17 700 25L697 {h-22}Q360 {h-16} 22 {h-23}Z" fill="none" stroke="#536377" stroke-width="1.3"/>']
 text(title,43,75,30);text(subtitle,43,111,19,True,'#536377')
def finish():
 parts.append('</svg>');root=ET.fromstring(''.join(parts));tag=lambda n:'{http://www.w3.org/2000/svg}'+n
 raw=ET.tostring(root,encoding='unicode')
 # Temporarily convert system text into a neutral wrapper so the outline helper skips it.
 rawroot=ET.fromstring(raw);saved=[]
 for parent in rawroot.iter():
  for node in list(parent):
   if node.get('data-system')=='true':
    idx=len(saved);saved.append(node);placeholder=ET.Element(tag('g'),{'data-system-placeholder':str(idx)});parent.insert(list(parent).index(node),placeholder);parent.remove(node)
 # Preserve Klee One for gray labels. Only missing glyphs fall back to a full
 # Traditional Chinese font, rather than switching the whole label to Lihsianti.
 for parent in rawroot.iter():
  for node in list(parent):
   if node.tag!=tag('text'):continue
   value=''.join(node.itertext());attrs=dict(node.attrib);preferred=ns['SUB_FONT'] if attrs.get('class')=='sub' else ns['MAP_FONT']
   size=float(attrs.pop('font-size','23'));x=float(attrs.pop('x','0'));y=float(attrs.pop('y','0'));anchor=attrs.pop('text-anchor','start');glyphs=[]
   for char in value:
    font=preferred if ord(char) in preferred.getBestCmap() else fallback_font
    glyph=font.getBestCmap().get(ord(char),'.notdef');scale=size/font['head'].unitsPerEm;glyphs.append((font,glyph,scale,font['hmtx'][glyph][0]*scale))
   total=sum(item[3] for item in glyphs)
   if anchor=='middle':x-=total/2
   elif anchor=='end':x-=total
   attrs['class']='text-shape '+attrs.get('class','');attrs['aria-label']=value
   group=ET.Element(tag('g'),attrs)
   for font,glyph,scale,advance in glyphs:
    pen=SVGPathPen(font.getGlyphSet());font.getGlyphSet()[glyph].draw(TransformPen(pen,(scale,0,0,-scale,x,y)));ET.SubElement(group,tag('path'),{'d':pen.getCommands()});x+=advance
   parent.insert(list(parent).index(node),group);parent.remove(node)
 rendered=rawroot
 for parent in rendered.iter():
  for node in list(parent):
   if node.get('data-system-placeholder') is not None:
    parent.insert(list(parent).index(node),saved[int(node.get('data-system-placeholder'))]);parent.remove(node)
 return ET.tostring(rendered,encoding='unicode')

# Regional diagram: west/Marunouchi on the left; east/Yaesu on the right.
start('東京站・1F 地面層','先在JR內買完，再從八重洲北口出站')
text('丸之內側',55,165,21);text('八重洲側',518,165,21)
box(43,199,293,556,'#dbe1d6');box(393,199,284,556,'#e6d8c4')
text('JR 改札內',65,237,25);text('改札外',415,237,25)
text('從月台下來先留在JR內',65,278,18,True,'#536377')
box(65,332,249,135,'#eeeade');system('B1 → 1F',85,366,21)
shop(2,86,408,20,info='吹拔區・08:00–22:00')
line('M180 485V532H365V343H399','#a94732',2,True)
box(314,510,101,55,'#eeeade','#a94732');text('八重洲',365,532,18,False,anchor='middle');text('北口',365,554,18,False,anchor='middle')
text('只在這裡出JR閘門',64,598,19,True,'#a94732')
text('不是新幹線轉乘口',64,631,18,True,'#536377')
text('往丸之內：北自由通路',64,707,17,True,'#536377')
box(412,271,245,185,'#eeeade');text('大丸東京 1F',432,306,24)
shop(4,435,352,18);shop(5,435,413,20)
box(412,488,245,260,'#eeeade');text('Gift Palette',432,523,23)
shop(6,435,565,18);shop(7,435,615,18);shop(8,435,665,18);shop(9,435,715,18)
text('大丸B1：PRESS在地下',50,805,24)
text('大丸館內下樓買採買編號3，再回1F逛Gift Palette',50,842,17,True,'#536377')
box(43,882,634,123,'#dedfd5');system('H',68,923,28);text('Gift Palette旁上下B1',104,922,25)
text('H樓梯／電扶梯前是「いちばんプラザ」',65,961,19,True,'#536377')
text('推車找現場電梯指標，不必搬推車走樓梯',65,990,18,True,'#536377')
text('區域相對位置示意・非比例，箭頭為採買順序',43,1054,17,True,'#536377')
one=finish()

start('東京站・B1 地下層','先找丸之內改札內的Ivorish，暫時不要出站')
text('丸之內側',55,165,21);text('八重洲側',518,165,21)
box(43,198,293,559,'#dbe1d6');box(393,198,284,559,'#e6d8c4')
text('JR 改札內',65,238,25);text('改札外',415,238,25)
shop(1,69,314,22,info='丸之內地下區・08:00–22:00')
text('找店時認這行日文',65,382,19,True,'#536377')
text('地下 丸の内改札内',65,416,22)
line('M184 454V497','#a94732',2,True)
box(64,512,250,112,'#eeeade');system('B1 → 1F',86,552,25);text('回1F找 Maple Mania',85,592,20)
text('先逛1與2，再出JR閘門',65,690,18,True,'#a94732')
box(413,271,243,133,'#eeeade');text('大丸東京 B1',434,305,24);shop(3,435,350,17,info='10:00–20:00・館內下樓')
box(413,446,243,81,'#dedfd5');system('H',435,482,27);text('往1F Gift Palette',473,482,17);text('「いちばんプラザ」前',435,512,17,True,'#536377')
box(413,575,243,148,'#eeeade');text('東京おかしランド',431,610,23);shop(10,435,658,23,info='零食・現做點心・自由選')
line('M337 650H394','#536377',1.4)
text('八重洲地下中央口',363,795,25,False,anchor='middle')
text('這是B1的JR出入口；本次出站使用1F八重洲北口',50,832,18,True,'#536377')
box(43,881,634,124,'#dedfd5');text('逛完不要為了回丸之內而刷回JR',65,921,25)
text('找「北地下自由通路」往丸之內側，再往KITTE',65,959,19,True,'#536377')
text('地下通道多，看到不確定的閘門先停下核對',65,991,18,True,'#536377')
text('區域相對位置示意・非比例，不把店名框當實際櫃位',43,1054,17,True,'#536377')
basement=finish()

# Gift Palette inset follows the actual two shop islands, using official G codes.
start('Gift Palette・1F 放大','用紅色採買編號找店，再核對官方G編號',1250)
text('八重洲北口｜JR閘門',45,169,23)
line('M179 188V245','#a94732',2,True)
box(45,210,625,50,'#dedfd5');text('北自由通路・從丸之內側過來',65,243,21)
box(65,293,240,290,'#d6dbcc');box(378,293,277,290,'#d6dbcc')
text('左側店舖島',85,329,22);text('右側店舖島',399,329,22)
box(86,440,82,119,'#eeeade');marker(9,125,490);system('G3',125,532,20,anchor='middle')
box(181,440,49,119,'#eeeade');marker(8,205,490);system('G8',205,532,18,anchor='middle')
box(242,440,43,119,'#eeeade');marker(7,263,490);system('G9',263,532,18,anchor='middle')
box(401,514,231,45,'#eeeade');marker(6,468,543);system('G32',552,543,20,anchor='middle')
text('通道',320,410,18);line('M330 431V570','#536377',1.2)
system('H',89,630,28);text('H樓梯／電扶梯往B1',128,630,23)
shop(6,71,711,25,info='G32・右側店島下緣｜開心果餅乾')
shop(7,71,800,25,info='G9・左側店島東緣｜布蕾奶油塔')
shop(8,71,889,25,info='G8・左側店島下方｜巧克力夾心餅')
shop(9,71,978,25,info='G3・左側店島下方｜奶油費南雪')
text('大丸側',70,1065,22);text('日本橋口側',508,1065,22)
text('紅色數字是本次採買編號，G編號為官方櫃位編號',56,1122,18,True,'#536377')
text('到現場自由選店；非比例，入口與電梯依現場指標',43,1193,18,True,'#536377')
gift=finish()
items=[{'id':'b1','label':'B1 地下','svg':basement,'file':'tokyo-station-b1.svg'}, {'id':'1f','label':'1F 地面','svg':one,'file':'tokyo-station-1f.svg'}, {'id':'gift','label':'Gift 放大','svg':gift,'file':'tokyo-station-gift.svg'}]
for item in items:(R/'assets'/item['file']).write_text(item['svg'],encoding='utf-8')
(R/'assets/tokyo-station-guide.js').write_text('window.TOKYO_STATION_GUIDE = '+json.dumps(items,ensure_ascii=False)+';\n',encoding='utf-8')
print('Built three Tokyo Station floor/paid-area SVGs; all ten shopping stops included')
