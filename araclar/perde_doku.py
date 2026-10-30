# -*- coding: utf-8 -*-
"""
DM PERDESİNİN DOKUSU (2026-10-29; siteye yüklenmez, çıktısı perde_blender.py ile masa/perde.glb'nin içine girer)
Kullanıcının örnekleri (proje kökünde perde-1/2/3): yakma işi motifli sıcak tahta (1), DM'e bakan yüzde çerçeveli
kâğıtlar (2), kalın tahta, kara demir menteşe ve perçinler (3). Bu betik tek bir doku sayfası çizer (2048×1024):
  üst sıra : orta kanadın önü (oyunculara bakan; amblem, "KERVANSARAY" şeridi, köşe süsleri), yan kanadın önü (d20, sarmaşık),
             çerçeve tahtası, demir
  alt sıra : DM'e bakan kâğıtlar: sol (zorluk dereceleri), orta (durumlar), sağ (siper, avantaj)
Tahta boyalı tarzda çizilir (hanın dokularıyla aynı his: uzun damarlar, birkaç ton basamağı, budaklar); motifler yakılmış
gibi koyu, kenarları hafif yanık. Kâğıtlarda sitenin kendi Türkçe terimleri (index.html CONDS).

Çalıştırma (proje klasöründen):  python araclar\\perde_doku.py   →  3d/perde/perde-doku.png (+ perde-onizleme.jpg)
Ölçüler perde_blender.py ile ortak (PERDE): kanat boyları, çerçeve eni; 1 m = PX piksel.
"""
import math, pathlib
import numpy as np
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:                                    # Blender'ın Python'unda Pillow yok: perde_blender.py yalnızca ölçüleri okur
    Image = None

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / '3d' / 'perde'
CIKTI.mkdir(parents=True, exist_ok=True)

# Ölçüler (m) ve doku sayfasındaki yerler (piksel: x0, y0, en, boy; y aşağı doğru). perde_blender.py aynılarını okur.
PERDE = dict(H=0.26, K=0.022, W_orta=0.32, W_yan=0.20, cerceve=0.022)
PX = 500 / PERDE['H']                                  # 1 m kaç piksel (kanadın boyu 500 piksel)
SAYFA = (2048, 1024)
YER = {
    'on_orta': (0, 0, round(PERDE['W_orta'] * PX), 500),
    'on_yan': (616, 0, round(PERDE['W_yan'] * PX), 500),
    'ahsap': (1004, 0, 520, 500),                       # çerçeve, kenarlar, ayaklar
    'demir': (1528, 0, 256, 256),
    'arka_sol': (616, 512, round(PERDE['W_yan'] * PX), 500),
    'arka_orta': (0, 512, round(PERDE['W_orta'] * PX), 500),
    'arka_sag': (1004, 512, round(PERDE['W_yan'] * PX), 500),
}
CER = round(PERDE['cerceve'] * PX)                     # çerçevenin piksel eni (altında kalan yer görünmez)
YAZI = 'C:/Windows/Fonts/'
YANIK, YANIK_KENAR = np.array([0.20, 0.10, 0.05]), np.array([0.36, 0.19, 0.09])
MUREKKEP, BASLIK = (58, 40, 26), (120, 40, 26)


def gurultu(rng, w, h, gw, gh):
    a = (rng.random((max(gh, 2), max(gw, 2))) * 255).astype(np.uint8)
    return np.asarray(Image.fromarray(a).resize((w, h), Image.BICUBIC), np.float32) / 255


