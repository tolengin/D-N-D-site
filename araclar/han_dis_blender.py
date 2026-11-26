# -*- coding: utf-8 -*-
"""
YENİ HAN — DIŞ CEPHE (Blender betiği)  (2026-11-26)
===================================================
Hanın dışı (kullanıcının kararları, 2026-11-26): taş alt kat; ahşap kirişli sıva üst kat, alt kattan taşar (Tudor "taşma");
kavisli destekli kirişler; 35° eğimli, ahşap pullu çatı; güneyde öne çıkan alınlık ve iki çatı penceresi; kuzeyde taş baca;
ozan bölümünün üstünde yarım külah; alacakaranlık.
Sitenin canlı 3D açılışında (kamera dışarıdan kapıya, oradan masaya uçar) kullanılacak: içerinin üstüne binen AYRI BİR KABUK.
Kural: kabuk içerideki hiçbir yüzün içine girmez (kamera kapıdan girince salonda yabancı yüz görmesin). Üst kat içi boş;
alttaki kaplama yalnızca taşan şeritte. Alt kattaki taş, içerinin gerçek pencereleri ve kapısı için delikli.

İçerideki model (han_detay_blender.py) DEĞİŞMEZ: bu betik 3d/han/han-detay.blend'i açar, dış cepheyi '10_Dis' koleksiyonuna
kurar ve 3d/han/han-dis.blend olarak kaydeder. Malzemeler içerinin boyalı malzemeleri (taş, sıva, koyu ahşap, çatı pulu);
pencere camı içerinin kurşunlu camının dışarıdan ışıyan kopyası (Dis_Pencere).

Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --python araclar\\han_dis_blender.py
Çıktılar (3d/han/): han-dis.blend; önizlemeler dis-yaklasma.png (kameranın başlayacağı yer), dis-gb.png (güneybatıdan,
yukarıdan), dis-kd.png (kuzeydoğudan), dis-kapi.png (sundurmanın önünden).
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from han_plan import *

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIKTI = os.path.join(KOK, '3d', 'han')
bpy.ops.wm.open_mainfile(filepath=os.path.join(CIKTI, 'han-detay.blend'))
sahne = bpy.context.scene

# ───────── Ölçüler (PLAN koordinatı, m) ─────────
G = 0.07                           # taş kaplamanın dış yüzü, içerideki duvarın dış yüzünden bu kadar dışarıda
KAT_Z = GALERI_Z                   # üst katın başladığı yükseklik (3,8)
TASMA = 0.35                       # üst katın alt kattan taşması (güney, batı)
KUZEY_TASMA = 1.15                 # kuzeyde daha çok: galerideki odalar (Oda_Ic, 0,8 m dışarıda) üst katın içinde kalır
DU = 0.12                          # üst kat sıvasının kalınlığı (içe doğru)
SIVA_D, KIRIS_D = 0.0, 0.06        # kirişler sıvanın önünde 6 cm
UX0, UY0 = -DK - G - TASMA, -DK - G - TASMA                  # üst katın dış yüzleri (doğuda taşma yok: ozan külahı dayanır)
UX1, UY1 = W + DK + G, H + DK + G + KUZEY_TASMA
SACAK = 0.55                       # çatının duvardan taşması
EGIM_CATI = 35
CATI_Z = DH + 0.1                  # çatının oturduğu yükseklik (iç tavanın hemen üstü)
KAL = 0.22                         # çatı kalınlığı
CATI_PENCERE = [5.0, 21.0]         # güney yüzündeki çatı pencereleri (X ortası)
ALINLIK_X = (10.0, 17.0)           # güneyde öne çıkan alınlık
ALINLIK_TASMA = 0.5
PEN_EN, PEN_BOY = 1.0, 1.3         # üst kattaki pencereler
RAY_Z = KAT_Z + 1.0                # üst katın ara kuşağı (pencerelerin altı)
KIRIS = os.environ.get('DIS_KIRIS', 'sade')   # 'dolu': her bölmede kemer / çapraz; 'sade': yalnızca pencere bölmeleri ve köşeler
eg = math.tan(math.radians(EGIM_CATI))
YM = (UY0 + UY1) / 2
MAHYA = CATI_Z + (YM - UY0) * eg

# ───────── Koleksiyon, malzemeler ─────────
def koleksiyon(ad, ust=None):
    eski = bpy.data.collections.get(ad)
    if eski:
        for o in list(eski.all_objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(eski)
    c = bpy.data.collections.new(ad); (ust or sahne.collection).children.link(c); return c
K = koleksiyon('10_Dis')
MAT = bpy.data.materials
def dis_pencere():
    """İçerinin kurşunlu camının kopyası: doku rengi × sıcak ışık → kurşun çizgiler karanlık, camlar ışır."""
    m = MAT.get('Dis_Pencere')
    if m: MAT.remove(m)
    m = MAT['M_Pencere'].copy(); m.name = 'Dis_Pencere'
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    renk = b.inputs['Base Color'].links[0].from_socket
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0; mix.inputs[7].default_value = (1.0, 0.62, 0.28, 1)
    nt.links.new(renk, mix.inputs[6]); nt.links.new(mix.outputs[2], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = 5.0
    return m
def renk_kopya(kaynak, ad, carpan):
    """Malzemenin kopyası, rengi çarpanla (ör. taş daha gri ve koyu)."""
    m = MAT.get(ad)
    if m: MAT.remove(m)
    m = MAT[kaynak].copy(); m.name = ad
    nt = m.node_tree; b = nt.nodes['Principled BSDF']; kay = b.inputs['Base Color'].links[0].from_socket
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0; mix.inputs[7].default_value = (*carpan, 1)
    nt.links.new(kay, mix.inputs[6]); nt.links.new(mix.outputs[2], b.inputs['Base Color'])
    return m
def cimen():
    m = MAT.get('Dis_Cimen')
    if m: MAT.remove(m)
    m = MAT.new('Dis_Cimen'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(KOK, '3d', 'dokular', 'cimen.jpg'), check_existing=True)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.95
    return m
M = {'tas': renk_kopya('M_Tas_Blok', 'Dis_Tas', (0.66, 0.64, 0.62)), 'siva': MAT['M_Duvar'], 'kiris': MAT['M_Ahsap_Koyu'], 'cati': MAT['M_Cati'],
     'pencere': dis_pencere(), 'fener': MAT['M_Fener_Cam'], 'demir': MAT['M_Demir'],
     'cimen': cimen(), 'yol': renk_kopya('M_Saksi', 'Dis_Yol', (0.50, 0.42, 0.36)), 'yaprak': renk_kopya('M_Sarmasik', 'Dis_Yaprak', (0.62, 0.72, 0.58))}
UVS = {'tas': 1.0, 'siva': 2.5, 'kiris': 1.0, 'cati': (1.55, 1.5), 'pencere': (1.04, 1.0), 'fener': 1.0, 'demir': 1.0,
       'cimen': 3.5, 'yol': 2.0, 'yaprak': 1.6}
SIRA = list(M)                     # her nesne bütün malzemeleri taşır; yüzün malzemesi sıradan

# ───────── Geometri yardımcıları (bmesh, DÜNYA koordinatı) ─────────
def W3(X, Y, zz): return Vector((*w(X, Y), zz))

def kutu(bm, X0, X1, Y0, Y1, z0, z1, mat):
    """PLAN koordinatlı kutu."""
    X0, X1 = sorted((X0, X1)); Y0, Y1 = sorted((Y0, Y1))
    v = [bm.verts.new(W3(x, y, zz)) for zz in (z0, z1) for y in (Y0, Y1) for x in (X0, X1)]
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([v[i] for i in f]).material_index = SIRA.index(mat)

def kalip(bm, alt, ust, mat):
    """İki eş köşe halkasından (alt yüz, üst yüz) kapalı cisim."""
    a = [bm.verts.new(p) for p in alt]; b = [bm.verts.new(p) for p in ust]
    mi = SIRA.index(mat)
    bm.faces.new(a).material_index = mi; bm.faces.new(list(reversed(b))).material_index = mi
    for i in range(len(a)):
        j = (i + 1) % len(a); bm.faces.new((a[i], a[j], b[j], b[i])).material_index = mi

def cubuk(bm, A, B, gen, nor, d0, d1, mat):
    """A'dan B'ye kiriş: genişliği gen (nor'a ve doğrultuya dik), kalınlığı nor yönünde d0…d1."""
    yon = (B - A).normalized(); yan = yon.cross(nor).normalized() * gen / 2
    halka = [A - yan, B - yan, B + yan, A + yan]
    kalip(bm, [p + nor * d0 for p in halka], [p + nor * d1 for p in halka], mat)

class Cephe:
    """Dikey düzlem: eksen 'x' (X boyunca, Y = c'de) ya da 'y' (Y boyunca, X = c'de); s dışarı yönü (+1 / −1).
    Noktalar (u, z, d): u düzlem boyunca PLAN koordinatı, d dışarı doğru uzaklık."""
    def __init__(s, eksen, c, yon): s.e, s.c, s.s = eksen, c, yon
    def p(s, u, zz, d=0.0):
        return W3(u, s.c + s.s * d, zz) if s.e == 'x' else W3(s.c + s.s * d, u, zz)
    @property
    def nor(s): return Vector((0, s.s, 0)) if s.e == 'x' else Vector((s.s, 0, 0))
    def kutu(s, bm, u0, u1, z0, z1, d0, d1, mat):
        if s.e == 'x': kutu(bm, u0, u1, s.c + s.s * d0, s.c + s.s * d1, z0, z1, mat)
        else: kutu(bm, s.c + s.s * d0, s.c + s.s * d1, u0, u1, z0, z1, mat)
    def cubuk(s, bm, a, b, gen=0.16, d0=SIVA_D, d1=KIRIS_D, mat='kiris'):
        cubuk(bm, s.p(*a), s.p(*b), gen, s.nor, d0, d1, mat)
    def yol(s, bm, pts, gen=0.15, **k):
        for a, b in zip(pts, pts[1:]): s.cubuk(bm, a, b, gen, **k)
    def cokgen(s, bm, pts, d0, d1, mat):
        kalip(bm, [s.p(u, zz, d0) for u, zz in pts], [s.p(u, zz, d1) for u, zz in pts], mat)

def taş_delikli(bm, cp, u0, u1, z0, z1, delikler, d0=0.01, d1=G):
    """Taş kaplama: deliklerin (u0, u1, z0, z1) kenarlarından geçen ızgaranın dolu hücreleri."""
    us = sorted({u0, u1} | {min(max(v, u0), u1) for a, b, _, _ in delikler for v in (a, b)})
    zs = sorted({z0, z1} | {min(max(v, z0), z1) for _, _, a, b in delikler for v in (a, b)})
    for a, b in zip(us, us[1:]):
        for za, zb in zip(zs, zs[1:]):
            um, zm = (a + b) / 2, (za + zb) / 2
            if b - a < 1e-3 or zb - za < 1e-3 or any(x0 < um < x1 and y0 < zm < y1 for x0, x1, y0, y1 in delikler): continue
            cp.kutu(bm, a, b, za, zb, d0, d1, 'tas')

def nesne(ad, bm, kol=None):
    """bmesh → nesne. UV: her yüz kendi düzleminde (yatay ekseni yerde yatay, düşey ekseni yüzün eğimi boyunca), malzemenin boyuna göre;
    eğik çatıda pullar eğim boyunca doğru boyda çıkar."""
    bm.normal_update()
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal; s = UVS[SIRA[f.material_index]]; su, sv = s if isinstance(s, tuple) else (s, s)
        if abs(n.z) > 0.92: t1, t2 = Vector((1, 0, 0)), Vector((0, 1, 0))
        else:
            t1 = Vector((-n.y, n.x, 0)).normalized(); t2 = n.cross(t1)
            if t2.z < 0: t2 = -t2
        for l in f.loops: l[uvl].uv = (l.vert.co.dot(t1) / su, l.vert.co.dot(t2) / sv)
    me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free()
    for m in M.values(): me.materials.append(m)
    o = bpy.data.objects.new(ad, me); (kol or K).objects.link(o); return o

# ───────── Üst katın yarı ahşap (kavisli destekli) cephesi ─────────
def kemer(cp, bm, ua, ub, za, zb, gen=0.13):
    """Bir bölmede iki kavisli destek: direklerden doğup üst kirişte birleşen yarım elips (╭─╮)."""
    um, a = (ua + ub) / 2, (ub - ua) / 2
    for isaret in (-1, 1):
        pts = [(um + isaret * a * math.cos(math.radians(t)), za + (zb - za) * math.sin(math.radians(t))) for t in range(0, 91, 15)]
        cp.yol(bm, pts, gen)

def capraz(cp, bm, ua, ub, za, zb, gen=0.13):
    cp.cubuk(bm, (ua, za), (ub, zb), gen); cp.cubuk(bm, (ua, zb), (ub, za), gen)

def pencere(cp, bm, uc, z0, en=PEN_EN, boy=PEN_BOY):
    """Kirişli cephede pencere: sıvanın önünde ışıyan kurşunlu cam, çevresinde kasa, altında denizlik, ortada kayıt."""
    u0, u1, z1 = uc - en / 2, uc + en / 2, z0 + boy
    cp.kutu(bm, u0, u1, z0, z1, 0.005, 0.02, 'pencere')
    for a, b in (((u0 - 0.07, z0), (u1 + 0.07, z0)), ((u0 - 0.07, z1), (u1 + 0.07, z1)), ((u0, z0), (u0, z1)), ((u1, z0), (u1, z1))):
        cp.cubuk(bm, a, b, 0.1, 0.0, 0.08)
    cp.cubuk(bm, (uc, z0), (uc, z1), 0.05, 0.0, 0.05)
    cp.kutu(bm, u0 - 0.14, u1 + 0.14, z0 - 0.12, z0 - 0.04, 0.0, 0.14, 'kiris')

def yari_ahsap(cp, bm, u0, u1, pencereler, z0=KAT_Z, z1=CATI_Z, bos=()):
    """u0…u1 arası dikdörtgen kirişli cephe. pencereler: pencere ortaları (u). bos: kiriş konmayacak aralıklar (önünde başka şey var).
    Düzen: alt eşik, üst başlık, ara kuşak (RAY_Z); direkler pencereleri kuşatır, aralar ≤ 1,7 m; alt sırada çapraz, üst sırada
    pencere ya da kemer."""
    cp.kutu(bm, u0, u1, z0, z1, -DU, SIVA_D, 'siva')
    cp.cubuk(bm, (u0, z0 + 0.11), (u1, z0 + 0.11), 0.22, d1=0.08)                     # alt eşik
    cp.cubuk(bm, (u0, z1 - 0.1), (u1, z1 - 0.1), 0.2)                                   # üst başlık
    cp.cubuk(bm, (u0, RAY_Z + 0.07), (u1, RAY_Z + 0.07), 0.14)                          # ara kuşak
    direk = {u0 + 0.09, u1 - 0.09}
    for uc in pencereler: direk |= {uc - PEN_EN / 2 - 0.12, uc + PEN_EN / 2 + 0.12}
    direk = sorted(direk)
    tam = [direk[0]]
    for a, b in zip(direk, direk[1:]):
        n = max(1, math.ceil((b - a) / 1.7 - 0.05))
        tam += [a + (b - a) * k / n for k in range(1, n + 1)]
    bos_mu = lambda u: any(a <= u <= b for a, b in bos)
    for u in tam:
        if not bos_mu(u): cp.cubuk(bm, (u, z0 + 0.2), (u, z1 - 0.18), 0.18)
    bolme = [(a, b) for a, b in zip(tam, tam[1:]) if b - a >= 0.45 and not bos_mu((a + b) / 2)]
    for k, (a, b) in enumerate(bolme):
        ia, ib = a + 0.09, b - 0.09
        pen = [uc for uc in pencereler if ia < uc < ib]
        kose = k in (0, len(bolme) - 1)
        if KIRIS == 'dolu' or pen or kose: capraz(cp, bm, ia, ib, z0 + 0.22, RAY_Z)
        if pen: pencere(cp, bm, pen[0], RAY_Z + 0.25)
        elif KIRIS == 'dolu' or kose: kemer(cp, bm, ia, ib, RAY_Z + 0.14 + 0.35, z1 - 0.2)

def alinlik(cp, bm, u0, u1, z0, tepe, pencere_z=None, sacak=SACAK):
    """Üçgen alınlık: sıva üçgen, ortada dikme, bir kuşak, iki kavisli destek, ortada pencere; eğim boyunca oymalı saçak tahtası."""
    um = (u0 + u1) / 2; h = tepe - z0
    cp.cokgen(bm, [(u0, z0), (u1, z0), (um, tepe)], -DU, SIVA_D, 'siva')
    kz = z0 + h * 0.42; kw = (tepe - kz) / h * (u1 - u0) / 2                           # kuşağın yüksekliği ve yarı boyu
    cp.cubuk(bm, (um - kw, kz), (um + kw, kz), 0.16)
    cp.cubuk(bm, (um, z0), (um, tepe - 0.15), 0.18)
    for isaret in (-1, 1):                                                              # yanlarda iki dikme ve kavisli destek
        ux = um + isaret * kw * 1.45
        uz = z0 + (h * (1 - abs(ux - um) / ((u1 - u0) / 2)))
        cp.cubuk(bm, (ux, z0), (ux, uz - 0.1), 0.16)
        pts = [(um + isaret * kw * (1 - math.cos(math.radians(t))), z0 + 0.1 + (kz - z0 - 0.1) * math.sin(math.radians(t))) for t in range(0, 91, 15)]
        cp.yol(bm, [(um + isaret * (kw - (p[0] - um) * isaret), p[1]) for p in pts], 0.13)
    if pencere_z is not None: pencere(cp, bm, um, pencere_z, 0.9, 1.1)
    for isaret in (-1, 1):                                                              # saçak tahtası (çatının ucunun altında)
        a = (um + isaret * ((u1 - u0) / 2 + sacak), z0 - sacak * eg)
        cp.cubuk(bm, (um, tepe + 0.02), a, 0.3, -sacak + 0.02, -sacak + 0.1)
        cp.cubuk(bm, (um, tepe - 0.1), (um + isaret * ((u1 - u0) / 2), z0), 0.2)          # eğik dış kiriş

# ═════════ ALT KAT: taş kaplama (içerinin pencere ve kapısı açık) ═════════
pz0, pz1 = PENCERE_Z
TAS_UST = KAT_Z - 0.22                                         # taşın üstü: üstünde duvar kirişi, onun üstünde taşmanın kirişleri
bm = bmesh.new()
gney = Cephe('x', -DK, -1)
taş_delikli(bm, gney, KANAT_X - DK - G, W + DK + G, DIS_Z, TAS_UST, [(a - 0.12, b + 0.12, pz0 - 0.18, pz1 + 0.14) for a, b in PENCERE_GUNEY])
bati = Cephe('y', -DK, -1)
taş_delikli(bm, bati, KANAT_Y0 - DK - G, H + DK + G, DIS_Z, TAS_UST,
            [(a - 0.12, b + 0.12, pz0 + UST_Z - 0.18, pz1 + UST_Z + 0.14) for a, b in PENCERE_KANAT])
kgney = Cephe('x', KANAT_Y0 - DK, -1)                                      # batı kanadının güneyi (girişin solu)
taş_delikli(bm, kgney, -DK - G, GIRIS_X0 - DK - G, DIS_Z, TAS_UST, [])
gbati = Cephe('y', GIRIS_X0 - DK, -1)                                      # giriş bölümünün batısı: kapı ve taş kemeri açık
KR = (KAPI_Y[1] - KAPI_Y[0]) / 2
taş_delikli(bm, gbati, GIRIS_Y0 - DK - G, KANAT_Y0 - DK + G, DIS_Z, TAS_UST, [(KAPI_Y[0] - KR * 0.22 - 0.04, KAPI_Y[1] + KR * 0.22 + 0.04, 0.0, 9)])
ggney = Cephe('x', GIRIS_Y0 - DK, -1)
taş_delikli(bm, ggney, GIRIS_X0 - DK - G, KANAT_X - DK - G, DIS_Z, TAS_UST, [])
kose = Cephe('y', KANAT_X - DK, -1)                                        # giriş bölümü ile ana gövdenin birleştiği köşe
taş_delikli(bm, kose, -DK - G, GIRIS_Y0 - DK - G, DIS_Z, TAS_UST, [])
cz, cr, ch = CIKINTI
dogu = Cephe('y', W + DK, 1)
taş_delikli(bm, dogu, -DK - G, cz - cr - DK, DIS_Z, KAT_Z, [])
taş_delikli(bm, dogu, cz + cr + DK, H + DK + G, DIS_Z, KAT_Z, [])
kuzey = Cephe('x', H + DK, 1)
taş_delikli(bm, kuzey, -DK - G, W + DK + G, DIS_Z, TAS_UST, [])
# ozan bölümünün yarım dairesi: dilim dilim taş, içerinin üç penceresi açık
N_YAY = 12; CX, CY = w(W, cz); r0, r1 = cr + DK + 0.01, cr + DK + G
def dilim(bm, t0, t1, z0, z1, ra=r0, rb=r1, mat='tas', n=2):
    for k in range(n):
        a0, a1 = math.radians(t0 + (t1 - t0) * k / n), math.radians(t0 + (t1 - t0) * (k + 1) / n)
        hal = [(ra, a0), (rb, a0), (rb, a1), (ra, a1)]
        kalip(bm, [Vector((CX + r * math.cos(a), CY + r * math.sin(a), z0)) for r, a in hal],
              [Vector((CX + r * math.cos(a), CY + r * math.sin(a), z1)) for r, a in hal], mat)
for i in range(N_YAY):
    t0, t1 = -90 + 180 * i / N_YAY, -90 + 180 * (i + 1) / N_YAY
    if i in PENCERE_CIKINTI:
        dilim(bm, t0, t1, DIS_Z, pz0 - 0.12); dilim(bm, t0, t1, pz1 + 0.42, ch)
        dilim(bm, t0, t0 + 1.6, pz0 - 0.12, pz1 + 0.42, n=1); dilim(bm, t1 - 1.6, t1, pz0 - 0.12, pz1 + 0.42, n=1)
    else: dilim(bm, t0, t1, DIS_Z, ch)
# mutfak çıkıntısı: içerideki mutfak girişinin arkası (Mutfak_Girisi) duvardan 0,6 m taşıyor → taşmanın altında küçük taş oda, arka kapı
MX0, MX1, MY1 = MUTFAK[0] - 0.9, MUTFAK[1] + 0.9, H + DK + 0.85
kutu(bm, MX0, MX1, H + DK, MY1, DIS_Z, TAS_UST, 'tas')
nesne('Dis_Alt_Kat', bm)
bm = bmesh.new()
ak = Cephe('x', MY1, 1)
ak.kutu(bm, MUTFAK[0] + 0.1, MUTFAK[1] - 0.1, 0.0, 2.1, 0.0, 0.05, 'kiris')
for uu in (MUTFAK[0] + 0.05, MUTFAK[1] - 0.05): ak.cubuk(bm, (uu, 0.0), (uu, 2.2), 0.12, 0.0, 0.09)
ak.cubuk(bm, (MUTFAK[0], 2.18), (MUTFAK[1], 2.18), 0.14, 0.0, 0.09)
for zz in (0.4, 1.6): ak.cubuk(bm, (MUTFAK[0] + 0.15, zz), (MUTFAK[1] - 0.15, zz), 0.06, 0.05, 0.08, 'demir')
nesne('Dis_Mutfak_Kapi', bm)

# İçerinin gerçek pencerelerinin dış yüzünde ışıyan cam (içerideki camın hemen dışında; içeriden görünmez)
bm = bmesh.new()
for a, b in PENCERE_GUNEY: kutu(bm, a, b, -0.15, -0.155, pz0, pz1, 'pencere')
for a, b in PENCERE_KANAT: kutu(bm, -0.15, -0.155, a, b, pz0 + UST_Z, pz1 + UST_Z, 'pencere')
for i in PENCERE_CIKINTI:
    t0, t1 = -90 + 180 * i / N_YAY, -90 + 180 * (i + 1) / N_YAY
    dilim(bm, t0 + 1.6, t1 - 1.6, pz0, pz1 + 0.3, cr + 0.17, cr + 0.175, 'pencere', n=1)
nesne('Dis_Pencere_Isik', bm)

# Duvar kirişi (taşın üstünde) ve taşmanın kirişleri (güney, batı, kuzey): uçları dışarıdan sıra sıra görünür
bm = bmesh.new()
for cp, u0, u1 in ((gney, KANAT_X - DK - G, W + DK + G), (bati, KANAT_Y0 - DK - G, H + DK + G), (kuzey, -DK - G, W + DK + G),
                   (kgney, -DK - G, GIRIS_X0 - DK - G), (ggney, GIRIS_X0 - DK - G, KANAT_X - DK - G), (gbati, GIRIS_Y0 - DK - G, KANAT_Y0 - DK + G),
                   (kose, -DK - G, GIRIS_Y0 - DK - G)):
    cp.kutu(bm, u0, u1, TAS_UST, KAT_Z - 0.06, 0.0, G + 0.02, 'kiris')
for cp, u0, u1, derin in ((gney, KANAT_X, W + DK, TASMA), (bati, KANAT_Y0, H + DK, TASMA), (kuzey, -DK, W + DK, KUZEY_TASMA)):
    u = u0 + 0.2
    while u < u1 - 0.1:
        cp.kutu(bm, u - 0.07, u + 0.07, TAS_UST, KAT_Z - 0.06, G, G + derin + 0.05, 'kiris'); u += 0.6
# taşmanın altı (yalnızca alt katın dışında kalan şerit) ve köşedeki örtülü geçidin kirişleri, direkleri
def alt_levha(X0, X1, Y0, Y1): kutu(bm, X0, X1, Y0, Y1, KAT_Z - 0.06, KAT_Z, 'kiris')
alt_levha(UX0, UX1, UY0, -DK - G)                                            # güney
alt_levha(UX0, -DK - G, -DK - G, UY1)                                        # batı
alt_levha(-DK - G, UX1, H + DK + G, UY1)                                     # kuzey
alt_levha(-DK - G, KANAT_X - DK - G, -DK - G, GIRIS_Y0 - DK - G)             # köşe: girişin önü
alt_levha(-DK - G, GIRIS_X0 - DK - G, GIRIS_Y0 - DK - G, KANAT_Y0 - DK - G)  # köşe: sundurmanın üstü
GD = 0.16                                                                    # geçit direklerinin yarı kalınlığı
dx, dy = UX0 + GD + 0.02, UY0 + GD + 0.02
for X0, Y0, X1, Y1 in ((dx, dy, KANAT_X - DK - G, dy), (dx, dy, dx, KANAT_Y0 - DK - G)):          # kalın kirişler
    kutu(bm, X0 - 0.16, X1 + 0.16, Y0 - 0.16, Y1 + 0.16, KAT_Z - 0.42, KAT_Z - 0.06, 'kiris')
for X, Y in ((dx, dy), (3.1, dy), (dx, GIRIS_Y0 - 0.3)):
    kutu(bm, X - GD, X + GD, Y - GD, Y + GD, DIS_Z, KAT_Z - 0.42, 'kiris')
    kutu(bm, X - GD - 0.06, X + GD + 0.06, Y - GD - 0.06, Y + GD + 0.06, DIS_Z, DIS_Z + 0.35, 'tas')
nesne('Dis_Tasma', bm)

# Taşmanın altında kavisli dirsekler (alt kat duvarından üst katın kirişine)
bm = bmesh.new()
def dirsek(cp, u, z_alt, derin):
    pts = [(z_alt, G)] + [(TAS_UST - (TAS_UST - z_alt) * (1 - math.sin(math.radians(t))), G + derin * math.sin(math.radians(t)) ** 0.7) for t in range(0, 91, 15)]
    for (za, da), (zb, db) in zip(pts, pts[1:]):
        cubuk(bm, cp.p(u, za, da), cp.p(u, zb, db), 0.14, Vector((1, 0, 0)) if cp.e == 'x' else Vector((0, 1, 0)), -0.06, 0.06, 'kiris')
for u in (8.2, 11.0, 14.0, 17.0, 20.0, 23.0): dirsek(gney, u, TAS_UST - 0.9, TASMA)
for u in (5.0, 8.0, 11.0, 14.0): dirsek(bati, u, TAS_UST - 0.9, TASMA)
nesne('Dis_Dirsekler', bm)

# ═════════ ÜST KAT: yarı ahşap cepheler ═════════
uGney, uBati, uKuzey, uDogu = Cephe('x', UY0, -1), Cephe('y', UX0, -1), Cephe('x', UY1, 1), Cephe('y', UX1, 1)
bm = bmesh.new()
yari_ahsap(uGney, bm, UX0, ALINLIK_X[0], [2.0, 4.6, 8.3])
yari_ahsap(uGney, bm, ALINLIK_X[1], UX1, [19.0, 21.7])
yari_ahsap(uBati, bm, UY0, UY1, [2.2, 6.0, 11.0, 15.0])
yari_ahsap(uKuzey, bm, UX0, UX1, [0.9, 7.3] + [X + 0.5 for X in ODA_KAPILARI], bos=[(SOMINE_X[0] - 0.3, SOMINE_X[1] + 0.3)])
yari_ahsap(uDogu, bm, UY0, UY1, [9.8, 13.5, 16.2])
alinlik(uBati, bm, UY0, UY1, CATI_Z, MAHYA, CATI_Z + 1.6)
alinlik(uDogu, bm, UY0, UY1, CATI_Z, MAHYA, CATI_Z + 1.6)
# güneyde öne çıkan alınlık: kendi cephesi, yan yüzleri, altı, üçgeni
a0, a1 = ALINLIK_X; am = (a0 + a1) / 2; ay0 = UY0 - ALINLIK_TASMA
aTepe = CATI_Z + (am - a0) * eg
uOn = Cephe('x', ay0, -1)
yari_ahsap(uOn, bm, a0, a1, [am - 1.6, am, am + 1.6])
alinlik(uOn, bm, a0, a1, CATI_Z, aTepe, CATI_Z + 0.45)
kutu(bm, a0, a0 + DU, ay0, UY0, KAT_Z, CATI_Z, 'siva'); kutu(bm, a1 - DU, a1, ay0, UY0, KAT_Z, CATI_Z, 'siva')
kutu(bm, a0, a1, ay0, UY0, KAT_Z - 0.06, KAT_Z, 'kiris')
nesne('Dis_Ust_Kat', bm)

# ═════════ ÇATI: pullu, iki yanında saçak; mahyada kiriş; alınlığın ve çatı pencerelerinin çatıları ═════════
def cati_prizma(bm, cp_kesit, a0_, a1_, eksen):
    """Kesiti (u, z) olan, eksen boyunca a0_…a1_ uzanan çatı levhası."""
    def p(a, u, zz): return W3(a, u, zz) if eksen == 'x' else W3(u, a, zz)
    kalip(bm, [p(a0_, u, zz) for u, zz in cp_kesit], [p(a1_, u, zz) for u, zz in cp_kesit], 'cati')
def cati_kesit(u0, um, u1, z0, tepe, sacak):
    za = z0 - sacak * eg
    return [(u0 - sacak, za), (um, tepe), (u1 + sacak, za), (u1 + sacak, za + KAL), (um, tepe + KAL / math.cos(math.radians(EGIM_CATI))), (u0 - sacak, za + KAL)]
bm = bmesh.new()
cati_prizma(bm, cati_kesit(UY0, YM, UY1, CATI_Z, MAHYA, SACAK), UX0 - SACAK, UX1 + SACAK, 'x')
cati_prizma(bm, cati_kesit(a0, am, a1, CATI_Z, aTepe, SACAK * 0.8), ay0 - SACAK * 0.8, YM - 1.0, 'y')
kutu(bm, UX0 - SACAK, UX1 + SACAK, YM - 0.12, YM + 0.12, MAHYA + 0.12, MAHYA + 0.36, 'kiris')               # mahya kirişi
# çatı pencereleri: sıva yanaklar, üçgen ön, küçük pullu çatı, ışıyan pencere
for X in CATI_PENCERE:
    en, yuk = 1.6, 1.5
    y_on = UY0 + 0.7; z0 = CATI_Z + (y_on - UY0) * eg
    derin = (yuk + 0.3) / eg + 0.3
    kutu(bm, X - en / 2, X - en / 2 + 0.1, y_on, y_on + derin, z0 - 0.3, z0 + yuk, 'siva')
    kutu(bm, X + en / 2 - 0.1, X + en / 2, y_on, y_on + derin, z0 - 0.3, z0 + yuk, 'siva')
    cp = Cephe('x', y_on, -1)
    dt = z0 + yuk + (en / 2) * eg * 1.4
    cp.cokgen(bm, [(X - en / 2, z0 + yuk), (X + en / 2, z0 + yuk), (X, dt)], -0.1, 0.0, 'siva')
    cp.kutu(bm, X - en / 2, X + en / 2, z0 - 0.3, z0 + 0.05, -0.1, 0.0, 'siva')
    pencere(cp, bm, X, z0 + 0.2, 0.9, 1.05)
    k = [(X - en / 2 - 0.2, z0 + yuk - 0.2 * 1.4 * eg), (X, dt), (X + en / 2 + 0.2, z0 + yuk - 0.2 * 1.4 * eg),
         (X + en / 2 + 0.2, z0 + yuk - 0.2 * 1.4 * eg + 0.12), (X, dt + 0.12), (X - en / 2 - 0.2, z0 + yuk - 0.2 * 1.4 * eg + 0.12)]
    kalip(bm, [W3(u, y_on - 0.25, zz) for u, zz in k], [W3(u, y_on + derin + 0.4, zz) for u, zz in k], 'cati')
nesne('Dis_Cati', bm)

# ═════════ BACA: şöminenin üstünde, kuzey yüzünde ═════════
s0, s1 = SOMINE_X
bm = bmesh.new()
BY0 = H + DK + G
BACA_UST = MAHYA - 1.6
kutu(bm, s0 - 0.25, s1 + 0.25, BY0 - 0.02, UY1 + 0.55, DIS_Z, KAT_Z + 1.2, 'tas')                 # geniş gövde (üst kattan dışarı çıkar)
kalip(bm, [W3(x, y, KAT_Z + 1.2) for x, y in ((s0 - 0.25, UY1 - 0.2), (s1 + 0.25, UY1 - 0.2), (s1 + 0.25, UY1 + 0.55), (s0 - 0.25, UY1 + 0.55))],
      [W3(x, y, KAT_Z + 2.2) for x, y in ((s0 + 0.35, UY1 - 0.2), (s1 - 0.35, UY1 - 0.2), (s1 - 0.35, UY1 + 0.45), (s0 + 0.35, UY1 + 0.45))], 'tas')   # omuz
kutu(bm, s0 + 0.35, s1 - 0.35, UY1 - 0.2, UY1 + 0.45, KAT_Z + 2.2, BACA_UST, 'tas')                 # boğaz
kutu(bm, s0 + 0.22, s1 - 0.22, UY1 - 0.33, UY1 + 0.58, BACA_UST, BACA_UST + 0.25, 'tas')            # başlık
for X in (s0 + 0.6, s1 - 0.6):                                                                     # iki ağız
    kutu(bm, X - 0.18, X + 0.18, UY1 - 0.06, UY1 + 0.32, BACA_UST + 0.25, BACA_UST + 0.75, 'tas')
nesne('Dis_Baca', bm)

# ═════════ OZAN BÖLÜMÜ: yarım külah, pullu ═════════
bm = bmesh.new()
n = 16; R = cr + DK + G + 0.45; tepe = ch + 2.4
alt = [Vector((CX + R * math.cos(math.radians(-90 + 180 * i / n)), CY + R * math.sin(math.radians(-90 + 180 * i / n)), ch - 0.15)) for i in range(n + 1)]
ust = [p + Vector((0, 0, KAL)) for p in alt]
t0v, t1v = Vector((CX, CY, tepe)), Vector((CX, CY, tepe + KAL))
A = [bm.verts.new(p) for p in alt]; B = [bm.verts.new(p) for p in ust]; ta, tb = bm.verts.new(t0v), bm.verts.new(t1v)
mi = SIRA.index('cati')
for i in range(n):
    for f in ((A[i + 1], A[i], ta), (B[i], B[i + 1], tb), (A[i], A[i + 1], B[i + 1], B[i])): bm.faces.new(f).material_index = mi
for f in ((A[0], ta, tb, B[0]), (ta, A[n], B[n], tb)): bm.faces.new(f).material_index = mi
kalip(bm, [Vector((CX + (r0 - 0.02) * math.cos(math.radians(-90 + 180 * i / n)), CY + (r0 - 0.02) * math.sin(math.radians(-90 + 180 * i / n)), ch - 0.2)) for i in range(n + 1)],
      [Vector((CX + (r1 + 0.06) * math.cos(math.radians(-90 + 180 * i / n)), CY + (r1 + 0.06) * math.sin(math.radians(-90 + 180 * i / n)), ch)) for i in range(n + 1)], 'kiris')
nesne('Dis_Ozan_Cati', bm)

# ═════════ FENERLER: geçidin direklerinde iki duvar feneri ═════════
bm = bmesh.new()
FENER = [(dx + GD + 0.25, dy, 2.3), (3.1, dy - GD - 0.25, 2.3)]
for X, Y, zz in FENER:
    kutu(bm, X - 0.12, X + 0.12, Y - 0.12, Y + 0.12, zz - 0.18, zz + 0.18, 'fener')
    kutu(bm, X - 0.15, X + 0.15, Y - 0.15, Y + 0.15, zz + 0.18, zz + 0.24, 'demir')
    kutu(bm, X - 0.1, X + 0.1, Y - 0.1, Y + 0.1, zz - 0.24, zz - 0.18, 'demir')
nesne('Dis_Fenerler', bm)
for i, (X, Y, zz) in enumerate(FENER):
    d = bpy.data.lights.new(f'Dis_Fener_{i + 1}', 'POINT'); d.energy = 60; d.color = (1.0, 0.55, 0.22); d.shadow_soft_size = 0.05
    o = bpy.data.objects.new(f'Dis_Fener_{i + 1}', d); o.location = W3(X, Y, zz); K.objects.link(o)

# ═════════ ÇEVRE (kullanıcının kararı: yol kenarında han) ═════════
# İçerinin taş döşemesi (Dis_Toprak, 54 × 40 m) hanın avlusu olarak kalır; çevresi çayır. Güneyden doğu-batı giden ana yol,
# ondan avluya sapan yan yol; yol ağzında tabela direği; avlunun güneyinde alçak çit; ağaçlar ve uzakta ağaç çizgisi.
KC = koleksiyon('11_Cevre')
import random
rnd = random.Random(11)
AVLU = (-15.0, 39.0, -12.0, 28.0)                     # içerinin taş döşemesinin PLAN sınırı (Dis_Toprak)
bm = bmesh.new(); kutu(bm, -200, 220, -200, 220, DIS_Z - 0.09, DIS_Z - 0.04, 'cimen'); nesne('Cevre_Cayir', bm, KC)

def serit(bm, pts, en, z, mat):
    """Yatay şerit (yol): orta çizginin iki yanında en / 2."""
    sol, sag = [], []
    for i, (X, Y) in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * en / 2, dx / L * en / 2
        sol.append(bm.verts.new(W3(X + nx, Y + ny, z))); sag.append(bm.verts.new(W3(X - nx, Y - ny, z)))
    for i in range(len(pts) - 1):
        bm.faces.new((sag[i], sag[i + 1], sol[i + 1], sol[i])).material_index = SIRA.index(mat)
def egri(p0, p1, p2, n=16):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (k / n for k in range(n + 1))]
ANA_YOL = egri((-150, -26), (10, -16), (170, -30), 40)
YAN_YOL = egri((-16, -21.5), (-12, -15), (-7, -11.0), 8)
bm = bmesh.new()
serit(bm, ANA_YOL, 5.0, DIS_Z - 0.035, 'yol'); serit(bm, YAN_YOL, 4.0, DIS_Z - 0.03, 'yol')
nesne('Cevre_Yol', bm, KC)

