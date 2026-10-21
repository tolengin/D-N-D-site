# -*- coding: utf-8 -*-
"""
Hazır karakter portrelerini site için hazırlar (yol haritası 15).
Girdi:  gorseller/karakter/<ad>.png|jpg|webp   (Nano Banana 2 çıktıları; promptlar: promptlar/karakter-portreleri.txt)
        adlar: buyucu-1 … buyucu-4, paladin-1 … paladin-4
Çıktı:  masa/karakter/<ad>.webp                 480×600 (4:5), ortadan kırpılmış; kart, kağıt ve isimlik bundan kesilir
Çalıştırma (proje klasöründe):  python araclar\\karakter_hazirla.py
Gerekenler: Python, Pillow.
"""
import pathlib
from PIL import Image

KOK = pathlib.Path(__file__).resolve().parent.parent
HAM, CIKTI = KOK / 'gorseller' / 'karakter', KOK / 'masa' / 'karakter'
EN, BOY = 480, 600                                       # 4:5

CIKTI.mkdir(parents=True, exist_ok=True)
for f in sorted(HAM.glob('*')):
    if f.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
        continue
    im = Image.open(f).convert('RGB')
    # 4:5'e ortadan kırp (görsel zaten 4:5 üretildiyse dokunulmaz); yüz üst yarıda olduğu için dikey kırpma üstten yapılır
    hedef_oran = EN / BOY
    if im.width / im.height > hedef_oran:
        g = round(im.height * hedef_oran); l = (im.width - g) // 2
        im = im.crop((l, 0, l + g, im.height))
    elif im.width / im.height < hedef_oran:
        y = round(im.width / hedef_oran); t = (im.height - y) // 4
        im = im.crop((0, t, im.width, t + y))
    im = im.resize((EN, BOY), Image.LANCZOS)
    hedef = CIKTI / (f.stem.lower() + '.webp')
    im.save(hedef, 'WEBP', quality=84, method=6)
    print(f'{hedef.name:16} {hedef.stat().st_size // 1024:3} KB')
