# POV panel görsellerini hazırlar: arka plan + macentası silinmiş el kareleri (şeffaf webp).
import os, sys
import numpy as np
from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # proje klasörü (araclar/ bir üstü)
SRC, DST = os.path.join(SITE, 'gorseller'), os.path.join(SITE, 'masa')
CROP_TOP = 11                      # 1792x2400 -> 1792x2389 (tam 3:4)
SIZE = (600, 800)
SHIFT = {'pov-el-3-acik': 55}      # sağa kaydırma (kaynak piksel): kolu el-3 ile hizalar

def load(name):
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    return im.crop((0, CROP_TOP, im.width, im.height))

def key_out(im, strong=False):
    a = np.asarray(im).astype(np.float32)
    # gerçek macenta tonu: köşelerden örnek
    c = np.concatenate([a[:40, :40].reshape(-1, 3), a[:40, -40:].reshape(-1, 3)])
    K = np.median(c, axis=0)
    Kd = min(K[0] - K[1], K[2] - K[1])
    d = np.minimum(a[..., 0] - a[..., 1], a[..., 2] - a[..., 1])          # pikselin "macentalığı"
    t0 = 12.0
    alpha = np.clip((Kd - d) / (Kd - t0), 0, 1)
    alpha[alpha < 0.03] = 0
    alpha[alpha > 0.985] = 1
    # renk ayrıştırma: P = aF + (1-a)K  ->  F = (P - (1-a)K) / a
    al = np.maximum(alpha, 1e-3)[..., None]
    F = (a - (1 - alpha[..., None]) * K) / al
    F = np.clip(F, 0, 255)
    # kalan pembe tonu temizle: R ve B, G'den fazlaysa fazlası atılır
    m = np.minimum(F[..., 0] - F[..., 1], F[..., 2] - F[..., 1])
    m = np.clip(m, 0, None)[..., None]
    F[..., 0:1] -= m; F[..., 2:3] -= m
    # Yarı saydam piksellerde (bulanık iz, kenarlar) macentayla karışmış pembe-kırmızı ton:
    # mavi yeşilden fazla olamaz, kırmızının yeşilden fazlası saydamlıkla orantılı kısılır,
    # ve renk saydamlık azaldıkça kahve-griye çekilir.
    # strong (bulanık el-1): macentayla karışmış yoğun bant da "yarı saydam" sayılır ve renk daha çok griye çekilir.
    # Bandı yakalamak için kaynakta yeşilin kırmızı ve maviden belirgin düşük olduğu pikseller de eklenir.
    semi = (alpha > 0) & (alpha < 0.97)
    w = np.clip((1 - alpha) * 1.6, 0, 1)                                  # ne kadar saydamsa o kadar
    R, G, B = F[..., 0], F[..., 1], F[..., 2]
    B2 = np.minimum(B, G)
    R2 = np.minimum(R, G + 45 * (1 - w))
    Y = 0.3 * R2 + 0.59 * G + 0.11 * B2
    warm = np.dstack([Y * 1.08, Y, Y * 0.86])                             # nötr değil, hafif sıcak gri: kahve tonlu masa üstünde sırıtmasın
    clean = np.dstack([R2, G, B2]) * (1 - w[..., None] * 0.7) + warm * (w[..., None] * 0.7)
    F = np.where(semi[..., None], clean, F)
    if strong:
        # Bulanık kare: tonu pembe-mor-bordo olan pikseller (ten ve deri 15–35° civarındadır) kolluğun kahve tonuna çevrilir.
        # Parlaklık korunur; ağırlık tona göre yumuşakça artar, sert kenar oluşmaz.
        mx, mn = F.max(axis=2), F.min(axis=2)
        sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-3), 0)
        R, G, B = F[..., 0], F[..., 1], F[..., 2]
        hue = (np.degrees(np.arctan2(np.sqrt(3) * (G - B), 2 * R - G - B)) + 360) % 360
        dist = np.minimum(np.abs(hue - 330), 360 - np.abs(hue - 330))   # 330° = pembe; 0° kırmızıya 30°, 300° mora 30°
        wt = np.clip((48 - dist) / 30, 0, 1) * np.clip(sat * 3, 0, 1)     # 18°'den yakınsa tam, 48°'den uzaksa hiç
        Y = 0.3 * R + 0.59 * G + 0.11 * B
        brown = np.dstack([Y * 1.18, Y * 0.97, Y * 0.78])
        F = F * (1 - wt[..., None]) + brown * wt[..., None]
    F[alpha == 0] = 0
    out = np.dstack([np.clip(F, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

def shift(im, dx):
    canvas = Image.new('RGBA', im.size, (0, 0, 0, 0))
    canvas.paste(im.crop((0, 0, im.width - dx, im.height)), (dx, 0))
    return canvas

SMALL = {'pov-el-1': (420, 560)}   # bulanık kare: düşük çözünürlük fark edilmez, dosya küçülür (CSS aynı boyuta büyütür)

def resize(im, n):
    return im.convert('RGBa').resize(SMALL.get(n, SIZE), Image.LANCZOS).convert('RGBA')

def save(im, name, q, **kw):
    p = os.path.join(DST, name + '.webp')
    im.save(p, 'WEBP', quality=q, method=6, **kw)
    return os.path.getsize(p) // 1024

bg = load('pov-masa').resize((900, 1200), Image.LANCZOS)
print('pov-masa', save(bg, 'pov-masa', 80), 'KB')
for n in ['pov-el-1b', 'pov-el-2', 'pov-el-3', 'pov-el-3-acik', 'pov-el-5']:
    if not os.path.exists(os.path.join(SRC, n + '.jpg')):
        print(n, 'YOK'); continue
    im = key_out(load(n), strong=(n == 'pov-el-1'))
    if n in SHIFT: im = shift(im, SHIFT[n])
    im = resize(im, n)
    q = 82
    while True:
        kb = save(im, n, q, alpha_quality=85)
        if kb < 60 or q <= 50: break
        q -= 6
    print(n, kb, 'KB', 'kalite', q)

