"""Improve current SVG badge legibility and reduce shop/food artwork size."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parent.parent
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
def tag(name): return '{' + NS + '}' + name

def polish(svg):
    root = ET.fromstring(svg)
    for anchor in root.iter(tag('a')):
        circles = [n for n in anchor if n.tag == tag('circle') and n.get('r') in ('13', '10.5')]
        for badge in circles: badge.set('r', '10.5')
        for node in list(anchor):
            label = node.get('aria-label', '')
            if node.tag == tag('g') and label.isdigit() and circles:
                badge = circles[-1]
                number = ET.Element(tag('text'), {
                    'x': badge.get('cx'), 'y': str(float(badge.get('cy')) + 4.5),
                    'text-anchor': 'middle', 'font-family': 'Arial, Helvetica, sans-serif',
                    'font-size': '13', 'font-weight': '700', 'fill': '#fff',
                    'class': 'map-number', 'aria-label': label,
                })
                number.text = label
                position = list(anchor).index(node)
                anchor.remove(node)
                anchor.insert(position, number)
            elif node.tag == tag('text') and node.get('class') == 'map-number' and circles:
                node.set('font-size', '13')
                node.set('y', str(float(circles[-1].get('cy')) + 4.5))
        for icon in anchor.findall(tag('g')):
            if icon.get('class') != 'icon': continue
            paths = [p.get('d', '') for p in icon.iter(tag('path'))]
            shopping_or_food=any(p.startswith('M-12 12L-10-9') or p.startswith('M-11-15V-1') for p in paths)
            transform = icon.get('transform', '').split(' scale(')[0]
            icon.set('transform', transform + (' scale(0.52)' if shopping_or_food else ' scale(0.85)'))
            for halo in anchor.findall(tag('ellipse')):
                halo.set('rx', '15' if shopping_or_food else '23')
                halo.set('ry', '14' if shopping_or_food else '20')
    # Geographic dots and tethers must be behind every label, including labels
    # belonging to a different shop. Keep the dot links clickable.
    for panel in root.iter(tag('svg')):
        anchors = panel.findall(tag('a'))
        if not anchors: continue
        layer = ET.Element(tag('g'), {'class': 'map-geographic-anchors'})
        for anchor in anchors:
            background = ET.Element(tag('a'), dict(anchor.attrib))
            for node in list(anchor):
                if (node.tag == tag('path') and node.get('class') == 'leader') or (node.tag == tag('circle') and node.get('r') == '3.5'):
                    anchor.remove(node)
                    background.append(node)
            if len(background): layer.append(background)
        if len(layer): panel.insert(list(panel).index(anchors[0]), layer)
    for anchor in root.iter(tag('a')):
        if anchor.get('aria-label')!='押上站：開啟Google Maps': continue
        halo=anchor.find(tag('ellipse'))
        if halo is not None and halo.get('cy')=='430.0':
            anchor.set('transform','translate(0 45)')
        for line in anchor.findall(tag('path')):
            if line.get('class')=='leader':
                line.set('d',line.get('d','').replace('L480.0 430.0','L480.0 475.0').replace('L480.0 395.0','L480.0 475.0'))
    return ET.tostring(root, encoding='unicode')

path = R / 'assets/trip-maps.js'
maps = json.loads(path.read_text(encoding='utf-8').split(' = ', 1)[1].strip().removesuffix(';'))
for i, item in enumerate(maps, 1):
    item['svg'] = polish(item['svg'])
    (R / f'assets/day-{i}-map.svg').write_text(item['svg'], encoding='utf-8')
path.write_text('window.TRIP_MAPS = ' + json.dumps(maps, ensure_ascii=False) + ';\n', encoding='utf-8')
print('All four maps: smaller badges and icons; geographic coordinates preserved')
