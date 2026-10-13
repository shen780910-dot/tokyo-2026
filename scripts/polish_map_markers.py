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
        circles = [n for n in anchor if n.tag == tag('circle') and n.get('r') == '13']
        for node in list(anchor):
            label = node.get('aria-label', '')
            if node.tag == tag('g') and label.isdigit() and circles:
                badge = circles[-1]
                number = ET.Element(tag('text'), {
                    'x': badge.get('cx'), 'y': str(float(badge.get('cy')) + 5.5),
                    'text-anchor': 'middle', 'font-family': 'Arial, Helvetica, sans-serif',
                    'font-size': '16', 'font-weight': '700', 'fill': '#fff',
                    'class': 'map-number', 'aria-label': label,
                })
                number.text = label
                position = list(anchor).index(node)
                anchor.remove(node)
                anchor.insert(position, number)
        for icon in anchor.findall(tag('g')):
            if icon.get('class') != 'icon': continue
            paths = [p.get('d', '') for p in icon.iter(tag('path'))]
            if not any(p.startswith('M-12 12L-10-9') or p.startswith('M-11-15V-1') for p in paths): continue
            transform = icon.get('transform', '').split(' scale(')[0]
            icon.set('transform', transform + ' scale(0.62)')
            for halo in anchor.findall(tag('ellipse')):
                halo.set('rx', '18')
                halo.set('ry', '17')
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
    return ET.tostring(root, encoding='unicode')

path = R / 'assets/trip-maps.js'
maps = json.loads(path.read_text(encoding='utf-8').split(' = ', 1)[1].strip().removesuffix(';'))
for i, item in enumerate(maps, 1):
    item['svg'] = polish(item['svg'])
    (R / f'assets/day-{i}-map.svg').write_text(item['svg'], encoding='utf-8')
path.write_text('window.TRIP_MAPS = ' + json.dumps(maps, ensure_ascii=False) + ';\n', encoding='utf-8')
print('All four maps: dots behind text; shop/food icons at 62% size')
