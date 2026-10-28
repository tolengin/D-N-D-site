# -*- coding: utf-8 -*-
"""
KARAKTER DOKUSUNU KÂĞIDA GÖRE BOYAR (2026-10-28; karakter_kur_blender.py çağırır, yalnızca numpy).
Girdi: C (H×W×3, 0…1, asıl doku) ve P (H×W×3: o pikselin modeldeki 3D yeri, metre; karakter_kur_blender.py pişirir).
Hazır modellerin dokuları yüzlerce küçük parçadan oluşur (özellikle Meshy); bu yüzden bölgeler renkten çok 3D yerden seçilir.
Yeniden boyamada asıl dokunun ışığı ve kıvrımları korunur: yeni renk = hedef renk × (pikselin parlaklığı / bölgenin ortanca parlaklığı).
"""
import numpy as np


def hsv(C):
    mx, mn = C.max(-1), C.min(-1)
    v, d = mx, mx - mn
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    r, g, b = C[..., 0], C[..., 1], C[..., 2]
    dd = np.maximum(d, 1e-6)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) / 6
    return np.where(d > 1e-6, h, 0), s, v


def lum(C):
    return C @ np.array([0.299, 0.587, 0.114], np.float32)


def renk(hex_):
    return np.array([int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


def boya(C, m, hedef, kontrast=1.0, taban=None):
    """m bölgesini hedef renge çevirir; asıl parlaklık farkları (kontrastla) kalır."""
    L = lum(C)
    ref = np.median(L[m]) if taban is None else taban
    k = np.clip(1 + (L[m] / max(ref, 1e-3) - 1) * kontrast, 0.15, 2.2)
    C[m] = np.clip(renk(hedef) * k[:, None], 0, 1)


def yakin(P, kaynak, hedef, r, adim=0.006):
    """hedef maskesindeki piksellerden kaynak maskesindekilere r metreden yakın olanlar (3D'de, kaba voksel)."""
    mn = P.reshape(-1, 3).min(0)
    I = np.floor((P - mn) / adim).astype(np.int32)
    n = I.reshape(-1, 3).max(0) + 1
    G = np.zeros(n, bool)
    k = I[kaynak]; G[k[:, 0], k[:, 1], k[:, 2]] = True
    for _ in range(max(1, int(round(r / adim)))):            # genişlet (6 komşu)
        H = G.copy()
        for ax in range(3):
            H[(slice(None),) * ax + (slice(1, None),)] |= G[(slice(None),) * ax + (slice(None, -1),)]
            H[(slice(None),) * ax + (slice(None, -1),)] |= G[(slice(None),) * ax + (slice(1, None),)]
        G = H
    sonuc = np.zeros(P.shape[:2], bool)
    k = I[hedef]; sonuc[hedef] = G[k[:, 0], k[:, 1], k[:, 2]]
    return sonuc


def gurultu(P, olcek, tohum=0):
    """3D konuma bağlı yumuşak değer gürültüsü (0…1): doku parçalarının dikişinde kesilmez."""
    rng = np.random.default_rng(tohum)
    T = rng.random((64, 64, 64)).astype(np.float32)
    q = P * olcek
    i = np.floor(q).astype(np.int64); f = q - i
    f = f * f * (3 - 2 * f)
    def t(dx, dy, dz): return T[(i[..., 0] + dx) % 64, (i[..., 1] + dy) % 64, (i[..., 2] + dz) % 64]
    x00 = t(0, 0, 0) * (1 - f[..., 0]) + t(1, 0, 0) * f[..., 0]
    x10 = t(0, 1, 0) * (1 - f[..., 0]) + t(1, 1, 0) * f[..., 0]
    x01 = t(0, 0, 1) * (1 - f[..., 0]) + t(1, 0, 1) * f[..., 0]
    x11 = t(0, 1, 1) * (1 - f[..., 0]) + t(1, 1, 1) * f[..., 0]
    y0 = x00 * (1 - f[..., 1]) + x10 * f[..., 1]
    y1 = x01 * (1 - f[..., 1]) + x11 * f[..., 1]
    return y0 * (1 - f[..., 2]) + y1 * f[..., 2]


def hucre_ort(P, deger, gecerli, adim):
    """deger'in (H×W ya da H×W×k) 3D hücrelerdeki (adim metre) ortalaması, hücreler arasında üç eksende ara değerle (en yakın
    hücreyi almak boyunda ve kollarda kare kare mozaik bırakıyordu)."""
    tek = deger.ndim == 2
    D = (deger[..., None] if tek else deger)[gecerli]
    Pg = P[gecerli]; mn = Pg.min(0) - adim
    q = (Pg - mn) / adim - 0.5                                          # hücre ortaları tam sayılarda
    n = np.floor(q.max(0)).astype(int) + 3
    i0 = np.floor(q).astype(int); f = q - i0
    top = np.zeros((n[0], n[1], n[2], D.shape[1]), np.float32); say = np.zeros(tuple(n), np.float32)
    kose = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    def w(a, b, c): return (f[:, 0] if a else 1 - f[:, 0]) * (f[:, 1] if b else 1 - f[:, 1]) * (f[:, 2] if c else 1 - f[:, 2])
    for a, b, c in kose:                                               # her piksel çevresindeki 8 hücreye ağırlığıyla
        ii = (i0[:, 0] + a, i0[:, 1] + b, i0[:, 2] + c); ww = w(a, b, c)
        np.add.at(say, ii, ww)
        for j in range(D.shape[1]): np.add.at(top[..., j], ii, D[:, j] * ww)
    ort = top / np.maximum(say, 1e-6)[..., None]
    sonuc = np.zeros((len(Pg), D.shape[1]), np.float32); ws = np.zeros(len(Pg), np.float32)
    for a, b, c in kose:                                               # geri okurken de ara değer (boş hücreler sayılmaz)
        ii = (i0[:, 0] + a, i0[:, 1] + b, i0[:, 2] + c); ww = w(a, b, c) * (say[ii] > 1e-6)
        sonuc += ort[ii] * ww[:, None]; ws += ww
    sonuc /= np.maximum(ws, 1e-6)[:, None]
    out = np.zeros(deger.shape[:2] + (D.shape[1],), np.float32); out[gecerli] = sonuc
    return out[..., 0] if tek else out


KAPSAM = None   # karakter_kur_blender.kur doldurur: dokunun gerçekten modele düşen pikselleri (UV üçgenleri; pişirme kenar payını da dolduruyor)


def tasir(C, gecerli, n=8):
    """Boyanan rengi doku parçalarının dışındaki kenar payına taşırır (n piksel). Pay asıl dokunun renginde kalınca ekran
    kenarı okurken onu karıştırıyor, önlükte ve yüzde çatlak gibi koyu çizgiler çıkıyordu."""
    C = C.copy(); g = gecerli.copy()
    for _ in range(n):
        top = np.zeros_like(C); say = np.zeros(g.shape, np.float32)
        for ax, k in ((0, 1), (0, -1), (1, 1), (1, -1)):
            gs = np.roll(g, k, ax); top += np.roll(C, k, ax) * gs[..., None]; say += gs
        yeni = ~g & (say > 0)
        C[yeni] = top[yeni] / say[yeni][:, None]; g |= yeni
    return C


def boyali(C, P, gecerli=None, adim=0.025, bant=0.12, firca=0.07, duz=0.75, koru=None, olcek=1.0):
    """Sitenin elle boyanmış tarzı (2026-10-28; büyücü ve han gibi): renk bölgeleri keskin kalır, ışık-gölge 3D'de yumuşatılıp
    birkaç yumuşak ton basamağına iner (Meshy dokularının fotoğraf gibi ince gürültüsü ve kırışıkları gider), üstüne dikine
    hafif fırça izi. duz: pişmiş gölgenin ne kadar kalacağı (üs; ışığı ve gölgeyi site kendisi verir). koru (0…1, H×W): bu kadar asıl doku kalır (yüz, gözler). olcek: modelin birimi metrenin kaçı (hancı 1/40)."""
    if gecerli is None: gecerli = KAPSAM if KAPSAM is not None else np.ones(P.shape[:2], bool)
    L = lum(C)
    renkk = C / np.maximum(L, 1e-3)[..., None]                          # rengin yönü (parlaklıktan bağımsız)
    Ls = hucre_ort(P, L, gecerli, adim / olcek)
    orta = np.median(Ls[gecerli])
    Ls = orta * (np.maximum(Ls, 1e-3) / orta) ** duz
    q = Ls / bant; f = q - np.floor(q)
    f = np.clip((f - 0.3) / 0.4, 0, 1); f = f * f * (3 - 2 * f)          # basamaklar arasında yumuşak geçiş
    Lq = (np.floor(q) + f) * bant * 0.8 + Ls * 0.2                       # tam basamak sert duruyordu: biraz da yumuşak ışık
    fz = gurultu(P * olcek * np.array([1, 1, 0.22], np.float32), 120, 11) # dikine uzun fırça darbeleri
    D = np.clip(renkk * (Lq * (1 + (fz - 0.5) * firca * 2))[..., None], 0, 1)
    if koru is not None: D = D * (1 - koru[..., None]) + C * koru[..., None]
    return np.where(gecerli[..., None], D, C).astype(np.float32)


# ---------------------------------------------------------------- DM (kâğıt: gorseller/3d karakterler/DM-human.jpg)
# Model: Meshy "Aurelian" (genç, gri cüppeli, kitap okuyan). Kâğıtta: lacivert, altın kenarlı uzun ceket; içte krem gömlek;
# kahverengi deri kemer; koyu pantolon; kahverengi çizmeler; kırçıl saç ve kısa sakal; yuvarlak gözlük (mesh), tüy (mesh).
# Model ölçüsü: boy ~1,85 (z −0,90…0,95), yüzü −y'ye; göğüs önü y≈0, sırt y≈0,3.
DM_YER = dict(cene=0.64, etek_on=-0.38, cizme=-0.60, kemer=(0.135, 0.245))
# Sol ön kol ve el kitabı alttan tutuyordu, kitabın gölgesinde koyu: kitap silinirken korunur (karakter_kur_blender.kutu_sil) ve
# burada bütünüyle tene boyanır (kitaptan kalan altın / deri kırıntıları da). (baş, uç, yarıçap; metre)
DM_KOL = [((0.225, 0.07, 0.33), (0.15, -0.195, 0.345), 0.042), ((0.15, -0.195, 0.345), (0.05, -0.295, 0.415), 0.04)]


def kapsul(P, liste):
    """P noktalarından (…×3) listedeki kapsüllerin (a, b, r) içinde kalanlar."""
    m = np.zeros(P.shape[:-1], bool)
    for a, b, r in liste:
        a, b = np.array(a, np.float32), np.array(b, np.float32)
        t = np.clip(((P - a) @ (b - a)) / ((b - a) @ (b - a)), 0, 1)
        m |= np.linalg.norm(P - (a + t[..., None] * (b - a)), axis=-1) < r
    return m


def _yuz(*noktalar):
    """Yüz yakın çekiminin (500 px, 0,38 m, ortası x 0 / z 0,798) piksellerinden (x, z) metreye."""
    return np.array([((px - 250) / 1316, 0.798 + (250 - py) / 1316) for px, py in noktalar], np.float32)


DM_YUZ = dict(   # önden yakın çekimde elle çizildi (3d/karakter önizlemesi)
    sakal=_yuz((222, 315), (225, 360), (240, 400), (265, 428), (300, 442), (335, 432), (360, 405), (378, 365), (385, 320),
               (368, 332), (350, 352), (330, 360), (310, 353), (300, 351), (288, 353), (268, 360), (252, 347), (240, 324)),
    dudak=_yuz((279, 382), (290, 375), (300, 374), (312, 376), (322, 383), (311, 390), (300, 391), (289, 389)),
    kaslar=[_yuz((230, 268), (255, 256), (284, 258), (285, 267), (256, 266), (232, 276)),
            (_yuz((316, 262), (342, 254), (372, 258), (371, 266), (344, 263), (318, 271)))],
)


def yumusak(p, poli, r):
    """p (N×2) noktalarının poli çokgeninin içinde olma derecesi: içeride 1, kenardan r kadar dışarıda 0 (r=0: keskin)."""
    x, y = p[:, 0:1], p[:, 1:2]
    a, b = poli, np.roll(poli, -1, 0)
    ic = (((a[:, 1] > y) != (b[:, 1] > y)) & (x < (b[:, 0] - a[:, 0]) * (y - a[:, 1]) / (b[:, 1] - a[:, 1] + 1e-12) + a[:, 0])).sum(1) % 2 == 1
    if r <= 0: return ic.astype(np.float32)
    ab = b - a
    t = np.clip(((x - a[:, 0]) * ab[:, 0] + (y - a[:, 1]) * ab[:, 1]) / (ab ** 2).sum(1), 0, 1)
    d = np.sqrt((x - a[:, 0] - t * ab[:, 0]) ** 2 + (y - a[:, 1] - t * ab[:, 1]) ** 2).min(1)
    return np.where(ic, np.clip(0.5 + d / (2 * r), 0, 1), np.clip(0.5 - d / (2 * r), 0, 1)).astype(np.float32)


def dm(C, P, parca=None, hata=False):
    C = C.copy()
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    h, s, v = hsv(C)
    Y = DM_YER
    ten = (h < 0.09) & (s > 0.26) & (s < 0.62) & (v > 0.55)          # cüppenin açık kıvrımları (s < 0,25) ten sayılmasın
    bas = z > Y['cene'] - 0.01
    r2 = x ** 2 + (y - 0.11) ** 2 + ((z - 0.81) * 0.85) ** 2
    kafa = r2 < 0.148 ** 2                                              # kapüşonun ensesi saç sayılmasın
    sac = ~ten & (z > 0.68) & (v < 0.52) & (kafa | ((r2 < 0.19 ** 2) & (s > 0.3) & (v < 0.45)))   # ensedeki tutamlar: koyu, doygun kahve; şakağın solgun teni değil
    eller = ten & ~bas & ((np.abs(x) > 0.1) | (y < -0.12)) & (z > 0.25) & (y < 0.12)  # yalnızca önkollar ve eller (sol el göğsün önünde)
    boyun = ten & (z > 0.55) & (np.abs(x) < 0.09) & ~eller
    kol = kapsul(P, DM_KOL) & ((s > 0.18) | (v < 0.3))                 # gölgedeki sol kol (gri cüppenin kolu değil)
    eller |= kol
    ten = (ten & (bas | eller | boyun | (z < Y['cizme']))) | kol
    canta = (x < -0.17) & (x > -0.32) & (z > 0.0) & (z < 0.2) & (y < 0.25) & ~ten
    koyu = (s > 0.33) & (v < 0.33) & (z < -0.3)                        # eteğin altında kalan pantolon (koyu, doygun kahve)
    govde = (z > Y['etek_on'] - 0.08) & (z < 0.78) & ~ten & ~canta & ~koyu & ~sac
    kemer = govde & (z > Y['kemer'][0]) & (z < Y['kemer'][1]) & (v < 0.42)
    yaka = govde & (z > 0.585) & (np.abs(x) < 0.05) & (y < 0.1) & (v > 0.42)       # boyun açıklığındaki açık kumaş → krem gömlek (kâğıtta küçük)
    tunik = govde & (h > 0.09) & (h < 0.3) & (s < 0.2) & (np.abs(x) < 0.075) & (y < 0.1) & (z < 0.6) & ~kemer & ~yaka
    ceket = govde & ~kemer & ~tunik & ~yaka
    alt = ((z < Y['etek_on'] + 0.02) | koyu) & ~ceket
    cizme = (z < Y['cizme'])
    pantolon = alt & ~cizme & ~ten
    # Baş kitaba doğru eğik ve dönük: sakal ve kaşlar yüzün önden görünüşünde çizilmiş şekillerle seçilir (DM_YUZ)
    on = bas & (y < 0.1)
    xz = np.stack([x, z], -1)
    sakal_k = np.zeros(x.shape, np.float32)
    sakal_k[on] = yumusak(xz[on], DM_YUZ['sakal'], 0.004) * (1 - yumusak(xz[on], DM_YUZ['dudak'], 0.003))
    sakal = ten & (sakal_k > 0)
    kas = np.zeros(x.shape, bool)
    for k in DM_YUZ['kaslar']:
        kas[on] |= yumusak(xz[on], k, 0.0) > 0.5
    kas &= ~sac & (v < 0.55)

    if hata:                                                   # sınıfları düz renkle göster
        D = C * 0.35
        for m, c in [(sac, '#808080'), (sakal, '#c0c0c0'), (ceket, '#203070'), (tunik, '#6080c0'), (yaka, '#f0e0b0'),
                     (kemer, '#804020'), (canta, '#c08040'), (pantolon, '#303030'), (cizme, '#603000'), (eller, '#ffb090'), (boyun, '#ff8060')]:
            D[m] = renk(c)
        return D

    g = gurultu(P, 260, 1)
    # saç: kırçıl (kahveden açık griye; tutamlar korunur)
    L = lum(C)
    gri = np.clip(0.1 + 1.25 * L[sac] + (g[sac] - 0.5) * 0.3, 0, 0.8)     # sitenin sıcak ışığında açık gri beyaz görünüyordu
    C[sac] = gri[:, None] * np.array([1.0, 0.99, 0.97], np.float32)
    # sakal: kısa, kırçıl, aşağı doğru kıl çizgileri; kenarlarda tene karışır
    tel = gurultu(P * np.array([1, 1, 0.25], np.float32), 1400, 2)
    sk = np.clip(0.5 + (L[sakal] - np.median(L[sakal])) * 0.6 + (tel[sakal] - 0.5) * 0.5 + (g[sakal] - 0.5) * 0.15, 0.2, 0.85)
    a = sakal_k[sakal][:, None] * 0.95
    C[sakal] = C[sakal] * (1 - a) + (sk[:, None] * np.array([1.0, 0.96, 0.92], np.float32)) * a
    C[kas] = np.clip(0.18 + 1.2 * L[kas], 0, 0.7)[:, None] * np.array([1.0, 0.97, 0.94], np.float32)
    isik = eller & ~kol
    boya(C, kol, '#%02x%02x%02x' % tuple((np.median(C[isik], 0) * 255).astype(int)) if isik.any() else '#c8967a', 0.45,
         taban=np.median(lum(C)[kol]) * 0.85)
    boya(C, ceket, '#24386a', 1.15)
    boya(C, tunik, '#263b6e', 1.0)                                     # kâğıtta ceket önden kapalı: iç kumaş da lacivert
    boya(C, yaka, '#e6dcc2', 0.8)
    boya(C, kemer, '#5e3a1e', 1.1)
    boya(C, pantolon, '#3b3532', 1.0)
    boya(C, cizme, '#76492a', 0.9)
    boya(C, cizme & (z > Y['cizme'] - 0.03), '#7a5233', 0.8)        # çizmenin kıvrık konçu
    boya(C, cizme & (z < -0.835), '#5a3a22', 0.35)                   # ayaklar: sandalet ve parmaklar ayakkabı rengine
    # altın şeritler: ceketin iç kumaşa, ele, boyna, gömleğe değdiği kenarlar ve etek ucu (pantolon cüppenin hemen
    # altında durduğu için sayılmaz; yoksa etek boyunca benek olur)
    komsu = yaka | eller | boyun
    serit = ceket & yakin(P, komsu, ceket, 0.012)
    # etek ucu: çevre açısına göre en alçak ceket noktasının 2,5 cm üstü
    a = np.arctan2(x - 0.0, y - 0.14)
    bol = np.clip(((a + np.pi) / (2 * np.pi) * 72).astype(int), 0, 71)
    etek = ceket & (z < 0.0)
    dip = np.full(72, 9.0)
    np.minimum.at(dip, bol[etek], z[etek])
    serit |= etek & (z < dip[bol] + 0.028)
    # sırtta kâğıttaki kısa pelerinin kenarı: kürek kemiği hizasında kavisli şerit
    serit |= ceket & (y > 0.16) & (np.abs(x) < 0.17) & (np.abs(z - (0.43 + 1.6 * x ** 2)) < 0.011)   # kollara taşmasın
    # önde: belin altında açılan iki etek kenarı ve göğüste kordon düğmeler (kâğıttaki gibi)
    onde = (ceket | tunik) & (y < 0.08)
    serit |= onde & (np.abs(np.abs(x) - 0.068) < 0.007) & (z < Y['kemer'][0]) & (z > Y['etek_on'] - 0.05)
    for zk in (0.30, 0.37, 0.44, 0.51):
        serit |= onde & (np.abs(x) < 0.032) & (np.abs(z - zk) < 0.008)
    serit |= onde & (np.abs(x) < 0.006) & (z > 0.27) & (z < 0.56)
    altin = renk('#c49a45')
    k = np.clip(0.75 + (lum(C)[serit] / max(np.median(lum(C)[ceket | tunik]), 1e-3) - 1) * 0.6, 0.5, 1.4)
    C[serit] = np.clip(altin * k[:, None], 0, 1)
    # kemer tokası (önde ortada)
    toka = kemer & (np.abs(x) < 0.03) & (y < 0.06)
    C[toka] = renk('#a88a4c') * np.clip(0.8 + lum(C)[toka] * 0.6, 0.6, 1.3)[:, None]
    return C


# ---------------------------------------------------------------- HANCI (kâğıt: gorseller/3d karakterler/hanci-dwarf.jpg)
# Model: "The Noble Craftsman" (demirci cüce: kel, ak sakallı, çıplak göğüslü, turkuaz-gümüş zırh plakalı). Kâğıtta: kızıl saç
# ve örgülü kızıl sakal, beyaz keten gömlek (kollar dirseğe kadar sıvalı), kahverengi deri önlük, koyu pantolon, deri çizme.
# Ölçüler modelin kendi biriminde (boy 54, yüzü −y'ye); eklemler modelin içindeki boş nesnelerden (Base Human_…).
HANCI_KOL = {'l': ((13.46, 3.6, 39.46), (19.65, 2.17, 31.87)), 'r': ((-13.83, 2.72, 38.51), (-19.99, 2.23, 30.79))}   # omuz, dirsek


def hanci(C, P, parca=None, hata=False):
    C = C.copy()
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    h, s, v = hsv(C)
    ax = np.abs(x)
    govde = parca == 0                                                 # en büyük parça: gövde, kollar, eller (karakter_kur_blender.parcalar)
    ten = (h < 0.11) & (s > 0.2) & (s < 0.68) & (v > 0.38)
    beyaz = (s < 0.12) & (v > 0.45)                                    # yüzün solgun teni (s ≈ 0,17) ak saç sayılmasın
    bas = (z > 37) & (ax < 12.5) & (y < 10)
    sakal = (s < 0.12) & (v > 0.2) & bas                               # ak saç ve sakal → kızıl (adaların koyu gri kenarları da)
    kel = ten & ~govde & bas & ((z > 50.5) | ((z > 45) & (y > 2)))      # başın tepesi ve arkası: saç (yüz önde kalır)
    # kol boyunca omuzdan (0) dirseğe (1)
    t = np.full(x.shape, 9.0, np.float32)
    for k, (o, d) in HANCI_KOL.items():
        o, d = np.array(o, np.float32), np.array(d, np.float32)
        tk = ((P - o) @ (d - o)) / ((d - o) @ (d - o))
        yan = (x > 10.5) if k == 'l' else (x < -10.5)
        t = np.where(yan, tk, t)
    yaka = (z > 37) & (ax < 5) & (y < -4)                             # gömleğin açık yakası: boyun teni
    boyun = (ax < 4.5) & (z > 42)
    gomlek = govde & ~yaka & ~boyun & (z < 44.5) & (((ax < 12) & (z > 24)) | ((ax >= 10.5) & (t < 1.02)))
    manset = govde & (ax >= 10.5) & (t >= 0.9) & (t < 1.12)            # sıvanmış kolun kıvrımı (dirseğin hemen altı)
    turkuaz = (h > 0.42) & (h < 0.6) & (s > 0.25) & (v > 0.35)
    lacivert = (h > 0.52) & (h < 0.72) & (s > 0.2) & (v <= 0.35)
    plaka_on = (ax < 8) & (z > 14) & (z < 29)                          # karındaki ve sırttaki arma → pirinç toka
    kalanplaka = (z < 12) | ((ax > 12) & (z > 20) & (z < 45))          # dizlik, bileklik, omuz bandı → deri
    gumus = beyaz & ~bas
    onluk = ~govde & ~ten & ~beyaz & ~turkuaz & ~lacivert & (v < 0.36) & (y < -4) & (z > 9) & (z < 40) & (ax < 13)
    pantolon = lacivert
    etek = turkuaz & ~plaka_on & ~kalanplaka                             # arkadaki açık mavi peştamal

    if hata:
        D = C * 0.35
        for m, c in [(sakal, '#ff8040'), (kel, '#c04020'), (gomlek, '#f0f0e0'), (manset, '#a0a0ff'), (onluk, '#805030'),
                     (pantolon, '#202060'), (turkuaz & plaka_on, '#ffd040'), (gumus & plaka_on, '#a08040'),
                     ((turkuaz | gumus) & kalanplaka, '#40ff40')]:
            D[m] = renk(c)
        return D

    L = lum(C)
    g = gurultu(P * 0.025, 260, 3)
    tel = gurultu(P * np.array([0.025, 0.006, 0.025], np.float32), 900, 4)     # tepedeki saç önden arkaya taranmış
    # sakal ve saç: ak tellerin ışığı korunur, kızıla çevrilir
    k = np.clip(L[sakal] / max(np.median(L[sakal]), 1e-3), 0.25, 1.5)
    C[sakal] = np.clip(renk('#b4552b') * k[:, None] ** 1.2, 0, 1)
    kk = np.clip(0.8 + (tel[kel] - 0.5) * 0.5 + (g[kel] - 0.5) * 0.2, 0.5, 1.15)
    C[kel] = np.clip(renk('#a84c26') * kk[:, None], 0, 1)
    boya(C, gomlek, '#e9e1cd', 0.55)
    boya(C, manset, '#d3c8ae', 0.6)
    boya(C, onluk, '#6f4d34', 0.9)
    boya(C, pantolon, '#38353a', 0.8)
    boya(C, etek, '#4b4239', 0.8)
    boya(C, turkuaz & plaka_on, '#bf9744', 0.8)
    boya(C, gumus & plaka_on, '#7f6640', 0.9)
    boya(C, (turkuaz | gumus) & kalanplaka & ~bas, '#4c3527', 0.8)
    return C


def _ciz(C, hata, siniflar):
    """hata: sınıfları düz renkle gösterir (denetim); değilse None."""
    if not hata: return None
    D = C * 0.35
    for m, c in siniflar: D[m] = renk(c)
    return D


# ---------------------------------------------------------------- KIZ GARSON (kâğıt: garson-human-kiz.jpg)
# Model: Meshy "Classic Maid Uniform" (restore50): kısa lacivert elbise, beyaz önlük ve yaka, topuklu, kıvırcık kahve saç.
# Kâğıtta: yeşil korse, krem bluz (kollar), kahverengi uzun etek (mesh olarak eklenir), krem önlük, başörtüsü, kızıl-kahve saç,
# açık ten. Model ölçüsü: boy ~1,9 (z −0,95…0,95), yüzü −y'ye, gövdenin ortası y ≈ −0,07.
def garson_kiz(C, P, parca=None, hata=False):
    C = C.copy()
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    h, s, v = hsv(C)
    ax = np.abs(x)
    kafa = (x ** 2 + (y + 0.06) ** 2 + (z - 0.76) ** 2) < 0.24 ** 2
    ten = (h < 0.1) & (s > 0.22) & (s < 0.7) & (v > 0.28) & ~((z > 0.55) & (s > 0.5) & (v < 0.45))
    beyaz = (s < 0.14) & (v > 0.55)
    lacivert = (h > 0.5) & (h < 0.75) & (v < 0.5) & (s > 0.15)
    mavi = (h > 0.45) & (h < 0.62) & (s > 0.3) & (v > 0.45)            # elindeki bez
    sac = kafa & ~ten & ~beyaz & (z > 0.45) & ~(lacivert & (z < 0.55))
    bone = kafa & beyaz & (z > 0.8)                                    # hizmetçi bonesi → başörtüsü rengi
    yaka = beyaz & (z > 0.43) & (z < 0.58) & ~kafa | (beyaz & (z > 0.43) & (z < 0.56) & (ax < 0.12))
    kol = (ax > 0.13) & (z > 0.26) & (z < 0.5)                         # kısa kollar ve manşetleri → krem bluz
    ust = lacivert & (z > 0.18) & ~kol                                 # korse
    etek = lacivert & (z <= 0.18)
    onluk = beyaz & (z <= 0.3) & (z > -0.3)
    ayakkabi = (z < -0.83) & ~ten
    D = _ciz(C, hata, [(sac, '#c04020'), (bone, '#ffff80'), (yaka, '#f0e0b0'), ((lacivert | beyaz) & kol, '#a0a0ff'), (ust, '#30a030'),
                       (etek, '#805030'), (onluk, '#ffffff'), (ayakkabi, '#202020'), (ten, '#ffb090'), (mavi, '#00ffff')])
    if D is not None: return D
    L = lum(C)
    boya(C, ten, '#dcaa8c', 0.85)                                      # kâğıtta açık ten
    k = np.clip(L[sac] / max(np.median(L[sac]), 1e-3), 0.3, 1.7)
    C[sac] = np.clip(renk('#8f4024') * k[:, None], 0, 1)                # kızıl kahve
    boya(C, bone, '#d8cbb0', 0.7)
    boya(C, yaka | ((lacivert | beyaz) & kol), '#ece2cc', 0.6)
    boya(C, ust, '#4f7d47', 1.0)
    boya(C, etek, '#6a5241', 1.0)
    boya(C, onluk, '#d9cdb3', 0.7)
    boya(C, mavi, '#cfc3a6', 0.7)                                       # bez → krem paçavra
    boya(C, ayakkabi, '#2c2522', 0.8)
    yuz = (kafa & ten).astype(np.float32) * np.clip((-0.1 - y) / 0.03, 0, 1)   # yüzün önü (gözler, ağız) olduğu gibi kalsın
    return boyali(C, P, koru=yuz)


# ---------------------------------------------------------------- ERKEK GARSON (kâğıt: garson-halfelf-erkek.jpg)
# Model: Meshy "Medieval Peasant Warrior" (Azura_SQ): sakallı, kahve saçlı, turuncu deri tunik, mavi gömlek, mavi-gri şalvar,
# kılıç (silindi). Kâğıtta: genç yarı-elf, siyah dağınık saç, sivri kulak (mesh), sakalsız; koyu yelek, krem gömlek (kollar sıvalı),
# uzun krem önlük, koyu pantolon, kahverengi çizme. Model: boy ~1,9, yüzü −y'ye, gövdenin ortası y ≈ 0,03.
def garson_erkek(C, P, parca=None, hata=False):
    C = C.copy()
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    h, s, v = hsv(C)
    ax = np.abs(x)
    kafa = (x ** 2 + (y - 0.02) ** 2 + ((z - 0.81) * 0.9) ** 2) < 0.19 ** 2
    # Deri tunik tenle aynı renkte: ten yalnızca yüzde, boyunda, göğsün açıklığında ve önkollarda aranır
    tenrenk = (h < 0.1) & (s > 0.2) & (s < 0.68) & (v > 0.3)
    yuz = kafa & (y < 0.03) & (z < 0.85)
    tenbolge = yuz | ((z > 0.55) & (ax < 0.09) & (y < 0.0)) | ((ax > 0.19) & (z < 0.3) & (z > -0.2))
    ten = tenrenk & tenbolge
    sac = kafa & (z > 0.72) & ~(yuz & tenrenk)                           # yüzün teni dışında başın üstü ve arkası
    dudak = ((h < 0.03) | (h > 0.95)) & (s > 0.3) & (v > 0.35)
    sakal = kafa & (y < 0.04) & (z > 0.585) & (z < 0.758) & (ax < 0.078) & ~dudak   # çene, yanak altı, bıyık: tenle kapanır
    teal = (h > 0.42) & (h < 0.62) & (s > 0.15) & (z > 0.15)            # gömlek (kollar, yaka)
    sharvar = (h > 0.42) & (h < 0.7) & (z < 0.0) & (z > -0.62)
    tunik = (h < 0.12) & (s > 0.3) & ~ten & (z > -0.4) & (z < 0.65) & ~kafa & ~((ax > 0.2) & (z < 0.3))
    kemer = (z > 0.08) & (z < 0.2) & (v < 0.32) & (ax < 0.2)
    yelek = tunik & (z > 0.17)
    onluk = tunik & (z <= 0.1) & (y < 0.02)
    arka = tunik & (z <= 0.1) & (y >= 0.02)
    D = _ciz(C, hata, [(sac, '#202020'), (sakal, '#ff00ff'), (teal, '#f0e0b0'), (sharvar, '#303060'), (yelek, '#504030'),
                       (onluk, '#ffffff'), (arka, '#806040'), (kemer, '#c0a060'), (ten, '#ffb090')])
    if D is not None: return D
    L = lum(C)
    # sakal: yanağın teniyle kapatılır (traşlı genç yüz); tenin ışığı hafifçe kalır
    yanak = yuz & tenrenk & (z > 0.76) & (z < 0.8)
    tr = np.median(C[yanak], 0) if yanak.any() else renk('#c8906c')
    k = np.clip(0.92 + (L[sakal] / max(np.median(L[sakal]), 1e-3) - 1) * 0.18, 0.78, 1.08)
    C[sakal] = np.clip(tr * k[:, None], 0, 1)
    k = np.clip(L[sac] / max(np.median(L[sac]), 1e-3), 0.4, 2.2)
    C[sac] = np.clip(renk('#1d1b1e') * k[:, None] ** 0.8 + 0.02, 0, 1)
    boya(C, teal, '#e6dcc6', 0.65)
    boya(C, sharvar, '#2a2727', 0.9)
    boya(C, yelek, '#3a332f', 0.9)
    boya(C, onluk, '#d6ccb2', 0.45)
    g = gurultu(P, 30, 7)                                              # önlükte birkaç hafif leke
    lk = onluk & (g > 0.7)
    C[lk] = C[lk] * np.array([0.94, 0.9, 0.84], np.float32)
    boya(C, arka, '#3a332f', 0.9)
    boya(C, kemer, '#9b8a66', 0.8)
    yuz_ = (yuz & tenrenk).astype(np.float32) * np.clip((-0.02 - y) / 0.03, 0, 1)
    return boyali(C, P, koru=yuz_)


# ---------------------------------------------------------------- FIGHTER (kâğıt: gorseller/3d karakterler/fighter-human.jpg)
# Model: "GA Free_251_The Shrewd Scoundrel" (Galaxy Abundant): yeşil kapüşonlu ve pelerinli okçu, kahverengi deri ceket (yırtık
# etekli), zeytin yeşili kollar ve pantolon, deri omuzluk, kolluk ve parmaksız eldiven, kemerde iki kese ve hançer. Kâğıtta:
# kırçıl kısa saçlı, sakalı uzamış gazi; kızıl yırtık tabar, altında zincir zırh, deri omuzluk ve kolluk, çapraz kayış, kemer,
# kese, çizme. Kapüşon saça çevrildi (karakter_kur_blender.fighter_bas), omuz pelerini zincir yaka olur, arkadaki pelerinin
# kalanı tabarın arkası. Model: boy 1,8 (z 0…1,8), yüzü −y'ye.
FIGHTER_KAFA = ((0.0, 0.008, 1.68), (0.083, 0.098, 0.096))   # saçın oturduğu kafa elipsi: orta, yarıçaplar (m)


def fighter(C, P, parca=None, hata=False):
    import os
    hata = hata or os.environ.get('BOYA_HATA') == '1'
    C = C.copy()
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    h, s, v = hsv(C)
    ax = np.abs(x)
    c, r = (np.array(a, np.float32) for a in FIGHTER_KAFA)
    n = np.linalg.norm((P - c) / r, axis=-1)
    tenrenk = (h < 0.1) & (s > 0.22) & (s < 0.68) & (v > 0.3)
    bas = (z > 1.53) & (n < 1.6)
    ten = tenrenk & ((bas & (y < 0.03)) | ((ax > 0.44) & (z < 1.06)))   # yüz (elipsin önünde); parmaksız eldivenden çıkan parmaklar
    sac = bas & ~ten & (n > 0.75) & ((z > 1.665) | ((y > 0.035) & (z > 1.575)))   # kısa saç: yanlarda kulak hizasında biter
    kulak = bas & ~ten & ~sac & (n > 0.75) & (z > 1.5)                 # kapüşonun yanlara inen kısmı → ten (kulak, boyun)
    yesil = (h > 0.17) & (h < 0.5) & (s > 0.08) & ~sac & ~ten
    yaka = yesil & (z > 1.28)                                           # omuz pelerini ve boyun → zincir yaka
    pelerin = yesil & (y > 0.05) & (z <= 1.28) & (ax < 0.3)
    kol = yesil & (ax > 0.17) & (z > 0.98) & ~yaka & ~pelerin            # kollar → zincir (gölgedeki koyu yanları aşağıda)
    ic = yesil & (ax < 0.1) & (y < -0.02) & (z > 0.76) & (z < 1.06)     # ceketin önündeki açıklık → zincir etek
    pantolon = yesil & (z <= 0.8) & ~pelerin & ~ic
    deri = (h < 0.13) & (s > 0.18) & ~ten & ~sac & ~yesil & (v < 0.75)
    metal = (s < 0.15) & (v > 0.4) & ~sac & ~yesil
    cizme = deri & (z < 0.45)
    omuzluk = deri & (ax >= 0.165) & (z > 1.27)
    kolluk = deri & (ax > 0.3) & (z <= 1.27)
    kemer = deri & (z > 1.035) & (z < 1.125) & (ax < 0.26)
    kese = deri & (z > 0.88) & (z < 1.07) & (ax > 0.1) & (ax < 0.27) & (y < -0.03)
    ceket = deri & (z > 0.74) & (z < 1.47) & (ax < 0.25) & ~omuzluk & ~kemer & ~kese & ~cizme
    kol |= (ax > 0.2) & (z > 1.0) & (z < 1.4) & ~deri & ~ten & ~metal & ~yaka & ~pelerin & ~sac
    x0 = -0.16 + (1.43 - z) / 0.37 * 0.33                               # sağ omuzdan sol kalçaya çapraz kayış (önde ve arkada)
    kayis = ceket & (np.abs(x - x0) < 0.022) & (z > 1.06) & (z < 1.44)
    ceket &= ~kayis
    D = _ciz(C, hata, [(sac, '#9090a0'), (kulak, '#ff8060'), (ten, '#ffb090'), (yaka | kol | ic, '#00ffff'), (pelerin, '#800040'), (pantolon, '#303060'),
                       (ceket, '#ff2020'), (omuzluk, '#c08040'), (kolluk, '#806020'), (kemer | kese, '#40ff40'),
                       (kayis, '#ff00ff'), (cizme, '#603000'), (metal, '#ffffff')])
    if D is not None: return D
    L = lum(C)
    boya(C, ceket, '#7b1e24', 0.9)
    boya(C, pelerin, '#6a1a20', 0.9)
    boya(C, yaka | kol | ic, '#44474d', 0.5)                          # sitenin sıcak ışığında açık gri beyaz görünüyordu
    boya(C, omuzluk, '#5e3f2a', 0.9)
    boya(C, kolluk, '#4f3424', 0.9)
    boya(C, kemer | kese | kayis, '#4a3022', 0.8)
    boya(C, pantolon, '#3a3633', 0.8)
    boya(C, cizme, '#5c4130', 0.9)
    boya(C, sac, '#4e4b4b', 0.5)
    yuz_ten = ten & bas & (y < -0.05)
    boya(C, kulak, '#%02x%02x%02x' % tuple((np.median(C[yuz_ten], 0) * 255).astype(int)), 0.4)
    # yüz: kâğıttaki gibi uzamış kısa sakal (çene ve yanak altı; dudaklar hariç)
    cene = ten & bas & (y < -0.02) & (z > 1.555) & (z < 1.614) & ~((ax < 0.024) & (z > 1.6))
    yuz = (ten & bas).astype(np.float32)
    ten |= kulak
    D = boyali(C, P, koru=yuz)
    # boyalı tarzdan sonra ince desenler (yumuşatma onları silerdi): zincirin halkaları, saçın telleri, sakalın kılları
    z_ = (yaka | kol | ic)
    halka = gurultu(P, 1400, 21)
    D[z_] = np.clip(D[z_] * (0.62 + 0.75 * halka[z_])[:, None], 0, 1)
    tel = gurultu(P * np.array([1, 1, 0.3], np.float32), 700, 22)
    ak = np.clip((ax - 0.045) / 0.04, 0, 1) * 0.45 + np.clip((gurultu(P, 260, 24) - 0.55) * 2.5, 0, 0.4)   # şakaklar ve tutam tutam ak (kırçıl)
    sk = np.clip(0.75 + 0.9 * (tel - 0.5), 0.5, 1.25)
    D[sac] = np.clip(D[sac] * sk[sac][:, None] * (1 - ak[sac][:, None]) + renk('#7c7a7c') * sk[sac][:, None] * ak[sac][:, None], 0, 1)
    kil = gurultu(P * np.array([1, 1, 0.4], np.float32), 2600, 23)
    a = np.clip(0.28 + (kil - 0.5) * 0.6, 0, 0.6)[cene][:, None]
    D[cene] = D[cene] * (1 - a) + renk('#3d3735') * a
    return D
