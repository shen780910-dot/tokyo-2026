from pathlib import Path
import sys,json,re,html
r=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(r.parent/'.fonttools'))
from fontTools.ttLib import TTFont
from fontTools.subset import Options,Subsetter
source=Path(r'E:\hejhusyuan\Downloads\lihsianti-proportional (1).ttf')
font=TTFont(source)
text=html.unescape(re.sub('<[^>]+>','',(r/'index.html').read_text(encoding='utf-8')))
data=json.loads((r/'assets/trip-data.js').read_text(encoding='utf-8')[len('window.TRIP = '):].rstrip().removesuffix(';'))
text+=''.join(day['title']+day['area']+day['date']+day['weekday'] for day in data['days'])
for filename in ['app.js','station-guide.js']:
    text+=(r/'assets'/filename).read_text(encoding='utf-8')
text+='東京 2026四天三夜行前清單TOKYO JAPAN0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
options=Options();options.flavor='woff';options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*']
subsetter=Subsetter(options=options);subsetter.populate(text=text);subsetter.subset(font);font.flavor='woff'
(r/'assets/fonts').mkdir(exist_ok=True)
font.save(r/'assets/fonts/lihsianti-heading.woff')
print('Heading font subset:',(r/'assets/fonts/lihsianti-heading.woff').stat().st_size,'bytes')
