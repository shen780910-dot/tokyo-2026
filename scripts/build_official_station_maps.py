"""Official floor-plan bases with SVG pins and matching shop-name annotations.

GRANSTA/Daimaru publish JPEG maps; those originals are embedded without tracing
or inventing corridors. Gift Palette's official PDF is converted to vector SVG.
"""
from pathlib import Path
from html import escape
import base64,json,math,xml.etree.ElementTree as ET
import pymupdf
R=Path(__file__).resolve().parent.parent
sources=R/'previews/official-floor-sources'
namespace={'__file__':str(R/'scripts/build_tokyo_station_guide.py')}
exec((R/'scripts/build_tokyo_station_guide.py').read_text(encoding='utf-8').split('# Regional diagram:')[0],namespace)
namespace['shops'][3]=(4,'TRIPLE DECKER LONDON',*namespace['shops'][3][2:])
start,text,system,shop,finish=(namespace[n] for n in ['start','text','system','shop','finish'])
notion_pages={
 1:'3fc400d1c43e8130bdf7f5c1b010fc37',2:'3c8400d1c43e81a985a9c845bfa52374',
 3:'3c7400d1c43e81488678d4e80adca25a',4:'3fc400d1c43e816c9f57fe3a3ac985fa',
 5:'3fc400d1c43e8102b256e78387891620',6:'3fc400d1c43e8124a778d8226edc756b',
 7:'3fc400d1c43e814d9f05c5fc431d8ec0',8:'3fc400d1c43e8190842fd262f79cd702',
 10:'3c8400d1c43e815d9915c9c8631d6d0d',
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
out=[]
for spec in specs:
 uri,source_w,source_h=data_url(sources/spec['base']);cx,cy,cw,ch=spec['crop'];scale=650/cw;map_y=160;map_h=ch*scale;legend_y=map_y+map_h+56
 height=math.ceil(legend_y+len(spec['shops'])*91+168)
 start(spec['title'],spec['subtitle'],height)
 parts=namespace['parts']
 parts.append(f'<svg class="official-plan" x="35" y="{map_y}" width="650" height="{map_h}" viewBox="{cx} {cy} {cw} {ch}" overflow="hidden"><image href="{uri}" width="{source_w}" height="{source_h}"/></svg>')
 for number,x,y,dx,dy in spec['pins']:
  px,py=35+(x-cx)*scale,map_y+(y-cy)*scale;bx,by=px+dx,py+dy
  parts.append(f'<g class="official-shop-pin" data-shop="{number}"><path d="M{bx} {by}L{px} {py}" stroke="#a94732" stroke-width="1.7" fill="none"/><circle cx="{px}" cy="{py}" r="4" fill="#a94732" stroke="#fff" stroke-width="1.2"/><circle cx="{bx}" cy="{by}" r="14" fill="#a94732" stroke="#fff" stroke-width="2"/>')
  system(str(number),bx,by+6,20,'#fff','middle');parts.append('</g>')
 for i,n in enumerate(spec['shops']):
  info=namespace['shops'][n-1][2]
  if spec['id']=='gift':info={6:'官方 G32・開心果餅乾',7:'官方 G9・布蕾奶油塔',8:'官方 G8・巧克力夾心餅',9:'官方 G3・奶油費南雪'}[n]
  shop(n,65,legend_y+i*91,26,info=info)
  link_y=legend_y+i*91
  if n in notion_pages:
   href='https://app.notion.com/p/'+notion_pages[n];label='Notion ↗';kind='notion'
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
 text(spec['source'],43,height-40,16,True,'#536377')
 svg=finish();(R/'assets'/spec['file']).write_text(svg,encoding='utf-8')
 out.append({k:spec[k] for k in ['id','label','file','source','url']}|{'svg':svg,'shops':spec['shops']})
(R/'assets/tokyo-station-guide.js').write_text('window.TOKYO_STATION_GUIDE = '+json.dumps(out,ensure_ascii=False)+';\n',encoding='utf-8')
print('Built seven official-base SVG guides; original raster bases preserved; official PDFs converted to vector')
