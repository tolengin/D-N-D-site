# -*- coding: utf-8 -*-
"""
YENİ HAN — ORTAK PARÇALAR (2026-10-21)
======================================
Eski tavernanın ayrıntılı modelindeki (taverna_detay_blender.py) yardımcılar, malzemeler ve parçalar; yeni hanın
ayrıntılı modeli (han_detay_blender.py) bunları kullanır. Eski betik olduğu gibi duruyor (sitedeki taverna değişene kadar).

Kullanım (Blender betiğinin içinde):
    import han_parcalar as hp
    hp.hazirla(DOKU_KLASORU)          # malzemeleri kurar (hp.M), yaprak kartlarını okur
    bm = bmesh.new(); hp.P(bm, hp.b_kutu(...), 0, pah=0.01); hp.nesne('Ad', bm, [hp.M['ahsap']], koleksiyon)

Stil (elle boyanmış, hafif stilize; örnek: ornek sanat.jpg): ince çubuklar kalınlaşır (STIL_KALIN), pahlar büyür
(STIL_PAH), her şey yatayda hafifçe yamulur (STIL_EGRI). Ölçüler metre; x doğu, y kuzey, z yukarı.
"""
import bpy, bmesh, math, os, random, json
from mathutils import Vector, Matrix, noise

DETAY = 2.0                            # yuvarlak parçaların inceliği: 1 = kaba, 2 = iki kat kenar + yumuşak profiller
STIL_KALIN = 0.45                      # ince çubuklar bu oranda kalınlaşır; 6 cm'den kalın parçalar değişmez
STIL_PAH = 1.6                         # pahlar bu kat büyür: kenarlar yumuşak, biraz "oyuncak gibi"
STIL_EGRI = 0.015                      # el yapımı eğrilik (m)
KUPA_OLCEK = 1.2
SISE_OLCEK = 1.15
SIVA_RENK = (0.62, 0.47, 0.30)
TAS_RENK = (0.40, 0.35, 0.29)
TAS_ZEMIN_RENK = (0.33, 0.29, 0.24)

# Dokunun gerçek boyu (m): doku bu kadar alanda bir tekrar eder
UVS = {'M_Zemin': 2.0, 'M_Masa': 1.2, 'M_Ahsap': 1.0, 'M_Ahsap_Koyu': 1.0, 'M_Duvar': 2.5, 'M_Somine': 1.5, 'M_Deri': 0.5, 'M_Kul': 1.5,
       'M_Tas_Blok': 1.0, 'M_Tas_Zemin': (0.90, 1.00), 'M_Demir_Dovme': 0.3, 'M_Cuval': 0.4, 'M_Saksi': 0.4, 'M_Sarmasik': 0.5,
       'M_Kursu': 2.0, 'M_Dis_Zemin': 1.3, 'M_Perde': 1.2, 'M_Cati': (1.55, 1.5), 'M_Pencere': (1.04, 1.0)}
EGRI_YOK = ['Zemin', 'alev_', 'Mutfak_Girisi', 'Tas_Zemin', 'Oda_Ic', 'Dis_']   # yamulmayanlar (ad öneki)

M = {}
DOKU = None
KUTU = None                            # yaprak kartı atlasının hücreleri
sus = random.Random(99)                # süs eşyaları için "rastgele" (her çalıştırmada aynı)
ISIKLAR = []                           # (ad, x, y, z, tür): önizleme ve site ışıkları
MUM_NO = [0]

# ───────── Malzemeler ─────────
def resim(ad, renksiz=False):
    p = os.path.join(DOKU, ad)
    if not os.path.exists(p):
        raise SystemExit(f'Doku yok: {p}  →  önce "python araclar\\doku_hazirla.py" çalıştır')
    img = bpy.data.images.load(p, check_existing=True)
    if renksiz: img.colorspace_settings.name = 'Non-Color'
    return img

def _principled(ad):
    m = bpy.data.materials.new(ad)
    try: m.use_nodes = True
    except Exception: pass
    return m, m.node_tree, m.node_tree.nodes.get('Principled BSDF')

def mat_doku(ad, dosya, carpan=None, normal_guc=1.0, puruz=True, puruz_sabit=0.8, alfa=False, metal=0.0):
    """Dokulu malzeme: renk (+ isteğe bağlı ton çarpanı), normal ve pürüz haritaları. alfa: resmin saydamlığı kullanılır."""
    m, nt, p = _principled(ad)
    p.inputs['Metallic'].default_value = metal
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = resim(dosya + ('.png' if alfa else '.jpg')); t.location = (-800, 300)
    if carpan:
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.location = (-450, 300)
        mx.inputs[0].default_value = 1.0
        nt.links.new(t.outputs['Color'], mx.inputs[6]); mx.inputs[7].default_value = (*carpan, 1)
        nt.links.new(mx.outputs[2], p.inputs['Base Color'])
    else:
        nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    if alfa:
        nt.links.new(t.outputs['Alpha'], p.inputs['Alpha'])
        for ad_, deger in (('use_transparent_shadow', True), ('shadow_method', 'HASHED'), ('blend_method', 'HASHED')):
            try: setattr(m, ad_, deger)                   # saydam yerler gölge de düşürmesin (post, halı saçağı, yapraklar)
            except Exception: pass
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = resim(dosya + '-normal.jpg', True); tn.location = (-800, -150)
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = normal_guc; nm.location = (-450, -150)
    nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
    if puruz and os.path.exists(os.path.join(DOKU, dosya + '-puruz.jpg')):
        tr = nt.nodes.new('ShaderNodeTexImage'); tr.image = resim(dosya + '-puruz.jpg', True); tr.location = (-800, 50)
        nt.links.new(tr.outputs['Color'], p.inputs['Roughness'])
    else:
        p.inputs['Roughness'].default_value = puruz_sabit
    m.diffuse_color = (*(carpan or (0.5, 0.35, 0.2)), 1)
    return m

def mat_duz(ad, renk, puruz=0.6, metal=0.0, isik=None, isik_guc=0.0):
    m, nt, p = _principled(ad)
    p.inputs['Base Color'].default_value = (*renk, 1)
    p.inputs['Roughness'].default_value = puruz; p.inputs['Metallic'].default_value = metal
    if isik:
        p.inputs['Emission Color'].default_value = (*isik, 1); p.inputs['Emission Strength'].default_value = isik_guc
    m.diffuse_color = (*renk, 1)
    return m

def doku_var(dosya, alfa=False):
    return os.path.exists(os.path.join(DOKU, dosya + ('.png' if alfa else '.jpg')))

def mat_yeni(ad, dosya, yedek_renk, isik=None, isik_guc=0.0, **k):
    """Dokusu varsa onu, yoksa düz renk kullanır: görseller gelene kadar sahne yine kurulur."""
    if doku_var(dosya, k.get('alfa', False)): return mat_doku(ad, dosya, **k)
    print(f'  {dosya}: doku henüz yok, düz renk kullanılıyor')
    return mat_duz(ad, yedek_renk, 0.85, isik=isik, isik_guc=isik_guc)

