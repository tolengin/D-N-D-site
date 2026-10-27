# -*- coding: utf-8 -*-
"""
YENİ HAN — BLOCKOUT (kaba taslak) Blender betiği  (2026-10-21, 2. sürüm)
=========================================================================
Blockout: dokusuz, düz renkli kutu ve silindirlerle yerleşimi, seviyeleri ve oranları kurmak.
Kullanıcı onaylayınca ayrıntılı modele geçilir. Betik her çalıştığında her şeyi sıfırdan kurar.
Referans görseller: gorseller/referans/yeni-han/ ve ornek sanat.jpg (aynısı değil, benzeri).
1. sürüm (dikdörtgen salon, çukur, köşede kürsü) ve önizlemeleri: 3d/han/v1/.

Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --factory-startup --python araclar\\han_blockout_blender.py
  python araclar\\han_etiketle.py          (tepeden önizlemenin etiketli kopyası)

Çıktılar (3d/han/):
  han-blockout.blend         kaynak dosya
  onizleme-ustten.png        tam tepeden (kuş bakışı; galeri, avize ve tavanlar gizli)
  onizleme-site.png          sitenin eğik açısından (iç yüzü kameraya bakan duvarlar alçak)
  onizleme-goz.png           oyun masasından bara ve galeriye, göz hizası
  onizleme-giris.png         giriş kapısından salona, göz hizası
  etiketler.json             etiketlerin tepeden önizlemedeki yeri (han_etiketle.py okur)

Yerleşim (kuzey yukarıda; örnek sanattaki gibi iki seviye):
  • Yukarıdaki seviye (+0,60): batı kanadı (şömine ve önünde temiz oturma yeri, uzun masa, okuma köşesi),
    kuzey bandı (düz bar, görev panosu) ve kuzeydoğu uzantısı (doğu duvarı boyunca galeriye çıkan merdiven).
  • Aşağıdaki salon (0): taş zemin; ortada alçak kürsüde oyun masası ve şamdanlı avize, çevresinde dört yan masa.
  • İki seviye arasında uzun, köşesi kavisli üç basamak.
  • Güneybatıda girintide giriş: dışta saçaklı sundurma, kemerli çift kanatlı kapı, içeride halılı, sandıklı giriş alanı.
  • Doğuda dışa taşan yarım daire çıkıntı: ozan bölümü (sahne çıkıntının tamamını kaplar; direkler, kiriş, perdeler).
  • Galeri (üst kat): kuzey duvarı boyunca barın üstünden doğu duvarına; 6 oda kapısı (ikisi aralık), sonuncusu merdivenin tepesinde.
  • Dekor (09_Dekor): şişeler, fıçılar, kupalar, tabela, sancaklar, fenerler, aplikler, kalkanlar, av hatırası, odun, saksılar…

İki çeşit koordinat:
  • PLAN koordinatı (X, Y): ana gövdenin güneybatı köşesi (0, 0); 1 birim = 1 m. AYARLAR bunu kullanır.
  • DÜNYA koordinatı (x, y): (0, 0) = oyun masasının merkezi (sitenin kamerası buraya bakar). w(X, Y) çevirir.
  x doğuya, y kuzeye, z yukarı. z = 0: salonun zemini. Yukarıdaki seviye +0,60, kürsü +0,30.
  Duvar parçalarında 'ic' özelliği: duvarın iç yüzünün yönü (site kameraya bakan duvarları buna göre alçaltır).
"""
import bpy, bmesh, math, os, json, random, mathutils

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIKTI = os.path.join(KOK, '3d', 'han')
os.makedirs(CIKTI, exist_ok=True)

# ───────── AYARLAR: ortak ölçüler han_plan.py'de (ayrıntılı model de oradan okur) ─────────
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from han_plan import *
TOHUM = 11

# ───────── Koleksiyonlar ─────────
bpy.ops.wm.read_factory_settings(use_empty=True)
sahne = bpy.context.scene
def koleksiyon(ad, ust=None):
    c = bpy.data.collections.new(ad)
    (ust or sahne.collection).children.link(c)
    return c
K = koleksiyon('Han')
K_YAPI = koleksiyon('01_Yapi', K)
K_ZEMIN, K_DUVAR, K_KAPI = koleksiyon('Zemin', K_YAPI), koleksiyon('Duvarlar', K_YAPI), koleksiyon('Kapilar_Pencereler', K_YAPI)
K_BASAMAK = koleksiyon('Basamaklar', K_YAPI)
K_TAVAN = koleksiyon('Tavan', K_YAPI)
K_GIRIS = koleksiyon('02_Giris', K)
K_BAR = koleksiyon('03_Bar', K)
K_TABURE = koleksiyon('Bar_Tabureleri', K_BAR)
K_SALON = koleksiyon('04_Salon', K)
K_AVIZE = koleksiyon('Avize', K_SALON)
K_KANAT = koleksiyon('05_Kanat_Somine', K)
K_UST = koleksiyon('06_Ust_Kat', K)
K_GALERI = koleksiyon('Galeri', K_UST)
K_ISIK = koleksiyon('07_Isik_Isaretleri', K)
K_SAB = koleksiyon('08_Sablonlar', K)
K_ONI = koleksiyon('99_Onizleme')

# ───────── Malzemeler: düz renk; seviyeler ayrı renkte (basamaklar okunsun) ─────────
def malzeme(ad, renk, isik=0.0, puruz=0.85):
    m = bpy.data.materials.new(ad)
    try: m.use_nodes = True
    except Exception: pass
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*renk, 1)
    p.inputs['Roughness'].default_value = puruz
    if isik:
        p.inputs['Emission Color'].default_value = (*renk, 1)
        p.inputs['Emission Strength'].default_value = isik
    m.diffuse_color = (*renk, 1)
    return m
M_SALON  = malzeme('BO_Zemin_Salon', (0.42, 0.40, 0.37))   # 0: taş grisi
M_UST    = malzeme('BO_Zemin_Ust',   (0.36, 0.25, 0.16))   # +0,60: ahşap tonu
M_KURSU  = malzeme('BO_Zemin_Kursu', (0.30, 0.14, 0.10))   # +0,30: koyu kızıl ahşap
M_GIRIS  = malzeme('BO_Zemin_Giris', (0.46, 0.43, 0.38))
M_DIS    = malzeme('BO_Dis',         (0.12, 0.12, 0.11))
M_DUVAR  = malzeme('BO_Duvar',       (0.55, 0.52, 0.47))
M_KAPI   = malzeme('BO_Kapi',        (0.26, 0.16, 0.09))
M_KARANLIK = malzeme('BO_Karanlik',  (0.03, 0.025, 0.02))
M_CAM    = malzeme('BO_Cam',         (0.45, 0.62, 0.75), isik=0.6)
M_MASA   = malzeme('BO_Masa',        (0.48, 0.32, 0.18))
M_ORTA   = malzeme('BO_Masa_Orta',   (0.56, 0.36, 0.18))
M_SAND   = malzeme('BO_Sandalye',    (0.33, 0.22, 0.13))
M_BAR    = malzeme('BO_Bar',         (0.26, 0.16, 0.09))
M_TAS    = malzeme('BO_Tas',         (0.30, 0.29, 0.28))
M_ATES   = malzeme('BO_Ates',        (1.00, 0.35, 0.06), isik=6.0)
M_MUM    = malzeme('BO_Mum',         (0.88, 0.82, 0.68))
M_ALEV   = malzeme('BO_Alev',        (1.00, 0.70, 0.30), isik=8.0)
M_KOLTUK = malzeme('BO_Koltuk',      (0.42, 0.13, 0.08))
M_HALI   = malzeme('BO_Hali',        (0.36, 0.10, 0.08))
M_POST   = malzeme('BO_Post',        (0.78, 0.72, 0.62))
M_KAGIT  = malzeme('BO_Kagit',       (0.85, 0.80, 0.66))
M_KITAP  = malzeme('BO_Kitap',       (0.25, 0.12, 0.18))
M_DEMIR  = malzeme('BO_Demir',       (0.08, 0.08, 0.08), puruz=0.5)
M_FICI   = malzeme('BO_Fici',        (0.38, 0.24, 0.12))
M_SANDIK = malzeme('BO_Sandik',      (0.45, 0.33, 0.20))
M_TABELA = malzeme('BO_Tabela',      (0.62, 0.45, 0.22))
zar = random.Random(TOHUM)
def oyna(en_cok): return zar.uniform(-en_cok, en_cok)

# ───────── Şekil kurucular (DÜNYA koordinatı) ─────────
def _nesne(ad, bm, mat, kol, konum, aci=0.0):
    me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free()
    if mat: me.materials.append(mat)
    ob = bpy.data.objects.new(ad, me)
    ob.location = konum; ob.rotation_euler = (0, 0, -math.radians(aci))   # aci: yukarıdan bakınca saat yönünde derece
    kol.objects.link(ob)
    return ob