def ahsap(w, h, acik, koyu, tohum, bant=34, budak=2):
    """Boyalı tahta: yatay damarlar (gürültüyle bükülen bantlar), 5 ton basamağı, birkaç budak, hafif fırça yumuşaklığı."""
    rng = np.random.default_rng(tohum)
    n = 0.5 * gurultu(rng, w, h, w // 170, h // 6) + 0.3 * gurultu(rng, w, h, w // 60, h // 14) + 0.2 * gurultu(rng, w, h, w // 22, h // 40)
    y = np.arange(h, dtype=np.float32)[:, None] / h
    x = np.arange(w, dtype=np.float32)[None, :] / w
    egri = np.zeros((h, w), np.float32)
    for _ in range(budak):                                # budakların çevresinde damar kıvrılır
        bx, by, br = rng.uniform(0.15, 0.85), rng.uniform(0.15, 0.85), rng.uniform(0.04, 0.07)
        d = np.sqrt(((x - bx) * w / h) ** 2 + (y - by) ** 2)
        egri += np.exp(-(d / (br * 2.2)) ** 2) * np.sign(y - by) * 0.06
        n = np.where(d < br * 0.45, n * 0.35, n)          # budağın ortası koyu
    t = np.sin(((y + egri) * bant + n * 2.6) * 2 * np.pi) * 0.5 + 0.5
    genis = gurultu(rng, w, h, 3, 2)                                       # tahtanın geniş ton farkı (boyalı)
    v = np.clip(0.55 * n + 0.22 * t ** 2.2 + 0.35 * (genis - 0.5) + 0.12, 0, 1)
    v = np.round(v * 5) / 5                               # ton basamakları (boyalı)
    img = koyu[None, None] * (1 - v[..., None]) + acik[None, None] * v[..., None]
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.3))
    return np.asarray(im, np.float32) / 255


def yak(taban, maske):
    """Yakma işi: maske (0…1) koyu yanığa, çevresi hafif kararır."""
    m = np.asarray(maske, np.float32) / 255
    hale = np.asarray(maske.filter(ImageFilter.GaussianBlur(4)), np.float32) / 255
    out = taban * (1 - 0.35 * np.clip(hale * 1.6, 0, 1))[..., None] + YANIK_KENAR * (0.35 * np.clip(hale * 1.6, 0, 1))[..., None]
    return out * (1 - m[..., None]) + YANIK * m[..., None]


class Ciz:
    """2 kat büyük maskeye çizer (kenarlar yumuşak çıksın), sonra küçültür."""
    def __init__(self, w, h, k=2):
        self.k = k; self.im = Image.new('L', (w * k, h * k), 0); self.d = ImageDraw.Draw(self.im)

    def P(self, *xy): return [(x * self.k, y * self.k) for x, y in xy]
    def cizgi(self, pts, en): self.d.line(self.P(*pts), fill=255, width=round(en * self.k), joint='curve')
    def daire(self, cx, cy, r, en): k = self.k; self.d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], outline=255, width=round(en * k))
    def dolu(self, pts): self.d.polygon(self.P(*pts), fill=255)
    def nokta(self, cx, cy, r): k = self.k; self.d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=255)

    def yazi(self, cx, cy, metin, boy, kalin=True):
        f = ImageFont.truetype(YAZI + ('constanb.ttf' if kalin else 'constan.ttf'), round(boy * self.k))
        self.d.text((cx * self.k, cy * self.k), metin, fill=255, font=f, anchor='mm')

    def kucuk(self, w, h): return self.im.resize((w, h), Image.LANCZOS)


def d20(c, cx, cy, r, en, sayi=True):
    """Önden bakınca yirmi yüzlü zar: altıgen, ortada üçgen, köşelerden yüzeylere çizgiler; ortada 20."""
    alt = [(cx + r * math.sin(math.radians(60 * i)), cy - r * math.cos(math.radians(60 * i))) for i in range(6)]
    uc = [(cx + r * 0.58 * math.sin(math.radians(120 * i)), cy - r * 0.58 * math.cos(math.radians(120 * i)) + r * 0.08) for i in range(3)]
    c.cizgi(alt + [alt[0]], en); c.cizgi(uc + [uc[0]], en)
    for i in range(6):                                    # altıgenin her köşesi en yakın üçgen köşelerine
        a = alt[i]
        for u in uc:
            if math.dist(a, u) < r * 0.95: c.cizgi([a, u], en * 0.8)
    if sayi: c.yazi(cx, cy + r * 0.12, '20', r * 0.36)


def kivrim(c, x, y, sx, sy, olc, en):
    """Köşe süsü: köşeden çıkan iki sarmal kıvrım ve bir yaprak (sx, sy: köşenin yönü, ±1)."""
    for yon in (0, 1):
        pts = []
        for i in range(36):
            t = i / 35; a = t * 4.2; r = olc * (1 - 0.75 * t)
            ux, uy = (math.cos(a) * r, math.sin(a) * r) if yon == 0 else (math.sin(a) * r, math.cos(a) * r)
            bx, by = (olc * 1.15, olc * 0.25) if yon == 0 else (olc * 0.25, olc * 1.15)
            pts.append((x + sx * (bx - ux * 0.55), y + sy * (by - uy * 0.55)))
        c.cizgi([(x + sx * 4, y + sy * 4)] + pts, en)
    lx, ly = x + sx * olc * 0.9, y + sy * olc * 0.9                     # köşegendeki yaprak
    c.dolu([(lx - sx * olc * 0.35, ly - sy * olc * 0.35), (lx + sx * olc * 0.05, ly - sy * olc * 0.25), (lx + sx * olc * 0.25, ly + sy * olc * 0.25),
            (lx - sx * olc * 0.25, ly + sy * olc * 0.05)])