def hazirla(doku):
    """Malzemeleri kurar (M sözlüğü) ve yaprak kartı atlasını okur."""
    global DOKU, KUTU
    DOKU = doku
    M.update({
        'zemin':  mat_doku('M_Zemin', 'zemin-ahsap'),
        'masa':   mat_doku('M_Masa', 'masa-ahsap'),
        'ahsap':  mat_doku('M_Ahsap', 'zemin-ahsap', carpan=(0.62, 0.50, 0.40), normal_guc=0.8),
        'koyu':   mat_doku('M_Ahsap_Koyu', 'zemin-ahsap', carpan=(0.30, 0.24, 0.20), normal_guc=0.8),
        'kursu':  mat_doku('M_Kursu', 'zemin-ahsap', carpan=(0.62, 0.42, 0.34), normal_guc=0.8),    # oyun kürsüsü: kızılımsı
        'duvar':  mat_yeni('M_Duvar', 'duvar-siva', SIVA_RENK, normal_guc=0.8),
        'tas':    mat_yeni('M_Tas_Blok', 'tas-blok', TAS_RENK, normal_guc=1.2),
        'tas_zemin': mat_yeni('M_Tas_Zemin', 'tas-altigen', TAS_ZEMIN_RENK, normal_guc=1.2),
        'dis_zemin': mat_yeni('M_Dis_Zemin', 'dis-zemin', (0.25, 0.23, 0.2), carpan=(0.42, 0.40, 0.38), normal_guc=1.0),   # dışarısı: koyu, göze batmasın
        'somine': mat_doku('M_Somine', 'somine-tas', normal_guc=1.3),
        'kul':    mat_doku('M_Kul', 'somine-tas', carpan=(0.18, 0.16, 0.15), normal_guc=1.0),
        'deri':   mat_doku('M_Deri', 'deri'),
        'hali':   mat_doku('M_Hali', 'hali', puruz=False, puruz_sabit=0.95, alfa=True),
        'post':   mat_doku('M_Post', 'post', puruz=False, puruz_sabit=0.95, alfa=True),
        'demir':  mat_duz('M_Demir', (0.06, 0.06, 0.07), 0.5, 0.85),
        'pirinc': mat_duz('M_Pirinc', (0.55, 0.35, 0.09), 0.32, 1.0),
        'kalay':  mat_duz('M_Kalay', (0.38, 0.36, 0.33), 0.42, 0.9),
        'mum':    mat_duz('M_Mum', (0.85, 0.72, 0.48), 0.45),
        'cam_y':  mat_duz('M_Cam_Yesil', (0.05, 0.20, 0.07), 0.12),
        'cam_k':  mat_duz('M_Cam_Kahve', (0.28, 0.09, 0.015), 0.12),
        'cam_s':  mat_duz('M_Cam_Saydam', (0.32, 0.40, 0.38), 0.08),
        'fener':  mat_duz('M_Fener_Cam', (0.12, 0.07, 0.03), 0.1, isik=(1.0, 0.52, 0.2), isik_guc=1.4),
        'bira':   mat_duz('M_Bira', (0.45, 0.22, 0.03), 0.15),
        'alev':   mat_duz('M_Alev', (0, 0, 0), 1.0, isik=(1.0, 0.45, 0.10), isik_guc=8.0),
        'alev_s': mat_duz('M_Alev_Somine', (0, 0, 0), 1.0, isik=(1.0, 0.36, 0.05), isik_guc=3.2),
        'kor':    mat_duz('M_Kor', (0.02, 0.01, 0.005), 0.9, isik=(1.0, 0.22, 0.03), isik_guc=2.5),
        'dovme':  mat_doku('M_Demir_Dovme', 'demir', metal=0.75),
        'cuval':  mat_doku('M_Cuval', 'cuval'),
        'saksi':  mat_doku('M_Saksi', 'saksi-toprak'),
        'sarmasik': mat_doku('M_Sarmasik', 'sarmasik', normal_guc=1.2),
        'yaprak': mat_doku('M_Yaprak', 'yaprak-kartlari', puruz=False, puruz_sabit=0.55, alfa=True),
        'kuru_ot': mat_doku('M_Kuru_Ot', 'yaprak-kartlari', carpan=(0.85, 0.62, 0.32), puruz=False, puruz_sabit=0.85, alfa=True),
        'kalkan1': mat_doku('M_Kalkan_1', 'kalkan-1', puruz=False, puruz_sabit=0.65, alfa=True),
        'kalkan2': mat_doku('M_Kalkan_2', 'kalkan-2', puruz=False, puruz_sabit=0.65, alfa=True),
        'tabela': mat_doku('M_Tabela', 'tabela', puruz=False, puruz_sabit=0.6, alfa=True),
        'sancak': mat_doku('M_Sancak', 'sancak', puruz=False, puruz_sabit=0.9, alfa=True),
        'harita': mat_doku('M_Harita', 'harita'),
        'pano':   mat_doku('M_Gorev_Panosu', 'gorev-panosu'),
        'kitap':  mat_doku('M_Kitaplar', 'kitap-sirtlari'),
        'celik':  mat_duz('M_Celik', (0.55, 0.56, 0.58), 0.28, 1.0),
        'kemik':  mat_duz('M_Kemik', (0.62, 0.55, 0.42), 0.6),
        'toprak': mat_duz('M_Toprak', (0.06, 0.045, 0.03), 1.0),
        'seramik': mat_duz('M_Seramik', (0.72, 0.67, 0.58), 0.35),
        'kagit':  mat_duz('M_Kagit', (0.78, 0.68, 0.48), 0.9),
        'kitap_d': mat_duz('M_Kitap_Deri', (0.22, 0.07, 0.05), 0.7),
        # Yeni dokular (promptlar/doku-han.txt) gelene kadar düz renk
        'perde':  mat_yeni('M_Perde', 'perde', (0.32, 0.05, 0.04), normal_guc=0.6),
        'pencere': mat_yeni('M_Pencere', 'pencere-kursun', (0.10, 0.16, 0.18), isik=(0.20, 0.30, 0.34), isik_guc=0.35, normal_guc=0.5),
        'cati':   mat_yeni('M_Cati', 'cati-sindira', (0.30, 0.20, 0.13), normal_guc=1.0),
        'karanlik': mat_duz('M_Karanlik', (0.03, 0.018, 0.01), 1.0, isik=(0.05, 0.025, 0.01), isik_guc=0.4),
        'gece':   mat_duz('M_Gece', (0.004, 0.005, 0.008), 1.0, isik=(0.010, 0.012, 0.018), isik_guc=0.6),
    })
    KUTU = json.load(open(os.path.join(DOKU, 'yaprak-kartlari.json'), encoding='utf-8'))['kutular']

def oran(dosya):
    """Resmin eni / boyu (parçanın ölçüsü resme uysun)."""
    im = resim(dosya); return im.size[0] / im.size[1]

# ───────── Parça kurucular ─────────
# Her parça kendi geçici "bmesh"inde kurulur, malzemesi ve pahı verilir, sonra nesnenin bmesh'ine eklenir.
_GECICI = bpy.data.meshes.new('_gecici')

def b_kutu(x0, x1, y0, y1, z0, z1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 if v.co.x < 0 else x1; v.co.y = y0 if v.co.y < 0 else y1; v.co.z = z0 if v.co.z < 0 else z1
    return bm

def _n(n):
    return max(3, int(round(n * DETAY)))

def _kalin(r):
    return r * (1 + STIL_KALIN * max(0.0, 1 - r / 0.06))

def _yumusat(h):
    """Torna profilindeki her iki halka arasına yumuşak (Catmull-Rom) bir ara halka ekler."""
    if DETAY <= 1 or len(h) < 3: return h
    out = []
    for i in range(len(h) - 1):
        p0, p1, p2, p3 = h[max(i - 1, 0)], h[i], h[i + 1], h[min(i + 2, len(h) - 1)]
        out.append(p1)
        out.append(tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * 0.5 + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * 0.25
                                + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * 0.125) for k in (0, 1)))
    out.append(h[-1])
    return [(z, max(r, 0.0005)) for z, r in out]

def b_silindir(x, y, r1, z0, z1, n=16, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=_n(n), radius1=r1, radius2=r1 if r2 is None else r2, depth=z1 - z0,
                          matrix=Matrix.Translation((x, y, (z0 + z1) / 2)))
    return bm

def b_arasi(p0, p1, r, n=8, r2=None):
    """İki nokta arasında silindir (eğik ayaklar, çubuklar, kütükler)."""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=_n(n), radius1=_kalin(r), radius2=_kalin(r if r2 is None else r2), depth=d.length)
    q = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) / 2) @ q, verts=bm.verts)
    return bm

