# -*- coding: utf-8 -*-
"""
Hazır düşmanların görsellerini site için hazırlar.
Girdi:  gorseller/npc/<ad>.png|jpg|webp   (Nano Banana 2 çıktıları; ad: goblin, ork, iskelet, haydut, kurt)
Çıktı:  masa/npc/<ad>.webp                256×256, ortadan kare kırpılmış (sitede yuvarlak kesilir)
Çalıştırma (proje klasöründe):  python araclar\\npc_hazirla.py
Gerekenler: Python, Pillow.
Yeni bir hazır düşman eklemek: görselini gorseller/npc/'ye koy, index.html'deki NPC_HAZIR listesine aynı adla ekle.
"""
import pathlib
from PIL import Image

KOK = pathlib.Path(__file__).resolve().parent.parent
HAM, CIKTI = KOK / 'gorseller' / 'npc', KOK / 'masa' / 'npc'
BOY = 256

CIKTI.mkdir(parents=True, exist_ok=True)
for f in sorted(HAM.glob('*')):
    if f.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
        continue
    im = Image.open(f).convert('RGB')
    k = min(im.size)                                     # ortadan kare: yüz görselin ortasında üretildi
    l, t = (im.width - k) // 2, (im.height - k) // 2
    im = im.crop((l, t, l + k, t + k)).resize((BOY, BOY), Image.LANCZOS)
    hedef = CIKTI / (f.stem.lower() + '.webp')
    im.save(hedef, 'WEBP', quality=84, method=6)
    print(f'{hedef.name:16} {hedef.stat().st_size // 1024:3} KB')