def agac(bm, X, Y, boy, z0=DIS_Z - 0.05):
    """Ağaç: altı köşeli gövde + üç yuvarlak taç (az çokgenli küre, yaprak dokusu)."""
    gr = boy * 0.045
    kalip(bm, [W3(X + gr * math.cos(t), Y + gr * math.sin(t), z0) for t in (k * math.pi / 3 for k in range(6))],
          [W3(X + gr * 0.6 * math.cos(t), Y + gr * 0.6 * math.sin(t), z0 + boy * 0.55) for t in (k * math.pi / 3 for k in range(6))], 'kiris')
    for k in range(3):
        r = boy * rnd.uniform(0.2, 0.28)
        merkez = W3(X + rnd.uniform(-0.6, 0.6) * r, Y + rnd.uniform(-0.6, 0.6) * r, z0 + boy * (0.62 + 0.13 * k))
        b2 = bmesh.new(); bmesh.ops.create_icosphere(b2, subdivisions=1, radius=r)
        for v in b2.verts: v.co = Vector((v.co.x, v.co.y, v.co.z * 0.85)) * rnd.uniform(0.9, 1.1) + merkez
        for f in b2.faces: f.material_index = SIRA.index('yaprak')
        me = bpy.data.meshes.new('_g'); b2.to_mesh(me); b2.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