def yaprak(c, px, py, dx, dy, L, W):
    """(px, py)'den (dx, dy) yönünde L boyunda, W enli damla yaprak."""
    nx, ny = -dy, dx
    c.dolu([(px, py), (px + dx * L * 0.35 + nx * W, py + dy * L * 0.35 + ny * W), (px + dx * L * 0.75 + nx * W * 0.6, py + dy * L * 0.75 + ny * W * 0.6),
            (px + dx * L, py + dy * L), (px + dx * L * 0.75 - nx * W * 0.6, py + dy * L * 0.75 - ny * W * 0.6),
            (px + dx * L * 0.35 - nx * W, py + dy * L * 0.35 - ny * W)])


def yaprakli_dal(c, cx, cy, R, a0, a1, yon, en, n=7):
    """Halkanın yanında defne dalı: yay boyunca sap, iki yana sapa 35° açıyla uzun yapraklar (uca doğru küçülür)."""
    sap = [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / 30)), cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / 30))) for i in range(31)]
    c.cizgi(sap, en)
    for i in range(n):
        t = (i + 0.6) / (n + 0.4); a = math.radians(a0 + (a1 - a0) * t)
        px, py = cx + R * math.cos(a), cy + R * math.sin(a)
        tx, ty = -math.sin(a) * yon, math.cos(a) * yon                      # sapın gidiş yönü (dalın ucuna doğru)
        rx, ry = math.cos(a), math.sin(a)                                    # dışarı
        L = 24 * (1 - 0.4 * t)
        for dis in (1, -1):
            dx, dy = tx * 0.82 + rx * dis * 0.57, ty * 0.82 + ry * dis * 0.57
            yaprak(c, px, py, dx, dy, L, L * 0.28)
    ax, ay = sap[-1]; tx, ty = -math.sin(math.radians(a1)) * yon, math.cos(math.radians(a1)) * yon
    yaprak(c, ax, ay, tx, ty, 16, 4.5)                                       # dalın ucunda tek yaprak


def serit(c, cx, cy, en_, boy, metin, cizgi):
    """Altta katlanmış uçlu şerit ve içinde yazı."""
    w, h = en_ / 2, boy / 2; e = 18
    ana = [(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h), (cx - w, cy + h)]
    c.cizgi(ana + [ana[0]], cizgi)
    for s in (-1, 1):                                                       # uçlar: arkaya katlanan, çatallı kuyruk
        x0 = cx + s * w
        kuyruk = [(x0, cy - h + 8), (x0 + s * e * 2.2, cy - h + 8), (x0 + s * e * 1.4, cy + 4), (x0 + s * e * 2.2, cy + h + 10), (x0, cy + h + 10)]
        c.cizgi(kuyruk, cizgi)
    c.yazi(cx, cy + 2, metin, boy * 0.6)


