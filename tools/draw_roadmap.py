#!/usr/bin/env python3
"""Draw the requested ProsperoCraft roadmap as SVG and a supersampled PNG.

Requires Pillow and explicit regular/bold TrueType font files. No generated art.
"""
import argparse
from html import escape
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--font', type=Path, required=True)
    p.add_argument('--bold-font', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    width, height, scale = 1800, 1830, 2
    bg, ink, muted = '#101413', '#131816', '#87928C'
    canvas = Image.new('RGB', (width * scale, height * scale), bg)
    draw = ImageDraw.Draw(canvas)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<title>ProsperoCraft roadmap</title>',
           '<desc>White completed milestones: Full 26.x.x support, microphone support, shader support, OpenGL support and 1.21.x support. Dark planned milestones: Forge support, 1.20.x support, NeoForge support, .mrpack imports, 1.19.x support, 1.18.x support, 1.17.x support, 1.16.x support and older versions.</desc>',
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

    text(76, 92, 'ProsperoCraft', 58, '#F4F6F4', True)
    text(79, 171, 'Roadmap', 28, muted)

    # Continuous four-row road, sampled from cubic curves for both formats.
    road = [(258 + i * 1284 / 100, 550) for i in range(101)]
    def curve(p0, p1, p2, p3):
        for i in range(1, 101):
            t=i/100; u=1-t
            road.append(tuple(u**3*p0[k]+3*u*u*t*p1[k]+3*u*t*t*p2[k]+t**3*p3[k] for k in (0,1)))
    curve((1542,550),(1760,550),(1760,910),(1542,910))
    road.extend((1542-i*1284/100,910) for i in range(1,101))
    curve((258,910),(40,910),(40,1270),(258,1270))
    road.extend((258+i*1284/100,1270) for i in range(1,101))
    curve((1542,1270),(1760,1270),(1760,1630),(1542,1630))
    road.extend((1542-i*428/100,1630) for i in range(1,101))
    line(road, '#35403A', 3)
    line(road[:101], '#A9B6AD', 3)
    for x,y,direction in [(940,550,1),(870,910,-1),(720,1270,1),(1350,1630,-1)]:
        line([(x-7*direction,y-6),(x,y),(x-7*direction,y+6)], muted, 2)

    def card(x, y, title, done, road_y, number):
        w,h=364,158; center=x+w/2
        line([(center,y+h),(center,road_y-12)], '#35403A', 2)
        if not done:
            rect(x-1,y-1,w+2,h+2,'#303A34',21)
        rect(x,y,w,h,'#F4F6F3' if done else '#1A211D',20)
        circle(center,road_y,11,bg)
        circle(center,road_y,7,'#F4F6F3' if done else '#68786D')
        status = 'DONE' if done else 'PLANNED'
        if number:
            status = f'{number:02d} / {status}'
        text(x+26,y+23,status,13,
             '#617168' if done else '#84958A')
        for i,label in enumerate(title):
            text(x+26,y+64+i*37,label,30,ink if done else '#D0D9D2',True)

    xs=[76,504,932,1360]
    completed=[['Full 26.x.x support'],['Microphone support'],['Shader support'],['OpenGL support']]
    # The first two longer labels fit on two lines at the same readable size.
    completed[0]=['Full 26.x.x','support']
    completed[1]=['Microphone','support']
    for x,title in zip(xs,completed): card(x,330,title,True,550,0)
    milestones = [
        '1.21.x support', 'Forge support', '1.20.x support', 'NeoForge support',
        '.mrpack imports', '1.19.x support', '1.18.x support', '1.17.x support',
        '1.16.x support', 'Older versions',
    ]
    for index, title in enumerate(milestones):
        row, column = divmod(index, 4)
        x = xs[3-column] if row % 2 == 0 else xs[column]
        card(x,690+row*360,[title],title == '1.21.x support',910+row*360,index+1)
    circle(1114,1630,4,'#84958A')
    circle(84,1740,5,'#F4F6F3')
    text(101,1730,'Completed',18,muted)
    circle(256,1740,5,'#68786D')
    text(273,1730,'Planned',18,muted)
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'prosperocraft-roadmap.svg').write_text('\n'.join(svg+['</svg>'])+'\n')
    canvas.resize((width,height),Image.Resampling.LANCZOS).save(a.output/'prosperocraft-roadmap.png',optimize=True)
    print(a.output/'prosperocraft-roadmap.png')


if __name__ == '__main__':
    main()
