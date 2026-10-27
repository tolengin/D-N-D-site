# -*- coding: utf-8 -*-
"""
Dokuları (texture) 3D sahne için hazırlar.
Girdi:  gorseller/dokular/*.jpg|png   (Nano Banana 2 çıktıları, büyük ham resimler)
Çıktı:  3d/dokular/<ad>.jpg          renk (biraz "girinti gölgesi" eklenmiş)
        3d/dokular/<ad>-normal.jpg   normal haritası: her pikselin hangi yöne baktığı (girinti/çıkıntı)
        3d/dokular/<ad>-puruz.jpg    pürüz haritası: beyaz = mat, siyah = parlak
Çalıştırma (proje klasöründe):  python araclar\\doku_hazirla.py
Gerekenler: Python, numpy, Pillow.

Ne yapar?
1) Döşenebilir yapar: doku yan yana dizilince dikiş görünmesin diye resmin karşılıklı kenar şeritleri üst üste konur ve
   ikisinin en çok benzediği yerden kıvrımlı bir kesim yolu bulunur (tahta aralığından, taş harcından geçer). Resim bu
   yüzden kenar başına ~%12 daralır, sonra hedef boya getirilir.
2) Renkten yükseklik tahmin eder: koyu yerler (derz, tahta aralığı, kırışık) çukur, açık yerler tümsek sayılır.
3) Yükseklikten normal haritası çıkarır. Taktik bu: 3D model dümdüz kalır ama ışık her pikselde "bu nokta şu yöne
   bakıyor" bilgisini kullanır; şömine ve mum ışığı taşın kenarında parlar, derzde kararır. Model ağırlaşmaz.
4) Girinti gölgesi (AO/oyuk): çukurlar renkte hafifçe koyulaştırılır; ışık hiç gelmeyen köşeler gibi.
5) Pürüz: koyu/çukur yerler daha mat, aşınmış açık yerler biraz daha parlak.
"""
import os
import numpy as np
from PIL import Image

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIRDI = os.path.join(KOK, 'gorseller', 'dokular')
CIKTI = os.path.join(KOK, '3d', 'dokular')
os.makedirs(CIKTI, exist_ok=True)

# ad: (hedef boy px, normal gücü, pürüz en az–en çok, girinti gölgesi gücü, çukur ayrıntı yarıçapı px)
AYAR = {
    'zemin-ahsap': (1024, 5.0, (0.55, 0.92), 0.45, 6),
    'masa-ahsap':  (1024, 3.5, (0.40, 0.78), 0.35, 5),
    'duvar-tas':   (1024, 7.0, (0.78, 0.97), 0.55, 10),
    'somine-tas':  (1024, 8.0, (0.75, 0.97), 0.60, 12),
    'deri':        (512,  3.0, (0.38, 0.72), 0.25, 4),
    # 2. tur (2026-10-15)
    'sarmasik':    (1024, 3.5, (0.35, 0.75), 0.55, 6),
    'saksi-toprak': (512, 2.5, (0.70, 0.95), 0.30, 4),
    'demir':       (512,  4.0, (0.40, 0.80), 0.40, 4),
    'cuval':       (512,  4.5, (0.85, 1.00), 0.35, 3),
    # 3. tur (2026-10-16, elle boyanmış tarz): yeni yüzeyler
    'duvar-siva':  (1024, 1.4, (0.80, 0.97), 0.10, 8),   # 2026-10-27: temizlikten sonra (çizgiler yok) girinti abartılıyordu: hafif
    'tas-blok':    (512,  6.0, (0.75, 0.95), 0.50, 6),
    'tas-altigen': (1024, 6.0, (0.70, 0.95), 0.50, 8),
    'dis-zemin':   (512,  6.0, (0.80, 0.97), 0.50, 8),
    # 4. tur (2026-10-21, yeni han; promptlar/doku-han.txt)
    'perde':          (512,  2.0, (0.85, 1.00), 0.25, 6),
    'pencere-kursun': (512,  3.0, (0.15, 0.45), 0.30, 4),
    'cati-sindira':   (512,  5.0, (0.75, 0.95), 0.45, 6),
}
# Boyalı dokularda derzlerin ve aralıkların koyuluğu zaten resimde çizili: betiğin eklediği girinti gölgesi bununla
# çarpılır (1 = eski gerçekçi dokulardaki gibi tam). Çok koyulaşırsa düşür.
AO_CARPAN = 0.4
# Düzenli desenler (altıgen ızgara): kıvrımlı kesim ızgaranın adımını bozuyordu (ortada baklava şeridi). Kesim şeridi tam
# bir desen adımı kadar seçilir (ham resimde ölçülen, px: yatay, dikey); üst üste gelen şeritler neredeyse aynı olur,
# ızgara bozulmaz. Sonuç kare olmaz; oran korunur (Blender'da tekrar boyu en × boy ayrı verilir: UVS).
DESEN = {'tas-altigen': (512, 342),
         'pencere-kursun': (538, 600),             # kurşun çizgileri bu şeritlerde örtüşüyor (2026-10-22, ölçüldü)
         'cati-sindira': (256, 320)}               # pul adımı 256 px, sıra ~216 px
