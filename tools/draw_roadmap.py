#!/usr/bin/env python3
"""Draw the requested ProsperoCraft roadmap as SVG and a supersampled PNG.

Requires Pillow and explicit regular/bold TrueType font files. No generated art.
"""
import argparse
from html import escape
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--font', type=Path, required=True)
    p.add_argument('--bold-font', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    width, height, scale = 1800, 1470, 2
    bg, ink, muted = '#E9EDE9', '#172E26', '#61746A'
    canvas = Image.new('RGB', (width * scale, height * scale), bg)
    draw = ImageDraw.Draw(canvas)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<title>ProsperoCraft roadmap</title>',
           '<desc>White completed milestones: Full 26.x.x support, microphone support, shader support, OpenGL support. A winding road continues through dark planned milestones: 1.21.x, 1.20.x, 1.19.x, 1.18.x, 1.17.x, 1.16.x support and older versions.</desc>',
           f'<rect width="{width}" height="{height}" fill="{bg}"/>']

    def rect(x, y, w, h, fill, radius=0):
        box = tuple(round(v * scale) for v in (x, y, x + w, y + h))
        draw.rounded_rectangle(box, radius=round(radius * scale), fill=fill)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"/>')

    def text(x, y, label, size, fill=ink, bold=False):
        font = ImageFont.truetype(str(a.bold_font if bold else a.font), size * scale)
        draw.text((x * scale, y * scale), label, font=font, fill=fill, anchor='lt')
        svg.append(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}" dominant-baseline="text-before-edge">{escape(label)}</text>')

    def line(points, fill, stroke):
        draw.line([(round(x * scale), round(y * scale)) for x, y in points], fill=fill, width=round(stroke * scale), joint='curve')
        svg.append('<polyline points="' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in points) + f'" fill="none" stroke="{fill}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"/>')

    def circle(x, y, r, fill):
        draw.ellipse(tuple(round(v * scale) for v in (x-r, y-r, x+r, y+r)), fill=fill)
        svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>')

    rect(76, 76, 8, 43, '#5D9D7A', 4)
    text(104, 81, 'PROSPEROCRAFT', 30, bold=True)
    text(76, 155, 'The road ahead.', 84, bold=True)
    text(80, 260, 'More ways to play. More versions to explore.', 28, muted)
    rect(1365, 82, 160, 42, '#FFFFFF', 21)
    text(1391, 93, 'DONE', 18, bold=True)
    rect(1540, 82, 184, 42, ink, 21)
    text(1566, 93, 'PLANNED', 18, '#FFFFFF', True)

    # Continuous three-row road, sampled from cubic curves for both formats.
    road = [(258 + i * 1284 / 100, 550) for i in range(101)]
    def curve(p0, p1, p2, p3):
        for i in range(1, 101):
            t=i/100; u=1-t
            road.append(tuple(u**3*p0[k]+3*u*u*t*p1[k]+3*u*t*t*p2[k]+t**3*p3[k] for k in (0,1)))
    curve((1542,550),(1760,550),(1760,910),(1542,910))
    road.extend((1542-i*1284/100,910) for i in range(1,101))
    curve((258,910),(40,910),(40,1270),(258,1270))
    road.extend((258+i*856/100,1270) for i in range(1,101))
    line(road, '#CAD4CC', 57)
    line(road, '#52685C', 43)
    # Evenly spaced lane marks follow arc length, including the curved sections.
    position = 0.0
    for start,end in zip(road,road[1:]):
        length=math.dist(start,end)
        if int(position/30)%2 == 0:
            line([start,end], '#DEE7DD', 3)
        position += length
    for x,y,direction in [(940,550,1),(870,910,-1),(720,1270,1)]:
        line([(x-10*direction,y-9),(x,y),(x-10*direction,y+9)], '#FFFFFF', 3)

    def card(x, y, title, done, road_y, number):
        w,h=364,158; center=x+w/2
        line([(center,y+h),(center,road_y-16)], '#AFBFB2', 2)
        rect(x,y+5,w,h,'#DCE3DC',25)
        rect(x,y,w,h,'#FFFFFF' if done else ink,25)
        circle(center,road_y,16,bg)
        circle(center,road_y,10,'#5D9D7A' if done else ink)
        if done:
            circle(x+30,y+30,10,'#E2EFE4')
            line([(x+25,y+30),(x+29,y+34),(x+36,y+26)],'#3F7B57',2)
            text(x+49,y+21,'DONE',15,'#4D7D60',True)
        else:
            text(x+26,y+22,f'{number:02d}  /  PLANNED',15,'#9DB9A6',True)
        for i,label in enumerate(title):
            text(x+26,y+64+i*37,label,30,ink if done else '#FFFFFF',True)

    xs=[76,504,932,1360]
    completed=[['Full 26.x.x support'],['Microphone support'],['Shader support'],['OpenGL support']]
    # The first two longer labels fit on two lines at the same readable size.
    completed[0]=['Full 26.x.x','support']
    completed[1]=['Microphone','support']
    for x,title in zip(xs,completed): card(x,330,title,True,550,0)
    for n,(x,version) in enumerate(zip(reversed(xs),['1.21.x','1.20.x','1.19.x','1.18.x']),1):
        card(x,690,[version+' support'],False,910,n)
    for n,(x,title) in enumerate(zip(xs,[['1.17.x support'],['1.16.x support'],['Older versions']]),5):
        card(x,1050,title,False,1270,n)
    circle(1114,1270,7,'#FFFFFF')
    text(80,1375,'PROSPEROCRAFT  /  DEVELOPMENT ROADMAP',18,muted,True)
    text(1242,1375,'COMPLETED → UPCOMING',18,muted,True)
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'prosperocraft-roadmap.svg').write_text('\n'.join(svg+['</svg>'])+'\n')
    canvas.resize((width,height),Image.Resampling.LANCZOS).save(a.output/'prosperocraft-roadmap.png',optimize=True)
    print(a.output/'prosperocraft-roadmap.png')


if __name__ == '__main__':
    main()
