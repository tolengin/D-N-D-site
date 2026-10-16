# -*- coding: utf-8 -*-
"""Blockout önizlemesinin üstüne parça adlarını ve POV panelinin kapladığı alanı yazar.
Çalıştırma (proje klasöründe): python araclar\\blockout_etiketle.py   (detaylı model için: ... blockout_etiketle.py detay)
Girdi: 3d/blockout-onizleme.png ve 3d/blockout-etiketler.json (ikisini de taverna_blockout_blender.py üretir)
Çıktı: 3d/blockout-onizleme-etiketli.png"""
import os, json
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
AD = sys.argv[1] if len(sys.argv) > 1 else 'blockout'          # 'blockout' ya da 'detay'
GIRDI = {'blockout': 'blockout-onizleme.png', 'detay': 'detay-ustten.png'}[AD]
im = Image.open(os.path.join(KOK, '3d', GIRDI)).convert('RGB')
with open(os.path.join(KOK, '3d', f'{AD}-etiketler.json'), encoding='utf-8') as f:
    veri = json.load(f)
d = ImageDraw.Draw(im)
W_, H_ = im.size
try:
    yazi = ImageFont.truetype('arialbd.ttf', 24)
except OSError:
    yazi = ImageFont.load_default()

# POV paneli (sitede): sol şerit, sahnenin yukarıdan aşağıya tamamı, genişliğin %31,64'ü (9:16)
ph = H_ - 4; pw = 0.3164 * W_; px = 0.0018 * W_; py = 2
mavi = (120, 200, 255)
for i in range(0, int(ph), 24):
    for x in (px, px + pw): d.line([(x, py + i), (x, py + min(i + 12, ph))], fill=mavi, width=4)
for i in range(0, int(pw), 24):
    for y in (py, py + ph): d.line([(px + i, y), (px + min(i + 12, pw), y)], fill=mavi, width=4)

def yaz(metin, x, y, renk=(255, 244, 220)):
    kutu = d.textbbox((x, y), metin, font=yazi, anchor='mm')
    d.rectangle([kutu[0] - 7, kutu[1] - 4, kutu[2] + 7, kutu[3] + 4], fill=(20, 14, 10))
    d.text((x, y), metin, font=yazi, fill=renk, anchor='mm')

for e in veri['etiketler']:
    yaz(e['metin'], e['x'] * W_, e['y'] * H_)
yaz('POV paneli burada (sitede)', px + pw / 2, H_ / 2 - 20, mavi)
yaz('KUZEY ↑', W_ - 90, 30, (255, 210, 120))
yaz(f"Oda: {veri['oda_m'][0]} × {veri['oda_m'][1]} m", 150, H_ - 26, (255, 210, 120))
im.save(os.path.join(KOK, '3d', GIRDI.replace('.png', '-etiketli.png')))
print('etiketli önizleme yazıldı')