# Tekrarı ele veren belirgin işaretlerin temizliği (2026-10-27, yeni han: duvarda tuğla lekeleri her 2,5 m'de sıra sıra
# diziliyordu). Döşemeden önce: kızıl kahve lekeler ve koyu mürekkep çizgiler (çatlak) çevresindeki sıvayla doldurulur
# (OpenCV inpaint); "duz" > 0 ise büyük ölçekli aydınlık farkı (ortası açık, kenarı koyu) o oranda düzleştirilir.
# ad: (kızıl leke eşiği r−b, çizgi eşiği (ortancadan ne kadar koyu), düzleştirme 0–1)
TEMIZLE = {'duvar-siva': (0.24, 0.24, 1.0)}
# Tek parça (kesik) görseller: macenta zemin silinir, kırpılır. ad: (en uzun kenar px, normal gücü)
KESIK = {'kalkan-1': (1024, 4.0), 'kalkan-2': (1024, 4.0), 'tabela': (1024, 4.0), 'sancak': (768, 2.0), 'yaprak-kartlari': (1024, 2.0),
         'post': (1024, 2.0)}                                        # post: şömine önündeki hayvan postu (2026-10-16)
# Çerçeveyi dolduran görseller: yalnızca küçültülür. ad: (genişlik px, normal gücü)
DOLU = {'harita': (1024, 1.5), 'gorev-panosu': (1024, 3.0), 'kitap-sirtlari': (1024, 3.0)}

def bul(ad):
    """Aynı adla birden çok dosya varsa (ör. eski zemin-ahsap.jpg ve yeni zemin-ahsap.png) en son kaydedileni alır."""
    adaylar = [p for p in (os.path.join(GIRDI, ad + uz) for uz in ('.jpg', '.jpeg', '.png', '.webp')) if os.path.exists(p)]
    return max(adaylar, key=os.path.getmtime) if adaylar else None

# ───────── Yardımcılar ─────────
def bulanik(a, sigma):
    """Kenarları sarmalayan (döşenebilir) Gauss bulanıklığı: frekans uzayında."""
    h, w = a.shape
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))

def kesim_yolu(E):
    """E (yükseklik × şerit genişliği) hata haritasında yukarıdan aşağı en az hatalı yol. Kenar sütunlarına değmez."""
    h, k = E.shape
    E = E.copy(); E[:, 0] = E[:, -1] = 1e18
    C = E.copy(); geri = np.zeros((h, k), int)
    for i in range(1, h):
        sol = np.r_[np.inf, C[i - 1, :-1]]; sag = np.r_[C[i - 1, 1:], np.inf]
        yig = np.stack([sol, C[i - 1], sag]); j = yig.argmin(0)
        C[i] += yig[j, np.arange(k)]; geri[i] = j - 1
    yol = np.zeros(h, int); yol[-1] = C[-1].argmin()
    for i in range(h - 1, 0, -1): yol[i - 1] = yol[i] + geri[i, yol[i]]
    return np.clip(yol, 1, k - 2)

def yatay_doseme(img, k):
    """Resmi yatayda döşenebilir yapar; genişlik k azalır."""
    h, w, _ = img.shape
    A, B = img[:, w - k:], img[:, :k]                     # sağ şerit, sol şerit
    yol = kesim_yolu(((A - B) ** 2).sum(2))
    maske = np.arange(k)[None, :] < yol[:, None]
    yeni_sol = np.where(maske[..., None], A, B)
    return np.concatenate([yeni_sol, img[:, k:w - k]], axis=1)

def doseme(img, oran=0.12):
    k = int(img.shape[1] * oran)
    img = yatay_doseme(img, k)
    img = yatay_doseme(img.transpose(1, 0, 2), k).transpose(1, 0, 2)
    return img

def boyut(img, w, h):
    return np.asarray(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), float) / 255