def kutu(ad, kol, x, y, w_, d, h, z0=0.0, mat=None, aci=0.0):
    """(x, y) merkezli, w_ (doğu-batı) × d (kuzey-güney) × h kutu."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= w_; v.co.y *= d; v.co.z = (v.co.z + 0.5) * h
    return _nesne(ad, bm, mat, kol, (x, y, z0), aci)

def pkutu(ad, kol, X0, X1, Y0, Y1, z0, z1, mat=None):
    """PLAN koordinatlı köşelerle kutu."""
    (x0, y0), (x1, y1) = w(min(X0, X1), min(Y0, Y1)), w(max(X0, X1), max(Y0, Y1))
    return kutu(ad, kol, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, z1 - z0, z0, mat)

def silindir(ad, kol, x, y, r, h, z0=0.0, mat=None, n=24, r_ust=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=(r if r_ust is None else r_ust), depth=h)
    for v in bm.verts: v.co.z += h / 2
    return _nesne(ad, bm, mat, kol, (x, y, z0))

def dilim(ad, kol, x, y, r0, r1, a0, a1, z0, z1, mat=None, n=24):
    """Halka dilimi: merkez (x, y), yarıçap r0…r1, açı a0…a1 (derece, doğudan saat yönünün tersine)."""
    bm = bmesh.new()
    aci = [math.radians(a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    pts = [(r1 * math.cos(t), r1 * math.sin(t)) for t in aci]
    pts += [(r0 * math.cos(t), r0 * math.sin(t)) for t in reversed(aci)] if r0 > 0 else [(0.0, 0.0)]
    alt = [bm.verts.new((px, py, z0)) for px, py in pts]
    ust = [bm.verts.new((px, py, z1)) for px, py in pts]
    bm.faces.new(list(reversed(alt))); bm.faces.new(ust)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((alt[i], alt[j], ust[j], ust[i]))
    return _nesne(ad, bm, mat, kol, (x, y, 0))

def bagla(cocuk, ebeveyn):
    bpy.context.view_layer.update()
    cocuk.parent = ebeveyn
    cocuk.matrix_parent_inverse = ebeveyn.matrix_world.inverted()

def bos(ad, kol, x, y, z=0.0, boy=0.3, tur='PLAIN_AXES'):
    e = bpy.data.objects.new(ad, None); e.empty_display_type = tur; e.empty_display_size = boy
    e.location = (x, y, z); kol.objects.link(e); return e

def kopya(ad, sablon, kol, x, y, z=0.0, aci=0.0):
    """Şablonun bağlı kopyası. aci: önünün baktığı yön, kuzeyden saat yönünde derece."""
    ob = bpy.data.objects.new(ad, sablon.data)
    ob.location = (x, y, z); ob.rotation_euler = (0, 0, -math.radians(aci))
    kol.objects.link(ob)
    return ob

ETIKET = []
def etiket(metin, X, Y): ETIKET.append((metin, X, Y))     # PLAN koordinatı
ISIK_YER = []                                             # önizleme ışıkları: (ad, dünya x, y, z, renk, güç)
def isik_isareti(ad, X, Y, z, renk, guc):
    x, y = w(X, Y)
    bos('isik_' + ad, K_ISIK, x, y, z, 0.12, 'SPHERE')
    ISIK_YER.append((ad, x, y, z, renk, guc))

# ───────── 08 Şablonlar: sandalye, tabure, koltuk (önü kuzeyde) ─────────
SW = SD = 0.6; B = 0.06
def _parca(bm, x0, x1, y0, y1, z0, z1, mi=0):
    m = bmesh.ops.create_cube(bm, size=1.0)
    for f in {f for v in m['verts'] for f in v.link_faces}: f.material_index = mi
    for v in m['verts']:
        v.co.x = x0 if v.co.x < 0 else x1
        v.co.y = y0 if v.co.y < 0 else y1
        v.co.z = z0 if v.co.z < 0 else z1
SAB_X = w(-6, 0)[0]                                   # şablonlar binanın dışında durur (resimlerde gizli)
bm = bmesh.new()
for sx in (-1, 1):
    x0, x1 = (SW / 2 - B, SW / 2) if sx > 0 else (-SW / 2, -SW / 2 + B)
    _parca(bm, x0, x1, SD / 2 - B, SD / 2, 0, 0.45)
    _parca(bm, x0, x1, -SD / 2, -SD / 2 + B, 0, 0.92, 1)
_parca(bm, -SW / 2, SW / 2, -SD / 2, SD / 2, 0.40, 0.47)
_parca(bm, -SW / 2 + B, SW / 2 - B, -SD / 2, -SD / 2 + B, 0.62, 0.92, 1)
SANDALYE = _nesne('Sandalye_Sablon', bm, M_SAND, K_SAB, (SAB_X, 1.0, 0))
SANDALYE.data.materials.append(M_BAR)

bm = bmesh.new()
for r1, r2, z0, z1 in ((0.17, 0.17, 0.0, 0.03), (0.04, 0.04, 0.03, 0.70), (0.19, 0.19, 0.70, 0.76), (0.13, 0.13, 0.25, 0.28)):
    m = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=r1, radius2=r2, depth=z1 - z0)
    for v in m['verts']: v.co.z += (z0 + z1) / 2
TABURE = _nesne('Tabure_Sablon', bm, M_SAND, K_SAB, (SAB_X, -1.0, 0))

KW = 0.8                                              # koltuk: kollu, geniş, alçak
bm = bmesh.new()
_parca(bm, -KW / 2, KW / 2, -KW / 2, KW / 2, 0.0, 0.40)
_parca(bm, -KW / 2, KW / 2, -KW / 2, -KW / 2 + 0.18, 0.40, 0.95, 1)
_parca(bm, -KW / 2, -KW / 2 + 0.14, -KW / 2 + 0.18, KW / 2, 0.40, 0.62, 1)
_parca(bm, KW / 2 - 0.14, KW / 2, -KW / 2 + 0.18, KW / 2, 0.40, 0.62, 1)
KOLTUK = _nesne('Koltuk_Sablon', bm, M_KOLTUK, K_SAB, (SAB_X, -3.0, 0))
KOLTUK.data.materials.append(M_BAR)

# ───────── 01 Yapı: zeminler ve seviyeler ─────────
(xa, ya), (xb, yb) = w(0, 0), w(W, H)
kutu('Dis_Toprak', K_ZEMIN, (xa + xb) / 2, (ya + yb) / 2, xb - xa + 30, yb - ya + 24, 0.05, DIS_Z - 0.05, M_DIS)
pkutu('Zemin_Salon', K_ZEMIN, KANAT_X, W, 0, H, DIS_Z, 0, M_SALON)                     # aşağıdaki salon (0)
pkutu('Zemin_Giris', K_ZEMIN, GIRIS_X0, KANAT_X, GIRIS_Y0, KANAT_Y0, DIS_Z, 0, M_GIRIS)
pkutu('Zemin_Kanat', K_ZEMIN, 0, KANAT_X, KANAT_Y0, H, DIS_Z, UST_Z, M_UST)            # yukarıdaki seviye (+0,60)
pkutu('Zemin_Kuzey_Bant', K_ZEMIN, KANAT_X, W, BANT_Y, H, 0, UST_Z, M_UST)
pkutu('Zemin_Kuzeydogu', K_ZEMIN, KD_X, W, KD_Y, BANT_Y, 0, UST_Z, M_UST)
# bant ile uzantının arasındaki köşe: kavisin dışında kalan parça da yukarıda
KCX, KCY = w(KD_X - KAVIS_R, BANT_Y - KAVIS_R)
dilim('Zemin_Kavis_Kose', K_ZEMIN, KCX, KCY, KAVIS_R, KAVIS_R * 1.42, 0, 90, 0, UST_Z, M_UST, n=24)
etiket('Yukarıdaki seviye (+0,60)', 11.2, 12.3)
etiket('Aşağıdaki salon (0)', 14.0, 9.6)

# ───────── 01 Yapı: basamaklar (yukarıdan salona; örnek sanattaki gibi uzun, köşesi kavisli) ─────────
for k in (1, 2):                                      # 1. bant +0,40, 2. bant +0,20; sonra salonun zemini
    z1 = UST_Z - 0.2 * k
    a, b = BAS_D * (k - 1), BAS_D * k
    pkutu(f'Basamak_{k}_Bati', K_BASAMAK, KANAT_X + a, KANAT_X + b, KANAT_Y0, BANT_Y - a, 0, z1, M_UST)
    pkutu(f'Basamak_{k}_Kuzey', K_BASAMAK, KANAT_X + a, KD_X - KAVIS_R, BANT_Y - b, BANT_Y - a, 0, z1, M_UST)
    dilim(f'Basamak_{k}_Kavis', K_BASAMAK, KCX, KCY, KAVIS_R - b, KAVIS_R - a, 0, 90, 0, z1, M_UST, n=20)
    pkutu(f'Basamak_{k}_Dogu', K_BASAMAK, KD_X - b, KD_X - a, KD_Y - b, BANT_Y - KAVIS_R, 0, z1, M_UST)
    pkutu(f'Basamak_{k}_Guney', K_BASAMAK, KD_X - b, W, KD_Y - b, KD_Y - a, 0, z1, M_UST)
etiket('3 basamak', 8.6, 11.0)

# ───────── 01 Yapı: duvarlar ─────────
def duvar(ad, eksen, sabit, a0, a1, disari, z_ust, bosluklar=(), z_alt=DIS_Z, mat=M_DUVAR, kol=K_DUVAR):
    """Eksene paralel duvar, boşluklarıyla parça parça.
    eksen 'x': Y = sabit'te, X a0…a1 boyunca; 'y': X = sabit'te, Y a0…a1 boyunca.
    disari: duvarın dışa doğru kalınlaştığı yön (+1 / −1). bosluklar: [(b0, b1, z0, z1)] (pencere, kapı)."""
    ic = (0, -disari) if eksen == 'x' else (-disari, 0)
    t0, t1 = sorted((sabit, sabit + disari * DK))
    sayac = [0]
    def parca(b0, b1, z0, z1):
        if b1 - b0 < 1e-3 or z1 - z0 < 1e-3: return
        sayac[0] += 1
        o = (pkutu(f'{ad}_{sayac[0]}', kol, b0, b1, t0, t1, z0, z1, mat) if eksen == 'x'
             else pkutu(f'{ad}_{sayac[0]}', kol, t0, t1, b0, b1, z0, z1, mat))
        o['ic'] = ic
    bas = a0
    for b0, b1, z0, z1 in sorted(bosluklar):
        parca(bas, b0, z_alt, z_ust)
        parca(b0, b1, z_alt, z0)
        parca(b0, b1, z1, z_ust)
        bas = b1
    parca(bas, a1, z_alt, z_ust)

def cam(ad, eksen, sabit, b0, b1, disari, z0, z1):
    t = sabit + disari * DK / 2
    o = (pkutu(ad, K_KAPI, b0, b1, t - 0.02, t + 0.02, z0, z1, M_CAM) if eksen == 'x'
         else pkutu(ad, K_KAPI, t - 0.02, t + 0.02, b0, b1, z0, z1, M_CAM))
    o['ic'] = (0, -disari) if eksen == 'x' else (-disari, 0)

pz0, pz1 = PENCERE_Z
cz, cr, ch = CIKINTI
# güney: salonun güney duvarı (girintinin doğusundan doğu köşesine)
duvar('Duvar_Guney', 'x', 0, KANAT_X - DK, W + DK, -1, DH, [(a, b, pz0, pz1) for a, b in PENCERE_GUNEY])
for i, (a, b) in enumerate(PENCERE_GUNEY): cam(f'Pencere_Guney_{i + 1}', 'x', 0, a, b, -1, pz0, pz1)
# girintinin kenarları: salonun batı yüzü (X = KANAT_X, Y 0…GIRIS_Y0), giriş bölümünün güney ve batı duvarları
duvar('Duvar_Bati_Kose', 'y', KANAT_X, -DK, GIRIS_Y0, -1, DH)
duvar('Duvar_Guney_Giris', 'x', GIRIS_Y0, GIRIS_X0 - DK, KANAT_X, -1, GIRIS_H)
duvar('Duvar_Bati_Giris', 'y', GIRIS_X0, GIRIS_Y0 - DK, KANAT_Y0, -1, GIRIS_H, [(KAPI_Y[0], KAPI_Y[1], 0, 2.6)])
pkutu('Giris_Tavan', K_TAVAN, GIRIS_X0 - DK, KANAT_X, GIRIS_Y0 - DK, KANAT_Y0, GIRIS_H, GIRIS_H + 0.15, M_DUVAR)
# kanadın güney duvarı: girintinin batısında tam boy; giriş bölümünün üstünde tavandan yukarı; arada diz duvarı
duvar('Duvar_Guney_Kanat', 'x', KANAT_Y0, -DK, GIRIS_X0 - DK, -1, DH)
duvar('Duvar_Guney_Kanat_Ust', 'x', KANAT_Y0, GIRIS_X0 - DK, KANAT_X, -1, DH, z_alt=GIRIS_H + 0.15)
pkutu('Giris_Diz_Duvari', K_GIRIS, GIRIS_X0, KANAT_X, KANAT_Y0 - 0.15, KANAT_Y0, 0, UST_Z + 0.9, M_DUVAR)
# batı: kanadın batı duvarı
duvar('Duvar_Bati', 'y', 0, KANAT_Y0 - DK, H + DK, -1, DH, [(a, b, pz0 + UST_Z, pz1 + UST_Z) for a, b in PENCERE_KANAT])
for i, (a, b) in enumerate(PENCERE_KANAT): cam(f'Pencere_Bati_{i + 1}', 'y', 0, a, b, -1, pz0 + UST_Z, pz1 + UST_Z)
# kuzey: mutfak kapısı ve galerideki oda kapıları
oda = [(x, x + 1.0, GALERI_Z, GALERI_Z + 2.1) for x in ODA_KAPILARI]
duvar('Duvar_Kuzey', 'x', H, -DK, W + DK, 1, DH, [(MUTFAK[0], MUTFAK[1], UST_Z, UST_Z + 2.2)] + oda)
# doğu: çıkıntının açıklığı ve galeri hizasında bir pencere
duvar('Duvar_Dogu', 'y', W, -DK, H + DK, 1, DH, [(cz - cr, cz + cr, DIS_Z, ch), (9.0, 10.6, GALERI_Z + 0.8, GALERI_Z + 2.2)])
cam('Pencere_Dogu_Ust', 'y', W, 9.0, 10.6, 1, GALERI_Z + 0.8, GALERI_Z + 2.2)
# doğudaki yarım daire çıkıntı: eğri duvar, üç pencere
CX, CY = w(W, cz)
dilim('Zemin_Cikinti', K_ZEMIN, CX, CY, 0, cr, -90, 90, DIS_Z, 0, M_SALON, n=32)
N_YAY = 12
for i in range(N_YAY):
    t0, t1 = -90 + 180 * i / N_YAY, -90 + 180 * (i + 1) / N_YAY
    tm = math.radians((t0 + t1) / 2)
    parcalar = [(DIS_Z, pz0, M_DUVAR), (pz1 + 0.3, ch, M_DUVAR), (pz0, pz1 + 0.3, M_CAM)] if i in (2, 5, 9) else [(DIS_Z, ch, M_DUVAR)]
    for j, (z0, z1, mat) in enumerate(parcalar):
        camsa = mat is M_CAM
        o = dilim(f'Duvar_Cikinti_{i + 1}_{j + 1}', K_KAPI if camsa else K_DUVAR, CX, CY,
                  cr + (0.1 if camsa else 0), cr + (0.15 if camsa else DK), t0, t1, z0, z1, mat, n=3)
        o['ic'] = (-math.cos(tm), -math.sin(tm))
dilim('Cikinti_Cati', K_TAVAN, CX, CY, 0, cr + DK, -90, 90, ch, ch + 0.15, M_DUVAR, n=32)
pkutu('Tavan', K_TAVAN, 0, W, 0, H, DH, DH + 0.2, M_DUVAR)                  # yalnızca göz hizası çekimlerinde

# ───────── 02 Giriş: dışta saçaklı sundurma, içeride halı ve sandıklar ─────────
SX0 = GIRIS_X0 - DK                                   # dış kapının dış yüzü
pkutu('Sundurma_Zemin', K_GIRIS, SX0 - 2.4, SX0, KAPI_Y[0] - 0.6, KAPI_Y[1] + 0.6, DIS_Z, 0, M_UST)
for i in (1, 2):
    pkutu(f'Sundurma_Basamak_{i}', K_GIRIS, SX0 - 2.4 - 0.32 * i, SX0 - 2.4 - 0.32 * (i - 1),
          KAPI_Y[0] - 0.4, KAPI_Y[1] + 0.4, DIS_Z, -0.15 * i, M_UST)
for i, Y in enumerate((KAPI_Y[0] - 0.5, KAPI_Y[1] + 0.5)):
    pkutu(f'Sundurma_Direk_{i + 1}', K_GIRIS, SX0 - 2.3, SX0 - 2.1, Y - 0.1, Y + 0.1, 0, 2.9, M_BAR)
for i in range(4):                                    # kavisli saçak: dört dilimle
    x0, x1 = SX0 - 2.5 + 2.6 * i / 4, SX0 - 2.5 + 2.6 * (i + 1) / 4
    z = 2.9 + 0.5 * math.sin(math.pi * (i + 0.5) / 4)
    pkutu(f'Sundurma_Sacak_{i + 1}', K_GIRIS, x0, x1, KAPI_Y[0] - 0.8, KAPI_Y[1] + 0.8, z, z + 0.08, M_KAPI)
pkutu('Sundurma_Tabela', K_GIRIS, SX0 - 2.25, SX0 - 2.15, KAPI_Y[1] + 0.65, KAPI_Y[1] + 1.5, 1.9, 2.6, M_TABELA)
# çift kanatlı kapı: güneydeki kanat kapalı, kuzeydeki içeri açık (menteşesi kuzey ucunda)
L = (KAPI_Y[1] - KAPI_Y[0]) / 2
x, y = w(GIRIS_X0 + 0.04, KAPI_Y[0] + L / 2)
kutu('Kapi_Giris_Kanat_1', K_KAPI, x, y, 0.07, L, 2.6, 0, M_KAPI)
x, y = w(GIRIS_X0 + 0.04, KAPI_Y[1])
o = kutu('Kapi_Giris_Kanat_2', K_KAPI, x, y, 0.07, L, 2.6, 0, M_KAPI)
o.data.transform(mathutils.Matrix.Translation((0, -L / 2, 0)))
o.rotation_euler.z = math.radians(70)
x, y = w((GIRIS_X0 + KANAT_X) / 2 - 0.3, (GIRIS_Y0 + KANAT_Y0) / 2)
kutu('Giris_Hali', K_GIRIS, x, y, 2.8, 1.6, 0.012, 0, M_HALI)
for i, (X, Y, s, z) in enumerate(((2.1, 1.3, 0.55, 0), (2.1, 1.3, 0.4, 0.55), (2.75, 1.2, 0.45, 0), (6.3, 3.3, 0.5, 0))):
    pkutu(f'Giris_Sandik_{i + 1}', K_GIRIS, X - s / 2, X + s / 2, Y - s / 2, Y + s / 2, z, z + s, M_SANDIK)
silindir('Giris_Fici', K_GIRIS, *w(6.3, 1.5), 0.3, 0.85, 0, M_FICI, n=16)
pkutu('Giris_Askilik', K_GIRIS, 3.9, 4.05, GIRIS_Y0, GIRIS_Y0 + 0.15, 0, 1.8, M_BAR)
pkutu('Giris_Bank', K_GIRIS, 4.3, 5.7, GIRIS_Y0, GIRIS_Y0 + 0.4, 0, 0.45, M_KAPI)
# salona açıklık: kalın bir direk ve üstünde kiriş (Lion's Inn'deki gibi)
pkutu('Giris_Gecit_Duvar', K_GIRIS, KANAT_X - DK, KANAT_X, GIRIS_Y0, GECIT_Y, 0, GIRIS_H, M_DUVAR)
pkutu('Giris_Gecit_Direk', K_GIRIS, KANAT_X - 0.35, KANAT_X + 0.1, KANAT_Y0 - 0.45, KANAT_Y0, 0, GIRIS_H, M_BAR)
pkutu('Giris_Gecit_Kiris', K_GIRIS, KANAT_X - 0.3, KANAT_X + 0.05, GECIT_Y, KANAT_Y0, 2.7, GIRIS_H, M_BAR)
isik_isareti('giris', 4.3, 2.4, 2.6, (1.0, 0.62, 0.3), 60)
isik_isareti('sundurma', SX0 - 1.2, (KAPI_Y[0] + KAPI_Y[1]) / 2, 2.5, (1.0, 0.6, 0.3), 40)
etiket('Giriş', 4.3, 2.4); etiket('Sundurma', SX0 - 1.2, 0.3)

# ───────── 04 Salon: kürsü ve oyun masası ─────────
silindir('Kursu_Basamak', K_SALON, 0, 0, KURSU_R + BAS_D, 0.15, 0, M_KURSU, n=64)
silindir('Kursu', K_SALON, 0, 0, KURSU_R, KURSU_H, 0, M_KURSU, n=64)
silindir('Kursu_Hali', K_SALON, 0, 0, 2.2, 0.012, KURSU_H, M_HALI, n=64)

def masa_kur(ad, kol, x, y, z, r, n, sr, mat, ayak_r, ilk_aci=0.0, donme=0.0):
    """Yuvarlak masa + sandalyeler; hepsi masanın boş nesnesine (tutamak) bağlı."""
    k = koleksiyon(ad, kol)
    kok = bos(ad, k, x, y, z, boy=r * 0.6, tur='CIRCLE')
    parcalar = [silindir(f'{ad}_Ust', k, x, y, r, 0.06, z0=z + 0.74, mat=mat, n=48),
                silindir(f'{ad}_Ayak', k, x, y, ayak_r, 0.68, z0=z + 0.06, mat=mat, n=16),
                silindir(f'{ad}_Taban', k, x, y, ayak_r * 2.6, 0.06, z0=z, mat=mat, n=24)]
    for i in range(n):
        a = ilk_aci + 360 * i / n + oyna(donme * 0.6)      # kuzeyden saat yönünde
        ra = math.radians(a)
        parcalar.append(kopya(f'{ad}_Sandalye_{i + 1}', SANDALYE, k, x + sr * math.sin(ra), y + sr * math.cos(ra), z, a + 180 + oyna(donme)))
    for p in parcalar: bagla(p, kok)
    return kok

MASA_KOK = masa_kur('Masa_Orta', K_SALON, 0, 0, KURSU_H, ORTA_R, ORTA_SANDALYE, ORTA_SANDALYE_R, M_ORTA, 0.15, 0, 4)
# masanın üstü: ortada harita, her koltuğun önünde kâğıt, kitap yığınları, mumlar (ortası zarlar için açık)
UZ = KURSU_H + 0.80
ust = [kutu('Masa_Harita', K_SALON, 0.05, -0.05, 0.95, 0.65, 0.006, UZ, M_KAGIT, aci=12)]
for i in range(ORTA_SANDALYE):
    a = math.radians(360 * i / ORTA_SANDALYE); rr = ORTA_R - 0.25
    ust.append(kutu(f'Masa_Kagit_{i + 1}', K_SALON, rr * math.sin(a), rr * math.cos(a), 0.21, 0.29, 0.004, UZ, M_KAGIT, aci=math.degrees(a) + oyna(15)))
for i, (a, n) in enumerate(((70, 3), (200, 2), (305, 2))):
    ra = math.radians(a); rr = ORTA_R - 0.5
    for j in range(n):
        ust.append(kutu(f'Masa_Kitap_{i + 1}_{j + 1}', K_SALON, rr * math.sin(ra), rr * math.cos(ra), 0.2, 0.27, 0.045, UZ + j * 0.045, M_KITAP, aci=a + oyna(20)))
for i, a in enumerate((120, 250, 15)):
    ra = math.radians(a); rr = ORTA_R - 0.45
    x, y = rr * math.sin(ra), rr * math.cos(ra)
    ust.append(silindir(f'Masa_Mum_{i + 1}', K_SALON, x, y, 0.035, 0.14, UZ, M_MUM, n=12))
    ust.append(silindir(f'Masa_Mum_{i + 1}_Alev', K_SALON, x, y, 0.02, 0.06, UZ + 0.14, M_ALEV, n=8, r_ust=0.0))
for p in ust: bagla(p, MASA_KOK)
etiket('Oyun masası (kürsü +0,30)', MASA[0], MASA[1] - 1.6)

# şamdanlı avize: tavandan zincirle inen demir çember, üstünde mumlar (ortası açık: zarlar görünsün)
AZ = KURSU_H + 3.2
AR = 0.95
silindir('Avize_Cember', K_AVIZE, 0, 0, AR, 0.07, AZ, M_DEMIR, n=40)
for i in range(4):                                    # çembere inen zincirler
    ra = math.radians(45 + 90 * i)
    p = mathutils.Vector((AR * math.cos(ra), AR * math.sin(ra), AZ + 0.07)); q = mathutils.Vector((0, 0, AZ + 1.3))
    o = silindir(f'Avize_Zincir_{i + 1}', K_AVIZE, 0, 0, 0.012, (q - p).length, 0, M_DEMIR, n=6)
    o.location = p; o.rotation_euler = (q - p).to_track_quat('Z', 'Y').to_euler()
silindir('Avize_Ana_Zincir', K_AVIZE, 0, 0, 0.02, DH - AZ - 1.3, AZ + 1.3, M_DEMIR, n=6)
for i in range(10):
    ra = math.radians(36 * i)
    x, y = AR * math.cos(ra), AR * math.sin(ra)
    silindir(f'Avize_Mum_{i + 1}', K_AVIZE, x, y, 0.035, 0.16, AZ + 0.07, M_MUM, n=10)
    silindir(f'Avize_Mum_{i + 1}_Alev', K_AVIZE, x, y, 0.022, 0.07, AZ + 0.23, M_ALEV, n=8, r_ust=0.0)
isik_isareti('avize', MASA[0], MASA[1], AZ + 0.3, (1.0, 0.68, 0.38), 260)

# yan masalar (kürsünün çevresinde)
for i, (X, Y) in enumerate(YAN_MASALAR):
    x, y = w(X, Y)
    kok = masa_kur(f'Masa_Yan_{i + 1}', K_SALON, x, y, 0, YAN_R, 4, YAN_SANDALYE_R, M_MASA, 0.11, 45 + oyna(20), 8)
    m = silindir(f'Mum_Yan_{i + 1}', K_SALON, x, y, 0.04, 0.12, 0.80, M_MUM, n=12)
    bagla(m, kok)
    isik_isareti(f'mum_yan_{i + 1}', X, Y, 1.0, (1.0, 0.6, 0.3), 30)

# dekor malzemeleri
M_SISE   = malzeme('BO_Sise',    (0.16, 0.34, 0.22), puruz=0.3)
M_SANCAK = malzeme('BO_Sancak',  (0.55, 0.10, 0.08))
M_SANCAK2 = malzeme('BO_Sancak_Yesil', (0.12, 0.30, 0.18))
M_KALAY  = malzeme('BO_Kalay',   (0.55, 0.55, 0.52), puruz=0.4)
M_BITKI  = malzeme('BO_Bitki',   (0.20, 0.42, 0.16))
M_CUVAL  = malzeme('BO_Cuval',   (0.62, 0.55, 0.40))
M_LAMBA  = malzeme('BO_Fener',   (1.00, 0.72, 0.35), isik=4.0)
K_DEKOR = koleksiyon('09_Dekor', K)

def yatik_fici(ad, X, Y, z0, r=0.25, boy=0.45, eksen='y', kol=None):
    """Yatırılmış fıçı. eksen 'y': kuzey-güney boyunca (duvara dik), 'x': doğu-batı boyunca."""
    x, y = w(X, Y)
    o = silindir(ad, kol or K_DEKOR, 0, 0, r, boy, -boy / 2, M_FICI, n=16)
    o.location = (x, y, z0 + r)
    o.rotation_euler = (math.radians(90), 0, 0) if eksen == 'y' else (0, math.radians(90), 0)
    return o

def kupa(ad, X, Y, z0, kol=None):
    return silindir(ad, kol or K_DEKOR, *w(X, Y), 0.05, 0.12, z0, M_KALAY, n=10)

def saksi(ad, X, Y, z0, boy=1.0):
    silindir(ad + '_Saksi', K_DEKOR, *w(X, Y), 0.22, 0.35, z0, M_FICI, n=14)
    silindir(ad + '_Yaprak', K_DEKOR, *w(X, Y), 0.38, boy * 0.7, z0 + 0.3, M_BITKI, n=10, r_ust=0.12)

def kalkan(ad, X, z, r=0.35):
    """Kuzey duvarına asılı yuvarlak kalkan (yüzü güneye)."""
    x, y = w(X, H)
    for ek, rr, kal, mat in (('', r, 0.05, M_SANDIK), ('_Gobek', r * 0.25, 0.09, M_DEMIR)):
        o = silindir(ad + ek, K_DEKOR, 0, 0, rr, kal, 0, mat, n=20)
        o.location = (x, y, z); o.rotation_euler = (math.radians(90), 0, 0)

def aplik(ad, X, Y, z, guc=20):
    """Duvar feneri: küçük, kendi kendine parlayan kutu + ışık işareti."""
    pkutu(ad, K_DEKOR, X - 0.08, X + 0.08, Y - 0.08, Y + 0.08, z, z + 0.22, M_LAMBA)
    isik_isareti(ad.lower(), X, Y, z + 0.1, (1.0, 0.62, 0.3), guc)

# ───────── Doğudaki çıkıntı: ozan bölümü ─────────
# Sahne çıkıntının tamamını kaplar (yuvarlak arka duvara dayanır), önünde bir basamak; açıklığın iki yanında kalın
# direk, üstünde kiriş, kenarlarda perde: salondan ayrı bir bölüm gibi görünür.
dilim('Ozan_Sahnesi', K_SALON, CX, CY, 0, cr + 0.02, -90, 90, 0, SAHNE_H, M_KURSU, n=32)
pkutu('Ozan_Sahnesi_Ic', K_SALON, W - 0.02, W + DK, cz - cr + 0.02, cz + cr - 0.02, 0, SAHNE_H, M_KURSU)   # duvarın kalınlığı boyunca
pkutu('Ozan_Basamak', K_SALON, W - 0.4, W, cz - cr + 0.4, cz + cr - 0.4, 0, 0.15, M_KURSU)
for i, (a, b) in enumerate(((cz - cr, cz - cr + 0.4), (cz + cr - 0.4, cz + cr))):
    pkutu(f'Ozan_Direk_{i + 1}', K_SALON, W - 0.2, W + 0.25, a, b, 0, ch, M_BAR)
    p0, p1 = (b, b + 0.55) if i == 0 else (a - 0.55, a)
    pkutu(f'Ozan_Perde_{i + 1}', K_DEKOR, W + 0.1, W + 0.2, p0, p1, SAHNE_H, ch - 0.5, M_SANCAK)
pkutu('Ozan_Kiris', K_SALON, W - 0.2, W + 0.25, cz - cr, cz + cr, ch - 0.5, ch, M_BAR)
pkutu('Ozan_Sancak', K_DEKOR, W + cr - 0.12, W + cr - 0.06, cz - 0.45, cz + 0.45, 1.4, 3.3, M_SANCAK)       # arka duvarda
kutu('Ozan_Tabure', K_SALON, CX + 1.3, CY - 0.3, 0.35, 0.35, 0.45, SAHNE_H, M_SAND)
silindir('Ozan_Davul', K_SALON, CX + 1.7, CY + 1.0, 0.3, 0.4, SAHNE_H, M_FICI, n=16)
pkutu('Ozan_Nota_Sehpasi', K_DEKOR, W + 0.85, W + 0.9, cz - 0.6, cz - 0.3, SAHNE_H, SAHNE_H + 1.1, M_DEMIR)
pkutu('Ozan_Lavta', K_DEKOR, W + 1.9, W + 2.05, cz - 1.3, cz - 0.95, SAHNE_H, SAHNE_H + 0.9, M_SANDIK)
for i, Y in enumerate((cz - cr + 0.75, cz + cr - 0.75)):                     # sahnenin önünde ayaklı şamdanlar
    silindir(f'Ozan_Samdan_{i + 1}', K_DEKOR, *w(W + 0.45, Y), 0.03, 1.3, SAHNE_H, M_DEMIR, n=8)
    silindir(f'Ozan_Samdan_{i + 1}_Mum', K_DEKOR, *w(W + 0.45, Y), 0.04, 0.15, SAHNE_H + 1.3, M_MUM, n=8)
    silindir(f'Ozan_Samdan_{i + 1}_Alev', K_DEKOR, *w(W + 0.45, Y), 0.025, 0.07, SAHNE_H + 1.45, M_ALEV, n=8, r_ust=0)
isik_isareti('ozan', W + 1.2, cz, 2.4, (1.0, 0.62, 0.3), 120)
etiket('Ozan bölümü', W + 1.4, cz)

# ───────── 03 Bar: kuzey duvarı boyunca, düz (yukarıdaki seviyede, galerinin altında) ─────────
z = UST_Z
pkutu('Bar_Tezgah', K_BAR, BAR_X[0], BAR_X[1], TEZ_Y, TEZ_Y + 0.6, z, z + TEZGAH_H, M_BAR)
# arkası: alçak dolap, üstünde iki açık raf ve şişeler (tek parça yüksek pano gibi durmasın)
for i, (a, b) in enumerate(((BAR_X[0] - 0.5, MUTFAK[0] - 0.1), (MUTFAK[1] + 0.1, BAR_X[1] + 1.0))):
    pkutu(f'Bar_Dolap_{i + 1}', K_BAR, a, b, H - RAF_D, H, z, z + 1.0, M_BAR)
    for j, rz in enumerate((1.55, 2.15)):
        pkutu(f'Bar_Raf_{i + 1}_{j + 1}', K_BAR, a, b, H - 0.3, H, z + rz, z + rz + 0.04, M_BAR)
        for k in range(int((b - a) / 0.16)):
            if zar.random() < 0.25: continue
            silindir(f'Bar_Sise_{i + 1}_{j + 1}_{k + 1}', K_BAR, *w(a + 0.08 + k * 0.16, H - 0.15), 0.04, 0.26 + oyna(0.05), z + rz + 0.04, M_SISE, n=8)
for i in range(3):                                    # dolabın üstünde yatık fıçılar
    yatik_fici(f'Bar_Fici_{i + 1}', BAR_X[0] - 0.2 + i * 0.55, H - 0.25, z + 1.0, kol=K_BAR)
for i in range(7):                                    # tezgâhta kupalar, iki mum
    kupa(f'Bar_Kupa_{i + 1}', BAR_X[0] + 0.5 + zar.uniform(0, BAR_X[1] - BAR_X[0] - 1.0), TEZ_Y + 0.3 + oyna(0.15), z + TEZGAH_H, K_BAR)
for i, X in enumerate((13.5, 19.0)):
    silindir(f'Bar_Mum_{i + 1}', K_BAR, *w(X, TEZ_Y + 0.3), 0.04, 0.14, z + TEZGAH_H, M_MUM, n=10)
pkutu('Kapi_Mutfak_Kanat', K_KAPI, MUTFAK[0], MUTFAK[0] + 0.06, H - 0.95, H, z, z + 2.15, M_KAPI)
pkutu('Mutfak_Girisi', K_KAPI, MUTFAK[0] - 0.3, MUTFAK[1] + 0.3, H + DK, H + DK + 1.2, z, z + 2.6, M_KARANLIK)
for i, (X, Y) in enumerate(((15.4, 15.1), (15.0, 15.25))):               # barmenin arkasında un çuvalları
    silindir(f'Bar_Cuval_{i + 1}', K_DEKOR, *w(X, Y), 0.22, 0.55, z, M_CUVAL, n=10, r_ust=0.15)
kok_t = bos('Bar_Tabureleri', K_TABURE, *w((BAR_X[0] + BAR_X[1]) / 2, TEZ_Y - 0.45), z, boy=0.4)
tab = [(BAR_X[0] + 0.6 + i * 0.85, TEZ_Y - 0.45) for i in range(11)]
for i, (X, Y) in enumerate(tab):
    bagla(kopya(f'Bar_Tabure_{i + 1:02d}', TABURE, K_TABURE, *w(X, Y), z), kok_t)
# galerinin kirişinden: barın tabelası, iki sancak ve üç fener
KZ = GALERI_Z - 0.45                                  # kirişin alt yüzü
pkutu('Bar_Tabela', K_DEKOR, 15.7, 17.3, GALERI_Y0 + 0.08, GALERI_Y0 + 0.14, KZ - 0.75, KZ - 0.1, M_TABELA)
for i, (X, mat) in enumerate(((12.6, M_SANCAK), (20.2, M_SANCAK2))):
    pkutu(f'Bar_Sancak_{i + 1}', K_DEKOR, X, X + 0.7, GALERI_Y0 - 0.04, GALERI_Y0, KZ - 1.4, KZ, mat)
for i, X in enumerate((14.2, 18.6, 21.0)):
    pkutu(f'Bar_Fener_{i + 1}_Zincir', K_DEKOR, X - 0.01, X + 0.01, GALERI_Y0 + 0.4, GALERI_Y0 + 0.42, KZ - 0.6, KZ, M_DEMIR)
    pkutu(f'Bar_Fener_{i + 1}', K_DEKOR, X - 0.1, X + 0.1, GALERI_Y0 + 0.31, GALERI_Y0 + 0.51, KZ - 0.85, KZ - 0.6, M_LAMBA)
    isik_isareti(f'bar_{i + 1}', X, GALERI_Y0 + 0.4, KZ - 0.75, (1.0, 0.65, 0.35), 110)
etiket('Bar', 19.8, 14.9); etiket('Mutfak kapısı', 16.6, 15.45); etiket(f'{len(tab)} tabure', 18.0, 12.9)

# barın batısında görev panosu (iğnelenmiş kâğıtlar, küçük çatı, önünde bank) ve yanında fıçı yığını
p0, p1 = PANO_X
pkutu('Gorev_Panosu', K_DEKOR, p0, p1, H - 0.06, H, z + 1.1, z + 2.3, M_TABELA)
pkutu('Gorev_Panosu_Cati', K_DEKOR, p0 - 0.15, p1 + 0.15, H - 0.3, H, z + 2.3, z + 2.42, M_KAPI)
for i in range(7):
    X = p0 + 0.2 + zar.uniform(0, p1 - p0 - 0.6); zz = z + 1.25 + zar.uniform(0, 0.75)
    pkutu(f'Gorev_Kagidi_{i + 1}', K_DEKOR, X, X + 0.28 + oyna(0.05), H - 0.08, H - 0.06, zz, zz + 0.32, M_KAGIT)
pkutu('Gorev_Panosu_Bank', K_DEKOR, p0 + 0.1, p1 - 0.1, H - 1.0, H - 0.65, z, z + 0.45, M_KAPI)
for i, (X, zz) in enumerate(((10.0, 0), (10.55, 0), (10.27, 0.48))):
    yatik_fici(f'Fici_Yigini_{i + 1}', X, H - 0.3, z + zz, r=0.25, boy=0.5)
etiket('Görev panosu', (p0 + p1) / 2, 15.3)

# ───────── 05 Batı kanadı: şömine ve önünde temiz oturma yeri; gerisinde uzun masa; güneyde okuma köşesi ─────────
s0, s1 = SOMINE_X
pkutu('Somine_Govde', K_KANAT, s0, s1, H - 0.9, H, z, z + 2.0, M_TAS)
pkutu('Somine_Baca', K_KANAT, s0 + 0.5, s1 - 0.5, H - 0.7, H, z + 2.0, DH + 0.6, M_TAS)
pkutu('Somine_Agiz', K_KANAT, s0 + 0.6, s1 - 0.6, H - 0.95, H - 0.3, z, z + 1.1, M_KARANLIK)
pkutu('Somine_Ates', K_KANAT, s0 + 0.8, s1 - 0.8, H - 0.75, H - 0.4, z, z + 0.4, M_ATES)
pkutu('Somine_Esik', K_KANAT, s0 - 0.2, s1 + 0.2, H - 1.5, H - 0.9, z, z + 0.06, M_TAS)
sx, sy = w((s0 + s1) / 2, H - 2.6)
post = silindir('Somine_Post', K_KANAT, sx, sy, 1.0, 0.015, z, M_POST, n=32); post.scale = (1.25, 0.85, 1)
for i in range(7):                                    # şömineye dönük kavisli kanepe (örnek sanattaki gibi)
    t = math.radians(200 + 140 * i / 6)
    o = kutu(f'Somine_Kanepe_{i + 1}', K_KANAT, sx + 2.0 * math.cos(t), sy + 0.3 + 1.6 * math.sin(t), 0.62, 0.7, 0.75, z, M_KOLTUK)
    o.rotation_euler.z = t + math.pi / 2
silindir('Somine_Sehpa', K_KANAT, sx, sy - 0.4, 0.35, 0.42, z, M_MASA, n=20)
kupa('Somine_Sehpa_Kupa', (s0 + s1) / 2 + 0.1, H - 3.0, z + 0.42)
# şöminenin üstünde av hatırası (boynuzlu baş), rafta mumlar; yanında odun yığını; iki yanında aplik
mx_ = (s0 + s1) / 2
pkutu('Somine_Trofe', K_DEKOR, mx_ - 0.3, mx_ + 0.3, H - 0.82, H - 0.7, z + 2.7, z + 3.3, M_POST)
for i, sg in enumerate((-1, 1)):
    pkutu(f'Somine_Trofe_Boynuz_{i + 1}', K_DEKOR, *sorted((mx_ + sg * 0.3, mx_ + sg * 0.75)), H - 0.8, H - 0.74, z + 3.2, z + 3.3, M_POST)
for i, X in enumerate((s0 + 0.3, s0 + 0.6, s1 - 0.35)):
    silindir(f'Somine_Raf_Mum_{i + 1}', K_DEKOR, *w(X, H - 0.6), 0.035, 0.14, z + 2.0, M_MUM, n=8)
for i in range(6):
    yatik_fici(f'Odun_{i + 1}', s1 + 0.6, H - 0.2 - (i % 3) * 0.22, z + (i // 3) * 0.2, r=0.1, boy=0.8, eksen='x')
aplik('Aplik_Somine_1', s0 - 0.3, H - 0.1, z + 2.0); aplik('Aplik_Somine_2', s1 + 0.3, H - 0.1, z + 2.0)
isik_isareti('somine', (s0 + s1) / 2, H - 0.6, z + 0.5, (1.0, 0.45, 0.15), 900)
etiket('Şömine', (s0 + s1) / 2, H - 1.2)
# uzun masa ve banklar (eski yuvarlak masanın yerinde)
pkutu('Kanat_Uzun_Masa', K_KANAT, 2.0, 5.6, 9.15, 10.05, z + 0.74, z + 0.8, M_MASA)
for i, X in enumerate((2.25, 5.35)):
    pkutu(f'Kanat_Uzun_Masa_Ayak_{i + 1}', K_KANAT, X - 0.1, X + 0.1, 9.25, 9.95, z, z + 0.74, M_MASA)
for i, (y0, y1) in enumerate(((8.6, 8.95), (10.25, 10.6))):
    pkutu(f'Kanat_Bank_{i + 1}', K_KANAT, 2.1, 5.5, y0, y1, z, z + 0.45, M_KAPI)
for i in range(5):
    kupa(f'Kanat_Kupa_{i + 1}', 2.4 + i * 0.75 + oyna(0.15), 9.6 + oyna(0.25), z + 0.8)
for i in range(3):
    silindir(f'Kanat_Tabak_{i + 1}', K_DEKOR, *w(2.8 + i * 1.1, 9.6 + oyna(0.15)), 0.14, 0.02, z + 0.8, M_KALAY, n=14)
isik_isareti('kanat_masa', 3.8, 9.6, z + 1.0, (1.0, 0.6, 0.3), 35)
etiket('Uzun masa', 3.8, 9.6)
# güneyde okuma köşesi: halı, karşılıklı iki koltuk, sehpa ve kitaplar
kutu('Okuma_Hali', K_KANAT, *w(3.8, 5.7), 3.0, 2.0, 0.012, z, M_HALI)
kopya('Okuma_Koltuk_1', KOLTUK, K_KANAT, *w(2.8, 5.7), z, 90)
kopya('Okuma_Koltuk_2', KOLTUK, K_KANAT, *w(4.8, 5.7), z, 270)
silindir('Okuma_Sehpa', K_KANAT, *w(3.8, 5.7), 0.3, 0.5, z, M_MASA, n=16)
for j in range(3):
    kutu(f'Okuma_Kitap_{j + 1}', K_DEKOR, *w(3.8, 5.7), 0.2, 0.27, 0.05, z + 0.5 + j * 0.05, M_KITAP, aci=oyna(25))
saksi('Okuma_Bitki', 0.6, 4.6, z)
etiket('Okuma köşesi', 3.8, 5.0)

# ───────── 06 Merdiven: doğu duvarı boyunca kuzeye; tepesinde galeri ve karşısında oda kapısı ─────────
n_bas = round((GALERI_Z - UST_Z) / 0.2)
uzun = GALERI_Y0 - MERDIVEN_Y0
for i in range(n_bas):
    y0 = MERDIVEN_Y0 + i * uzun / n_bas
    pkutu(f'Merdiven_Basamak_{i + 1:02d}', K_UST, MERDIVEN_X0, W, y0, y0 + uzun / n_bas, z, z + (i + 1) * (GALERI_Z - UST_Z) / n_bas, M_BAR)
for i in range(6):
    Y = MERDIVEN_Y0 + 0.2 + i * (uzun - 0.4) / 5
    zz = z + (Y - MERDIVEN_Y0) / uzun * (GALERI_Z - UST_Z)
    pkutu(f'Merdiven_Dikme_{i + 1}', K_UST, MERDIVEN_X0 - 0.08, MERDIVEN_X0, Y, Y + 0.08, z, zz + 0.95, M_BAR)
for i, (Y, s) in enumerate(((12.3, 0.5), (12.95, 0.45))):               # merdivenin altında sandık ve fıçı
    pkutu(f'Merdiven_Alti_Sandik_{i + 1}', K_DEKOR, 23.1, 23.1 + s, Y, Y + s, z, z + s, M_SANDIK)
yatik_fici('Merdiven_Alti_Fici', 23.4, 11.6, z, r=0.28, boy=0.55, eksen='x')
for i, (X, Y) in enumerate(((20.3, 8.7), (20.85, 8.55))):                 # merdivenin dibinde
    silindir(f'Fici_Merdiven_{i + 1}', K_DEKOR, *w(X, Y), 0.28, 0.8, z, M_FICI, n=16)
saksi('Merdiven_Bitki', 22.2, 8.5, z, 1.2)
etiket('Merdiven', 23.35, 10.4)

# ───────── 06 Üst kat: galeri (şöminenin üstüne gelmez), oda kapıları ─────────
gz0 = GALERI_Z - 0.25
pkutu('Galeri_Zemin', K_GALERI, GALERI_X0, W, GALERI_Y0, H, gz0, GALERI_Z, M_UST)
pkutu('Galeri_Kiris', K_GALERI, GALERI_X0, W, GALERI_Y0, GALERI_Y0 + 0.24, gz0 - 0.2, gz0, M_BAR)
pkutu('Galeri_Korkuluk_On', K_GALERI, GALERI_X0, MERDIVEN_X0, GALERI_Y0, GALERI_Y0 + 0.08, GALERI_Z, GALERI_Z + 0.95, M_BAR)
pkutu('Galeri_Korkuluk_Bati', K_GALERI, GALERI_X0, GALERI_X0 + 0.08, GALERI_Y0, H, GALERI_Z, GALERI_Z + 0.95, M_BAR)
for i, X in enumerate((GALERI_X0 + 0.15, 12.4, 16.4, 20.4)):            # galeriyi taşıyan direkler (yukarıdaki seviyeden)
    pkutu(f'Galeri_Direk_{i + 1}', K_UST, X - 0.13, X + 0.13, GALERI_Y0, GALERI_Y0 + 0.26, UST_Z, gz0 - 0.2, M_BAR)
for i, X in enumerate((10.6, 13.8, 18.6)):                               # korkuluğa asılı çiçek kutuları
    pkutu(f'Galeri_Cicek_{i + 1}', K_DEKOR, X, X + 0.9, GALERI_Y0 - 0.25, GALERI_Y0, GALERI_Z + 0.55, GALERI_Z + 0.85, M_BITKI)
for i, X in enumerate(ODA_KAPILARI):
    ac = ARALIK.get(i, 0)
    x, y = w(X, H + DK / 2)
    o = kutu(f'Galeri_Oda_Kapisi_{i + 1}', K_GALERI, x, y, 1.0, 0.06, 2.1, GALERI_Z, M_KAPI)
    o.data.transform(mathutils.Matrix.Translation((0.5, 0, 0)))   # menteşe batı kenarında
    if ac:                                            # aralık: içeri (kuzeye, odaya) açılır; arkasında loş oda
        o.rotation_euler.z = math.radians(ac)
        pkutu(f'Galeri_Oda_{i + 1}', K_GALERI, X - 0.3, X + 1.3, H + DK, H + DK + 0.8, GALERI_Z, GALERI_Z + 2.15, M_KARANLIK)   # sığ: eğik bakışta duvarın üstünden görünmesin
        isik_isareti(f'oda_{i + 1}', X + 0.5, H + DK + 0.5, GALERI_Z + 1.2, (1.0, 0.6, 0.3), 25)
    if i < len(ODA_KAPILARI) - 1:                     # kapıların arasında aplik, üstte kalkan
        ax = (X + 1.0 + ODA_KAPILARI[i + 1]) / 2
        aplik(f'Aplik_Galeri_{i + 1}', ax, H - 0.1, GALERI_Z + 1.5)
        kalkan(f'Kalkan_Galeri_{i + 1}', ax, GALERI_Z + 2.55)
for i, (X, zz) in enumerate(((1.4, 4.2), (6.6, 4.2), (4.0, 5.6))):      # kanadın üstünde, kuzey duvarında kalkanlar
    kalkan(f'Kalkan_Kanat_{i + 1}', X, zz, 0.45)
etiket(f'Galeri: {len(ODA_KAPILARI)} oda kapısı (tepeden gizli)', 12.6, 15.95)

# ───────── Salonda yaşanmışlık: masalarda kupa ve tabak, devrilmiş bir sandalye, saksılar, silah askısı ─────────
for i, (X, Y) in enumerate(YAN_MASALAR):
    for j in range(2):
        kupa(f'Yan_{i + 1}_Kupa_{j + 1}', X + oyna(0.4), Y + oyna(0.4), 0.80)
    silindir(f'Yan_{i + 1}_Tabak', K_DEKOR, *w(X + oyna(0.3), Y + oyna(0.3)), 0.13, 0.02, 0.80, M_KALAY, n=14)
for j in range(5):                                    # bir yan masada iskambil kâğıtları
    kutu(f'Yan_3_Kart_{j + 1}', K_DEKOR, *w(YAN_MASALAR[2][0] + oyna(0.3), YAN_MASALAR[2][1] + oyna(0.3)), 0.07, 0.1, 0.003, 0.82, M_KAGIT, aci=oyna(60))
o = kopya('Devrik_Sandalye', SANDALYE, K_DEKOR, *w(12.0, 3.7), 0.3, 30)
o.rotation_euler = (math.radians(-90), 0, math.radians(-30))
for i, (X, Y) in enumerate(((7.75, 0.45), (21.4, 0.45), (23.5, 7.75))):
    saksi(f'Salon_Bitki_{i + 1}', X, Y, seviye(X, Y))
pkutu('Silah_Askisi', K_DEKOR, W - 0.25, W, 0.15, 1.05, 0, 1.6, M_BAR)
for i in range(4):
    pkutu(f'Silah_{i + 1}', K_DEKOR, W - 0.3, W - 0.26, 0.25 + i * 0.22, 0.29 + i * 0.22, 0.1, 1.7 + oyna(0.15), M_DEMIR)
# giriş: askılıkta pelerinler
for i, X in enumerate((3.75, 4.2)):
    pkutu(f'Giris_Pelerin_{i + 1}', K_DEKOR, X - 0.2, X + 0.2, GIRIS_Y0 + 0.02, GIRIS_Y0 + 0.12, 0.6, 1.75, M_SANCAK2 if i else M_SANCAK)

# ───────── 99 Önizleme: ışıklar ve kameralar ─────────
def isik(ad, konum, renk, guc, yaricap=0.1, tur='POINT'):
    d = bpy.data.lights.new(ad, tur); d.color = renk; d.energy = guc
    if tur == 'POINT': d.shadow_soft_size = yaricap
    if guc < 100: d.use_shadow = False                # küçük ışıklar (mumlar) gölgesiz: önizleme hızlı ve uyarısız
    o = bpy.data.objects.new(ad, d); o.location = konum; K_ONI.objects.link(o)
    return o
for ad, x, y, zz, renk, guc in ISIK_YER:
    isik('Onizleme_' + ad, (x, y, zz), renk, guc, 0.15)
dolgu = isik('Onizleme_Dolgu', (0, 0, 20), (1.0, 0.86, 0.7), 1.4, tur='SUN')
dolgu.rotation_euler = (math.radians(30), 0, math.radians(-40))
dunya = bpy.data.worlds.new('Dunya'); sahne.world = dunya
try: dunya.use_nodes = True
except Exception: pass
dunya.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.10, 0.09, 0.08, 1)
dunya.node_tree.nodes.get('Background').inputs['Strength'].default_value = 1.2

sahne.render.engine = 'BLENDER_EEVEE'
for ad, deger in (('taa_render_samples', 32), ('use_shadows', True)):
    try: setattr(sahne.eevee, ad, deger)
    except Exception: pass
try: sahne.view_settings.view_transform = 'Filmic'; sahne.view_settings.look = 'Medium High Contrast'
except Exception: pass
sahne.render.image_settings.file_format = 'PNG'

def kamera(ad, konum, bakis_noktasi, orto=None, lens=24):
    d = bpy.data.cameras.new(ad)
    if orto: d.type = 'ORTHO'; d.ortho_scale = orto
    else: d.lens = lens
    d.clip_end = 150
    o = bpy.data.objects.new(ad, d); o.location = konum; K_ONI.objects.link(o)
    o.rotation_euler = (mathutils.Vector(bakis_noktasi) - mathutils.Vector(konum)).to_track_quat('-Z', 'Y').to_euler()
    return o

def cek(kam, dosya, gx, gy):
    sahne.camera = kam
    sahne.render.resolution_x, sahne.render.resolution_y = gx, gy
    sahne.render.filepath = os.path.join(CIKTI, dosya)
    bpy.ops.render.render(write_still=True)

def gizle(*adlar, kol=()):
    """Adı bu öneklerle başlayan nesneleri ve verilen koleksiyonları resimden gizler."""
    for o in bpy.data.objects:
        if adlar and o.name.startswith(adlar): o.hide_render = True
    for k in kol: k.hide_render = True

def hepsini_goster():
    for o in bpy.data.objects:
        o.hide_render = False
        if o.get('ic') is not None: o.scale.z = 1
    for k in bpy.data.collections: k.hide_render = False
    K_SAB.hide_render = True                          # şablonlar binanın dışında; resimlere girmesin

# 1) Tam tepeden (kuş bakışı): galeri, avize, tavanlar ve saçak gizli
SOL, SAG = SX0 - 3.2, W + cr + 0.6                    # sundurmadan çıkıntıya
ALT, UST = -0.6, H + 0.6
ox, oy = w((SOL + SAG) / 2, (ALT + UST) / 2)
k_ust = kamera('Kamera_Ustten', (ox, oy, 40), (ox, oy, 0), orto=SAG - SOL)
k_ust.rotation_euler = (0, 0, 0)
hepsini_goster()
gizle('Sundurma_Sacak', kol=(K_GALERI, K_AVIZE, K_TAVAN))
cek(k_ust, 'onizleme-ustten.png', 1920, round(1920 * (UST - ALT) / (SAG - SOL)))

# 2) Sitenin açısı: kuzeyden doğuya 30°, 45° eğik, ortografik; iç yüzü kameraya bakan duvarlar 0,95 m'ye alçalır
hepsini_goster()
th, ph = math.radians(YON), math.radians(EGIM)
bak = (math.sin(th) * math.cos(ph), math.cos(th) * math.cos(ph), -math.sin(ph))
for o in bpy.data.objects:
    ic = o.get('ic')
    if ic is None or ic[0] * math.sin(th) + ic[1] * math.cos(th) <= 0.15: continue
    zs = [v.co.z for v in o.data.vertices]
    z0, z1 = o.location.z + min(zs), o.location.z + max(zs)
    if o.data.materials[0].name == M_CAM.name or z0 >= KESIK: o.hide_render = True
    elif z1 > KESIK:
        if o.location.z == 0 and min(zs) < 0: o.scale.z = KESIK / z1       # eğri duvar dilimi (başlangıç noktası yerde)
        else: o.scale.z = (KESIK - z0) / (z1 - z0)
gizle('Giris_Tavan', 'Sundurma_Sacak', 'Sundurma_Tabela', kol=(K_TAVAN,))   # giriş bölümünün içi görünsün
mx, my = w((SOL + SAG) / 2 + 0.3, H / 2 + 0.8)
k_site = kamera('Kamera_Site', (mx - bak[0] * 60, my - bak[1] * 60, 1.5 - bak[2] * 60), (mx, my, 1.5), orto=36)
cek(k_site, 'onizleme-site.png', 1920, 1440)

# 3) Göz hizası: kürsünün güneybatı koltuğundan bara, galeriye ve şömineye
hepsini_goster()
ra = math.radians(200)
k_goz = kamera('Kamera_Goz', (1.45 * math.sin(ra), 1.45 * math.cos(ra), KURSU_H + 1.2), (*w(15.5, 13.5), 2.4), lens=18)
cek(k_goz, 'onizleme-goz.png', 1920, 1080)
# 4) Giriş kapısından salona
k_gir = kamera('Kamera_Giris', (*w(GIRIS_X0 + 0.6, (KAPI_Y[0] + KAPI_Y[1]) / 2), 1.6), (*w(15.0, 5.0), 1.2), lens=18)
cek(k_gir, 'onizleme-giris.png', 1920, 1080)
hepsini_goster()

with open(os.path.join(CIKTI, 'etiketler.json'), 'w', encoding='utf-8') as f:
    json.dump({'etiketler': [{'metin': m, 'x': (X - SOL) / (SAG - SOL), 'y': (UST - Y) / (UST - ALT)} for m, X, Y in ETIKET],
               'oda_m': [W, H]}, f, ensure_ascii=False, indent=1)

for ekran in bpy.data.screens:
    for alan in ekran.areas:
        if alan.type == 'VIEW_3D':
            for sp in alan.spaces:
                if sp.type == 'VIEW_3D': sp.shading.color_type = 'MATERIAL'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CIKTI, 'han-blockout.blend'), compress=True)
print(f'Gövde: {W} x {H} m (+ çıkıntı {cr} m, giriş girintisi), masa {MASA}')
print('TAMAM')
