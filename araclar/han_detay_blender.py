# -*- coding: utf-8 -*-
"""
YENİ HAN — AYRINTILI MODEL (dokulu) Blender betiği  (2026-10-21)
=================================================================
Onaylanan blockout'un (han_blockout_blender.py, 3. sürüm) yerleşimini kullanır; ölçüler han_plan.py'de.
Parçalar gerçek biçimlerine kavuşur, eski tavernanın boyalı dokuları ve parçaları (han_parcalar.py) kullanılır.
Her çalıştığında her şeyi sıfırdan kurar.

Önce dokular hazır olmalı:   python araclar\\doku_hazirla.py     (3d/dokular/)
Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --factory-startup --python araclar\\han_detay_blender.py

Çıktılar (3d/han/):
  han-detay.blend              kaynak dosya (dokular 3d/dokular/'dan okunur)
  detay-ustten.png             tam tepeden (kuş bakışı; galeri, avize ve tavanlar gizli)
  detay-site.png               sitenin eğik açısından (kameraya bakan duvarlar alçak, onlara asılanlar gizli)
  detay-goz.png                oyun masasından bara ve galeriye, göz hizası
  detay-giris.png              giriş kapısından salona, göz hizası

Site kesiti: adı Duvar_ / Direk_ ile başlayan parçalar ve duvara asılı parçalar 'duvar' özelliği taşır (kuzey, guney,
bati, dogu). Site kameraya bakan duvarları zeminden 0,95 m'ye alçaltır, onlara asılı parçaları gizler. Bu yüzden
duvarların başlangıç noktası zemindedir (z = 0).
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from han_plan import *

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOKU = os.path.join(KOK, '3d', 'dokular')
CIKTI = os.path.join(KOK, '3d', 'han')
os.makedirs(CIKTI, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)       # parça modülü kendi geçici verisini kurmadan önce
import han_parcalar as hp
from han_parcalar import (P, M, b_kutu, b_silindir, b_arasi, b_torna, b_dilim, b_halka, b_cokgen, b_levha,
                          dondur, tasi, nesne, bagla, bos, kopya, sus)
hp.hazirla(DOKU)
sahne = bpy.context.scene

# ───────── Koleksiyonlar (blockout ile aynı düzen) ─────────
def koleksiyon(ad, ust=None):
    c = bpy.data.collections.new(ad); (ust or sahne.collection).children.link(c); return c
K = koleksiyon('Han')
K_YAPI = koleksiyon('01_Yapi', K)
K_ZEMIN, K_DUVAR, K_KAPI = koleksiyon('Zemin', K_YAPI), koleksiyon('Duvarlar', K_YAPI), koleksiyon('Kapilar_Pencereler', K_YAPI)
K_BASAMAK = koleksiyon('Basamaklar', K_YAPI)
K_TAVAN = koleksiyon('Tavan', K_YAPI)
K_GIRIS = koleksiyon('02_Giris', K)
K_SUNDURMA = koleksiyon('Sundurma', K_GIRIS)
K_BAR = koleksiyon('03_Bar', K)
K_TABURE = koleksiyon('Bar_Tabureleri', K_BAR)
K_SALON = koleksiyon('04_Salon', K)
K_AVIZE = koleksiyon('Avize', K_SALON)
K_OZAN = koleksiyon('Ozan_Bolumu', K_SALON)
K_KANAT = koleksiyon('05_Kanat_Somine', K)
K_UST = koleksiyon('06_Ust_Kat', K)
K_GALERI = koleksiyon('Galeri', K_UST)
K_ISIK = koleksiyon('07_Isik_Isaretleri', K)
K_SAB = koleksiyon('08_Sablonlar', K)
K_DEKOR = koleksiyon('09_Dekor', K)
K_YESIL = koleksiyon('Yesillik', K_DEKOR)
K_ONI = koleksiyon('99_Onizleme')

z = UST_Z
cz, cr, ch = CIKINTI
CX, CY = w(W, cz)
SANDALYE, TABURE, KOLTUK = hp.sablonlar(K_SAB, w(-6, 0)[0])
ETIKET = []
def etiket(metin, X, Y): ETIKET.append((metin, X, Y))

def pk(X0, X1, Y0, Y1, z0, z1):
    """PLAN koordinatlı köşelerle kutu (dünya koordinatında bmesh)."""
    (x0, y0), (x1, y1) = w(min(X0, X1), min(Y0, Y1)), w(max(X0, X1), max(Y0, Y1))
    return b_kutu(x0, x1, y0, y1, z0, z1)

def pnesne(ad, bm, mats, kol, X, Y, zz=0.0, aci=0.0, **k):
    """Plan koordinatındaki bir noktaya yerleşen nesne (bm yerel koordinatta)."""
    return nesne(ad, bm, mats, kol, konum=(*w(X, Y), zz), aci=aci, **k)

# ═════════ 01 YAPI ═════════
# ───────── Zeminler ─────────
(xa, ya), (xb, yb) = w(0, 0), w(W, H)
bm = bmesh.new(); P(bm, b_kutu(xa - 15, xb + 15, ya - 12, yb + 12, DIS_Z - 0.05, DIS_Z))
nesne('Dis_Toprak', bm, [M['dis_zemin']], K_ZEMIN)
# taş temel: binanın altında, dış yüzde zeminden 0,45 m yüksek taş kaide olarak görünür
bm = bmesh.new()
for X0, X1, Y0, Y1 in ((-DK, KANAT_X, KANAT_Y0 - DK, H + DK), (KANAT_X - DK, W + DK, -DK, H + DK), (GIRIS_X0 - DK, KANAT_X, GIRIS_Y0 - DK, KANAT_Y0)):
    P(bm, pk(X0 - 0.06, X1 + 0.06, Y0 - 0.06, Y1 + 0.06, DIS_Z, -0.02), 0, pah=0.02)
P(bm, b_dilim(CX, CY, 0, cr + DK + 0.06, -90, 90, DIS_Z, -0.02, n=32), 0)
nesne('Dis_Temel', bm, [M['tas']], K_ZEMIN)
bm = bmesh.new(); P(bm, pk(KANAT_X, W, 0, H, -0.04, 0.0)); nesne('Zemin', bm, [M['tas_zemin']], K_ZEMIN)   # aşağıdaki salon: altıgen taş
bm = bmesh.new(); P(bm, pk(GIRIS_X0, KANAT_X, GIRIS_Y0, KANAT_Y0, -0.04, 0.0)); nesne('Zemin_Giris', bm, [M['tas']], K_ZEMIN)
# yukarıdaki seviye (+0,60): ahşap
bm = bmesh.new()
P(bm, pk(0, KANAT_X, KANAT_Y0, H, -0.02, z)); P(bm, pk(KANAT_X, W, BANT_Y, H, 0, z)); P(bm, pk(KD_X, W, KD_Y, BANT_Y, 0, z))
KCX, KCY = w(KD_X - KAVIS_R, BANT_Y - KAVIS_R)
P(bm, b_dilim(KCX, KCY, KAVIS_R, KAVIS_R * 1.42, 0, 90, 0, z, n=24))
nesne('Zemin_Ust', bm, [M['zemin']], K_ZEMIN)
etiket('Yukarıdaki seviye (+0,60)', 11.2, 12.3); etiket('Aşağıdaki salon (0)', 14.0, 9.6)

# ───────── Basamaklar: uzun, köşesi kavisli; her basamağın ucunda koyu ahşap burun ─────────
def bant(bm, a, b, z0, z1, mi, pah=0.0):
    """Yukarıdaki seviyenin kenarından a…b (m) uzaklıktaki şerit (beş parça: batı, kuzey, kavis, doğu, güney)."""
    P(bm, pk(KANAT_X + a, KANAT_X + b, KANAT_Y0, BANT_Y - a, z0, z1), mi, pah)
    P(bm, pk(KANAT_X + a, KD_X - KAVIS_R, BANT_Y - b, BANT_Y - a, z0, z1), mi, pah)
    P(bm, b_dilim(KCX, KCY, KAVIS_R - b, KAVIS_R - a, 0, 90, z0, z1, n=20), mi)
    P(bm, pk(KD_X - b, KD_X - a, KD_Y - b, BANT_Y - KAVIS_R, z0, z1), mi, pah)
    P(bm, pk(KD_X - b, W, KD_Y - b, KD_Y - a, z0, z1), mi, pah)
bm = bmesh.new()
for k in (1, 2):
    bant(bm, BAS_D * (k - 1), BAS_D * k, 0, z - 0.2 * k, 0)
for k in (0, 1, 2):
    bant(bm, BAS_D * k - 0.06, BAS_D * k + 0.01, z - 0.2 * k - 0.035, z - 0.2 * k + 0.006, 1)
nesne('Zemin_Basamaklar', bm, [M['zemin'], M['koyu']], K_BASAMAK)
etiket('3 basamak', 8.6, 11.0)

# ───────── Duvarlar: sıva, iç yüzde süpürgelik, galeri hizasında ve tepede ahşap kuşak ─────────
def duvar(ad, eksen, sabit, a0, a1, disari, z0, z1, bosluklar=(), zemin=0.0, tag=None, supurge=True, kusak=True):
    """Eksene paralel duvar, boşluklarıyla, tek nesne. eksen 'x': Y = sabit'te X a0…a1; 'y': X = sabit'te Y a0…a1.
    disari: dışa doğru kalınlaşma yönü (+1 / −1). bosluklar: [(b0, b1, z0, z1)]. zemin: iç taraftaki zemin yüksekliği
    (sayı ya da konuma göre işlev). tag: site kesiti için duvarın adı."""
    t0, t1 = sorted((sabit, sabit + disari * DK))
    i0, i1 = sorted((sabit, sabit - disari * 0.035))                  # iç yüze çakılı ahşap şeritler
    bm = bmesh.new()
    def kt(b0, b1, u0, u1, za, zb, mi, pah=0.0):
        if b1 - b0 < 1e-3 or zb - za < 1e-3: return
        P(bm, pk(b0, b1, u0, u1, za, zb) if eksen == 'x' else pk(u0, u1, b0, b1, za, zb), mi, pah)
    # Gövde: boşlukların kenarlarından geçen ızgaranın hücreleri; komşu hücreler aynı köşeleri paylaşır, aradaki yüzler silinir,
    # köşeler kaynar. (Önceden ayrı kutulardı: pencere köşesi komşu şeridin kenarına yalnızca değiyordu, eğrilik onu kaydırınca
    # yarık açılıyor, içerideki karanlık yüz kesik kesik çizgi gibi görünüyordu.)
    us = sorted({a0, a1} | {min(max(v, a0), a1) for b0, b1, _, _ in bosluklar for v in (b0, b1)})
    zs = sorted({z0, z1} | {min(max(v, z0), z1) for _, _, bz0, bz1 in bosluklar for v in (bz0, bz1)})
    gv = bmesh.new()
    for u0, u1 in zip(us, us[1:]):
        for za, zb in zip(zs, zs[1:]):
            um, zm = (u0 + u1) / 2, (za + zb) / 2
            if u1 - u0 < 1e-3 or zb - za < 1e-3 or any(b0 < um < b1 and bz0 < zm < bz1 for b0, b1, bz0, bz1 in bosluklar): continue
            P(gv, pk(u0, u1, t0, t1, za, zb) if eksen == 'x' else pk(t0, t1, u0, u1, za, zb), 0)
    anah = lambda f: tuple(sorted(tuple(round(c, 4) for c in v.co) for v in f.verts))
    say = {}
    for f in gv.faces: say[anah(f)] = say.get(anah(f), 0) + 1
    bmesh.ops.delete(gv, geom=[f for f in gv.faces if say[anah(f)] > 1], context='FACES_ONLY')
    bmesh.ops.remove_doubles(gv, verts=gv.verts, dist=1e-4)
    P(bm, gv, 0)
    zf = zemin if callable(zemin) else (lambda a: zemin)
    if supurge:                                       # süpürgelik: kapı boşluklarında kesilir, zemin değişen yerde bölünür
        kes = [a0] + [v for b0, b1, bz0, bz1 in sorted(bosluklar) if bz0 <= zf((b0 + b1) / 2) + 0.3 for v in (b0, b1)] + [a1]
        for s0, s1 in zip(kes[0::2], kes[1::2]):
            for p0, p1 in ([(s0, KD_Y), (KD_Y, s1)] if callable(zemin) and s0 < KD_Y < s1 else [(s0, s1)]):
                zz = zf((p0 + p1) / 2); kt(p0, p1, i0, i1, zz, zz + 0.22, 1, 0.008)
    if kusak and z1 > GALERI_Z:
        kz = GALERI_Z - 0.45
        nok = [a0] + [v for b0, b1, bz0, bz1 in sorted(bosluklar) if bz0 < kz + 0.2 and bz1 > kz for v in (b0, b1)] + [a1]
        for s0, s1 in zip(nok[0::2], nok[1::2]): kt(s0, s1, i0, i1, kz, kz + 0.2, 1, 0.01)
    kt(a0, a1, t0 - 0.03, t1 + 0.03, z1 - 0.2, z1, 1, 0.015)              # tepede kiriş
    return nesne(ad, bm, [M['duvar'], M['koyu']], K_DUVAR, ic=tag)

pz0, pz1 = PENCERE_Z
oda = [(x, x + 1.0, GALERI_Z, GALERI_Z + 2.1) for x in ODA_KAPILARI]
pu0, pu1 = PENCERE_DOGU_UST
duvar('Duvar_Guney', 'x', 0, KANAT_X - DK, W + DK, -1, 0, DH, [(a, b, pz0, pz1) for a, b in PENCERE_GUNEY], 0, 'guney')
duvar('Duvar_Bati_Kose', 'y', KANAT_X, -DK, GIRIS_Y0, -1, 0, DH, (), 0, 'bati', supurge=False)
duvar('Duvar_Bati_Gecit_Ust', 'y', KANAT_X, GIRIS_Y0, KANAT_Y0, -1, GIRIS_H + 0.15, DH, (), 0, 'bati', supurge=False)
duvar('Duvar_Guney_Giris', 'x', GIRIS_Y0, GIRIS_X0 - DK, KANAT_X - DK, -1, 0, GIRIS_H, (), 0, 'guney', kusak=False)
duvar('Duvar_Bati_Giris', 'y', GIRIS_X0, GIRIS_Y0 - DK, KANAT_Y0, -1, 0, GIRIS_H, [(KAPI_Y[0], KAPI_Y[1], -1, GIRIS_H + 1)], 0, 'bati', kusak=False)
duvar('Duvar_Guney_Kanat', 'x', KANAT_Y0, -DK, GIRIS_X0 - DK, -1, 0, DH, (), z, 'guney')
duvar('Duvar_Guney_Kanat_Ust', 'x', KANAT_Y0, GIRIS_X0 - DK, KANAT_X, -1, GIRIS_H + 0.15, DH, (), z, 'guney', supurge=False)
duvar('Duvar_Bati', 'y', 0, KANAT_Y0 - DK, H + DK, -1, 0, DH, [(a, b, pz0 + z, pz1 + z) for a, b in PENCERE_KANAT], z, 'bati')
duvar('Duvar_Kuzey', 'x', H, -DK, W + DK, 1, 0, DH, [(MUTFAK[0], MUTFAK[1], z, z + 2.2)] + oda, z, 'kuzey')
duvar('Duvar_Dogu', 'y', W, -DK, H + DK, 1, 0, DH, [(cz - cr, cz + cr, -1, ch), (pu0, pu1, GALERI_Z + 0.8, GALERI_Z + 2.2)],
      lambda a: z if a > KD_Y else 0.0, 'dogu')
# kemerli kapının üstü: kemer dolgusu (sıva) ve taş kemer (giriş bölümünün batı duvarında)
KR = (KAPI_Y[1] - KAPI_Y[0]) / 2; KMY = (KAPI_Y[0] + KAPI_Y[1]) / 2; KZ0 = GIRIS_H - KR   # kemerin doğduğu yükseklik
def dik_prizma(pts_uz, X0, X1):
    """Önden bakınca (Y, z) köşeli, X0…X1 kalınlığında prizma (batı / doğu duvarlarındaki kemerler)."""
    bm = bmesh.new()
    a = [bm.verts.new((*w(X0, u), zz)) for u, zz in pts_uz]; b = [bm.verts.new((*w(X1, u), zz)) for u, zz in pts_uz]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    for i in range(len(a)):
        j = (i + 1) % len(a); bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
yay = [(KMY + KR * math.cos(t), KZ0 + KR * math.sin(t)) for t in (math.pi * i / 24 for i in range(25))]   # doğu → batı
bm = bmesh.new()
for taraf in (0, 1):                                   # iki yandaki köşe dolgusu
    if taraf == 0: pts = [(KAPI_Y[1], GIRIS_H), (KAPI_Y[1], KZ0)] + [p for p in yay if p[0] >= KMY][1:] + [(KMY, GIRIS_H)]
    else:          pts = [(KMY, GIRIS_H)] + [p for p in yay if p[0] <= KMY] + [(KAPI_Y[0], GIRIS_H)]
    P(bm, dik_prizma(pts, GIRIS_X0 - DK, GIRIS_X0), 0)
dis = [(KMY + (KR + 0.22) * math.cos(t), KZ0 + (KR + 0.22) * math.sin(t)) for t in (math.pi * i / 24 for i in range(25))]
P(bm, dik_prizma(dis + list(reversed(yay)), GIRIS_X0 - DK - 0.05, GIRIS_X0 + 0.03), 1)
nesne('Duvar_Bati_Giris_Kemer', bm, [M['duvar'], M['tas']], K_DUVAR, ic='bati')

# ───────── Ahşap direkler (duvar boyunca; site kameraya bakanları da alçaltır) ─────────
def direkler(ad, tag, noktalar, alt, ust):
    bm = bmesh.new()
    for X, Y in noktalar:
        P(bm, pk(X - 0.13, X + 0.13, Y - 0.13, Y + 0.13, alt(X, Y), ust), 0, pah=0.015)
        P(bm, pk(X - 0.17, X + 0.17, Y - 0.17, Y + 0.17, alt(X, Y), alt(X, Y) + 0.12), 1, pah=0.015)   # taş kaide
    return nesne(ad, bm, [M['koyu'], M['tas']], K_DUVAR, ic=tag)
lv = lambda X, Y: seviye(X, Y)
direkler('Direk_Guney', 'guney', [(KANAT_X + 0.13, 0.13), (11.7, 0.13), (15.7, 0.13), (19.7, 0.13), (W - 0.13, 0.13)], lv, DH - 0.2)
direkler('Direk_Bati', 'bati', [(0.13, KANAT_Y0 + 0.13), (0.13, 8.5), (0.13, 12.0), (0.13, H - 0.13)], lv, DH - 0.2)
direkler('Direk_Kuzey', 'kuzey', [(KANAT_X, H - 0.13), (GALERI_X0 - 0.4, H - 0.13)], lv, DH - 0.2)
direkler('Direk_Dogu', 'dogu', [(W - 0.13, KD_Y - 0.2), (W - 0.13, H - 0.13)], lv, DH - 0.2)

# ───────── Pencereler: ahşap kasa, haç kayıt, kurşunlu cam (duvara asılı: kesitte gizlenir) ─────────
def pencere(ad, eksen, sabit, b0, b1, z0, z1, disari, tag):
    """Duvar boşluğunun iki yüzünde kasa, ortada haç biçimli kayıt ve cam."""
    t0, t1 = sorted((sabit, sabit + disari * DK)); tm = (t0 + t1) / 2
    bm = bmesh.new()
    def kt(c0, c1, u0, u1, za, zb, mi, pah=0.0):
        P(bm, pk(c0, c1, u0, u1, za, zb) if eksen == 'x' else pk(u0, u1, c0, c1, za, zb), mi, pah)
    for u0, u1 in ((t0 - 0.04, t0 + 0.04), (t1 - 0.04, t1 + 0.04)):          # iki yüzde kasa
        kt(b0 - 0.1, b1 + 0.1, u0, u1, z0 - 0.1, z0, 0, 0.008); kt(b0 - 0.1, b1 + 0.1, u0, u1, z1, z1 + 0.12, 0, 0.008)
        kt(b0 - 0.1, b0, u0, u1, z0, z1, 0, 0.008); kt(b1, b1 + 0.1, u0, u1, z0, z1, 0, 0.008)
    kt(b0 - 0.15, b1 + 0.15, t0 - 0.12, t1 + 0.12, z0 - 0.16, z0 - 0.08, 0, 0.01)   # denizlik
    mb, mz = (b0 + b1) / 2, z0 + (z1 - z0) * 0.62
    kt(mb - 0.03, mb + 0.03, tm - 0.03, tm + 0.03, z0, z1, 0); kt(b0, b1, tm - 0.03, tm + 0.03, mz - 0.03, mz + 0.03, 0)
    kt(b0, b1, tm - 0.008, tm + 0.008, z0, z1, 1)
    return nesne(ad, bm, [M['koyu'], M['pencere']], K_KAPI, ic=tag)
for i, (a, b) in enumerate(PENCERE_GUNEY): pencere(f'Pencere_Guney_{i + 1}', 'x', 0, a, b, pz0, pz1, -1, 'guney')
for i, (a, b) in enumerate(PENCERE_KANAT): pencere(f'Pencere_Bati_{i + 1}', 'y', 0, a, b, pz0 + z, pz1 + z, -1, 'bati')
pencere('Pencere_Dogu_Ust', 'y', W, pu0, pu1, GALERI_Z + 0.8, GALERI_Z + 2.2, 1, 'dogu')

# ───────── Doğudaki çıkıntı: eğri duvar (dilim dilim), üç pencere ─────────
N_YAY = 12
for i in range(N_YAY):
    t0, t1 = -90 + 180 * i / N_YAY, -90 + 180 * (i + 1) / N_YAY; tm = (t0 + t1) / 2
    tag = 'guney' if tm < -45 else ('kuzey' if tm > 45 else 'dogu')
    bm = bmesh.new()
    if i in PENCERE_CIKINTI:
        for za, zb in ((0, pz0), (pz1 + 0.3, ch)): P(bm, b_dilim(CX, CY, cr, cr + DK, t0, t1, za, zb, n=2), 0)
        P(bm, b_dilim(CX, CY, cr - 0.035, cr, t0, t1, pz0 - 0.1, pz0, n=2), 1); P(bm, b_dilim(CX, CY, cr - 0.035, cr, t0, t1, pz1 + 0.3, pz1 + 0.42, n=2), 1)
    else:
        P(bm, b_dilim(CX, CY, cr, cr + DK, t0, t1, 0, ch, n=2), 0)
    P(bm, b_dilim(CX, CY, cr - 0.035, cr, t0, t1, SAHNE_H, SAHNE_H + 0.22, n=2), 1)          # süpürgelik
    P(bm, b_dilim(CX, CY, cr - 0.03, cr + DK + 0.03, t0, t1, ch - 0.2, ch, n=2), 1)          # tepede kiriş
    nesne(f'Duvar_Cikinti_{i + 1:02d}', bm, [M['duvar'], M['koyu']], K_DUVAR, ic=tag)
    if i in PENCERE_CIKINTI:
        bm = bmesh.new()
        P(bm, b_dilim(CX, CY, cr + 0.1, cr + 0.14, t0 + 1.5, t1 - 1.5, pz0, pz1 + 0.3, n=2), 1)
        P(bm, b_dilim(CX, CY, cr + 0.08, cr + 0.16, (t0 + t1) / 2 - 0.6, (t0 + t1) / 2 + 0.6, pz0, pz1 + 0.3, n=1), 0)
        nesne(f'Pencere_Cikinti_{i + 1:02d}', bm, [M['koyu'], M['pencere']], K_KAPI, ic=tag)
bm = bmesh.new(); P(bm, b_dilim(CX, CY, 0, cr + DK + 0.1, -90, 90, ch, ch + 0.12, n=32), 0)
nesne('Cikinti_Tavan', bm, [M['koyu']], K_TAVAN)

# ───────── Tavan: tahta ve kalın kirişler (yalnızca göz hizasında görünür) ─────────
bm = bmesh.new()
P(bm, pk(-DK, W + DK, -DK, H + DK, DH, DH + 0.08), 0)
X = 1.2
while X < W:
    P(bm, pk(X - 0.14, X + 0.14, 0, H, DH - 0.3, DH), 1, pah=0.02); X += 2.6
nesne('Tavan', bm, [M['zemin'], M['koyu']], K_TAVAN)

# ═════════ 02 GİRİŞ ═════════
# Kemerli çift kanatlı kapı: güneydeki kanat kapalı, kuzeydeki içeri açık; üstte kemerli ahşap ayna
def kanat_bm(L, hz):
    """Dikey tahtalı kapı kanadı (yerel: menteşe x=0, kanat +y boyunca L, kalınlık x)."""
    bm = bmesh.new()
    n = 5
    for i in range(n):
        P(bm, b_kutu(-0.03, 0.03, L * i / n + 0.004, L * (i + 1) / n - 0.004, 0.0, hz), 0, pah=0.006)
    for zz in (0.35, hz - 0.45):
        P(bm, b_kutu(-0.045, 0.045, 0.04, L - 0.04, zz, zz + 0.07), 1)                    # demir kuşak
    P(bm, b_arasi((0.06, L - 0.15, 1.0), (0.06, L - 0.15, 1.1), 0.03, n=8), 1)            # halka tokmak
    return bm
L = KR
kx, _ = w(GIRIS_X0 + 0.04, 0)
for i, (Y, aci) in enumerate(((KAPI_Y[0], 0), (KAPI_Y[1], 72))):
    bm = kanat_bm(L, KZ0)
    if i == 1:
        for v in bm.verts: v.co.y = -v.co.y                                              # kuzey kanadın menteşesi kuzey ucunda
    o = nesne(f'Kapi_Giris_Kanat_{i + 1}', bm, [M['koyu'], M['demir']], K_KAPI, konum=(kx, w(0, Y)[1], 0), ic='bati')
    o.rotation_euler.z = math.radians(aci)                                                  # içeri (doğuya) açılır
bm = bmesh.new(); P(bm, dik_prizma([(KAPI_Y[0], KZ0)] + list(reversed(yay)) + [(KAPI_Y[1], KZ0)], GIRIS_X0 + 0.0, GIRIS_X0 + 0.06), 0)
nesne('Kapi_Giris_Ayna', bm, [M['koyu']], K_KAPI, ic='bati')
# İç: tavan, diz duvarı, salona açılan geçit (direk ve kiriş), halı, sandıklar, fıçı, askılık ve pelerinler, bank
bm = bmesh.new(); P(bm, pk(GIRIS_X0 - DK, KANAT_X, GIRIS_Y0 - DK, KANAT_Y0, GIRIS_H, GIRIS_H + 0.15), 0)
X = GIRIS_X0 + 0.6
while X < KANAT_X:
    P(bm, pk(X - 0.1, X + 0.1, GIRIS_Y0, KANAT_Y0, GIRIS_H - 0.2, GIRIS_H), 1, pah=0.015); X += 1.3
nesne('Giris_Tavan', bm, [M['zemin'], M['koyu']], K_TAVAN)
bm = bmesh.new()
P(bm, pk(GIRIS_X0, KANAT_X, KANAT_Y0 - 0.15, KANAT_Y0, 0, z + 0.85), 0)
P(bm, pk(GIRIS_X0, KANAT_X, KANAT_Y0 - 0.2, KANAT_Y0 + 0.05, z + 0.85, z + 0.93), 1, pah=0.012)
nesne('Giris_Diz_Duvari', bm, [M['duvar'], M['koyu']], K_GIRIS)
bm = bmesh.new()
P(bm, pk(KANAT_X - DK, KANAT_X, GIRIS_Y0, GECIT_Y, 0, GIRIS_H), 0)
P(bm, pk(KANAT_X - 0.36, KANAT_X + 0.1, KANAT_Y0 - 0.46, KANAT_Y0, 0, GIRIS_H), 1, pah=0.02)
P(bm, pk(KANAT_X - 0.32, KANAT_X + 0.06, GECIT_Y, KANAT_Y0, 2.7, GIRIS_H), 1, pah=0.02)
for Y in (GECIT_Y + 0.05, KANAT_Y0 - 0.5):                                                    # kirişin köşe destekleri
    s = 1 if Y < 2 else -1
    P(bm, b_arasi((*w(KANAT_X - 0.13, Y), 2.2), (*w(KANAT_X - 0.13, Y + s * 0.5), 2.72), 0.05, n=6), 1)
nesne('Giris_Gecit', bm, [M['duvar'], M['koyu']], K_GIRIS)
gx, gy = w((GIRIS_X0 + KANAT_X) / 2 - 0.3, (GIRIS_Y0 + KANAT_Y0) / 2)
HB = 1.6; HE = HB * hp.oran('hali.png')
def yer_levha(en, boy, zz):
    """Yerde duran tek yüzlü levha (halı, post): zeminin 4 mm üstünde; alt yüzü olmadığı için zeminle çakışmaz."""
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x, y, zz + 0.004)) for x, y in ((-en / 2, -boy / 2), (en / 2, -boy / 2), (en / 2, boy / 2), (-en / 2, boy / 2))])
    f.normal_update()
    if f.normal.z < 0: f.normal_flip()
    return bm
def hali_uv(en, boy):
    def f(bm, uvl):
        for fc in bm.faces:
            for l in fc.loops: l[uvl].uv = (l.vert.co.x / en + 0.5, l.vert.co.y / boy + 0.5)
    return f
bm = bmesh.new(); P(bm, yer_levha(HE, HB, 0.0)); nesne('Giris_Hali', bm, [M['hali']], K_GIRIS, konum=(gx, gy, 0), uv_ozel=hali_uv(HE, HB))
for i, (X, Y, s, zz, a) in enumerate(((2.1, 1.3, 0.55, 0, 8), (2.1, 1.3, 0.42, 0.55, -10), (2.8, 1.2, 0.45, 0, 20), (6.3, 3.3, 0.5, 0, -6))):
    hp.sandik(f'Giris_Sandik_{i + 1}', K_GIRIS, *w(X, Y), zz, s, s, s * 0.9, a)
hp.fici('Giris_Fici', K_GIRIS, *w(6.3, 1.5), 0.3, 0.85, 15)
bm = bmesh.new()                                                                              # askılık: duvara çakılı tahta ve çiviler
P(bm, pk(3.4, 4.6, GIRIS_Y0, GIRIS_Y0 + 0.04, 1.7, 1.82), 0, pah=0.006)
for X in (3.6, 3.95, 4.3):
    P(bm, b_arasi((*w(X, GIRIS_Y0 + 0.03), 1.76), (*w(X, GIRIS_Y0 + 0.16), 1.8), 0.012, n=6), 1)
for i, (X, mat) in enumerate(((3.6, 'perde'), (4.3, 'sancak'))):                              # asılı pelerinler
    b = bmesh.new(); hp.perde(b, -0.2, 0.2, 0.75, 1.78, 0.0, kivrim=2, derin=0.03); tasi(b, *w(X, GIRIS_Y0 + 0.12)); P(bm, b, 2 + i, yumusak=True)
nesne('Giris_Askilik', bm, [M['koyu'], M['demir'], M['perde'], M['cuval']], K_GIRIS, ic='guney')
hp.bank_kur('Giris_Bank', 1.4, K_GIRIS, (*w(5.1, GIRIS_Y0 + 0.25), 0))
hp.aplik('Aplik_Giris', K_GIRIS, *w(6.0, GIRIS_Y0), 0, 2.2, ic='guney')
etiket('Giriş', 4.3, 2.4)

# Sundurma: ahşap döşeme, iki basamak, iki direk ve köşe destekleri, kavisli saçak, direğe asılı tabela ve fener
SX0 = GIRIS_X0 - DK
bm = bmesh.new()
P(bm, pk(SX0 - 2.4, SX0, KAPI_Y[0] - 0.6, KAPI_Y[1] + 0.6, DIS_Z, 0), 0, pah=0.01)
for i in (1, 2):
    P(bm, pk(SX0 - 2.4 - 0.32 * i, SX0 - 2.4 - 0.32 * (i - 1) + 0.02, KAPI_Y[0] - 0.4, KAPI_Y[1] + 0.4, DIS_Z, -0.15 * i), 0, pah=0.01)
for Y in (KAPI_Y[0] - 0.5, KAPI_Y[1] + 0.5):
    P(bm, pk(SX0 - 2.32, SX0 - 2.08, Y - 0.12, Y + 0.12, 0, 2.95), 1, pah=0.015)
    P(bm, b_arasi((*w(SX0 - 2.2, Y), 2.3), (*w(SX0 - 1.5, Y), 2.95), 0.05, n=6), 1)
P(bm, pk(SX0 - 2.4, SX0, KAPI_Y[1] + 0.38, KAPI_Y[1] + 0.62, 2.85, 3.05), 1, pah=0.015)
P(bm, pk(SX0 - 2.4, SX0, KAPI_Y[0] - 0.62, KAPI_Y[0] - 0.38, 2.85, 3.05), 1, pah=0.015)
nesne('Sundurma', bm, [M['zemin'], M['koyu']], K_SUNDURMA)
bm = bmesh.new()
for i in range(8):                                                                            # kavisli saçak: duvardan öne doğru bombeli
    t0, t1 = i / 8, (i + 1) / 8
    x0, x1 = SX0 + 0.1 - 2.7 * t0, SX0 + 0.1 - 2.7 * t1
    z0_, z1_ = 3.45 - 0.55 * t0 + 0.35 * math.sin(math.pi * t0), 3.45 - 0.55 * t1 + 0.35 * math.sin(math.pi * t1)
    b = bmesh.new()
    ys = (KAPI_Y[0] - 0.85, KAPI_Y[1] + 0.85)
    v = [b.verts.new((*w(x0, ys[0]), z0_)), b.verts.new((*w(x0, ys[1]), z0_)), b.verts.new((*w(x1, ys[1]), z1_)), b.verts.new((*w(x1, ys[0]), z1_))]
    v2 = [b.verts.new((p.co.x, p.co.y, p.co.z + 0.06)) for p in v]
    b.faces.new(v); b.faces.new(list(reversed(v2)))
    for j in range(4): b.faces.new((v[j], v[(j + 1) % 4], v2[(j + 1) % 4], v2[j]))
    bmesh.ops.recalc_face_normals(b, faces=b.faces); P(bm, b, 0)
nesne('Sundurma_Sacak', bm, [M['cati']], K_SUNDURMA)
kur, uv, mats = hp.tabela(0.9, 1.75, 2.45)
hp.duvar_parcasi('Sundurma_Tabela', K_SUNDURMA, *w(SX0 - 2.2, KAPI_Y[1] + 1.15), 90, kur, mats, uv)
hp.sarkit('Sarkit_Sundurma', *w(SX0 - 1.2, (KAPI_Y[0] + KAPI_Y[1]) / 2), 2.15, K_SUNDURMA, 3.1)
hp.saksi('Bitki_Sundurma', K_SUNDURMA, *w(SX0 - 0.35, KAPI_Y[0] - 0.4), 1.1, 0.24, 0.0, kart=9)
etiket('Sundurma', SX0 - 1.2, 0.3)

# ═════════ 04 SALON ═════════
# Kürsü: kızıl ahşap, kenarında koyu çıta, ortasında kakma halka; çevresinde bir basamak
bm = bmesh.new()
P(bm, b_silindir(0, 0, KURSU_R + BAS_D, 0, 0.15, n=64), 0, pah=0.01)
P(bm, b_silindir(0, 0, KURSU_R, 0.15, KURSU_H, n=64), 0, pah=0.01)
P(bm, b_halka(KURSU_R - 0.05, KURSU_R + 0.01, KURSU_H - 0.03, KURSU_H + 0.006, n=64), 1)
P(bm, b_halka(KURSU_R + BAS_D - 0.05, KURSU_R + BAS_D + 0.01, 0.12, 0.156, n=64), 1)
P(bm, b_halka(2.0, 2.06, KURSU_H, KURSU_H + 0.003, n=64), 1)
nesne('Kursu', bm, [M['kursu'], M['koyu']], K_SALON)

def masa_kur(ad, kol, x, y, zz, r, n, sr, ilk_aci, donme):
    k = koleksiyon(ad, kol)
    kok = bos(ad, k, x, y, zz, boy=r * 0.6, tur='CIRCLE')
    parcalar = [hp.masa_govde(ad, r, k, (x, y, zz))]
    for i in range(n):
        a = ilk_aci + 360 * i / n + sus.uniform(-donme, donme) * 0.6; ra = math.radians(a)
        parcalar.append(kopya(f'{ad}_Sandalye_{i + 1}', SANDALYE, k, x + sr * math.sin(ra), y + sr * math.cos(ra), zz, a + 180 + sus.uniform(-donme, donme)))
    for p in parcalar: bagla(p, kok)
    return kok, k

# Oyun masası: ortada harita, her koltuğun önünde karakter kâğıdı, kitap yığınları, mumlar (ortası zarlar için açık)
KOK_ORTA, KOL_ORTA = masa_kur('Masa_Orta', K_SALON, 0, 0, KURSU_H, ORTA_R, ORTA_SANDALYE, ORTA_SANDALYE_R, 0, 4)
UZ = KURSU_H + 0.80
HW_ = 0.95; HH_ = HW_ / hp.oran('harita.jpg')
bm = bmesh.new(); P(bm, b_kutu(-HW_ / 2, HW_ / 2, -HH_ / 2, HH_ / 2, UZ, UZ + 0.004))
def harita_uv(bm, uvl):
    for fc in bm.faces:
        for l in fc.loops: l[uvl].uv = (l.vert.co.x / HW_ + 0.5, l.vert.co.y / HH_ + 0.5)
bagla(nesne('Masa_Harita', bm, [M['harita']], KOL_ORTA, aci=12, uv_ozel=harita_uv), KOK_ORTA)
bm = bmesh.new()
for i in range(ORTA_SANDALYE):
    a = 360 * i / ORTA_SANDALYE; ra = math.radians(a); rr = ORTA_R - 0.24
    b = b_kutu(-0.105, 0.105, -0.145, 0.145, UZ, UZ + 0.003); dondur(b, a + sus.uniform(-15, 15)); tasi(b, rr * math.sin(ra), rr * math.cos(ra)); P(bm, b, 0)
for i, (a, n) in enumerate(((70, 3), (200, 2), (305, 2))):
    ra = math.radians(a); rr = ORTA_R - 0.5
    for j in range(n):
        b = b_kutu(-0.1, 0.1, -0.135, 0.135, UZ + j * 0.045, UZ + (j + 1) * 0.045 - 0.004); dondur(b, a + sus.uniform(-20, 20))
        tasi(b, rr * math.sin(ra), rr * math.cos(ra)); P(bm, b, 1, pah=0.006)
for j in range(6):                                                                            # iskambil / büyü kartları
    b = b_kutu(-0.032, 0.032, -0.045, 0.045, UZ + 0.004, UZ + 0.006); dondur(b, sus.uniform(0, 180)); tasi(b, 0.35 + sus.uniform(-0.1, 0.1), -0.45 + sus.uniform(-0.1, 0.1)); P(bm, b, 0)
bagla(nesne('Masa_Orta_Kagitlar', bm, [M['kagit'], M['kitap_d']], KOL_ORTA), KOK_ORTA)
for a in (120, 250, 15):
    ra = math.radians(a); rr = ORTA_R - 0.42
    hp.yeni_mum(rr * math.sin(ra), rr * math.cos(ra), UZ, KOL_ORTA, KOK_ORTA)
etiket('Oyun masası (kürsü +0,30)', MASA[0], MASA[1] - 1.6)
hp.avize_cember('Avize', K_AVIZE, 0, 0, KURSU_H + 3.2, 0.95, 10, DH - 0.3)

# Yan masalar: ad yalnızca harf (site: /^Masa_[A-Za-z]+$/), üstünde mum, kupalar, tabak
YAN_ADLAR = ['Masa_Kuzeybati', 'Masa_Guneybati', 'Masa_Dogu', 'Masa_Guneydogu']
for i, ((X, Y), ad) in enumerate(zip(YAN_MASALAR, YAN_ADLAR)):
    x, y = w(X, Y)
    kok, k = masa_kur(ad, K_SALON, x, y, 0, YAN_R, 4, YAN_SANDALYE_R, 45 + sus.uniform(-20, 20), 8)
    hp.yeni_mum(x + sus.uniform(-0.1, 0.1), y + sus.uniform(-0.1, 0.1), 0.80, k, kok)
    bm = bmesh.new()
    for _ in range(2):
        a = sus.uniform(0, 2 * math.pi); rr = YAN_R * sus.uniform(0.45, 0.7)
        hp.kupa_kur(bm, x + rr * math.cos(a), y + rr * math.sin(a), 0.80, sus.uniform(0, 360))
    a = sus.uniform(0, 2 * math.pi); hp.tabak_kur(bm, x + 0.4 * math.cos(a), y + 0.4 * math.sin(a), 0.80, mi=0)
    if i == 2:                                                                                # birinde iskambil kâğıtları
        for j in range(6):
            b = b_kutu(-0.032, 0.032, -0.045, 0.045, 0.80, 0.803); dondur(b, sus.uniform(0, 180)); tasi(b, x + sus.uniform(-0.3, 0.3), y + sus.uniform(-0.3, 0.3)); P(bm, b, 2)
    bagla(nesne(f'{ad}_Ustu', bm, [M['kalay'], M['bira'], M['kagit']], k), kok)
    etiket(ad, X, Y - 1.4)
o = kopya('Devrik_Sandalye', SANDALYE, K_DEKOR, *w(12.0, 3.7), 0.3, 30)
o.rotation_euler = (math.radians(-90), 0, math.radians(-30))

# ═════════ OZAN BÖLÜMÜ (doğudaki çıkıntı) ═════════
# Sahne çıkıntının tamamını kaplar, önünde bir basamak; açıklığın iki yanında kalın direk, üstünde kiriş, perdeler
bm = bmesh.new()
P(bm, b_dilim(CX, CY, 0, cr + 0.02, -90, 90, 0, SAHNE_H, n=32), 0)
P(bm, pk(W - 0.02, W + DK, cz - cr + 0.02, cz + cr - 0.02, 0, SAHNE_H), 0)
P(bm, pk(W - 0.4, W, cz - cr + 0.4, cz + cr - 0.4, 0, 0.15), 0, pah=0.01)
P(bm, pk(W - 0.06, W + 0.01, cz - cr + 0.4, cz + cr - 0.4, SAHNE_H - 0.035, SAHNE_H + 0.006), 1)
P(bm, pk(W - 0.46, W - 0.39, cz - cr + 0.4, cz + cr - 0.4, 0.115, 0.156), 1)
nesne('Ozan_Sahnesi', bm, [M['zemin'], M['koyu']], K_OZAN)
bm = bmesh.new()
for a, b in ((cz - cr, cz - cr + 0.4), (cz + cr - 0.4, cz + cr)):
    P(bm, pk(W - 0.22, W + 0.25, a, b, 0, ch), 0, pah=0.02)
    P(bm, pk(W - 0.27, W + 0.3, a - 0.05, b + 0.05, 0, 0.3), 1, pah=0.02)
P(bm, pk(W - 0.22, W + 0.25, cz - cr, cz + cr, ch - 0.55, ch), 0, pah=0.02)
for s in (-1, 1):                                                                            # kirişin köşe destekleri
    Y = cz + s * (cr - 0.4)
    P(bm, b_arasi((*w(W - 0.05, Y), ch - 1.25), (*w(W - 0.05, Y - s * 0.7), ch - 0.55), 0.06, n=6), 0)
nesne('Ozan_Cerceve', bm, [M['koyu'], M['tas']], K_OZAN)
bm = bmesh.new()
for s in (-1, 1):
    Y0 = cz + s * (cr - 0.4); Y1 = Y0 - s * 0.75
    wy0, wy1 = sorted((w(0, Y0)[1], w(0, Y1)[1]))
    b = bmesh.new(); hp.perde(b, wy0, wy1, SAHNE_H + 0.02, ch - 0.55, w(W + 0.12, 0)[0], kivrim=4, derin=0.05)
    for v in b.verts: v.co.x, v.co.y = v.co.y, v.co.x                                         # perde düzlemi kuzey-güney boyunca
    P(bm, b, 0, yumusak=True)
P(bm, b_arasi((*w(W + 0.12, cz - cr + 0.35), ch - 0.6), (*w(W + 0.12, cz + cr - 0.35), ch - 0.6), 0.02, n=8), 1)
nesne('Ozan_Perdeler', bm, [M['perde'], M['dovme']], K_OZAN)
kur, mats, SH = hp.sancak(3.4, 0.9)
hp.duvar_parcasi('Ozan_Sancak', K_OZAN, *w(W + cr - 0.02, cz), 270, kur, mats, koru={2}, ic='dogu')
bm = bmesh.new(); hp.ozan_esyalari(bm, SAHNE_H)
pnesne('Ozan_Esyalari', bm, [M['zemin'], M['ahsap'], M['masa'], M['deri'], M['koyu'], M['dovme']], K_OZAN, W + 1.5, cz, 0, aci=-90)
for i, Y in enumerate((cz - cr + 0.75, cz + cr - 0.75)):                                     # sahnenin önünde ayaklı şamdanlar
    bm = bmesh.new()
    P(bm, b_torna(0, 0, [(0, 0.16), (0.04, 0.17), (0.08, 0.05), (1.2, 0.03), (1.25, 0.08), (1.3, 0.09)], n=12), 0, yumusak=True)
    for k_ in range(3):
        a = math.radians(120 * k_); P(bm, b_arasi((0, 0, 0.3), (0.2 * math.cos(a), 0.2 * math.sin(a), 0.0), 0.02, n=6), 0)
    pnesne(f'Ozan_Samdan_{i + 1}', bm, [M['dovme']], K_OZAN, W + 0.45, Y, SAHNE_H)
    hp.yeni_mum(*w(W + 0.45, Y), SAHNE_H + 1.3, K_OZAN)
hp.saksi('Bitki_Ozan', K_OZAN, *w(W + 2.2, cz + 1.6), 1.0, 0.24, SAHNE_H, kart=9)
etiket('Ozan bölümü', W + 1.4, cz)

# ═════════ 03 BAR (kuzey duvarı boyunca, düz; yukarıdaki seviyede) ═════════
BX0, BX1 = BAR_X
bm = bmesh.new()
P(bm, pk(BX0, BX1, TEZ_Y + 0.06, TEZ_Y + 0.6, z + 0.10, z + TEZGAH_H - 0.06), 0)
P(bm, pk(BX0, BX1, TEZ_Y + 0.12, TEZ_Y + 0.6, z, z + 0.10), 1)
P(bm, pk(BX0 - 0.03, BX1 + 0.03, TEZ_Y - 0.06, TEZ_Y + 0.63, z + TEZGAH_H - 0.07, z + TEZGAH_H), 2, pah=0.015, seg=2)
X = BX0 + 0.1
while X < BX1:
    P(bm, pk(X - 0.05, X + 0.05, TEZ_Y + 0.02, TEZ_Y + 0.07, z + 0.10, z + TEZGAH_H - 0.07), 1, pah=0.01); X += 1.6
nesne('Bar_Tezgah', bm, [M['ahsap'], M['koyu'], M['masa']], K_BAR)
bm = bmesh.new()
P(bm, b_arasi((*w(BX0 + 0.1, TEZ_Y - 0.14), z + 0.2), (*w(BX1 - 0.1, TEZ_Y - 0.14), z + 0.2), 0.022, n=12), 0, yumusak=True)
X = BX0 + 0.6
while X < BX1:
    P(bm, b_arasi((*w(X, TEZ_Y - 0.14), z + 0.2), (*w(X, TEZ_Y + 0.06), z + 0.2), 0.012, n=8), 0, yumusak=True); X += 1.6
nesne('Bar_Ayak_Cubugu', bm, [M['pirinc']], K_BAR)
# arkası: alçak dolap, üstünde iki açık raf (dikmeli), raflarda şişeler ve kupalar
DOLAPLAR = ((BX0 - 0.5, MUTFAK[0] - 0.15), (MUTFAK[1] + 0.15, BX1 + 1.0))
bm = bmesh.new()
for a, b in DOLAPLAR:
    P(bm, pk(a, b, H - RAF_D, H, z, z + 0.95), 0)
    P(bm, pk(a - 0.02, b + 0.02, H - RAF_D - 0.03, H, z + 0.95, z + 1.0), 1, pah=0.01)
    for rz in (1.55, 2.15):
        P(bm, pk(a, b, H - 0.3, H, z + rz, z + rz + 0.04), 1, pah=0.008)
    n_d = max(1, round((b - a) / 1.6))
    for i in range(n_d + 1):
        X = a + 0.04 + (b - a - 0.08) * i / n_d
        P(bm, pk(X - 0.04, X + 0.04, H - 0.3, H, z + 1.0, z + 2.3), 1, pah=0.008)
nesne('Bar_Arka_Raf', bm, [M['ahsap'], M['koyu']], K_BAR)
CAMLAR = [M['cam_y'], M['cam_k'], M['cam_s']]
for ri, rz in enumerate((1.0, 1.59, 2.19)):
    bm = bmesh.new()
    for a, b in DOLAPLAR:
        X = a + 0.15
        while X < b - 0.15:
            if ri == 0 and a < BX0 and X < BX0 + 1.2: X += 0.2; continue           # dolabın batı ucunda fıçılar duruyor
            if sus.random() < 0.72:
                x, y = w(X, H - 0.16 + sus.uniform(-0.04, 0.04))
                if sus.random() < 0.25: hp.kupa_kur(bm, x, y, z + rz, sus.uniform(0, 360))
                else: hp.sise_kur(bm, x, y, z + rz, mi=2 + sus.randrange(3))
            X += sus.uniform(0.11, 0.2)
    nesne(f'Bar_Raf_{ri + 1}', bm, [M['kalay'], M['bira']] + CAMLAR, K_BAR)
for i in range(3):                                                                            # dolabın üstünde yatık fıçılar (musluklu)
    hp.fici(f'Bar_Fici_{i + 1}', K_BAR, *w(BX0 - 0.2 + i * 0.5, H - 0.25), 0.22, 0.42, 90, z + 1.0, yatik=True)
bm = bmesh.new()
for _ in range(8):
    hp.kupa_kur(bm, *w(sus.uniform(BX0 + 0.5, BX1 - 0.5), TEZ_Y + 0.3 + sus.uniform(-0.15, 0.15)), z + TEZGAH_H, sus.uniform(0, 360))
nesne('Bar_Tezgah_Kupalar', bm, [M['kalay'], M['bira']], K_BAR)
for X in (13.4, 18.9):
    hp.yeni_mum(*w(X + sus.uniform(-0.2, 0.2), TEZ_Y + 0.3), z + TEZGAH_H, K_BAR)
hp.saksi('Bitki_Tezgah', K_BAR, *w(BX1 - 0.4, TEZ_Y + 0.3), 0.55, 0.1, z + TEZGAH_H, kart=8)
bm = bmesh.new()
for X, Y, a in ((15.35, 15.1, 10), (14.95, 15.25, -25), (15.15, 15.5, 40)):
    hp.cuval_kur(bm, *w(X, Y), z, a)
nesne('Bar_Cuvallar', bm, [M['cuval']], K_BAR)
kok_t = bos('Bar_Tabureleri', K_TABURE, *w((BX0 + BX1) / 2, TEZ_Y - 0.45), z, boy=0.4)
for i in range(11):
    bagla(kopya(f'Bar_Tabure_{i + 1:02d}', TABURE, K_TABURE, *w(BX0 + 0.6 + i * 0.85 + sus.uniform(-0.06, 0.06), TEZ_Y - 0.45 + sus.uniform(-0.05, 0.05)), z, sus.uniform(0, 90)), kok_t)
# Mutfak kapısı: kasa, içeri açık kanat, arkasında loş mutfak girişi
M0, M1 = MUTFAK
bm = bmesh.new()
for X0_, X1_ in ((M0 - 0.12, M0), (M1, M1 + 0.12)): P(bm, pk(X0_, X1_, H - 0.04, H + DK + 0.02, z, z + 2.3), 0, pah=0.01)
P(bm, pk(M0 - 0.12, M1 + 0.12, H - 0.04, H + DK + 0.02, z + 2.2, z + 2.36), 0, pah=0.01)
nesne('Kapi_Mutfak_Kasa', bm, [M['koyu']], K_KAPI, ic='kuzey')
bm = kanat_bm(M1 - M0 - 0.06, 2.15)
o = nesne('Kapi_Mutfak_Kanat', bm, [M['koyu'], M['demir']], K_KAPI, konum=(*w(M0 + 0.03, H + 0.05), z), ic='kuzey')
o.rotation_euler.z = math.radians(-90 + 25)
bm = bmesh.new()
P(bm, pk(M0 - 0.6, M1 + 0.6, H + DK, H + DK + 0.62, z - 0.05, z)); P(bm, pk(M0 - 0.6, M1 + 0.6, H + DK + 0.6, H + DK + 0.62, z, z + 2.3))
for X0_ in (M0 - 0.6, M1 + 0.58): P(bm, pk(X0_, X0_ + 0.02, H + DK, H + DK + 0.62, z, z + 2.3))
nesne('Mutfak_Girisi', bm, [M['karanlik']], K_KAPI)
# Galerinin kirişinden: tabela, iki sancak, üç sarkıt fener; barmenin üstünde kuru ot demetleri
KZ = GALERI_Z - 0.45
kur, uv, mats = hp.tabela(1.5, KZ - 0.95, KZ)
hp.duvar_parcasi('Tabela_Bar', K_DEKOR, *w(16.5, GALERI_Y0 + 0.1), 180, kur, mats, uv)
for i, X in enumerate((12.9, 20.0)):
    kur, mats, SH = hp.sancak(KZ - 0.02, 0.7)
    hp.duvar_parcasi(f'Sancak_Bar_{i + 1}', K_DEKOR, *w(X, GALERI_Y0 + 0.06), 180, kur, mats, koru={2})
for i, X in enumerate((14.2, 18.6, 21.0)):
    hp.sarkit(f'Sarkit_Bar_{i + 1}', *w(X, GALERI_Y0 + 0.4), KZ - 0.95, K_DEKOR, KZ)
for i, X in enumerate((12.5, 14.0, 17.8, 19.5, 21.0)):
    hp.kuru_ot(f'Kuru_Ot_{i + 1}', K_YESIL, *w(X, 15.0), GALERI_Z - 0.25)
etiket('Bar', 19.8, 14.9); etiket('Mutfak kapısı', 16.6, 15.45); etiket('11 tabure', 18.0, 12.9)

# Görev panosu (barın batısında), önünde bank, yanında fıçı yığını
kur, uv, mats, PH = hp.pano(1.7, z + 1.05)
hp.duvar_parcasi('Gorev_Panosu', K_DEKOR, *w((PANO_X[0] + PANO_X[1]) / 2, H), 180, kur, mats, uv, ic='kuzey')
hp.bank_kur('Gorev_Panosu_Bank', 1.6, K_DEKOR, (*w((PANO_X[0] + PANO_X[1]) / 2, H - 0.85), z))
for i, (X, zz) in enumerate(((10.0, 0), (10.55, 0), (10.27, 0.45))):
    hp.fici(f'Fici_Yigini_{i + 1}', K_DEKOR, *w(X, H - 0.35), 0.24, 0.5, 90, z + zz, yatik=True)
etiket('Görev panosu', (PANO_X[0] + PANO_X[1]) / 2, 15.3)

# ═════════ 05 BATI KANADI: şömine ve önü (temiz), uzun masa, okuma köşesi ═════════
s0, s1 = SOMINE_X; sm = (s0 + s1) / 2
SY0 = H - 0.9                                                                                 # şöminenin ön yüzü
bm = bmesh.new()
P(bm, pk(s0, s0 + 0.55, SY0, H, z, z + 1.9), 0, pah=0.02); P(bm, pk(s1 - 0.55, s1, SY0, H, z, z + 1.9), 0, pah=0.02)
P(bm, pk(s0, s1, H - 0.3, H, z, z + 1.9), 0, pah=0.02)
P(bm, pk(s0 + 0.2, s1 - 0.2, SY0 + 0.15, H, z + 1.9, z + 2.6), 0, pah=0.02)                 # davlumbaz
P(bm, pk(s0 + 0.5, s1 - 0.5, H - 0.7, H, z + 2.6, DH + 0.6), 0, pah=0.02)                    # baca
P(bm, pk(s0 - 0.3, s1 + 0.3, SY0 - 0.6, SY0, z, z + 0.08), 0, pah=0.015)                     # taş eşik
nesne('Somine_Govde', bm, [M['somine']], K_KANAT)
bm = bmesh.new(); P(bm, pk(s0 - 0.12, s1 + 0.12, SY0 - 0.12, SY0 + 0.1, z + 1.88, z + 2.04), 0, pah=0.02, seg=2)
nesne('Somine_Raf', bm, [M['koyu']], K_KANAT)
bm = bmesh.new(); P(bm, pk(s0 + 0.55, s1 - 0.55, SY0, H - 0.3, z, z + 0.03)); nesne('Somine_Ocak_Tabani', bm, [M['kul']], K_KANAT)
bm = bmesh.new()
for p0, p1, r in (((s0 + 0.7, H - 0.55, z + 0.08), (s1 - 0.8, H - 0.45, z + 0.08), 0.075), ((s0 + 0.9, H - 0.75, z + 0.08), (s1 - 0.6, H - 0.5, z + 0.09), 0.07),
                  ((sm - 0.2, H - 0.45, z + 0.2), (sm + 0.15, H - 0.75, z + 0.17), 0.06)):
    P(bm, b_arasi((*w(p0[0], p0[1]), p0[2]), (*w(p1[0], p1[1]), p1[2]), r, n=10), 0, yumusak=True)
nesne('Somine_Kutukler', bm, [M['koyu']], K_KANAT)
bm = bmesh.new()
for _ in range(26):
    b = b_kutu(-0.04, 0.04, -0.03, 0.03, 0.03, 0.03 + sus.uniform(0.015, 0.04)); dondur(b, sus.uniform(0, 180))
    tasi(b, *w(sm + sus.uniform(-0.75, 0.75), H - sus.uniform(0.4, 0.8)), z); P(bm, b, 0)
nesne('korlar', bm, [M['kor']], K_KANAT)
for i in range(10):
    X = sm - 0.6 + 1.2 * (i + sus.uniform(-0.3, 0.3)) / 9; Y = H - sus.uniform(0.45, 0.7)
    hh = sus.uniform(0.22, 0.6) * (1.15 - abs(X - sm) / 1.2); r = hh * sus.uniform(0.18, 0.26)
    bm = bmesh.new()
    P(bm, b_torna(0, 0, [(0, r * 0.5), (hh * 0.15, r), (hh * 0.4, r * 0.85), (hh * 0.65, r * 0.5), (hh * 0.85, r * 0.2), (hh, 0.002)], n=8), 0, yumusak=True)
    yon, buk = sus.uniform(0, 2 * math.pi), sus.uniform(0.04, 0.12)
    for v in bm.verts:
        t = v.co.z / hh; v.co.y *= 0.6
        v.co.x += buk * t * t * math.cos(yon); v.co.y += buk * t * t * math.sin(yon) * 0.5
    pnesne(f'alev_somine_{i + 1}', bm, [M['alev_s']], K_KANAT, X, Y, z + 0.08)
hp.isik_ekle('isik_somine', K_ISIK, *w(sm, H - 0.6), z + 0.45, 'somine')
kur, mats = hp.trofe(z + 2.95)
hp.duvar_parcasi('Somine_Trofe', K_DEKOR, *w(sm, H - 0.7), 180, kur, mats, ic='kuzey')
for X in (s0 + 0.25, s0 + 0.55, s1 - 0.3):
    hp.yeni_mum(*w(X, SY0 + 0.0), z + 2.04, K_DEKOR)
bm = bmesh.new(); hp.odun(bm); pnesne('Odun_Yigini', bm, [M['ahsap']], K_DEKOR, s1 + 0.85, H - 0.02, z, aci=180)   # şöminenin doğu yanında
hp.aplik('Aplik_Somine_1', K_DEKOR, *w(s0 - 0.35, H), 180, z + 1.9, ic='kuzey')
hp.aplik('Aplik_Somine_2', K_DEKOR, *w(s1 + 1.2, H), 180, z + 1.9, ic='kuzey')
etiket('Şömine', sm, H - 1.2)
# önü: post ve şömineye dönük kavisli deri kanepe, alçak sehpa
PE = 2.3; PB = PE / hp.oran('post.png')
bm = bmesh.new(); P(bm, yer_levha(PE, PB, z))
nesne('Somine_Post', bm, [M['post']], K_KANAT, konum=(*w(sm, H - 2.6), 0), aci=4, uv_ozel=hali_uv(PE, PB))
kx_, ky_ = w(sm, H - 2.3)
bm = bmesh.new()
for i in range(7):
    t0, t1 = 200 + 140 * i / 7, 200 + 140 * (i + 1) / 7
    P(bm, b_dilim(kx_, ky_, 1.65, 2.3, t0 + 0.6, t1 - 0.6, z + 0.08, z + 0.45, n=4), 0, pah=0.04, seg=2)   # oturak minderi
    P(bm, b_dilim(kx_, ky_, 2.12, 2.35, t0 + 0.6, t1 - 0.6, z + 0.45, z + 0.95, n=4), 0, pah=0.05, seg=2)  # arkalık
P(bm, b_dilim(kx_, ky_, 1.6, 2.38, 200, 340, z, z + 0.08, n=20), 1, pah=0.01)
nesne('Somine_Kanepe', bm, [M['deri'], M['koyu']], K_KANAT)
bm = bmesh.new()
P(bm, b_silindir(0, 0, 0.36, 0.40, 0.45, n=32), 0, pah=0.01, seg=2); P(bm, b_silindir(0, 0, 0.05, 0.03, 0.40, n=8), 1); P(bm, b_silindir(0, 0, 0.18, 0.0, 0.03, n=16), 1, pah=0.008)
pnesne('Somine_Sehpa', bm, [M['masa'], M['ahsap']], K_KANAT, sm, H - 3.05, z)
bm = bmesh.new(); hp.kupa_kur(bm, *w(sm + 0.12, H - 3.0), z + 0.45, 200); nesne('Somine_Sehpa_Kupa', bm, [M['kalay'], M['bira']], K_KANAT)
hp.yeni_mum(*w(sm - 0.1, H - 3.1), z + 0.45, K_KANAT)
# uzun masa ve banklar (şöminenin gerisinde), üstünde kupalar, tabaklar, ekmek, mum
hp.uzun_masa_govde('Masa_Uzun', 3.6, 0.9, K_KANAT, (*w(3.8, 9.6), z))
for i, Y in enumerate((8.78, 10.42)): hp.bank_kur(f'Kanat_Bank_{i + 1}', 3.4, K_KANAT, (*w(3.8, Y), z))
bm = bmesh.new()
for i in range(5): hp.kupa_kur(bm, *w(2.4 + i * 0.75 + sus.uniform(-0.15, 0.15), 9.6 + sus.uniform(-0.25, 0.25)), z + 0.8, sus.uniform(0, 360))
for i in range(3): hp.tabak_kur(bm, *w(2.8 + i * 1.1, 9.6 + sus.uniform(-0.15, 0.15)), z + 0.8, mi=0)
P(bm, b_torna(*w(4.3, 9.55), [(z + 0.82, 0.12), (z + 0.86, 0.13), (z + 0.9, 0.09)], n=14), 2, yumusak=True)   # ekmek
nesne('Masa_Uzun_Ustu', bm, [M['kalay'], M['bira'], M['cuval']], K_KANAT)
for X in (3.2, 4.6): hp.yeni_mum(*w(X, 9.62), z + 0.8, K_KANAT)
etiket('Uzun masa', 3.8, 9.6)
# okuma köşesi: halı, karşılıklı iki koltuk, sehpa ve kitaplar, saksı
HB2 = 2.0; HE2 = HB2 * hp.oran('hali.png')
bm = bmesh.new(); P(bm, yer_levha(HE2, HB2, z)); nesne('Okuma_Hali', bm, [M['hali']], K_KANAT, konum=(*w(3.8, 5.7), 0), uv_ozel=hali_uv(HE2, HB2))
kopya('Okuma_Koltuk_1', KOLTUK, K_KANAT, *w(2.75, 5.7), z, 90); kopya('Okuma_Koltuk_2', KOLTUK, K_KANAT, *w(4.85, 5.7), z, 270)
bm = bmesh.new()
P(bm, b_silindir(0, 0, 0.3, 0.45, 0.5, n=28), 0, pah=0.01); P(bm, b_silindir(0, 0, 0.05, 0.03, 0.45, n=8), 1); P(bm, b_silindir(0, 0, 0.16, 0.0, 0.03, n=16), 1)
for j in range(3):
    b = b_kutu(-0.1, 0.1, -0.135, 0.135, 0.5 + j * 0.05, 0.5 + (j + 1) * 0.05 - 0.005); dondur(b, sus.uniform(-25, 25)); P(bm, b, 2, pah=0.006)
pnesne('Okuma_Sehpa', bm, [M['masa'], M['ahsap'], M['kitap_d']], K_KANAT, 3.8, 5.7, z)
hp.yeni_mum(*w(3.95, 5.55), z + 0.5, K_KANAT)
hp.saksi('Bitki_Okuma', K_YESIL, *w(0.6, 4.6), 1.4, 0.28, z, kart=11)
etiket('Okuma köşesi', 3.8, 5.0)
# kanadın üstünde, kuzey duvarında kalkanlar ve kılıç-kalkan
for i, (X, zz, r, d) in enumerate(((1.2, 4.3, 0.42, 'kalkan1'), (6.6, 4.3, 0.42, 'kalkan2'))):
    kur, uv, mats = hp.kalkan_yuvarlak(zz, r, d)
    hp.duvar_parcasi(f'Kalkan_Kanat_{i + 1}', K_DEKOR, *w(X, H), 180, kur, mats, uv, ic='kuzey')
kur, uv, mats = hp.kalkan_kilic(4.7, 0.36, 'kalkan1')
hp.duvar_parcasi('Kalkan_Kilic_Baca', K_DEKOR, *w(sm, H - 0.7), 180, kur, mats, uv, ic='kuzey')
for X, Y in ((0.6, 15.4), (6.6, 15.4)):
    hp.saksi(f'Bitki_Kanat_{int(X)}', K_YESIL, *w(X, Y), 1.5, 0.3, z, kart=12)

# ═════════ 06 MERDİVEN (doğu duvarı boyunca) VE GALERİ ═════════
n_bas = round((GALERI_Z - UST_Z) / 0.2); uzun = GALERI_Y0 - MERDIVEN_Y0; adim = uzun / n_bas; yuk = (GALERI_Z - UST_Z) / n_bas
bm = bmesh.new()
for i in range(n_bas):
    y0 = MERDIVEN_Y0 + i * adim
    P(bm, pk(MERDIVEN_X0 + 0.08, W, y0 - 0.03, y0 + adim, z + (i + 1) * yuk - 0.05, z + (i + 1) * yuk), 0, pah=0.008)   # basamak tahtası
    P(bm, pk(MERDIVEN_X0 + 0.1, W, y0 - 0.01, y0 + 0.02, z + i * yuk, z + (i + 1) * yuk - 0.05), 1)                       # rıht
nesne('Merdiven_Basamaklar', bm, [M['zemin'], M['ahsap']], K_UST)
bm = bmesh.new()
for Y0_, z0_, Y1_, z1_ in ((MERDIVEN_Y0, z, GALERI_Y0, GALERI_Z),):
    a = Vector((*w(MERDIVEN_X0 + 0.04, Y0_), z0_ - 0.1)); b = Vector((*w(MERDIVEN_X0 + 0.04, Y1_), z1_ - 0.1))
    P(bm, b_arasi(a, b, 0.11, n=4), 0)                                                         # yan kiriş
    a2, b2 = a + Vector((0, 0, 1.0)), b + Vector((0, 0, 1.0))
    P(bm, b_arasi(a2, b2, 0.035, n=10), 0, yumusak=True)                                        # küpeşte
    for i in range(1, n_bas):
        t = i / n_bas; p = a.lerp(b, t)
        P(bm, b_torna(p.x, p.y, [(p.z + 0.08, 0.02), (p.z + 0.3, 0.028), (p.z + 0.55, 0.018), (p.z + 0.85, 0.026), (p.z + 1.0, 0.02)], n=8), 1, yumusak=True)
for Y_, zz in ((MERDIVEN_Y0, z), (GALERI_Y0, GALERI_Z)):
    P(bm, pk(MERDIVEN_X0 - 0.06, MERDIVEN_X0 + 0.14, Y_ - 0.1, Y_ + 0.1, zz - 0.25 if Y_ > 10 else zz, zz + 1.15), 0, pah=0.015)   # baba direkleri
nesne('Merdiven_Korkuluk', bm, [M['koyu'], M['ahsap']], K_UST)
for i, (Y, s) in enumerate(((12.3, 0.5), (12.95, 0.45))):
    hp.sandik(f'Merdiven_Alti_Sandik_{i + 1}', K_DEKOR, *w(23.4, Y + s / 2), z, s, s, s * 0.9, sus.uniform(-10, 10))
hp.fici('Merdiven_Alti_Fici', K_DEKOR, *w(23.45, 11.55), 0.28, 0.55, 0, z, yatik=True)
for i, (X, Y) in enumerate(((20.3, 8.75), (20.85, 8.6))): hp.fici(f'Fici_Merdiven_{i + 1}', K_DEKOR, *w(X, Y), 0.3, 0.85, sus.uniform(0, 90), z)
hp.saksi('Bitki_Merdiven', K_YESIL, *w(22.2, 8.5), 1.4, 0.28, z, kart=11)
etiket('Merdiven', 23.35, 10.4)

gz0 = GALERI_Z - 0.25
bm = bmesh.new()
P(bm, pk(GALERI_X0, W, GALERI_Y0, H, gz0, GALERI_Z), 0)                                       # döşeme
P(bm, pk(GALERI_X0, W, GALERI_Y0, GALERI_Y0 + 0.26, gz0 - 0.22, gz0), 1, pah=0.02)            # ön kiriş
X = GALERI_X0 + 0.4
while X < W:                                                                                  # altta döşeme kirişleri
    P(bm, pk(X - 0.07, X + 0.07, GALERI_Y0 + 0.26, H, gz0 - 0.16, gz0), 1, pah=0.01); X += 0.9
nesne('Galeri_Doseme', bm, [M['zemin'], M['koyu']], K_GALERI)
bm = bmesh.new()
for (X0_, Y0_), (X1_, Y1_) in (((GALERI_X0 + 0.04, GALERI_Y0 + 0.04), (MERDIVEN_X0, GALERI_Y0 + 0.04)), ((GALERI_X0 + 0.04, GALERI_Y0 + 0.04), (GALERI_X0 + 0.04, H))):
    a, b = Vector((*w(X0_, Y0_), GALERI_Z + 0.95)), Vector((*w(X1_, Y1_), GALERI_Z + 0.95))
    P(bm, pk(min(X0_, X1_) - 0.05, max(X0_, X1_) + 0.05, min(Y0_, Y1_) - 0.05, max(Y0_, Y1_) + 0.05, GALERI_Z + 0.9, GALERI_Z + 0.98), 0, pah=0.012)   # küpeşte
    n_ = int((a - b).length / 0.2)
    for i in range(1, n_):
        p = a.lerp(b, i / n_)
        P(bm, b_torna(p.x, p.y, [(GALERI_Z, 0.022), (GALERI_Z + 0.2, 0.03), (GALERI_Z + 0.45, 0.02), (GALERI_Z + 0.75, 0.028), (GALERI_Z + 0.9, 0.022)], n=8), 1, yumusak=True)
for X in (GALERI_X0 + 0.04, 12.4, 16.4, 20.4, MERDIVEN_X0 - 0.06):
    P(bm, pk(X - 0.07, X + 0.07, GALERI_Y0 - 0.03, GALERI_Y0 + 0.11, GALERI_Z, GALERI_Z + 1.1), 0, pah=0.01)
nesne('Galeri_Korkuluk', bm, [M['koyu'], M['ahsap']], K_GALERI)
bm = bmesh.new()
for X in (GALERI_X0 + 0.15, 12.4, 16.4, 20.4):                                                # taşıyan direkler ve köşe destekleri
    P(bm, pk(X - 0.13, X + 0.13, GALERI_Y0, GALERI_Y0 + 0.26, z, gz0 - 0.22), 0, pah=0.02)
    P(bm, pk(X - 0.17, X + 0.17, GALERI_Y0 - 0.04, GALERI_Y0 + 0.3, z, z + 0.12), 1, pah=0.015)
    for s in (-1, 1):
        if GALERI_X0 + 0.5 < X + s * 0.6 < W - 0.3:
            P(bm, b_arasi((*w(X + s * 0.1, GALERI_Y0 + 0.13), gz0 - 0.95), (*w(X + s * 0.7, GALERI_Y0 + 0.13), gz0 - 0.24), 0.055, n=6), 0)
nesne('Galeri_Direkleri', bm, [M['koyu'], M['tas']], K_UST)
for i, X in enumerate((10.6, 13.9, 18.7)):
    hp.cicek_kutusu(f'Galeri_Cicek_{i + 1}', K_YESIL, *w(X + 0.45, GALERI_Y0 - 0.16), GALERI_Z + 0.55, 0.9, 180)
# odaların kapıları: kasa, tahta kanat (iki tanesi aralık; arkasında loş oda), aralarda aplik, üstte kalkan
for i, X in enumerate(ODA_KAPILARI):
    bm = bmesh.new()
    for X0_, X1_ in ((X - 0.1, X), (X + 1.0, X + 1.1)): P(bm, pk(X0_, X1_, H - 0.04, H + DK + 0.02, GALERI_Z, GALERI_Z + 2.2), 0, pah=0.01)
    P(bm, pk(X - 0.1, X + 1.1, H - 0.04, H + DK + 0.02, GALERI_Z + 2.1, GALERI_Z + 2.26), 0, pah=0.01)
    nesne(f'Kapi_Oda_{i + 1}_Kasa', bm, [M['koyu']], K_GALERI, ic='kuzey')
    ac = ARALIK.get(i, 0)
    bm = kanat_bm(0.98, 2.08)
    o = nesne(f'Kapi_Oda_{i + 1}', bm, [M['koyu'], M['demir']], K_GALERI, konum=(*w(X + 0.01, H + 0.04), GALERI_Z), ic='kuzey')
    o.rotation_euler.z = math.radians(-90 + ac)                                                  # yerel +y boyunca kanat → doğuya
    if ac:
        bm = bmesh.new(); P(bm, pk(X - 0.3, X + 1.3, H + DK, H + DK + 0.8, GALERI_Z - 0.02, GALERI_Z + 2.15))
        nesne(f'Oda_Ic_{i + 1}', bm, [M['karanlik']], K_GALERI)
        hp.isik_ekle(f'isik_oda_{i + 1}', K_ISIK, *w(X + 0.5, H + DK + 0.4), GALERI_Z + 1.2, 'oda')
    if i < len(ODA_KAPILARI) - 1:
        ax = (X + 1.1 + ODA_KAPILARI[i + 1] - 0.1) / 2
        hp.aplik(f'Aplik_Galeri_{i + 1}', K_DEKOR, *w(ax, H), 180, GALERI_Z + 1.6, ic='kuzey')
        kur, uv, mats = hp.kalkan_yuvarlak(GALERI_Z + 2.6, 0.32, 'kalkan1' if i % 2 == 0 else 'kalkan2')
        hp.duvar_parcasi(f'Kalkan_Galeri_{i + 1}', K_DEKOR, *w(ax, H), 180, kur, mats, uv, ic='kuzey')
etiket(f'Galeri: {len(ODA_KAPILARI)} oda kapısı (tepeden gizli)', 12.6, 15.95)

# ═════════ SALONDA: saksılar, silah askısı, sarmaşıklar ═════════
for i, (X, Y) in enumerate(((7.75, 0.45), (21.4, 0.45), (23.5, 7.75))):
    hp.saksi(f'Bitki_Salon_{i + 1}', K_YESIL, *w(X, Y), 1.5, 0.3, seviye(X, Y), kart=12)
hp.duvar_parcasi('Silah_Askisi', K_DEKOR, *w(W, 0.6), 270, hp.aski, [M['koyu'], M['celik'], M['kalkan2'], M['ahsap']], hp.ASKI_UV(), ic='dogu')
for ad, X, Y, z0_, yon in (('Sarmasik_Direk_Ozan_1', W - 0.05, cz - cr + 0.2, 0.3, 270), ('Sarmasik_Direk_Ozan_2', W - 0.05, cz + cr - 0.2, 0.3, 270),
                           ('Sarmasik_Galeri_1', 12.4, GALERI_Y0 + 0.13, z + 1.2, 180), ('Sarmasik_Galeri_2', 20.4, GALERI_Y0 + 0.13, z + 1.2, 180)):
    hp.sarmasik(ad, K_YESIL, *w(X, Y), z0_, GALERI_Z - 0.5 if 'Galeri' in ad else ch - 0.6, yon)

# ═════════ 99 ÖNİZLEME: ışıklar, kameralar, çekimler ═════════
def isik(ad, konum, renk, guc, yaricap, golge=True):
    d = bpy.data.lights.new(ad, 'POINT'); d.color = renk; d.energy = guc; d.shadow_soft_size = yaricap; d.use_shadow = golge
    o = bpy.data.objects.new(ad, d); o.location = konum; K_ONI.objects.link(o)
GUC = {'somine': (900, 0.4, True), 'avize': (240, 0.5, True), 'aplik': (45, 0.04, False), 'sarkit': (55, 0.04, False),
       'mum': (12, 0.02, False), 'oda': (25, 0.1, False)}
for ad, x, y, zz, tur in hp.ISIKLAR:
    g, r, golge = GUC.get(tur, (12, 0.02, False))
    isik('Onizleme_' + ad, (x, y, zz), (1.0, 0.5, 0.18) if tur == 'somine' else (1.0, 0.6, 0.3), g, r, golge)
sx_, sy_ = w(sm, H - 2.0); isik('Onizleme_Somine_Oda', (sx_, sy_, z + 1.2), (1.0, 0.5, 0.2), 500, 0.6)
dolgu = bpy.data.lights.new('Onizleme_Dolgu', 'SUN'); dolgu.energy = 1.2; dolgu.color = (1.0, 0.86, 0.7)
od = bpy.data.objects.new('Onizleme_Dolgu', dolgu); od.rotation_euler = (math.radians(30), 0, math.radians(-40)); K_ONI.objects.link(od)
dunya = bpy.data.worlds.new('Dunya'); sahne.world = dunya
try: dunya.use_nodes = True
except Exception: pass
dunya.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.06, 0.045, 0.03, 1)
dunya.node_tree.nodes.get('Background').inputs['Strength'].default_value = 1.6
sahne.render.engine = 'BLENDER_EEVEE'
for ad, deger in (('use_raytracing', True), ('taa_render_samples', 32), ('use_shadows', True)):
    try: setattr(sahne.eevee, ad, deger)
    except Exception: pass
try: sahne.view_settings.view_transform = 'Filmic'; sahne.view_settings.look = 'Medium High Contrast'
except Exception: pass
sahne.render.image_settings.file_format = 'PNG'

def kamera(ad, konum, bakis, orto=None, lens=24):
    d = bpy.data.cameras.new(ad)
    if orto: d.type = 'ORTHO'; d.ortho_scale = orto
    else: d.lens = lens; d.clip_start = 0.05
    d.clip_end = 150
    o = bpy.data.objects.new(ad, d); o.location = konum; K_ONI.objects.link(o)
    o.rotation_euler = (Vector(bakis) - Vector(konum)).to_track_quat('-Z', 'Y').to_euler()
    return o
def cek(kam, dosya, gx, gy):
    sahne.camera = kam; sahne.render.resolution_x, sahne.render.resolution_y = gx, gy
    sahne.render.filepath = os.path.join(CIKTI, dosya); bpy.ops.render.render(write_still=True)
def hepsini_goster():
    for o in bpy.data.objects:
        o.hide_render = False
        if o.get('duvar') and o.name.startswith(('Duvar_', 'Direk_')): o.scale.z = 1
    for k in bpy.data.collections: k.hide_render = False
    K_SAB.hide_render = True

# 1) Tam tepeden: galeri, avize, tavanlar, saçak gizli
SOL, SAG = SX0 - 3.2, W + cr + 0.6
ALT, UST = -0.6, H + 0.6
ox, oy = w((SOL + SAG) / 2, (ALT + UST) / 2)
k_ust = kamera('Kamera_Ustten', (ox, oy, 40), (ox, oy, 0), orto=SAG - SOL); k_ust.rotation_euler = (0, 0, 0)
hepsini_goster()
for k in (K_GALERI, K_AVIZE, K_TAVAN): k.hide_render = True
bpy.data.objects['Sundurma_Sacak'].hide_render = True
cek(k_ust, 'detay-ustten.png', 1920, round(1920 * (UST - ALT) / (SAG - SOL)))

# 2) Sitenin açısı: kameraya bakan duvarlar 0,95 m'ye alçalır (Duvar_ / Direk_), onlara asılı parçalar gizlenir
hepsini_goster()
th, ph = math.radians(YON), math.radians(EGIM)
bak = (math.sin(th) * math.cos(ph), math.cos(th) * math.cos(ph), -math.sin(ph))
IC = {'kuzey': (0, -1), 'guney': (0, 1), 'bati': (1, 0), 'dogu': (-1, 0)}
ONDE = {k for k, (a, b) in IC.items() if a * math.sin(th) + b * math.cos(th) > 0.15}
for o in bpy.data.objects:
    d = o.get('duvar')
    if d not in ONDE: continue
    if o.name.startswith(('Duvar_', 'Direk_')):
        ust = max((o.matrix_world @ v.co).z for v in o.data.vertices)
        o.scale.z = KESIK / max(ust, 0.1)
    else: o.hide_render = True
for o in bpy.data.objects:
    if o.parent and o.parent.hide_render: o.hide_render = True
for k in (K_TAVAN,): k.hide_render = True
for ad in ('Sundurma_Sacak',): bpy.data.objects[ad].hide_render = True
mx, my = w((SOL + SAG) / 2 + 0.3, H / 2 + 0.8)
k_site = kamera('Kamera_Site', (mx - bak[0] * 60, my - bak[1] * 60, 1.5 - bak[2] * 60), (mx, my, 1.5), orto=36)
cek(k_site, 'detay-site.png', 1920, 1440)

# 3) Göz hizası: kürsünün güneybatı koltuğundan bara ve galeriye; 4) giriş kapısından salona
hepsini_goster()
ra = math.radians(200)
cek(kamera('Kamera_Goz', (1.45 * math.sin(ra), 1.45 * math.cos(ra), KURSU_H + 1.2), (*w(15.5, 13.5), 2.4), lens=18), 'detay-goz.png', 1920, 1080)
cek(kamera('Kamera_Giris', (*w(GIRIS_X0 + 0.6, (KAPI_Y[0] + KAPI_Y[1]) / 2), 1.6), (*w(15.0, 5.0), 1.2), lens=18), 'detay-giris.png', 1920, 1080)
hepsini_goster()

import json
with open(os.path.join(CIKTI, 'detay-etiketler.json'), 'w', encoding='utf-8') as f:
    json.dump({'etiketler': [{'metin': m, 'x': (X - SOL) / (SAG - SOL), 'y': (UST - Y) / (UST - ALT)} for m, X, Y in ETIKET],
               'oda_m': [W, H]}, f, ensure_ascii=False, indent=1)
for ekran in bpy.data.screens:
    for alan in ekran.areas:
        if alan.type == 'VIEW_3D':
            for sp in alan.spaces:
                if sp.type == 'VIEW_3D': sp.shading.type = 'MATERIAL'
hp.temizle()
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CIKTI, 'han-detay.blend'), compress=True, relative_remap=True)
yuz = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
print(f'Nesne: {len(bpy.data.objects)}, yüz (kopyalar dahil): {yuz}, mum: {hp.MUM_NO[0]}, ışık işareti: {len(hp.ISIKLAR)}')
print('TAMAM')
