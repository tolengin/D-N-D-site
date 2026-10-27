# -*- coding: utf-8 -*-
r"""Yeni hanın tepeden önizlemesine parça adlarını yazar.
Çalıştırma (proje klasöründe): python araclar\han_etiketle.py
Girdi: 3d/han/onizleme-ustten.png ve 3d/han/etiketler.json (ikisini de han_blockout_blender.py üretir)
Çıktı: 3d/han/onizleme-ustten-etiketli.png"""
import os, json
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KLASOR = os.path.join(KOK, '3d', 'han')
im = Image.open(os.path.join(KLASOR, 'onizleme-ustten.png')).convert('RGB')
with open(os.path.join(KLASOR, 'etiketler.json'), encoding='utf-8') as f:
    veri = json.load(f)
d = ImageDraw.Draw(im)
W_, H_ = im.size
try:
    yazi = ImageFont.truetype('arialbd.ttf', 26)
except OSError:
    yazi = ImageFont.load_default()

def yaz(metin, x, y, renk=(255, 244, 220)):
    kutu = d.textbbox((x, y), metin, font=yazi, anchor='mm')
    d.rectangle([kutu[0] - 7, kutu[1] - 4, kutu[2] + 7, kutu[3] + 4], fill=(20, 14, 10))
    d.text((x, y), metin, font=yazi, fill=renk, anchor='mm')

for e in veri['etiketler']:
    yaz(e['metin'], e['x'] * W_, e['y'] * H_)
yaz('KUZEY ↑', W_ - 90, 26, (255, 210, 120))
yaz(f"Salon: {veri['oda_m'][0]:g} × {veri['oda_m'][1]:g} m", 170, H_ - 22, (255, 210, 120))
im.save(os.path.join(KLASOR, 'onizleme-ustten-etiketli.png'))
print('etiketli önizleme yazıldı')
