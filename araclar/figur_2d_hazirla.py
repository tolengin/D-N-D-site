# -*- coding: utf-8 -*-
"""
FİGÜR KARELERİ — siteye hazırlar (siteye yüklenmez).
Önce Blender betiği çalışmış olmalı (araclar/figur_2d_blender.py → 3d/fig2d/*.png).
Çalıştırma:  python araclar\\figur_2d_hazirla.py

Saydam .png kareleri masa/fig2d/ klasörüne .webp olarak yazar. Kareler kırpılmaz: resmin ortası koltuğun yer noktasıdır.
(2026-10-15'e kadar bu iş taverna_2d_hazirla.py'deydi; o betik taverna resimlerini de hazırlıyordu, gereksizler/ içinde.)
"""
import pathlib
import cv2

KOK = pathlib.Path(__file__).resolve().parent.parent
HAM, CIKTI = KOK / '3d' / 'fig2d', KOK / 'masa' / 'fig2d'
CIKTI.mkdir(exist_ok=True)
toplam = 0
for p in sorted(HAM.glob('*.png')):
    yol = CIKTI / (p.stem + '.webp')
    cv2.imwrite(str(yol), cv2.imread(str(p), cv2.IMREAD_UNCHANGED), [cv2.IMWRITE_WEBP_QUALITY, 85])
    toplam += yol.stat().st_size
print('fig2d:', len(list(CIKTI.glob('*.webp'))), 'kare,', round(toplam / 1024), 'KB')