def bos_mu(X, Y, pay):
    if AVLU[0] - pay < X < AVLU[1] + pay and AVLU[2] - pay < Y < AVLU[3] + pay: return False
    return all(math.hypot(X - a, Y - b) > pay + 3 for a, b in ANA_YOL + YAN_YOL)
bm = bmesh.new()
YAKIN = [(-22, -6), (-26, 4), (-20, 14), (-24, 24), (44, -6), (46, 12), (-9, -30), (6, -32), (24, -31), (-34, -12), (40, 32), (10, 34)]
for X, Y in YAKIN:
    if bos_mu(X, Y, 1.5): agac(bm, X, Y, rnd.uniform(7, 10))
nesne('Cevre_Agaclar', bm, KC)
bm = bmesh.new(); sayi = 0
for i in range(90):                                    # uzaktaki ağaç çizgisi (55–85 m), yolun geçtiği yerde boşluk
    t = 2 * math.pi * i / 90 + rnd.uniform(-0.02, 0.02); r = rnd.uniform(55, 85)
    X, Y = 12 + r * math.cos(t), 8 + r * math.sin(t)
    if bos_mu(X, Y, 2): agac(bm, X, Y, rnd.uniform(9, 14)); sayi += 1
nesne('Cevre_Agac_Cizgisi', bm, KC)