def on_orta():
    x0, y0, w, h = YER['on_orta']
    taban = ahsap(w, h, np.array([0.80, 0.56, 0.33]), np.array([0.55, 0.33, 0.17]), 3, bant=20)
    c = Ciz(w, h)
    cx, cy, R = w / 2, h * 0.44, 118
    c.daire(cx, cy, R, 5); c.daire(cx, cy, R - 11, 3)
    for i in range(36):                                                    # halkanın arasında çentikler, 8 yerde baklava
        a = math.radians(i * 10)
        if i % 9 == 0:
            p = [(cx + (R - 5.5 + d * 6) * math.cos(a + s * 0.06), cy + (R - 5.5 + d * 6) * math.sin(a + s * 0.06)) for d, s in ((1, 0), (0, 1), (-1, 0), (0, -1))]
            c.dolu([(cx + (R + 1) * math.cos(a), cy + (R + 1) * math.sin(a)), (cx + (R - 5.5) * math.cos(a + 0.07), cy + (R - 5.5) * math.sin(a + 0.07)),
                    (cx + (R - 12) * math.cos(a), cy + (R - 12) * math.sin(a)), (cx + (R - 5.5) * math.cos(a - 0.07), cy + (R - 5.5) * math.sin(a - 0.07))])
        else:
            c.cizgi([(cx + (R - 9) * math.cos(a), cy + (R - 9) * math.sin(a)), (cx + (R - 2) * math.cos(a), cy + (R - 2) * math.sin(a))], 2.4)
    d20(c, cx, cy + 2, 74, 4.5)
    for s, (a0, a1) in ((-1, (118, 222)), (1, (62, -42))):                 # iki yanda defne dalı (alttan yukarı)
        yaprakli_dal(c, cx, cy, R + 22, a0, a1, s, 3.5)
    for i, (dx, dy, r) in enumerate(((0, -R - 34, 9), (-26, -R - 22, 4), (26, -R - 22, 4))):   # üstte hilal ve iki yıldız
        if i == 0:
            c.daire(cx + dx, cy + dy, r, 4)
        else:
            px, py = cx + dx, cy + dy
            c.dolu([(px, py - r * 2), (px + r * 0.5, py - r * 0.5), (px + r * 2, py), (px + r * 0.5, py + r * 0.5), (px, py + r * 2),
                    (px - r * 0.5, py + r * 0.5), (px - r * 2, py), (px - r * 0.5, py - r * 0.5)])
    serit(c, cx, h * 0.44 + R + 44, 330, 46, 'KERVANSARAY', 4)
    i0 = CER + 10
    for sx, sy, px, py in ((1, 1, i0, i0), (-1, 1, w - i0, i0), (1, -1, i0, h - i0), (-1, -1, w - i0, h - i0)):
        kivrim(c, px, py, sx, sy, 46, 3.5)
    return yak(taban, c.kucuk(w, h))


def on_yan():
    x0, y0, w, h = YER['on_yan']
    taban = ahsap(w, h, np.array([0.80, 0.56, 0.33]), np.array([0.55, 0.33, 0.17]), 7, bant=20, budak=1)
    c = Ciz(w, h)
    cx, cy = w / 2, h / 2
    d20(c, cx, cy, 58, 4)
    for s in (-1, 1):                                                       # zarın üstünde ve altında sarmaşık
        y_a, y_b = cy + s * 74, cy + s * (h / 2 - CER - 26)
        c.cizgi([(cx, y_a), (cx, y_b)], 3.5)
        for i in range(1, 5):
            yy = y_a + (y_b - y_a) * i / 5; yan = 1 if i % 2 else -1
            c.dolu([(cx, yy), (cx + yan * 16, yy - s * 6), (cx + yan * 26, yy + s * 6), (cx + yan * 10, yy + s * 8)])
        c.nokta(cx, y_b, 6)
    i0 = CER + 8
    for sx, sy, px, py in ((1, 1, i0, i0), (-1, 1, w - i0, i0), (1, -1, i0, h - i0), (-1, -1, w - i0, h - i0)):
        kivrim(c, px, py, sx, sy, 30, 3)
    return yak(taban, c.kucuk(w, h))


