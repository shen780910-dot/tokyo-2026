"""Integrate all shopping candidates and the Tokyo Station floor guide."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent.parent
p=R/'index.html';s=p.read_text(encoding='utf-8');needle='<script defer src="assets/app.js"></script>'
if 'src="assets/station-guide.js"' not in s:s=s.replace(needle,'<script defer src="assets/tokyo-station-guide.js"></script><script defer src="assets/station-guide.js"></script>'+needle)
p.write_text(s,encoding='utf-8')
p=R/'assets/trip-data.js';d=json.loads(p.read_text(encoding='utf-8').split(' = ',1)[1].strip().removesuffix(';'));day=d['days'][1]
schedule=day['schedule'];i=next(i for i,r in enumerate(schedule) if r['activity']=='Gift Palette・東京おかしランド・GRANSTA')
def notion(name,id):return {'name':name+'（Notion）','url':'https://app.notion.com/p/'+id}
schedule[i:i+1]=[
 {'time':'上午｜站區合計預留約3小時','activity':'JR改札內｜Ivorish → Maple Mania','detail':'搭JR抵達後暫時不要出站。先到B1丸之內改札內逛Ivorish MAISON，再回1F吹拔區逛The Maple Mania；買完從1F八重洲北口出JR。候選全部保留，現場可跳過；先別進新幹線轉乘口。','links':[notion('Ivorish MAISON','3fc400d1c43e8130bdf7f5c1b010fc37'),notion('The Maple Mania','3c8400d1c43e81a985a9c845bfa52374')]},
 {'time':'10:00開門後｜大丸','activity':'大丸東京｜1F兩間 → B1 PRESS','detail':'八重洲北口出站後，先逛1F TRIPLE DECKER LONDON、N.Y.C.SAND，再由大丸館內下B1找PRESS BUTTER SAND。三間全列候選，排隊太久可直接跳過；逛完回1F前往Gift Palette。','links':[notion('TRIPLE DECKER LONDON','3fc400d1c43e816c9f57fe3a3ac985fa'),{'name':'N.Y.C.SAND｜大丸官方資訊','url':'https://www.daimaru.co.jp/tokyo/nycsand/'},notion('PRESS BUTTER SAND','3c7400d1c43e81488678d4e80adca25a')]},
 {'time':'上午｜Gift Palette 1F','activity':'PISTA・BRULEE MERIZE・VANILLABEANS・Butter Butler','detail':'都在JR改札外，四間現場選。官方櫃位G32＝PISTA、G9＝BRULEE MERIZE、G8＝VANILLABEANS、G3＝Butter Butler；可切換上方Gift放大圖。下午繼續銀座採買，冷藏甜點優先現吃或確認保冷條件。','links':[notion('PISTA & TOKYO','3fc400d1c43e8124a778d8226edc756b'),notion('BRULEE MERIZE','3fc400d1c43e814d9f05c5fc431d8ec0'),notion('VANILLABEANS','3fc400d1c43e8190842fd262f79cd702'),{'name':'Butter Butler｜官方店舖資訊','url':'https://www.tokyoeki-1bangai.co.jp/shop/detail/?cd=000196'}]},
 {'time':'午餐前｜B1','activity':'東京おかしランド｜Calbee＋等零食','detail':'從Gift Palette旁H樓梯／電扶梯到B1「いちばんプラザ」前，再往東京おかしランド；推車依現場電梯指標。Calbee＋等零食全部現場自由選，逛完用餐，再找自由通路往丸之內側接KITTE，不需重新刷進JR。','links':[notion('Calbee＋','3c8400d1c43e815d9915c9c8631d6d0d')]}
]
day['note']='東京站上午採買全部列候選、現場自由跳過：JR內Ivorish與Maple Mania → 八重洲北口出站 → 大丸1F TRIPLE DECKER與N.Y.C.SAND、B1 PRESS → Gift Palette四間 → B1東京おかしランド。午餐後接KITTE、有樂町與銀座；其餘行程依採買進度調整。'
p.write_text('window.TRIP = '+json.dumps(d,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
(R/'VERSION').write_text('v1.18\n',encoding='utf-8')
p=R/'CHANGELOG.md';s=p.read_text(encoding='utf-8');entry='## v1.18\n\n- 11/13新增東京站B1、1F與Gift Palette放大SVG，可切換樓層並查看Google Maps地點。\n- 標示JR閘門內外、八重洲北口、地下中央口、H樓梯及官方G櫃位編號，提供官方樓層圖備查。\n- 十個伴手禮採買候選全部排入行程；先逛JR內、再出站逛大丸與一番街，現場自由取捨。\n- 大丸採買改成從1F兩間下B1 PRESS，減少重複上下樓；不修改Notion。\n\n'
if '## v1.18\n' not in s:i=s.index('## ');p.write_text(s[:i]+entry+s[i:],encoding='utf-8')
