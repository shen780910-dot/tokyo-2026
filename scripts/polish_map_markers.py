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
        circles = [n for n in anchor if n.tag == tag('circle') and n.get('r') in ('13', '10.5', '9')]
        for badge in circles: badge.set('r', '9')
        for node in list(anchor):
            label = node.get('aria-label', '')
            if node.tag == tag('g') and label.isdigit() and circles:
                badge = circles[-1]
                number = ET.Element(tag('text'), {
                    'x': badge.get('cx'), 'y': str(float(badge.get('cy')) + 4.5),
                    'text-anchor': 'middle', 'font-family': 'Arial, Helvetica, sans-serif',
                    'font-size': '11', 'font-weight': '700', 'fill': '#fff',
                    'class': 'map-number', 'aria-label': label,
                })
                number.text = label
                position = list(anchor).index(node)
                anchor.remove(node)
                anchor.insert(position, number)
            elif node.tag == tag('text') and node.get('class') == 'map-number' and circles:
                node.set('font-size', '11')
                node.set('y', str(float(circles[-1].get('cy')) + 4.5))
        for icon in anchor.findall(tag('g')):
            if icon.get('class') != 'icon': continue
            paths = [p.get('d', '') for p in icon.iter(tag('path'))]
            shopping_or_food=any(p.startswith('M-12 12L-10-9') or p.startswith('M-11-15V-1') for p in paths)
            transform = icon.get('transform', '').split(' scale(')[0]
            icon.set('transform', transform + (' scale(0.66)' if shopping_or_food else ' scale(0.92)'))
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
    for line in root.iter(tag('path')):
        if line.get('class')=='leader':
            line.set('style','stroke:#536377;stroke-width:1.1;stroke-linecap:round;fill:none')
    for text in root.iter(tag('g')):
        if 'sub' not in text.get('class','').split() or text.get('data-compact-gray')=='true': continue
        path=text.find(tag('path'))
        if path is None: continue
        # The outlines retain their baseline; shrink each line by one font size.
        import re
        numbers=re.findall(r'-?\d+(?:\.\d+)?',path.get('d',''))
        if len(numbers)<2: continue
        px,py=map(float,numbers[:2])
        text.set('transform',f'translate({px} {py}) scale(0.92) translate({-px} {-py})')
        text.set('data-compact-gray','true')
    for panel in root.iter(tag('svg')):
        dots={}
        for layer in panel.findall(tag('g')):
            if layer.get('class')!='map-geographic-anchors': continue
            for anchor in layer.findall(tag('a')):
                for dot in anchor.findall(tag('circle')):
                    if dot.get('r')=='3.5': dots[anchor.get('aria-label')]=dot
        for anchor in panel.findall(tag('a')):
            dot=dots.get(anchor.get('aria-label'))
            number=anchor.find(tag('text')+'[@class="map-number"]')
            if dot is None or number is None: continue
            badge=next((node for node in anchor.findall(tag('circle')) if node.get('r')=='9'),None)
            if badge is None: continue
            dx,dy=(14,-14) if number.text=='1' else (-14,-14)
            cx,cy=float(dot.get('cx'))+dx,float(dot.get('cy'))+dy
            # Keep badge positions in the map's coordinate system even when
            # its shop artwork is translated away from the geographic dot.
            moved=anchor.get('transform','')
            if moved=='translate(0 45)': cy-=45
            badge.set('cx',str(cx));badge.set('cy',str(cy))
            number.set('x',str(cx));number.set('y',str(cy+4))
    for panel in root.iter(tag('svg')):
        geographic={}
        for layer in panel.findall(tag('g')):
            if layer.get('class')!='map-geographic-anchors': continue
            for anchor in layer.findall(tag('a')):
                dot=anchor.find(tag('circle')+'[@r="3.5"]')
                if dot is not None: geographic[anchor.get('aria-label')]=(anchor,dot)
        for anchor in panel.findall(tag('a')):
            icon=anchor.find(tag('g')+'[@class="icon"]')
            halo=anchor.find(tag('ellipse'))
            if icon is None or halo is None: continue
            station=icon.find(tag('rect')) is not None
            stay=any(n.get('d','').startswith('M-17-1L0-17') for n in icon.findall(tag('path')))
            pair=geographic.get(anchor.get('aria-label'))
            if not (station or stay) or pair is None: continue
            background,dot=pair
            ax,ay=float(dot.get('cx')),float(dot.get('cy'))
            shift_y=45 if anchor.get('transform')=='translate(0 45)' else 0
            if shift_y:
                anchor.attrib.pop('transform',None)
                for text in anchor.findall(tag('g')):
                    if 'text-shape' in text.get('class',''):
                        text.set('transform','translate(0 45) '+text.get('transform',''))
                for hit in anchor.findall(tag('rect')): hit.set('y',str(float(hit.get('y'))+45))
                number=anchor.find(tag('text')+'[@class="map-number"]')
                badge=anchor.find(tag('circle')+'[@r="9"]')
                if number is not None:number.set('y',str(float(number.get('y'))+45))
                if badge is not None:badge.set('cy',str(float(badge.get('cy'))+45))
            icon.set('transform',f'translate({ax} {ay}) scale(0.92)')
            icon.set('data-direct-location','true')
            halo.set('cx',str(ax));halo.set('cy',str(ay));halo.set('data-direct-location','true')
            dot.set('visibility','hidden')
            hits=anchor.findall(tag('rect'))
            icon_hit=next((n for n in hits if n.get('width')=='48'),None)
            if icon_hit is not None:
                icon_hit.set('x',str(ax-24));icon_hit.set('y',str(ay-24))
            label_hit=next((n for n in hits if n.get('width')!='48'),None)
            if label_hit is None:continue
            lx,ly=float(label_hit.get('x'))+5,float(label_hit.get('y'))+26
            if stay and anchor.get('data-label-at-location')!='true':
                dx,dy=ax+36-lx,ay-8-ly
                for text in anchor.findall(tag('g')):
                    if 'text-shape' in text.get('class',''):
                        text.set('transform',f'translate({dx} {dy}) '+text.get('transform',''))
                label_hit.set('x',str(float(label_hit.get('x'))+dx))
                label_hit.set('y',str(float(label_hit.get('y'))+dy))
                lx+=dx;ly+=dy
                anchor.set('data-label-at-location','true')
            for line in background.findall(tag('path')):
                if line.get('class')=='leader':line.set('d',f'M{ax} {ay}L{lx-10} {ly-5}')
        # Other nearby geographic dots remain visible in front of directly
        # placed station/stay artwork; their coordinates remain unchanged.
        foreground=panel.find(tag('g')+'[@class="map-visible-dots"]')
        if foreground is None:
            foreground=ET.Element(tag('g'),{'class':'map-visible-dots'})
            panel.append(foreground)
        for background,dot in geographic.values():
            if dot.get('visibility')=='hidden':continue
            background.remove(dot)
            link=ET.SubElement(foreground,tag('a'),dict(background.attrib));link.append(dot)
    return ET.tostring(root, encoding='unicode')

path = R / 'assets/trip-maps.js'
maps = json.loads(path.read_text(encoding='utf-8').split(' = ', 1)[1].strip().removesuffix(';'))
for i, item in enumerate(maps, 1):
    item['svg'] = polish(item['svg'])
    (R / f'assets/day-{i}-map.svg').write_text(item['svg'], encoding='utf-8')
path.write_text('window.TRIP_MAPS = ' + json.dumps(maps, ensure_ascii=False) + ';\n', encoding='utf-8')
print('All four maps: smaller badges and icons; geographic coordinates preserved')
