# -*- coding: utf-8 -*-
"""
ÇİMEN DOKUSU (kodla boyanmış, döşenebilir)  (2026-11-26)
=======================================================
Hanın dışındaki çayır için. Nano Banana yokken yer tutucu: yumuşak lekeler (dönemli gürültü: kenarları birbirine uyar)
+ kısa fırça darbeleri (açık ve koyu otlar, kenardan taşan darbe öbür kenardan girer). Elle boyanmış sitenin tarzına yakın.
Kullanıcı isterse Photopea / Krita'da kendisi boyayıp aynı adla değiştirebilir (1024 × 1024, döşenebilir).

Çalıştırma (proje klasöründe):  python araclar\\cimen_doku.py      →  3d/dokular/cimen.jpg
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIKTI = os.path.join(KOK, '3d', 'dokular', 'cimen.jpg')
N = 1024
rs = np.random.default_rng(7)

def donemli_gurultu(olcek):
    """Kenarları uyan gürültü: beyaz gürültünün düşük frekansları (FFT, dönemli)."""
    f = np.fft.fft2(rs.standard_normal((N, N)))
    ky, kx = np.meshgrid(np.fft.fftfreq(N), np.fft.fftfreq(N), indexing='ij')
    g = np.real(np.fft.ifft2(f * np.exp(-(kx ** 2 + ky ** 2) * (olcek ** 2))))
    return (g - g.min()) / (g.max() - g.min())

# Taban: koyu ve açık yeşil lekeler, aralarda sarımsı kuru ot
a, b, c = donemli_gurultu(60), donemli_gurultu(160), donemli_gurultu(20)
koyu, acik, kuru = np.array([46, 64, 30]), np.array([88, 112, 48]), np.array([122, 116, 62])
t = np.clip((0.6 * a + 0.4 * b - 0.25) * 1.6, 0, 1)[..., None]
renk = koyu * (1 - t) + acik * t
k = np.clip((c - 0.62) * 4, 0, 1)[..., None] * 0.55
renk = renk * (1 - k) + kuru * k
renk = np.round(renk / 6) * 6                                            # hafif basamaklı ton (boyalı his)
img = Image.fromarray(np.clip(renk, 0, 255).astype(np.uint8), 'RGB')

# Fırça darbeleri: kısa, hafif eğik otlar; 3 × 3 kopyaya çizilip ortası alınır (kenarlar döşenince birleşir)
buyuk = Image.new('RGB', (N * 3, N * 3))
for i in range(3):
    for j in range(3): buyuk.paste(img, (i * N, j * N))
d = ImageDraw.Draw(buyuk)
for _ in range(9000):
    x, y = rs.uniform(0, N), rs.uniform(0, N)
    boy = rs.uniform(10, 26); aci = np.radians(rs.uniform(-25, 25)); kal = int(rs.integers(2, 4))
    ton = rs.uniform()
    r = (34, 50, 22) if ton < 0.45 else ((104, 130, 58) if ton < 0.85 else (140, 134, 72))
    for ox in (0, N, 2 * N):
        for oy in (0, N, 2 * N):
            x0, y0 = x + ox, y + oy
            d.line([(x0, y0), (x0 + boy * np.sin(aci), y0 - boy * np.cos(aci))], fill=r, width=kal)
img = buyuk.crop((N, N, 2 * N, 2 * N)).filter(ImageFilter.GaussianBlur(0.7))
img.save(CIKTI, quality=90)
print('Yazıldı:', CIKTI)