# avlunun güney kenarında alçak çit (yan yolun ağzı açık), yol ağzında tabela direği
bm = bmesh.new()
for X0, X1 in ((-14.6, -9.5), (-4.5, 20.0)):
    Y = AVLU[2] - 0.3; X = X0
    while X <= X1 + 0.01:
        kutu(bm, X - 0.06, X + 0.06, Y - 0.06, Y + 0.06, DIS_Z - 0.05, DIS_Z + 1.0, 'kiris'); X += 2.0
    for zz in (0.45, 0.85): kutu(bm, X0, X1, Y - 0.03, Y + 0.03, DIS_Z + zz - 0.04, DIS_Z + zz + 0.04, 'kiris')
TX, TY = -13.2, -19.0                                   # tabela direği: yan yolun ağzı
kutu(bm, TX - 0.1, TX + 0.1, TY - 0.1, TY + 0.1, DIS_Z - 0.05, DIS_Z + 3.2, 'kiris')
kutu(bm, TX - 0.05, TX + 1.3, TY - 0.06, TY + 0.06, DIS_Z + 2.9, DIS_Z + 3.02, 'kiris')
cubuk(bm, W3(TX, TY, DIS_Z + 2.3), W3(TX + 0.7, TY, DIS_Z + 2.92), 0.08, Vector((0, 1, 0)), -0.04, 0.04, 'kiris')
nesne('Cevre_Cit', bm, KC)
import han_parcalar as hp; hp.DOKU = os.path.join(KOK, '3d', 'dokular')   # içerinin hazır parçaları (fıçı, sandık, tabela), içerinin malzemeleriyle
hp.M.update({'ahsap': MAT['M_Ahsap'], 'demir': MAT['M_Demir'], 'masa': MAT['M_Masa'], 'koyu': MAT['M_Ahsap_Koyu'],
             'dovme': MAT['M_Demir_Dovme'], 'tabela': MAT['M_Tabela']})