def b_torna(x, y, halkalar, n=12, ust=True, alt=True):
    """Dönen gövde: [(z, yarıçap)] halkaları (şişe, kupa, mum, fıçı, tornalı ayak)."""
    n = _n(n); halkalar = [(z, _kalin(r)) for z, r in _yumusat(halkalar)]
    bm = bmesh.new(); Hs = []
    for z, r in halkalar:
        Hs.append([bm.verts.new((x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n), z)) for i in range(n)])
    for a, b in zip(Hs, Hs[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    if ust: bm.faces.new(Hs[-1])
    if alt: bm.faces.new(Hs[0][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def b_dilim(x, y, r0, r1, a0, a1, z0, z1, n=24):
    """Halka dilimi: merkez (x, y), yarıçap r0…r1, açı a0…a1 (derece, doğudan saat yönünün tersine). r0 = 0: pasta dilimi."""
    bm = bmesh.new(); n = _n(n)
    aci = [math.radians(a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    pts = [(x + r1 * math.cos(t), y + r1 * math.sin(t)) for t in aci]
    pts += [(x + r0 * math.cos(t), y + r0 * math.sin(t)) for t in reversed(aci)] if r0 > 0 else [(x, y)]
    alt = [bm.verts.new((px, py, z0)) for px, py in pts]
    ust = [bm.verts.new((px, py, z1)) for px, py in pts]
    bm.faces.new(list(reversed(alt))); bm.faces.new(ust)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((alt[i], alt[j], ust[j], ust[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def b_halka(r0, r1, z0, z1, n=48, x=0.0, y=0.0):
    """Yuvarlak çerçeve: iç yarıçap r0, dış r1 (üstü, dış ve iç yüzü)."""
    n = _n(n); bm = bmesh.new()
    def cember(r, z): return [bm.verts.new((x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n), z)) for i in range(n)]
    A, B, C, D = cember(r1, z0), cember(r1, z1), cember(r0, z1), cember(r0, z0)
    for a, b in ((A, B), (B, C), (C, D)):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def b_cokgen(pts, z0, z1):
    """Yukarıdan bakınca verilen (x, y) köşeli dik prizma (kemer dolgusu, eğri parçalar)."""
    bm = bmesh.new()
    alt = [bm.verts.new((px, py, z0)) for px, py in pts]
    ust = [bm.verts.new((px, py, z1)) for px, py in pts]
    bm.faces.new(list(reversed(alt))); bm.faces.new(ust)
    for i in range(len(pts)):
        j = (i + 1) % len(pts); bm.faces.new((alt[i], alt[j], ust[j], ust[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def b_dik_cokgen(pts, t0, t1):
    """Önden bakınca (u, z) köşeli, kalınlığı y = t0…t1 olan levha (kemerler, kapı üstleri). Yerel: u → x."""
    bm = b_cokgen(pts, t0, t1)
    for v in bm.verts: v.co.x, v.co.y, v.co.z = v.co.x, v.co.z, v.co.y
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def b_levha(x0, x1, z0, z1, y=0.0):
    """Önü +y'ye bakan ince düz yüzey (görsel yapıştırmak için)."""
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1))]
    f = bm.faces.new(vs); f.normal_update()
    if f.normal.y < 0: f.normal_flip()
    return bm

def dondur(bm, aci, merkez=(0, 0)):
    """Parçayı yukarıdan bakınca saat yönünde 'aci' derece döndürür."""
    cx, cy = merkez
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(cx, cy, 0), matrix=Matrix.Rotation(-math.radians(aci), 3, 'Z'))
    return bm

def tasi(bm, dx, dy, dz=0.0):
    bmesh.ops.translate(bm, verts=bm.verts, vec=(dx, dy, dz)); return bm

def P(hedef, bm, mi=0, pah=0.0, seg=1, yumusak=False):
    """Parçayı hedefe ekler. pah: keskin kenarları bu kadar yontar (m)."""
    for f in bm.faces:
        f.material_index = mi; f.smooth = yumusak
    pah *= STIL_PAH
    if pah > 0:
        kenar = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(35)]
        if kenar:
            bmesh.ops.bevel(bm, geom=kenar, offset=pah, segments=seg + (1 if DETAY > 1 else 0), affect='EDGES', profile=0.5, clamp_overlap=True)
    bm.to_mesh(_GECICI); bm.free()
    hedef.from_mesh(_GECICI)

def _egri(bm, konum):
    """Stil: el yapımı eğrilik (dünyadaki yere bağlı yumuşak gürültü; komşu parçalar birlikte kayar, yükseklik değişmez)."""
    k = Vector(konum)
    for v in bm.verts:
        g = noise.noise_vector((v.co + k) * 1.4)
        v.co.x += g.x * STIL_EGRI; v.co.y += g.y * STIL_EGRI

def nesne(ad, bm, mats, kol, konum=(0, 0, 0), aci=0.0, uv_ozel=None, koru=(), ic=None):
    """bmesh'ten nesne kurar. UV: her yüz baktığı yöne göre izdüşümlenir, malzemenin gerçek boyuna göre.
    koru: bu malzeme sıralarının UV'sine dokunulmaz. ic: duvara bağlı parçanın duvarı ('kuzey', 'guney', 'bati', 'dogu'):
    site, kameraya bakan duvarları ve onlara asılı parçaları buna göre alçaltır / gizler (userData.duvar)."""
    bm.normal_update()
    uvl = bm.loops.layers.uv.verify()
    olc = [UVS.get(m.name, 1.0) for m in mats]
    for f in bm.faces:
        if f.material_index in koru: continue
        n = f.normal; ax = max(range(3), key=lambda k: abs(n[k])); s = olc[min(f.material_index, len(olc) - 1)]
        su, sv = s if isinstance(s, tuple) else (s, s)
        for l in f.loops:
            p = l.vert.co + Vector(konum)
            u, v = (p.x, p.y) if ax == 2 else ((p.y, p.z) if ax == 0 else (p.x, p.z))
            l[uvl].uv = (u / su, v / sv)
    if uv_ozel: uv_ozel(bm, uvl)
    if STIL_EGRI > 0 and not ad.startswith(tuple(EGRI_YOK)): _egri(bm, konum)
    me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    if any(p.use_smooth for p in me.polygons):
        try: me.set_sharp_from_angle(angle=math.radians(40))
        except Exception: pass
    ob = bpy.data.objects.new(ad, me)
    ob.location = konum; ob.rotation_euler = (0, 0, -math.radians(aci)); kol.objects.link(ob)
    if ic is not None: ob['duvar'] = ic
    return ob

def bagla(cocuk, ebeveyn):
    bpy.context.view_layer.update()
    cocuk.parent = ebeveyn; cocuk.matrix_parent_inverse = ebeveyn.matrix_world.inverted()

def bos(ad, kol, x, y, z=0.0, boy=0.3, tur='PLAIN_AXES'):
    e = bpy.data.objects.new(ad, None); e.empty_display_type = tur; e.empty_display_size = boy
    e.location = (x, y, z); kol.objects.link(e); return e

def kopya(ad, sablon, kol, x, y, z=0.0, aci=0.0):
    ob = bpy.data.objects.new(ad, sablon.data); ob.location = (x, y, z); ob.rotation_euler = (0, 0, -math.radians(aci))
    kol.objects.link(ob); return ob

def uv_duz(mi_set, x0, x1, z0, z1):
    """Duvara asılan görsellerin UV'si: önden bakınca resim parçanın üstüne bir kez oturur (x → u, z → v)."""
    def f(bm, uvl):
        for fc in bm.faces:
            if fc.material_index in mi_set:
                for l in fc.loops:
                    l[uvl].uv = ((l.vert.co.x - x0) / (x1 - x0), (l.vert.co.z - z0) / (z1 - z0))
    return f

def isik_ekle(ad, kol, x, y, z, tur, ebeveyn=None):
    """Işık işareti (boş nesne). Işığın kendisini site / önizleme koyar."""
    e = bos(ad, kol, x, y, z, boy=0.08, tur='SPHERE')
    if ebeveyn: bagla(e, ebeveyn)
    ISIKLAR.append((ad, x, y, z, tur))
    return e

# ───────── Şablonlar: sandalye, tabure, koltuk ─────────
def sablonlar(kol, x0):
    """Sandalye, bar taburesi ve koltuk şablonları (önü kuzeyde, merkez oturağın ortası ve yer seviyesi).
    Malzeme 0: ahşap, 1: deri. Bütün kopyalar bunların bağlı kopyasıdır."""
    bm = bmesh.new()
    for sx in (-1, 1):
        P(bm, b_torna(sx * 0.23, 0.22, [(0, 0.020), (0.12, 0.026), (0.18, 0.019), (0.26, 0.026), (0.42, 0.024)], n=10), 0, yumusak=True)
        P(bm, b_arasi((sx * 0.23, -0.21, 0), (sx * 0.23, -0.27, 0.95), 0.024, n=10), 0, yumusak=True)
        P(bm, b_torna(sx * 0.23, -0.27, [(0.95, 0.026), (0.975, 0.03), (1.0, 0.012)], n=10, alt=False), 0, yumusak=True)
        P(bm, b_arasi((sx * 0.23, 0.22, 0.15), (sx * 0.23, -0.215, 0.15), 0.013, n=8), 0, yumusak=True)
    P(bm, b_arasi((-0.23, 0.22, 0.2), (0.23, 0.22, 0.2), 0.013, n=8), 0, yumusak=True)
    P(bm, b_arasi((-0.23, -0.215, 0.2), (0.23, -0.215, 0.2), 0.013, n=8), 0, yumusak=True)
    P(bm, b_kutu(-0.27, 0.27, -0.25, 0.26, 0.41, 0.45), 0, pah=0.01)
    P(bm, b_kutu(-0.245, 0.245, -0.22, 0.235, 0.45, 0.49), 1, pah=0.018, seg=2)
    P(bm, b_kutu(-0.23, 0.23, -0.29, -0.255, 0.84, 0.93), 0, pah=0.008)
    P(bm, b_kutu(-0.23, 0.23, -0.27, -0.245, 0.55, 0.59), 0, pah=0.006)
    for x in (-0.11, 0.0, 0.11):
        P(bm, b_arasi((x, -0.258, 0.59), (x, -0.272, 0.84), 0.011, n=6), 0, yumusak=True)
    sandalye = nesne('Sandalye_Sablon', bm, [M['ahsap'], M['deri']], kol, konum=(x0, 1.0, 0))

    bm = bmesh.new(); TR = 0.19
    P(bm, b_silindir(0, 0, TR, 0.70, 0.75, n=24), 0, pah=0.01)
    P(bm, b_silindir(0, 0, TR - 0.02, 0.75, 0.77, n=24), 1, pah=0.008, yumusak=True)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        P(bm, b_arasi((0.11 * math.cos(a), 0.11 * math.sin(a), 0.70), (0.2 * math.cos(a), 0.2 * math.sin(a), 0.0), 0.018, n=8), 0, yumusak=True)
        b = math.radians(135 + 90 * i)
        P(bm, b_arasi((0.17 * math.cos(a), 0.17 * math.sin(a), 0.26), (0.17 * math.cos(b), 0.17 * math.sin(b), 0.26), 0.011, n=6), 0, yumusak=True)
    tabure = nesne('Tabure_Sablon', bm, [M['ahsap'], M['deri']], kol, konum=(x0, -1.0, 0))

    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            P(bm, b_torna(sx * 0.32, sy * 0.32, [(0, 0.025), (0.09, 0.03)], n=10), 0, yumusak=True)
    P(bm, b_kutu(-0.4, 0.4, -0.38, 0.4, 0.09, 0.40), 1, pah=0.04, seg=3)
    P(bm, b_kutu(-0.27, 0.27, -0.2, 0.38, 0.40, 0.50), 1, pah=0.045, seg=3)
    P(bm, b_kutu(-0.4, 0.4, -0.4, -0.2, 0.40, 1.02), 1, pah=0.06, seg=3)
    for sx in (-1, 1):
        P(bm, b_kutu(sx * 0.4 - (0.13 if sx > 0 else 0), sx * 0.4 + (0 if sx > 0 else 0.13), -0.25, 0.4, 0.40, 0.66), 1, pah=0.05, seg=3)
    koltuk = nesne('Koltuk_Sablon', bm, [M['ahsap'], M['deri']], kol, konum=(x0, -3.0, 0))
    return sandalye, tabure, koltuk

# ───────── Küçük eşyalar ─────────
def mum_kur(no, x, y, z, kol, ebeveyn=None, ad=None):
    """Pirinç şamdan, mum (erimiş tepe, damlalar), fitil; alev ayrı nesne (site titretir). Işık işareti döner."""
    ad = ad or f'Mum_{no}'
    bm = bmesh.new()
    P(bm, b_torna(0, 0, [(0, 0.05), (0.004, 0.058), (0.010, 0.060), (0.013, 0.056), (0.012, 0.045), (0.016, 0.03), (0.03, 0.027), (0.034, 0.03)], n=16), 0, yumusak=True)
    h = 0.11 + sus.uniform(0, 0.07)
    P(bm, b_torna(0, 0, [(0.02, 0.022), (h * 0.5, 0.0225), (h, 0.0215), (h + 0.006, 0.019), (h + 0.002, 0.012), (h - 0.002, 0.006)], n=14), 1, yumusak=True)
    for _ in range(3):
        a = sus.uniform(0, 2 * math.pi); boy = sus.uniform(0.015, 0.05)
        P(bm, b_arasi((0.021 * math.cos(a), 0.021 * math.sin(a), h + 0.004), (0.0225 * math.cos(a), 0.0225 * math.sin(a), h - boy), 0.0045, n=6, r2=0.0065), 1, yumusak=True)
    P(bm, b_arasi((0, 0, h - 0.004), (0.002, 0, h + 0.012), 0.0012, n=4), 2)
    ob = nesne(ad, bm, [M['pirinc'], M['mum'], M['demir']], kol, konum=(x, y, z))
    ust = h + 0.008
    bm = bmesh.new(); P(bm, b_torna(0, 0, [(0, 0.003), (0.008, 0.008), (0.02, 0.0105), (0.034, 0.008), (0.048, 0.004), (0.06, 0.0005)], n=10), 0, yumusak=True)
    alev = nesne(f'alev_mum_{no}', bm, [M['alev']], kol, konum=(x, y, z + ust))
    isaret = isik_ekle(f'isik_mum_{no}', kol, x, y, z + ust + 0.06, 'mum')
    bagla(alev, ob); bagla(isaret, ob)
    if ebeveyn: bagla(ob, ebeveyn)
    return ob

def yeni_mum(x, y, z, kol, ebeveyn=None):
    MUM_NO[0] += 1
    return mum_kur(MUM_NO[0], x, y, z, kol, ebeveyn)

def kupa_kur(bm, x, y, z, aci=0):
    s = KUPA_OLCEK
    P(bm, b_torna(x, y, [(z, 0.04 * s), (z + 0.01 * s, 0.042 * s), (z + 0.11 * s, 0.045 * s), (z + 0.12 * s, 0.047 * s)], n=14, ust=False), 0, yumusak=True)
    P(bm, b_torna(x, y, [(z + 0.10 * s, 0.043 * s)], n=14, alt=False), 1)
    a = math.radians(aci); c, si = math.cos(a) * s, math.sin(a) * s
    P(bm, b_arasi((x + 0.045 * c, y + 0.045 * si, z + 0.09 * s), (x + 0.075 * c, y + 0.075 * si, z + 0.06 * s), 0.009 * s, n=6), 0, yumusak=True)
    P(bm, b_arasi((x + 0.075 * c, y + 0.075 * si, z + 0.06 * s), (x + 0.045 * c, y + 0.045 * si, z + 0.025 * s), 0.009 * s, n=6), 0, yumusak=True)

def sise_kur(bm, x, y, z, h=None, r=None, mi=2):
    h = h or sus.uniform(0.22, 0.32); r = (r or sus.uniform(0.032, 0.045)) * SISE_OLCEK
    P(bm, b_torna(x, y, [(z, r * 0.9), (z + 0.005, r), (z + h * 0.62, r), (z + h * 0.75, r * 0.45), (z + h * 0.95, 0.013), (z + h, 0.014)], n=10), mi, yumusak=True)

def tabak_kur(bm, x, y, z, r=0.13, mi=0):
    P(bm, b_torna(x, y, [(z, r * 0.55), (z + 0.008, r * 0.62), (z + 0.016, r), (z + 0.02, r * 1.02)], n=18, ust=True), mi, yumusak=True)

def masa_govde(ad, r, kol, konum, masa_z=0.80):
    """Yuvarlak masa: pahlı kalın tabla, demir çember, ortada sekizgen ayak, dört kollu taban ve dört destek kolu."""
    bm = bmesh.new()
    P(bm, b_silindir(0, 0, r, masa_z - 0.08, masa_z, n=64), 0, pah=0.015, seg=2)
    P(bm, b_silindir(0, 0, r + 0.006, masa_z - 0.065, masa_z - 0.035, n=64), 2)
    ar = 0.13 if r > 0.9 else 0.09
    P(bm, b_silindir(0, 0, ar, 0.10, masa_z - 0.08, n=8), 1, pah=0.01)
    for i in range(4):
        b = b_kutu(0, r * 0.72, -0.05, 0.05, 0.0, 0.10); dondur(b, 45 + 90 * i); P(bm, b, 1, pah=0.012)
        a = math.radians(45 + 90 * i)
        P(bm, b_arasi((ar * math.cos(a), ar * math.sin(a), 0.42), (r * 0.62 * math.cos(a), r * 0.62 * math.sin(a), masa_z - 0.085), 0.025, n=8), 1, yumusak=True)
    return nesne(ad + '_Govde', bm, [M['masa'], M['ahsap'], M['demir']], kol, konum=konum)

def uzun_masa_govde(ad, boy, en, kol, konum, aci=0.0, masa_z=0.80):
    """Uzun ziyafet masası (yerel: boyu x boyunca): kalın tabla, iki yanda çapraz ayak, ortada kiriş."""
    bm = bmesh.new()
    P(bm, b_kutu(-boy / 2, boy / 2, -en / 2, en / 2, masa_z - 0.08, masa_z), 0, pah=0.015, seg=2)
    for s in (-1, 1):
        x = s * (boy / 2 - 0.3)
        for d in (-1, 1):
            P(bm, b_arasi((x - 0.18 * d, -en / 2 + 0.1, 0.0), (x + 0.18 * d, en / 2 - 0.1, masa_z - 0.08), 0.045, n=8), 1, yumusak=True)
        P(bm, b_kutu(x - 0.06, x + 0.06, -en / 2 + 0.05, en / 2 - 0.05, 0.0, 0.08), 1, pah=0.01)
    P(bm, b_kutu(-boy / 2 + 0.3, boy / 2 - 0.3, -0.05, 0.05, 0.32, 0.42), 1, pah=0.01)
    return nesne(ad, bm, [M['masa'], M['ahsap']], kol, konum=konum, aci=aci)

def bank_kur(ad, boy, kol, konum, aci=0.0):
    """Uzun bank (yerel: boyu x boyunca)."""
    bm = bmesh.new()
    P(bm, b_kutu(-boy / 2, boy / 2, -0.17, 0.17, 0.40, 0.46), 0, pah=0.012)
    for s in (-1, 1):
        x = s * (boy / 2 - 0.2)
        P(bm, b_kutu(x - 0.05, x + 0.05, -0.15, 0.15, 0.0, 0.40), 0, pah=0.008)
    P(bm, b_kutu(-boy / 2 + 0.2, boy / 2 - 0.2, -0.03, 0.03, 0.12, 0.18), 0, pah=0.005)
    return nesne(ad, bm, [M['ahsap']], kol, konum=konum, aci=aci)

def fici(ad, kol, x, y, r=0.3, h=0.9, aci=0, z=0.0, yatik=False):
    """Fıçı: tahta gövde, demir çemberler, kapak. yatik: yan yatırılmış (ekseni yerel x boyunca)."""
    bm = bmesh.new()
    P(bm, b_torna(0, 0, [(0, r * 0.86), (h * 0.15, r * 0.96), (h * 0.5, r), (h * 0.85, r * 0.96), (h, r * 0.86)], n=24), 0, yumusak=True)
    for zz in (h * 0.1, h * 0.3, h * 0.7, h * 0.9):
        rr = r * (0.94 if zz in (h * 0.1, h * 0.9) else 0.99) + 0.006
        P(bm, b_torna(0, 0, [(zz - 0.02, rr), (zz + 0.02, rr)], n=24, ust=False, alt=False), 1, yumusak=True)
    P(bm, b_silindir(0, 0, r * 0.8, h - 0.015, h + 0.005, n=24), 2)
    if yatik:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'))
        tasi(bm, -h / 2, 0, r)
    return nesne(ad, bm, [M['ahsap'], M['demir'], M['masa']], kol, konum=(x, y, z), aci=aci)

def sandik(ad, kol, x, y, z=0.0, en=0.6, boy=0.6, h=0.55, aci=0.0):
    bm = bmesh.new()
    P(bm, b_kutu(-en / 2, en / 2, -boy / 2, boy / 2, 0, h), 0, pah=0.012)
    for zz in (0.0, h - 0.05):
        P(bm, b_kutu(-en / 2 - 0.01, en / 2 + 0.01, -boy / 2 - 0.01, boy / 2 + 0.01, zz, zz + 0.05), 1, pah=0.006)
    return nesne(ad, bm, [M['ahsap'], M['koyu']], kol, konum=(x, y, z), aci=aci)

def cuval_kur(bm, x, y, z, a, mi=0):
    b = b_torna(0, 0, [(0, 0.17), (0.12, 0.24), (0.32, 0.22), (0.45, 0.1), (0.52, 0.04), (0.56, 0.05)], n=14)
    for v in b.verts: v.co.y *= 0.75
    dondur(b, a); tasi(b, x, y, z); P(bm, b, mi, yumusak=True)

# ───────── Işıklı parçalar ─────────
def sarkit(ad, x, y, z_alt, kol, tavan_z):
    """Zincirle sarkan altıgen dövme demir fener: külah, altı dikme, içten parlayan camlar, mum ve alev."""
    bm = bmesh.new()
    P(bm, b_arasi((0, 0, z_alt + 0.46), (0, 0, tavan_z), 0.007, n=4), 0)
    P(bm, b_torna(0, 0, [(z_alt + 0.44, 0.0), (z_alt + 0.46, 0.028), (z_alt + 0.5, 0.02)], n=8, alt=False), 0)
    P(bm, b_silindir(0, 0, 0.14, z_alt + 0.32, z_alt + 0.44, n=3, r2=0.025), 0, pah=0.005)
    P(bm, b_silindir(0, 0, 0.14, z_alt, z_alt + 0.035, n=3), 0, pah=0.004)
    for i in range(6):
        a = math.radians(60 * i)
        P(bm, b_arasi((0.125 * math.cos(a), 0.125 * math.sin(a), z_alt + 0.03), (0.125 * math.cos(a), 0.125 * math.sin(a), z_alt + 0.33), 0.009, n=4), 0)
    P(bm, b_silindir(0, 0, 0.118, z_alt + 0.035, z_alt + 0.32, n=3), 1)
    P(bm, b_silindir(0, 0, 0.02, z_alt + 0.035, z_alt + 0.12, n=8), 2)
    ob = nesne(ad, bm, [M['dovme'], M['fener'], M['mum']], kol, konum=(x, y, 0))
    bm = bmesh.new(); P(bm, b_torna(0, 0, [(0, 0.004), (0.01, 0.009), (0.025, 0.007), (0.04, 0.001)], n=8), 0, yumusak=True)
    bagla(nesne('alev_' + ad.lower(), bm, [M['alev']], kol, konum=(x, y, z_alt + 0.12)), ob)
    isik_ekle('isik_' + ad.lower(), kol, x, y, z_alt + 0.18, 'sarkit', ob)
    return ob

def aplik(ad, kol, x, y, yon, z=1.8, ic=None):
    """Duvar feneri: duvara çakılı plaka, kol, fener (cam, külah, mum). yon: fenerin odaya baktığı yön (kuzeyden saat
    yönünde derece). z: fenerin ortası."""
    d = z - 1.8
    bm = bmesh.new()
    P(bm, b_kutu(-0.05, 0.05, -0.02, 0.0, 1.7 + d, 2.05 + d), 0)
    P(bm, b_arasi((0, 0, 1.95 + d), (0, 0.22, 1.95 + d), 0.012, n=6), 0, yumusak=True)
    P(bm, b_arasi((0, 0, 1.78 + d), (0, 0.18, 1.95 + d), 0.008, n=6), 0, yumusak=True)
    P(bm, b_silindir(0, 0.22, 0.075, 1.72 + d, 1.74 + d, n=12), 0)
    P(bm, b_silindir(0, 0.22, 0.065, 1.74 + d, 1.90 + d, n=12), 1, yumusak=True)
    P(bm, b_silindir(0, 0.22, 0.08, 1.90 + d, 1.97 + d, n=12, r2=0.02), 0)
    P(bm, b_torna(0, 0.22, [(1.74 + d, 0.018), (1.80 + d, 0.018)], n=8), 2)
    ob = nesne(ad, bm, [M['dovme'], M['fener'], M['mum']], kol, konum=(x, y, 0), aci=yon, ic=ic)
    a = math.radians(yon); fx, fy = x + 0.22 * math.sin(a), y + 0.22 * math.cos(a)
    bm = bmesh.new(); P(bm, b_torna(0, 0, [(0, 0.005), (0.01, 0.009), (0.025, 0.006), (0.04, 0.001)], n=8), 0, yumusak=True)
    bagla(nesne('alev_' + ad.lower(), bm, [M['alev']], kol, konum=(fx, fy, 1.80 + d)), ob)
    isik_ekle('isik_' + ad.lower(), kol, fx, fy, 1.84 + d, 'aplik', ob)
    return ob

def avize_cember(ad, kol, x, y, az, ar, n_mum, tavan_z):
    """Şamdanlı avize: tavandan zincirle inen dövme demir çember (araba tekerleği gibi, ortası açık), üstünde mumlar."""
    bm = bmesh.new(); N = 32
    nokt = [(ar * math.cos(2 * math.pi * i / N), ar * math.sin(2 * math.pi * i / N)) for i in range(N)]
    for i in range(N):
        (x0, y0), (x1, y1) = nokt[i], nokt[(i + 1) % N]
        P(bm, b_arasi((x0, y0, az), (x1, y1, az), 0.03, n=8), 0, yumusak=True)                     # dış çember
        P(bm, b_arasi((x0 * 0.92, y0 * 0.92, az - 0.06), (x1 * 0.92, y1 * 0.92, az - 0.06), 0.014, n=6), 0, yumusak=True)
    for i in range(4):                                                                             # zincirler
        a = 2 * math.pi * (i + 0.5) / 4
        P(bm, b_arasi((ar * math.cos(a), ar * math.sin(a), az), (0, 0, az + 1.1), 0.007, n=4), 0)
    P(bm, b_torna(0, 0, [(az + 1.08, 0.05), (az + 1.12, 0.07), (az + 1.18, 0.03)], n=10), 0, yumusak=True)
    P(bm, b_arasi((0, 0, az + 1.18), (0, 0, tavan_z), 0.012, n=4), 0)
    mumlar = []
    for i in range(n_mum):
        a = 2 * math.pi * i / n_mum; cx, cy = ar * math.cos(a), ar * math.sin(a)
        P(bm, b_torna(cx, cy, [(az, 0.045), (az + 0.015, 0.05), (az + 0.025, 0.03)], n=12), 0, yumusak=True)
        h = sus.uniform(0.1, 0.18)
        P(bm, b_torna(cx, cy, [(az + 0.025, 0.022), (az + 0.025 + h, 0.022), (az + 0.031 + h, 0.018), (az + 0.027 + h, 0.01)], n=10), 1, yumusak=True)
        mumlar.append((cx, cy, az + 0.033 + h))
    ob = nesne(ad, bm, [M['dovme'], M['mum']], kol, konum=(x, y, 0))
    for i, (cx, cy, cz) in enumerate(mumlar):
        bm = bmesh.new(); P(bm, b_torna(0, 0, [(0, 0.003), (0.008, 0.008), (0.02, 0.01), (0.034, 0.007), (0.05, 0.0005)], n=8), 0, yumusak=True)
        bagla(nesne(f'alev_{ad.lower()}_{i + 1}', bm, [M['alev']], kol, konum=(x + cx, y + cy, cz)), ob)
    isik_ekle('isik_' + ad.lower(), kol, x, y, az + 0.15, 'avize', ob)
    return ob

# ───────── Duvar süsleri (yerel düzen: duvar yüzü y = 0, parça +y yönünde odaya bakar) ─────────
def duvar_parcasi(ad, kol, x, y, yon, kur, mats, uv=None, z=0.0, koru=(), ic=None):
    bm = bmesh.new(); kur(bm); return nesne(ad, bm, mats, kol, konum=(x, y, z), aci=yon, uv_ozel=uv, koru=koru, ic=ic)

def kalkan_kilic(zc, r, kalkan):
    """Çapraz iki kılıç ve önlerinde yuvarlak kalkan. Malzeme: 0 çelik, 1 demir, 2 deri, 3 ahşap, 4 kalkan resmi."""
    def kur(bm):
        for aci in (-34, 34):
            for bb, mi in ((b_kutu(-0.022, 0.022, 0.02, 0.03, zc - 0.33, zc + 0.5), 0), (b_kutu(-0.13, 0.13, 0.012, 0.038, zc - 0.36, zc - 0.33), 1),
                           (b_kutu(-0.018, 0.018, 0.014, 0.036, zc - 0.52, zc - 0.36), 2), (b_kutu(-0.03, 0.03, 0.01, 0.04, zc - 0.57, zc - 0.52), 1)):
                bmesh.ops.rotate(bb, verts=bb.verts, cent=(0, 0, zc), matrix=Matrix.Rotation(math.radians(aci), 3, 'Y')); P(bm, bb, mi, pah=0.003)
        P(bm, b_arasi((0, 0.04, zc), (0, 0.085, zc), r * 0.99, n=32), 3)
        P(bm, b_arasi((0, 0.085, zc), (0, 0.088, zc), r, n=32), 4)
        P(bm, b_arasi((0, 0.088, zc), (0, 0.13, zc), r * 0.2, n=16, r2=r * 0.07), 1, yumusak=True)
    return kur, uv_duz({4}, -r, r, zc - r, zc + r), [M['celik'], M['dovme'], M['deri'], M['ahsap'], M[kalkan]]

def kalkan_yuvarlak(zc, r, kalkan):
    """Duvara asılı yuvarlak kalkan (boyalı yüz, ortada demir tümsek). Malzeme: 0 ahşap, 1 demir, 2 resim."""
    def kur(bm):
        P(bm, b_arasi((0, 0, zc), (0, 0.045, zc), r * 0.99, n=32), 0)
        P(bm, b_arasi((0, 0.045, zc), (0, 0.048, zc), r, n=32), 2)
        P(bm, b_arasi((0, 0.048, zc), (0, 0.085, zc), r * 0.2, n=16, r2=r * 0.07), 1, yumusak=True)
    return kur, uv_duz({2}, -r, r, zc - r, zc + r), [M['ahsap'], M['dovme'], M[kalkan]]

def tabela(TW, TZ, zincir_z):
    """Asılı tabela: ahşap gövde, iki yüzünde resim, iki zincir. TZ: alt kenar."""
    TH = TW / oran('tabela.png')
    def kur(bm):
        P(bm, b_kutu(-TW / 2 + 0.06, TW / 2 - 0.06, -0.015, 0.015, TZ + 0.05, TZ + TH - 0.05), 0)
        P(bm, b_levha(-TW / 2, TW / 2, TZ, TZ + TH, 0.018), 2)
        b = b_levha(-TW / 2, TW / 2, TZ, TZ + TH, 0.018); dondur(b, 180); P(bm, b, 3)
        for s in (-1, 1):
            P(bm, b_arasi((s * TW * 0.38, 0, TZ + TH - 0.03), (s * TW * 0.38, 0, zincir_z), 0.006, n=4), 1)
    def uv(bm, uvl):
        for fc in bm.faces:
            if fc.material_index in (2, 3):
                for l in fc.loops:
                    u = (l.vert.co.x + TW / 2) / TW
                    l[uvl].uv = (u if fc.material_index == 2 else 1 - u, (l.vert.co.z - TZ) / TH)
    return kur, uv, [M['koyu'], M['dovme'], M['tabela'], M['tabela']]

def pano(PW, PZ):
    """Görev panosu: ahşap çerçeve, iğnelenmiş kâğıtlar resmi, küçük çatı."""
    PH = PW / oran('gorev-panosu.jpg')
    def kur(bm):
        P(bm, b_kutu(-PW / 2, PW / 2, 0.0, 0.035, PZ, PZ + PH), 0)
        P(bm, b_levha(-PW / 2, PW / 2, PZ, PZ + PH, 0.036), 1)
        for x0, x1, z0, z1 in ((-PW / 2 - 0.06, PW / 2 + 0.06, PZ - 0.06, PZ), (-PW / 2 - 0.06, PW / 2 + 0.06, PZ + PH, PZ + PH + 0.06),
                               (-PW / 2 - 0.06, -PW / 2, PZ - 0.06, PZ + PH + 0.06), (PW / 2, PW / 2 + 0.06, PZ - 0.06, PZ + PH + 0.06)):
            P(bm, b_kutu(x0, x1, 0.0, 0.07, z0, z1), 0, pah=0.008)
        for s in (-1, 1):
            b = b_kutu(min(0, s * (PW / 2 + 0.15)), max(0, s * (PW / 2 + 0.15)), 0.0, 0.24, PZ + PH + 0.06, PZ + PH + 0.1)
            bmesh.ops.rotate(b, verts=b.verts, cent=(0, 0, PZ + PH + 0.08), matrix=Matrix.Rotation(math.radians(-s * 22), 3, 'Y')); P(bm, b, 0, pah=0.006)
    return kur, uv_duz({1}, -PW / 2, PW / 2, PZ, PZ + PH), [M['koyu'], M['pano']], PH

def harita(HW, HZ):
    HH = HW / oran('harita.jpg')
    def kur(bm):
        P(bm, b_levha(-HW / 2, HW / 2, HZ, HZ + HH, 0.03), 1)
        P(bm, b_kutu(-HW / 2, HW / 2, 0.0, 0.028, HZ, HZ + HH), 0)
        for x0, x1, z0, z1 in ((-HW / 2 - 0.06, HW / 2 + 0.06, HZ + HH, HZ + HH + 0.06), (-HW / 2 - 0.06, HW / 2 + 0.06, HZ - 0.06, HZ),
                               (-HW / 2 - 0.06, -HW / 2, HZ - 0.06, HZ + HH + 0.06), (HW / 2, HW / 2 + 0.06, HZ - 0.06, HZ + HH + 0.06)):
            P(bm, b_kutu(x0, x1, 0.0, 0.055, z0, z1), 0, pah=0.008)
    return kur, uv_duz({1}, -HW / 2, HW / 2, HZ, HZ + HH), [M['koyu'], M['harita']]

def sancak(z_ust, SW=0.76, kumas='sancak'):
    """Direkli kumaş sancak; kumaş hafif dalgalı. Malzeme: 0 ahşap, 1 demir, 2 kumaş (koru={2})."""
    SH = SW / oran('sancak.png')
    def kur(bm):
        P(bm, b_arasi((-SW / 2 - 0.07, 0.08, z_ust + 0.01), (SW / 2 + 0.07, 0.08, z_ust + 0.01), 0.02, n=8), 0, yumusak=True)
        for s in (-1, 1):
            P(bm, b_arasi((s * (SW / 2 + 0.07), 0.08, z_ust + 0.01), (s * (SW / 2 + 0.11), 0.08, z_ust + 0.01), 0.03, n=8), 1)
        b = bmesh.new(); uvl = b.loops.layers.uv.new('UVMap'); N_ = 10; sat = []
        for j in range(N_ + 1):
            z = z_ust - SH * j / N_; dy = 0.07 + 0.012 * math.sin(j * 1.3)
            sat.append([b.verts.new((-SW / 2, dy, z)), b.verts.new((SW / 2, dy, z))])
        for j in range(N_):
            f = b.faces.new((sat[j + 1][0], sat[j + 1][1], sat[j][1], sat[j][0]))
            for l in f.loops:
                l[uvl].uv = ((l.vert.co.x + SW / 2) / SW, (l.vert.co.z - (z_ust - SH)) / SH)
        P(bm, b, 2)
    return kur, [M['koyu'], M['dovme'], M[kumas]], SH

def perde(bm, x0, x1, z0, z1, y=0.0, kivrim=6, derin=0.06, mi=0):
    """Dalgalı kumaş perde (yerel: genişliği x boyunca, düzlemi y'de). Kıvrımlar sinüs."""
    N = kivrim * 6; ust, alt = [], []
    for i in range(N + 1):
        t = i / N; x = x0 + (x1 - x0) * t; dy = y + derin * math.sin(t * kivrim * 2 * math.pi)
        alt.append(bm.verts.new((x, dy, z0))); ust.append(bm.verts.new((x, dy, z1)))
    for i in range(N):
        f = bm.faces.new((alt[i], alt[i + 1], ust[i + 1], ust[i])); f.material_index = mi; f.smooth = True

def odun(bm):
    """Duvara dayalı üç sıra kütük (yerel: duvar y = 0, kütükler y boyunca)."""
    for sira, adet in enumerate((5, 4, 3)):
        for i in range(adet):
            x = 0.07 + 0.14 * i + 0.07 * sira; z = 0.07 + 0.125 * sira
            P(bm, b_arasi((x, 0.0, z), (x + sus.uniform(-0.02, 0.02), 0.5, z), 0.066, n=10), 0, yumusak=True)

def trofe(z):
    """Boynuzlu av hatırası: duvara çakılı yuvarlak ahşap levha, kemik boynuzlar. Malzeme: 0 koyu ahşap, 1 kemik."""
    def kur(bm):
        P(bm, b_arasi((0, 0, z), (0, 0.04, z), 0.18, n=24), 0, pah=0.008)
        for s in (-1, 1):
            P(bm, b_arasi((s * 0.05, 0.08, z + 0.05), (s * 0.35, 0.12, z + 0.25), 0.02, n=8, r2=0.012), 1, yumusak=True)
            P(bm, b_arasi((s * 0.22, 0.1, z + 0.16), (s * 0.3, 0.16, z + 0.3), 0.012, n=6, r2=0.005), 1, yumusak=True)
            P(bm, b_arasi((s * 0.3, 0.11, z + 0.22), (s * 0.48, 0.13, z + 0.27), 0.012, n=6, r2=0.005), 1, yumusak=True)
            P(bm, b_arasi((s * 0.12, 0.09, z + 0.1), (s * 0.18, 0.15, z - 0.04), 0.01, n=6, r2=0.004), 1, yumusak=True)
    return kur, [M['koyu'], M['kemik']]

def aski(bm):
    """Silah askısı: mızraklar, balta, küçük kalkan (yerel: duvar y = 0). Malzeme: 0 koyu, 1 çelik, 2 kalkan resmi, 3 ahşap."""
    P(bm, b_kutu(-0.6, 0.6, 0.0, 0.05, 1.75, 1.85), 0, pah=0.006); P(bm, b_kutu(-0.6, 0.6, 0.0, 0.05, 0.25, 0.35), 0, pah=0.006)
    for x in (-0.42, -0.2):
        P(bm, b_arasi((x, 0.09, 0.3), (x, 0.09, 2.05), 0.017, n=8), 0, yumusak=True)
        P(bm, b_arasi((x, 0.09, 2.05), (x, 0.09, 2.3), 0.03, n=6, r2=0.002), 1)
    P(bm, b_arasi((0.42, 0.09, 0.3), (0.42, 0.09, 1.75), 0.02, n=8), 0, yumusak=True)
    P(bm, b_kutu(0.43, 0.62, 0.075, 0.105, 1.45, 1.75), 1, pah=0.004)
    P(bm, b_arasi((0.08, 0.06, 1.1), (0.08, 0.1, 1.1), 0.21, n=24), 3)
    P(bm, b_arasi((0.08, 0.1, 1.1), (0.08, 0.103, 1.1), 0.215, n=24), 2)
ASKI_UV = lambda: uv_duz({2}, 0.08 - 0.215, 0.08 + 0.215, 1.1 - 0.215, 1.1 + 0.215)

def obek(bm, x, y, z, r, mi):
    P(bm, b_torna(x, y, [(z - r * 0.75, r * 0.12), (z - r * 0.45, r * 0.85), (z, r), (z + r * 0.45, r * 0.8), (z + r * 0.75, r * 0.12)], n=10), mi, yumusak=True)

def b_kart(hucre, boy, ust, yon, egim, sarkan=True, ters=False):
    """Yaprak kartı (saydam dal resmi). hucre: atlas hücresi (0–2 sarmaşık, 3–5 pothos, 6–8 eğrelti)."""
    u0, v0, u1, v1 = KUTU[hucre]
    w = boy * (u1 - u0) / (v1 - v0)
    vu, va = (v0, v1) if not ters else (v1, v0)
    if sarkan: P_ = [(-w / 2, 0, 0, u0, va), (w / 2, 0, 0, u1, va), (w / 2, 0, -boy, u1, vu), (-w / 2, 0, -boy, u0, vu)]
    else:      P_ = [(-w / 2, 0, 0, u0, vu), (w / 2, 0, 0, u1, vu), (w / 2, 0, boy, u1, va), (-w / 2, 0, boy, u0, va)]
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap')
    f = bm.faces.new([bm.verts.new(p[:3]) for p in P_])
    for l, p in zip(f.loops, P_): l[uvl].uv = (p[3], p[4])
    T = Matrix.Translation(ust) @ Matrix.Rotation(-math.radians(yon), 4, 'Z') @ Matrix.Rotation(math.radians(egim) * (1 if sarkan else -1), 4, 'X')
    bmesh.ops.transform(bm, matrix=T, verts=bm.verts)
    return bm

def saksi(ad, kol, x, y, boy=1.3, r=0.28, z0=0.0, kart=10):
    """Saksı bitkisi: pişmiş toprak saksı, toprak, yaprak öbeği, yukarı büyüyen eğrelti ve sarkan pothos."""
    bm = bmesh.new()
    P(bm, b_torna(0, 0, [(0, r * 0.72), (r * 1.3, r), (r * 1.38, r * 1.08), (r * 1.55, r * 1.08), (r * 1.55, r * 1.0)], n=16, ust=False), 0, yumusak=True)
    P(bm, b_silindir(0, 0, r * 0.98, r * 1.3, r * 1.36, n=16), 1)
    g = boy - r * 1.4
    obek(bm, 0, 0, r * 1.4 + g * 0.3, max(r * 0.8, g * 0.28), 2)
    for i in range(kart):
        a = 360 * i / kart + sus.uniform(-15, 15); ra = math.radians(a)
        if i % 3 == 2:
            P(bm, b_kart(sus.choice((3, 4, 5)), sus.uniform(0.6, 1.0) * max(g, 0.25) * 0.8, (r * math.sin(ra), r * math.cos(ra), r * 1.5), a, sus.uniform(10, 25)), 3)
        else:
            P(bm, b_kart(sus.choice((6, 7, 8)), sus.uniform(0.8, 1.1) * max(g, 0.25), (0.3 * r * math.sin(ra), 0.3 * r * math.cos(ra), r * 1.35), a, sus.uniform(15, 45), sarkan=False), 3)
    return nesne(ad, bm, [M['saksi'], M['toprak'], M['sarmasik'], M['yaprak']], kol, konum=(x, y, z0), koru={3})

def cicek_kutusu(ad, kol, x, y, z, boy, yon=0.0, kart=8):
    """Korkuluğa asılı uzun çiçek kutusu, kenarından sarkan sarmaşıklar (yerel: boyu x boyunca, dışı +y)."""
    bm = bmesh.new()
    P(bm, b_kutu(-boy / 2, boy / 2, -0.12, 0.12, 0.0, 0.2), 0, pah=0.01)
    P(bm, b_kutu(-boy / 2 + 0.03, boy / 2 - 0.03, -0.1, 0.1, 0.17, 0.21), 1)
    for i in range(3):
        obek(bm, -boy / 3 + i * boy / 3, 0, 0.25, 0.13, 2)
    for i in range(kart):
        xx = -boy / 2 + 0.1 + (boy - 0.2) * i / max(1, kart - 1)
        P(bm, b_kart(sus.choice((0, 1, 2, 3)), sus.uniform(0.4, 0.8), (xx, 0.12, 0.2), sus.uniform(-25, 25), sus.uniform(5, 20)), 3)
    return nesne(ad, bm, [M['ahsap'], M['toprak'], M['sarmasik'], M['yaprak']], kol, konum=(x, y, z), aci=yon, koru={3})

def sarmasik(ad, kol, x, y, z0, z1, disari):
    """Direğe sarılan sarmaşık: direğin çevresinde sarmal yaprak öbekleri ve aralardan sarkan dallar."""
    bm = bmesh.new(); z, a = z0, sus.uniform(0, 6.28)
    while z < z1:
        r = sus.uniform(0.045, 0.07)
        obek(bm, 0.19 * math.cos(a), 0.19 * math.sin(a), z, r, 0)
        if sus.random() < 0.85:
            P(bm, b_kart(sus.choice((0, 1, 2)), sus.uniform(0.3, 0.55), (0.2 * math.cos(a), 0.2 * math.sin(a), z + 0.05), disari + sus.uniform(-50, 50), sus.uniform(5, 20)), 1)
        z += sus.uniform(0.12, 0.2); a += sus.uniform(0.8, 1.3)
    return nesne(ad, bm, [M['sarmasik'], M['yaprak']], kol, konum=(x, y, 0), koru={1})

def kuru_ot(ad, kol, x, y, z_kiris, adet=2, aralik=0.5):
    """Kirişten baş aşağı sarkan kuru ot demetleri."""
    bm = bmesh.new()
    for k in range(adet):
        xx = (k - (adet - 1) / 2) * aralik + sus.uniform(-0.08, 0.08); boy = sus.uniform(0.3, 0.45)
        P(bm, b_arasi((xx, 0, z_kiris), (xx, 0, z_kiris - 0.08), 0.005, n=4), 0)
        for j in range(3):
            P(bm, b_kart(sus.choice((6, 7, 8)), boy, (xx, 0, z_kiris - 0.06), 60 * j + sus.uniform(-20, 20), sus.uniform(2, 10), sarkan=True, ters=True), 1)
    return nesne(ad, bm, [M['koyu'], M['kuru_ot']], kol, konum=(x, y, 0), koru={1})

# ───────── Ozan eşyaları ─────────
def ozan_esyalari(bm, H):
    """Tabure, sehpada lavta, nota sehpası ve davul (yerel; dinleyiciler +x yönünde değil, -x'te). H: sahnenin yüksekliği.
    Malzeme: 1 ahşap, 2 masa ahşabı, 3 deri, 4 koyu, 5 dövme demir."""
    P(bm, b_silindir(0.1, -0.2, 0.17, H + 0.4, H + 0.45, n=20), 1, pah=0.006)
    P(bm, b_silindir(0.1, -0.2, 0.15, H + 0.45, H + 0.47, n=20), 3, pah=0.006)
    for i in range(3):
        a = math.radians(120 * i + 30)
        P(bm, b_arasi((0.1 + 0.1 * math.cos(a), -0.2 + 0.1 * math.sin(a), H + 0.41), (0.1 + 0.16 * math.cos(a), -0.2 + 0.16 * math.sin(a), H), 0.016, n=8), 1, yumusak=True)
    P(bm, b_arasi((-0.25, 0.35, H), (-0.25, 0.3, H + 0.4), 0.015, n=6), 1)
    P(bm, b_torna(-0.25, 0.35, [(H + 0.35, 0.02), (H + 0.41, 0.13), (H + 0.53, 0.16), (H + 0.65, 0.13), (H + 0.73, 0.07), (H + 0.75, 0.04)], n=16), 2, yumusak=True)
    P(bm, b_arasi((-0.25, 0.35, H + 0.75), (-0.25, 0.35, H + 1.1), 0.022, n=8), 4, yumusak=True)
    P(bm, b_kutu(-0.29, -0.21, 0.32, 0.38, H + 1.1, H + 1.21), 4, pah=0.004)
    P(bm, b_arasi((0.45, 0.25, H), (0.45, 0.25, H + 0.95), 0.012, n=6), 5)
    P(bm, b_kutu(0.25, 0.65, 0.22, 0.25, H + 0.9, H + 1.2), 5)
    P(bm, b_torna(-0.55, -0.35, [(H, 0.2), (H + 0.05, 0.22), (H + 0.33, 0.22), (H + 0.36, 0.2)], n=24), 2, yumusak=True)
    P(bm, b_silindir(-0.55, -0.35, 0.205, H + 0.36, H + 0.375, n=24), 3)
    for zz in (H + 0.06, H + 0.31):
        P(bm, b_torna(-0.55, -0.35, [(zz - 0.012, 0.226), (zz + 0.012, 0.226)], n=24, ust=False, alt=False), 5)

def temizle():
    bpy.data.meshes.remove(_GECICI)
