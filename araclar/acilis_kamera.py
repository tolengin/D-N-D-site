# -*- coding: utf-8 -*-
"""
AÇILIŞ KAMERASI (2026-11-26)
============================
Sitenin canlı 3D açılışında kameranın yolu: yoldaki tabela direğinden patikadan kapıya, giriş bölümünden geçitle salona,
sonra masanın üstüne yükselir. Kaba yolu kullanıcı Blender'da anahtar karelerle kurdu (3d/han/kamera-acilis-ham-2026-11-26.blend);
düzeltmeler (kullanıcının isteğiyle Claude): 135–180'deki salondan dönüp duvara bakış kalktı, kapının ve geçidin tam ortasından
geçer, hız dengelendi (dışarıda hızlı, kapıda ve içeride yavaş, başta yumuşak kalkış, sonda yumuşak duruş).

ANAHTAR tablosu kaynaktır: bir satırı değiştirip betiği yeniden çalıştırmak yeter. Konum DÜNYA koordinatı (m; (0, 0) oyun
masasının ortası, x doğu, y kuzey, z yukarı); bakış Blender kamerasının açıları: 'egim' = Rotation X (90 = ufka düz, küçüldükçe
aşağı bakar), 'yon' = Rotation Z (0 = kuzeye, −90 = doğuya). 'hiz' o noktadaki göreli hız.

Yol: anahtar noktalardan geçen yumuşak eğri (merkezcil Catmull-Rom); zaman: hızın tersinin yol boyunca toplamı.
Bakış açıları da yol boyunca aynı yumuşak eğriyle.

Çalıştırma (proje klasöründe; Blender gerekmez):  python araclar\\acilis_kamera.py
Çıktı: 3d/han/acilis-kamera.json (her kare: x, y, z, egim, yon). han_dis_blender.py bunu okuyup 'Kamera_Acilis'i kurar;
site bağlanınca aynı veri siteye gidecek.
"""
import json, math, os

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIKTI = os.path.join(KOK, '3d', 'han', 'acilis-kamera.json')
FPS, SURE = 30, 10.0                 # 300 kare (kullanıcı: 8 sn hızlıydı)
LENS, SENSOR = 34.2, 36.0            # kullanıcının seçtiği odak (mm); yatay görüş ~55°
KALKIS, DURUS = 0.9, 1.3             # yumuşak kalkış / duruş süresi (sn)

# (konum x, y, z), egim, yon, hiz      ← kullanıcının karesi (Blender karesi) ve değişiklik
ANAHTAR = [
    ((-28.28, -24.45, 1.42), 98.1, -13.7, 1.00),   # 1   tabela direğinin yanı, han arkada (kullanıcının)
    ((-24.45, -8.47, 1.34), 98.8, -48.1, 1.00),    # 45  patikada (kullanıcının)
    ((-19.76, -4.14, 1.41), 96.0, -76.7, 0.80),    # 90  sundurmanın önü (kullanıcının; biraz daha düz bakış)
    ((-12.87, -3.00, 1.55), 92.0, -92.0, 0.50),    # 127 kapının ortası (Y −2,4 → −3,0: taşa sürtünüyordu)
    ((-10.70, -3.00, 1.60), 93.0, -94.0, 0.55),    # 135 giriş bölümü, salon geçitten görünür (dönüş kalktı)
    ((-7.30, -3.00, 1.70), 95.0, -88.0, 0.60),     # 180 geçidin ortası (direk ile girişin duvarı arası)
    ((-4.00, -3.60, 3.00), 71.0, -48.0, 0.75),     # 205 salonda yükselir, masaya döner
    ((-1.56, -5.00, 6.55), 51.2, -12.8, 0.80),     # 240 masanın üstü (kullanıcının; site kamerasına sonra oturtulacak)
]

def catmull(p0, p1, p2, p3, t, alfa=0.5):
    """Merkezcil Catmull-Rom (aşırı dolanmaz). p: demet."""
    def d(a, b): return max(math.dist(a, b) ** alfa, 1e-4)
    t0, t1 = 0.0, d(p0, p1); t2 = t1 + d(p1, p2); t3 = t2 + d(p2, p3)
    u = t1 + (t2 - t1) * t
    def l(a, b, ta, tb): return tuple(((tb - u) * x + (u - ta) * y) / (tb - ta) for x, y in zip(a, b))
    a1, a2, a3 = l(p0, p1, t0, t1), l(p1, p2, t1, t2), l(p2, p3, t2, t3)
    b1, b2 = l(a1, a2, t0, t2), l(a2, a3, t1, t3)
    return l(b1, b2, t1, t2)