kur, uv, mats = hp.tabela(0.9, DIS_Z + 1.95, DIS_Z + 2.9)
hp.duvar_parcasi('Cevre_Tabela', KC, *w(TX + 0.85, TY), 0, kur, mats, uv)
for i, (X, Y, r, h, a) in enumerate(((-2.2, 4.6, 0.32, 0.9, 10), (-2.0, 5.4, 0.3, 0.85, -20), (-1.4, 5.1, 0.26, 0.75, 40))):
    hp.fici(f'Cevre_Fici_{i + 1}', KC, *w(X, Y), r, h, a, z=DIS_Z)
hp.sandik('Cevre_Sandik', KC, *w(-2.4, -0.2), DIS_Z, 0.7, 0.6, 0.55, 12)
print('Çevre: yakın ağaç', len(YAKIN), ', uzak ağaç', sayi)

print('Dış cephe kuruldu. Mahya:', round(MAHYA, 2), 'm; yüz (bina):', sum(len(o.data.polygons) for o in K.objects if o.type == 'MESH'),
      ', yüz (çevre):', sum(len(o.data.polygons) for o in KC.objects if o.type == 'MESH'))

# ═════════ ÖNİZLEME: alacakaranlık ═════════
for o in bpy.data.objects:
    if o.name.startswith(('Duvar_', 'Direk_')): o.scale.z = 1
    o.hide_render = False
