#!/usr/bin/env python3
"""Generate icon textures and QR; requires Pillow13,cairosvg2.9.1,qrcode8.2."""
from pathlib import Path
import sys,hashlib,json,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.tools/ui-python'))
import cairosvg,qrcode
from PIL import Image
root=Path(__file__).resolve().parents[1];dest=root/'assets/launcher-icons'
manifest=json.loads((dest/'attribution.json').read_text());files=manifest['files'];names=manifest['names']
pixels=[];pins={}
for i,name in enumerate(files):
 if name is None:im=Image.open(root/'assets/branding/ProsperoCraftTransparent.png').convert('RGBA').resize((72,72),Image.Resampling.LANCZOS)
 else:
  src=dest/f'{name}.svg';pins[src.name]=hashlib.sha256(src.read_bytes()).hexdigest();cairosvg.svg2png(url=str(src),write_to=str(dest/f'{name}.png'),output_width=72,output_height=72);im=Image.open(dest/f'{name}.png').convert('RGBA')
 pixels.append([r|(g<<8)|(b<<16)|(a<<24)for r,g,b,a in im.getdata()])
header='// Generated from pinned Prism/MultiMC and original replacement icons; see assets/launcher-icons/attribution.json.\n#pragma once\n#include <cstdint>\nnamespace prospero_icons {\ninline constexpr unsigned count='+str(len(files))+';\ninline constexpr std::uint32_t pixels[count][72*72]={\n'
for row in pixels:header+='{'+','.join(hex(v)+'u'for v in row)+'},\n'
header+='};\n}\n';(root/'client/launcher/instance_icons.hpp').write_text(header)
qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4);qr.add_data('https://www.microsoft.com/link');qr.make(fit=True);m=qr.get_matrix();(root/'client/launcher/login_qr.hpp').write_text('// QR encodes exactly https://www.microsoft.com/link; generated with qrcode8.2.\n#pragma once\nnamespace prospero_qr {\ninline constexpr int size='+str(len(m))+';\ninline constexpr char modules[]="'+''.join('1'if c else'0'for row in m for c in row)+'";\n}\n');qr.make_image().save(dest/'microsoft-link-qr.png')
print('Generated',len(files),'icons and fixed Microsoft-link QR')