def egri(noktalar, n=60):
    """Bütün noktalardan geçen örnekler: [(parça no, parça içi t, nokta)]."""
    P = [noktalar[0]] + list(noktalar) + [noktalar[-1]]
    P[0] = tuple(2 * a - b for a, b in zip(noktalar[0], noktalar[1]))
    P[-1] = tuple(2 * a - b for a, b in zip(noktalar[-1], noktalar[-2]))
    out = []
    for i in range(len(noktalar) - 1):
        for k in range(n):
            out.append((i, k / n, catmull(P[i], P[i + 1], P[i + 2], P[i + 3], k / n)))
    out.append((len(noktalar) - 2, 1.0, noktalar[-1]))
    return out

konum = [a[0] for a in ANAHTAR]
bakis = [(a[1], a[2]) for a in ANAHTAR]
hiz = [a[3] for a in ANAHTAR]
ornek = egri(konum)
# yol uzunluğu
uz = [0.0]
for (_, _, a), (_, _, b) in zip(ornek, ornek[1:]): uz.append(uz[-1] + math.dist(a, b))
L = uz[-1]
# zaman: her küçük adımda süre = yol / hız; hız anahtarlar arasında yumuşak geçer, başta ve sonda sıfıra iner (rampa)
def yumusak(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
zaman = [0.0]
for j in range(1, len(ornek)):
    i, t, _ = ornek[j]
    v = hiz[i] + (hiz[i + 1] - hiz[i]) * yumusak(t)
    zaman.append(zaman[-1] + (uz[j] - uz[j - 1]) / v)
T = zaman[-1]
# kalkış ve duruş: gerçek zamanda hız başta sıfırdan yükselir, sonda sıfıra iner; 'ilerleme' gerçek zaman oranını iç zamana çevirir
N = 4000
hizp = []
for k in range(N + 1):
    x = k / N
    hizp.append(min(1.0, yumusak(x / (KALKIS / SURE)) if x < KALKIS / SURE else 1.0, yumusak((1 - x) / (DURUS / SURE)) if x > 1 - DURUS / SURE else 1.0) + 1e-3)
ilerleme = [0.0]
for k in range(1, N + 1): ilerleme.append(ilerleme[-1] + (hizp[k] + hizp[k - 1]) / 2)
ilerleme = [p / ilerleme[-1] for p in ilerleme]            # gerçek zaman oranı → "iç zaman" oranı

def bul(dizi, deger):
    lo, hi = 0, len(dizi) - 1
    while lo < hi:
        m = (lo + hi) // 2
        if dizi[m] < deger: lo = m + 1
        else: hi = m
    return max(lo, 1)

kareler = []
NK = int(round(FPS * SURE))
# bakış açıları için: her anahtarın yol üzerindeki "iç zamanı" (anahtar noktaya varış), açılar o zamana göre yumuşak eğriyle
an_zaman = [zaman[[j for j, o in enumerate(ornek) if o[0] == i and o[1] == 0.0][0]] if i < len(ANAHTAR) - 1 else T for i in range(len(ANAHTAR))]
def aci(t):
    i = min(max(bul(an_zaman, t) - 1, 0), len(ANAHTAR) - 2)
    f = (t - an_zaman[i]) / (an_zaman[i + 1] - an_zaman[i])
    P = [bakis[max(i - 1, 0)], bakis[i], bakis[i + 1], bakis[min(i + 2, len(bakis) - 1)]]
    # tek tip Catmull-Rom (açılar için yeterli), uçlarda aşmasın diye sınırlı
    def cr(a, b, c, d, t): return 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
    return tuple(cr(*(p[k] for p in P), f) for k in range(2))
for k in range(NK):
    x = k / (NK - 1)
    ic = ilerleme[min(int(round(x * N)), N)] * T              # iç zaman
    j = bul(zaman, ic)
    f = (ic - zaman[j - 1]) / max(zaman[j] - zaman[j - 1], 1e-9)
    p = tuple(a + (b - a) * f for a, b in zip(ornek[j - 1][2], ornek[j][2]))
    eg, yo = aci(ic)
    kareler.append([round(v, 4) for v in p] + [round(eg, 3), round(yo, 3)])

json.dump({'fps': FPS, 'lens': LENS, 'sensor': SENSOR, 'kareler': kareler}, open(CIKTI, 'w'), separators=(',', ':'))
hizlar = [math.dist(kareler[k][:3], kareler[k + 1][:3]) * FPS for k in range(NK - 1)]
print(f'Yol {L:.1f} m, {NK} kare; hız en çok {max(hizlar):.1f} m/sn, kapıda {hizlar[int(NK * 0.48)]:.1f} m/sn; yazıldı: {CIKTI}')