for k in bpy.data.collections: k.hide_render = False
if '08_Sablonlar' in bpy.data.collections: bpy.data.collections['08_Sablonlar'].hide_render = True
for o in bpy.data.objects:
    if o.name.startswith('Onizleme_') and o.type == 'LIGHT' and o.name != 'Onizleme_Dolgu': o.data.energy *= 0.5
if 'Onizleme_Dolgu' in bpy.data.objects: bpy.data.objects['Onizleme_Dolgu'].hide_render = True
gun = bpy.data.lights.new('Dis_Gunes', 'SUN'); gun.energy = 1.0; gun.color = (1.0, 0.55, 0.38); gun.angle = math.radians(4)
go = bpy.data.objects.new('Dis_Gunes', gun); go.rotation_euler = (math.radians(84), 0, math.radians(-115)); K.objects.link(go)
ay = bpy.data.lights.new('Dis_Gok', 'SUN'); ay.energy = 0.35; ay.color = (0.55, 0.62, 1.0); ay.angle = math.radians(30)
ao = bpy.data.objects.new('Dis_Gok', ay); ao.rotation_euler = (math.radians(35), 0, math.radians(60)); K.objects.link(ao)
nt = sahne.world.node_tree; arka = nt.nodes.get('Background')
koord = nt.nodes.new('ShaderNodeTexCoord'); ayir = nt.nodes.new('ShaderNodeSeparateXYZ'); aralik = nt.nodes.new('ShaderNodeMapRange')
renk = nt.nodes.new('ShaderNodeValToRGB')
aralik.inputs['From Min'].default_value = -0.05; aralik.inputs['From Max'].default_value = 0.6
nt.links.new(koord.outputs['Generated'], ayir.inputs['Vector']); nt.links.new(ayir.outputs['Z'], aralik.inputs['Value'])
nt.links.new(aralik.outputs['Result'], renk.inputs['Fac']); nt.links.new(renk.outputs['Color'], arka.inputs['Color'])
cr_ = renk.color_ramp
cr_.elements[0].position = 0.0; cr_.elements[0].color = (0.90, 0.42, 0.25, 1)      # ufuk: turuncu-pembe
cr_.elements[1].position = 1.0; cr_.elements[1].color = (0.035, 0.04, 0.12, 1)    # tepe: lacivert
e = cr_.elements.new(0.22); e.color = (0.30, 0.17, 0.32, 1)                       # mor
arka.inputs['Strength'].default_value = 0.7
sahne.render.engine = 'BLENDER_EEVEE'
def kam(ad, konum, bakis, lens=24):
    d = bpy.data.cameras.new(ad); d.lens = lens; d.clip_end = 400
    o = bpy.data.objects.new(ad, d); o.location = konum; K.objects.link(o)
    o.rotation_euler = (Vector(bakis) - Vector(konum)).to_track_quat('-Z', 'Y').to_euler(); return o