def kagit(ad, baslik_sat):
    """DM'e bakan kâğıt: parşömen zemin (lekeli, kenarları koyu), başlıklar kızıl, satırlar mürekkep, aralarında ince çizgi."""
    x0, y0, w, h = YER[ad]
    rng = np.random.default_rng(len(ad) * 7)
    n = 0.6 * gurultu(rng, w, h, 9, 11) + 0.4 * gurultu(rng, w, h, 40, 50)
    yy, xx = np.mgrid[0:h, 0:w]
    kenar = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / 40.0
    t = np.clip(0.85 + 0.15 * n - 0.25 * np.exp(-kenar), 0, 1)
    zem = np.array([0.93, 0.86, 0.70])[None, None] * t[..., None] + np.array([0.55, 0.42, 0.24])[None, None] * (1 - t[..., None])
    im = Image.fromarray((np.clip(zem, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    sol, sag = CER + 18, w - CER - 18
    y = CER + 22
    for tur, metin in baslik_sat:
        if tur == 'b':                                                    # başlık
            f = ImageFont.truetype(YAZI + 'constanb.ttf', 27)
            y += 8; d.text((w / 2, y + 14), metin, fill=BASLIK, font=f, anchor='mm'); y += 34
            d.line([(sol, y), (sag, y)], fill=BASLIK, width=2); y += 10
        elif tur == 's':                                                  # satır: "ad | değer"
            f = ImageFont.truetype(YAZI + 'constan.ttf', 21)
            a, b = metin.split('|') if '|' in metin else (metin, '')
            d.text((sol, y + 12), a.strip(), fill=MUREKKEP, font=f, anchor='lm')
            if b: d.text((sag, y + 12), b.strip(), fill=MUREKKEP, font=f, anchor='rm')
            y += 27; d.line([(sol, y), (sag, y)], fill=(170, 140, 100), width=1); y += 3
        elif tur == 'iki':                                                # iki sütun
            f = ImageFont.truetype(YAZI + 'constan.ttf', 21)
            a, b = metin
            d.text((sol, y + 12), a, fill=MUREKKEP, font=f, anchor='lm')
            d.text((w / 2 + 8, y + 12), b, fill=MUREKKEP, font=f, anchor='lm')
            y += 27
        elif tur == 'not':
            f = ImageFont.truetype(YAZI + 'constani.ttf' if pathlib.Path(YAZI + 'constani.ttf').exists() else YAZI + 'constan.ttf', 19)
            y += 6; d.text((w / 2, y + 11), metin, fill=MUREKKEP, font=f, anchor='mm'); y += 24
    return np.asarray(im, np.float32) / 255


DURUM = ['Kör', 'Büyülenmiş', 'Sağır', 'Korkmuş', 'Yakalanmış', 'Etkisiz', 'Görünmez',
         'Felçli', 'Taşlaşmış', 'Zehirlenmiş', 'Yerde', 'Bağlı', 'Sersemlemiş', 'Baygın']


def sayfa():
    S = np.zeros((SAYFA[1], SAYFA[0], 3), np.float32)

    def koy(ad, A):
        x0, y0, w, h = YER[ad]; S[y0:y0 + h, x0:x0 + w] = A[:h, :w]
    koy('on_orta', on_orta())
    koy('on_yan', on_yan())
    x0, y0, w, h = YER['ahsap']
    koy('ahsap', ahsap(w, h, np.array([0.56, 0.35, 0.19]), np.array([0.30, 0.17, 0.08]), 11, bant=18, budak=3))
    x0, y0, w, h = YER['demir']
    rng = np.random.default_rng(4)
    g = 0.7 * gurultu(rng, w, h, 8, 8) + 0.3 * gurultu(rng, w, h, 30, 30)
    koy('demir', np.array([0.13, 0.13, 0.15])[None, None] + (g[..., None] - 0.5) * np.array([0.08, 0.07, 0.06])[None, None])
    koy('arka_sol', kagit('arka_sol', [('b', 'ZORLUK'), ('s', 'Çok kolay | 5'), ('s', 'Kolay | 10'), ('s', 'Orta | 15'), ('s', 'Zor | 20'),
                                         ('s', 'Çok zor | 25'), ('s', 'Neredeyse imkânsız | 30'), ('b', 'SİPER'),
                                         ('s', 'Yarım | +2 AC'), ('s', 'Dörtte üç | +5 AC'), ('s', 'Tam | hedef olmaz')]))
    koy('arka_orta', kagit('arka_orta', [('b', 'DURUMLAR')] + [('iki', (DURUM[i], DURUM[i + 7])) for i in range(7)] +
                           [('not', 'Bitkinlik: her kademe d20 − 2'), ('b', 'ÖLÜM ZARI'), ('not', 'Tek başarı yeter · üç başarısızlık ölüm')]))
    koy('arka_sag', kagit('arka_sag', [('b', 'ZARLAR'), ('s', 'Avantaj | 2d20 yüksek'), ('s', 'Dezavantaj | 2d20 düşük'),
                                         ('s', 'Doğal 20 | kritik'), ('s', 'Doğal 1 | ıska'), ('b', 'IŞIK'), ('s', 'Parlak | görür'),
                                         ('s', 'Loş | dezavantaj'), ('s', 'Karanlık | kör')]))
    Image.fromarray((np.clip(S, 0, 1) * 255).astype(np.uint8)).save(CIKTI / 'perde-doku.png')
    Image.fromarray((np.clip(S, 0, 1) * 255).astype(np.uint8)).resize((1024, 512), Image.LANCZOS).save(CIKTI / 'perde-onizleme.jpg', quality=88)
    print('YAZILDI', CIKTI / 'perde-doku.png')


if __name__ == '__main__':
    sayfa()