def kaydet(dizi, ad, kalite=88, gri=False):
    a = (np.clip(dizi, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(a, 'L' if gri else 'RGB').save(os.path.join(CIKTI, ad), quality=kalite, subsampling=0 if not gri else 2)

def haritalar(renk, guc, puruz, ao_guc, r):
    lum = renk @ np.array([0.2126, 0.7152, 0.0722])
    # Yükseklik: büyük ölçekli aydınlık farkları atılır (yalnızca küçük girinti/çıkıntı kalsın)
    yuk = lum - bulanik(lum, renk.shape[0] / 12)
    yuk = bulanik(yuk, 1.2)
    yuk = (yuk - yuk.mean()) / (yuk.std() + 1e-6)
    # Normal: yüksekliğin eğiminden (OpenGL/glTF düzeni: yeşil yukarı)
    dx = (np.roll(yuk, -1, 1) - np.roll(yuk, 1, 1)) / 2
    dy = (np.roll(yuk, 1, 0) - np.roll(yuk, -1, 0)) / 2
    s = guc / 10
    n = np.stack([-dx * s, -dy * s, np.ones_like(yuk)], 2)
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    normal = n * 0.5 + 0.5
    # Girinti gölgesi: çevresinden alçakta kalan yerler
    oyuk = np.clip(bulanik(yuk, r) - yuk, 0, None)
    ao = 1 - np.clip(oyuk / (oyuk.std() * 3 + 1e-6), 0, 1) * ao_guc
    # Pürüz: koyu/çukur → mat, açık/aşınmış → biraz parlak
    l = (lum - np.percentile(lum, 2)) / (np.percentile(lum, 98) - np.percentile(lum, 2) + 1e-6)
    pur = puruz[1] - (puruz[1] - puruz[0]) * np.clip(l, 0, 1)
    return normal, ao, pur

def temizle(img, esik_leke, esik_cizgi, duz):
    """Belirgin lekeleri ve çizgileri çevresiyle doldurur, büyük ölçekli aydınlık farkını düzleştirir (TEMIZLE)."""
    import cv2                                             # yalnızca temizlenen dokular için gerekir
    lum = img @ np.array([0.2126, 0.7152, 0.0722]); zemin = np.median(lum)
    leke = ((img[..., 0] - img[..., 2]) > esik_leke) & (lum < zemin - 0.12)
    cizgi = lum < zemin - esik_cizgi
    m = (leke | cizgi).astype(np.uint8) * 255
    k = max(3, img.shape[0] // 230) | 1
    m = cv2.dilate(m, np.ones((k, k), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k * 3, k * 3), np.uint8))   # leke bütün olarak kapansın
    bgr = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    img = cv2.cvtColor(cv2.inpaint(bgr, m, img.shape[0] // 110, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB).astype(float) / 255
    if duz > 0:                                            # ortası açık / kenarı koyu: tekrarda büyük leke olarak görünürdü
        lum = img @ np.array([0.2126, 0.7152, 0.0722])
        genel = bulanik(lum, img.shape[0] / 9)
        img = img * ((genel.mean() / np.maximum(genel, 1e-3)) ** duz)[..., None]
    print(f'  temizlik: %{100 * (m > 0).mean():.1f} dolduruldu')
    return np.clip(img, 0, 1)

# ───────── Döşenen dokular ─────────
# Yalnızca bazılarını hazırlamak için adlarını yaz: python araclar\doku_hazirla.py duvar-siva
import sys
SECILEN = set(sys.argv[1:])
for ad, (N, guc, puruz, ao_guc, r) in AYAR.items():
    if SECILEN and ad not in SECILEN: continue
    yol = bul(ad)
    if not yol:
        print(f'{ad}: bulunamadı, atlandı'); continue
    img = np.asarray(Image.open(yol).convert('RGB'), float) / 255
    if ad in TEMIZLE: img = temizle(img, *TEMIZLE[ad])
    if ad in DESEN:
        kx, ky = DESEN[ad]
        img = yatay_doseme(img, kx)
        img = yatay_doseme(img.transpose(1, 0, 2), ky).transpose(1, 0, 2)
        img = boyut(img, N, round(N * img.shape[0] / img.shape[1]))
    else:
        img = doseme(img)
        img = boyut(img, N, N)
    normal, ao, pur = haritalar(img, guc, puruz, ao_guc * AO_CARPAN, r * N / 1024)
    kaydet(img * ao[..., None], ad + '.jpg')
    kaydet(normal, ad + '-normal.jpg', 92)
    kaydet(pur, ad + '-puruz.jpg', 85, gri=True)
    dikis = np.abs(img[:, 0] - img[:, -1]).mean() * 255, np.abs(np.diff(img, axis=1)).mean() * 255
    print(f'{ad}: {N}px, dikiş {dikis[0]:.1f} (normal {dikis[1]:.1f})')

if SECILEN: sys.exit(0)                                   # yalnızca seçilen döşenen dokular istendi

# ───────── Halı: döşenmez, tek parça; saçaklar için saydamlık korunur ─────────
yol = bul('hali')
if yol:
    im = Image.open(yol).convert('RGBA')
    a = np.asarray(im)
    alfa = a[..., 3] > 20
    if alfa.all():                                     # saydamlık yoksa beyaz arka planı at
        alfa = a[..., :3].min(2) < 235
    ys, xs = np.where(alfa)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    w = 1024; h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    im.save(os.path.join(CIKTI, 'hali.png'), optimize=True)
    renk = np.asarray(im.convert('RGB'), float) / 255
    normal, ao, _ = haritalar(renk, 2.5, (0.9, 0.95), 0.2, 3)
    kaydet(normal, 'hali-normal.jpg', 90)
    print(f'hali: {w}x{h} px (en/boy {w / h:.2f})')

# ───────── Kesik görseller (macenta zeminli): kalan macentayı sil, kenardaki pembe hâleyi temizle, kırp ─────────
def macenta_temizle(rgba):
    """Pembelik = min(kırmızı, mavi) − yeşil. Macenta çok pembe, yeşil yaprak / kırmızı-mavi kalkan değil.
    Pembeliği yüksek pikseller tamamen saydam olur (yaprakların arasında kalan kapalı adacıklar dahil);
    kenardaki yarı pembe pikseller saydamlaşır ve rengi griye çekilir (pembe hâle kalmasın)."""
    a = rgba.astype(float)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    pembe = np.minimum(r, b) - g
    sil = np.clip((pembe - 25) / 60, 0, 1)                          # 25'in altı dokunulmaz, 85'in üstü tamamen silinir
    al = al * (1 - sil)
    kenar = pembe > 8                                                # hafif pembe: kırmızı ve maviyi yeşile doğru çek
    tavan = g + 8
    r = np.where(kenar, np.minimum(r, np.maximum(tavan, r - pembe)), r)
    b = np.where(kenar, np.minimum(b, np.maximum(tavan, b - pembe)), b)
    al[al < 12] = 0
    return np.stack([r, g, b, al], 2).clip(0, 255).astype(np.uint8)

def daire_kes(ham, a):
    """Kalkanlar (2026-10-17): Nano Banana altlarına ahşap duvar şeridi çizmişti; macenta silmek onu gidermez. Kalkanın dairesi
    resmin üst yarısından ölçülür (en sol/sağ ve en üst kalkan pikseli), dışı saydam olur. İçerideki renklere dokunulmaz
    (bordo/mor boya macenta sanılıp delinmesin); macenta temizliği yalnızca dış kenarın 12 piksellik şeridinde geçerli."""
    pembe = np.minimum(ham[..., 0], ham[..., 2]).astype(int) - ham[..., 1]
    h, w = pembe.shape
    ys, xs = np.where(pembe[:h // 2] < 60)
    cx, r = (xs.min() + xs.max()) / 2, (xs.max() - xs.min() + 1) / 2
    cy = ys.min() + r
    Y, X = np.mgrid[:h, :w]
    d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    disk = np.clip(r - d, 0, 1) * 255                                 # kenarda 1 piksellik yumuşak geçiş
    al = np.where(d < r - 12, 255, np.minimum(a[..., 3], disk))
    a = a.copy(); a[..., 3] = al.astype(np.uint8)
    return a

def tahta_sil(a):
    """Yaprak kartları (2026-10-17): alt satırdaki eğreltilerin yarısı ahşap duvar şeridinin üstüne çizilmişti.
    Tahtanın başladığı satır bulunur (satırın yarısından çoğu kızıl-kahve); oradan (ve 100 px yukarıdaki pembe parıltıdan)
    aşağıda yalnızca yeşil yapraklar ve koyu saplar kalır, tahta saydam olur. Kalan tek tük tahta lekeleri süzülür."""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    h = a.shape[0]
    kahve = (r > g + 25) & (np.minimum(r, b) - g < 20)
    satir = kahve.mean(1)
    aday = [y for y in range(2 * h // 3, h) if satir[y] > 0.5]
    if not aday: return a, None
    y0 = max(2 * h // 3, aday[0] - 100)
    tut = (g >= r - 12) | (np.maximum(np.maximum(r, g), b) < 75)       # yeşil yaprak ya da koyu sap
    m = Image.fromarray((tut * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(7))
    tut = np.asarray(m) > 127
    a = a.copy()
    alt = np.zeros(h, bool); alt[y0:] = True
    a[..., 3] = np.where(alt[:, None] & ~tut, 0, a[..., 3])
    return a, y0

import json
from PIL import ImageFilter
for ad, (N, guc) in KESIK.items():
    yol = bul(ad)
    if not yol:
        print(f'{ad}: bulunamadı'); continue
    ham = np.asarray(Image.open(yol).convert('RGBA'))
    a = macenta_temizle(ham)
    if ad.startswith('kalkan'):
        a = daire_kes(ham, a)
    if ad == 'yaprak-kartlari':
        a, y0 = tahta_sil(a)
        if y0: print(f'  yaprak-kartlari: {y0}. satırdan aşağısı tahtadan temizlendi')
    kalinti = ((np.minimum(a[..., 0], a[..., 2]).astype(int) - a[..., 1] > 40) & (a[..., 3] > 20)).mean() * 100
    im = Image.fromarray(a, 'RGBA')
    if ad == 'yaprak-kartlari':
        # Atlas kırpılmaz (3×3 ızgara korunur); her dalın resimdeki kutusu ölçülüp kaydedilir (Blender kartları buna göre keser)
        im = im.resize((N, N), Image.LANCZOS); a = np.asarray(im)
        kutular = []
        for sat in range(3):
            for sut in range(3):
                h = a[sat * N // 3:(sat + 1) * N // 3, sut * N // 3:(sut + 1) * N // 3, 3] > 20
                ys, xs = np.where(h)
                x0, x1 = (sut * N // 3 + xs.min()) / N, (sut * N // 3 + xs.max() + 1) / N
                y0, y1 = (sat * N // 3 + ys.min()) / N, (sat * N // 3 + ys.max() + 1) / N
                kutular.append([round(x0, 4), round(1 - y1, 4), round(x1, 4), round(1 - y0, 4)])   # UV: v aşağıdan yukarı
        with open(os.path.join(CIKTI, 'yaprak-kartlari.json'), 'w', encoding='utf-8') as f:
            json.dump({'not': 'sıra: 1. satır sarkan sarmaşık ×3, 2. satır pothos ×3, 3. satır eğrelti ×3; [u0, v0, u1, v1]', 'kutular': kutular}, f, ensure_ascii=False)
    else:
        ys, xs = np.where(a[..., 3] > 20)
        im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        o = N / max(im.size); im = im.resize((max(1, round(im.width * o)), max(1, round(im.height * o))), Image.LANCZOS)
    im.save(os.path.join(CIKTI, ad + '.png'), optimize=True)
    renk = np.asarray(im.convert('RGB'), float) / 255
    normal, _, _ = haritalar(renk, guc, (0.5, 0.9), 0.0, 3)
    kaydet(normal, ad + '-normal.jpg', 90)
    print(f'{ad}: {im.size[0]}x{im.size[1]} px, kalan macenta %{kalinti:.3f}')

# ───────── Çerçeveyi dolduran görseller: harita, görev panosu, kitap sırtları ─────────
for ad, (N, guc) in DOLU.items():
    yol = bul(ad)
    if not yol:
        print(f'{ad}: bulunamadı'); continue
    im = Image.open(yol).convert('RGBA')
    a = np.asarray(im)
    if (a[..., 3] < 20).any():                                       # saydam kenar varsa kırp
        ys, xs = np.where(a[..., 3] > 20); im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    im = im.convert('RGB'); im = im.resize((N, round(im.height * N / im.width)), Image.LANCZOS)
    renk = np.asarray(im, float) / 255
    normal, ao, pur = haritalar(renk, guc, (0.6, 0.95), 0.3 * AO_CARPAN, 4)
    kaydet(renk * ao[..., None], ad + '.jpg')
    kaydet(normal, ad + '-normal.jpg', 90)
    kaydet(pur, ad + '-puruz.jpg', 85, gri=True)
    print(f'{ad}: {im.size[0]}x{im.size[1]} px (en/boy {im.size[0] / im.size[1]:.2f})')
print('bitti:', CIKTI)                                                # (ok işareti Windows konsolunda hata veriyordu)