sahne.render.resolution_x, sahne.render.resolution_y = 1600, 900
CEKIM = {'dis-yaklasma': ((*w(-22, -14), 1.7), (*w(4, 3), 5.0), 22),
         'dis-gb': ((*w(-24, -22), 14), (*w(10, 7), 5), 24),
         'dis-kd': ((*w(46, 36), 18), (*w(12, 8), 5), 26),
         'dis-kapi': ((*w(-7.5, 0.0), 1.6), (*w(GIRIS_X0, (KAPI_Y[0] + KAPI_Y[1]) / 2), 2.0), 20)}
SADECE = os.environ.get('DIS_CEK')                                                  # ör. DIS_CEK=dis-kapi: yalnızca o çekim
for ad, (k, b, lens) in CEKIM.items():
    if SADECE and ad not in SADECE.split(','): continue
    sahne.camera = kam('Kamera_' + ad, k, b, lens)
    sahne.render.filepath = os.path.join(CIKTI, ad + ('' if KIRIS == 'sade' else '-dolu') + '.png')
    bpy.ops.render.render(write_still=True)

bpy.context.preferences.filepaths.save_version = 0
if KIRIS == 'sade': bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CIKTI, 'han-dis.blend'), compress=True, relative_remap=True)
print('TAMAM')
