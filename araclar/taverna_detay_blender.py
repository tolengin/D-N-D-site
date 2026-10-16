# -*- coding: utf-8 -*-
"""
YENİ TAVERNA — DETAYLI MODEL (dokulu) Blender betiği
====================================================
Blockout'un (taverna_blockout_blender.py) yerleşimini aynen kullanır; parçaları gerçek biçimlerine kavuşturur ve
Nano Banana 2 dokularını uygular. Her çalıştığında her şeyi sıfırdan kurar.

Önce dokular hazır olmalı:   python araclar\\doku_hazirla.py     (3d/dokular/ klasörünü üretir)
Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --factory-startup --python araclar\\taverna_detay_blender.py

Çıktılar:
  3d/taverna-detay.blend           kaynak dosya (dokular 3d/dokular/'dan okunur, dosyaya gömülmez)
  3d/detay-ustten.png              tam tepeden önizleme (sitedeki kamera gibi)
  3d/detay-goz-<yön>.png           oyun masasının çevresinden göz hizasında dört yöne bakış (kuzey, guney, dogu, bati)
  3d/detay-etiketler.json          tepeden önizlemenin etiketleri (python araclar\\blockout_etiketle.py detay)

Gerçekçilik için kullanılan taktikler:
  • Normal haritası: düz yüzey, ışığa "her pikselde girinti/çıkıntı var" der; derzler ve tahta aralıkları ışıkta belirir.
  • Pürüz haritası: aynı yüzeyde mat ve parlak yerler (aşınmış ahşap biraz parlar, derz mat kalır).
  • Pah: kenarlar 1–3 cm yontulur; ışık bu ince yüzeylerde parlar, nesne "kutu" gibi durmaz.
  • Yumuşak gölgeli, sıcak, alçak ışık kaynakları (şömine, mumlar); oda karanlıkta kalır, ışık yerinde parlar.

Ölçüler METRE. Oda merkezi (0, 0) = oyun masasının merkezi = kameranın ortası. x doğu, y kuzey, z yukarı.
Outliner düzeni blockout ile aynıdır (01_Yapi, 02_Bar, 03_Masalar, 04_Somine, 05_Isik_Isaretleri, 06_Sablonlar, 99_Onizleme).
"""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOKU = os.path.join(KOK, '3d', 'dokular')
BLEND = os.path.join(KOK, '3d', 'taverna-detay.blend')
USTTEN = os.path.join(KOK, '3d', 'detay-ustten.png')
GOZ = os.path.join(KOK, '3d', 'detay-goz-hizasi.png')

# ───────── AYARLAR (blockout ile aynı; değiştirirsen ikisinde birden değiştir) ─────────
# 2026-10-15: oda küçültüldü (22,2 × 12,5 m çok boş duruyordu): iç ölçü 15,6 × 10 m. Artık 16:9'a bağlı değil.
# Blockout betiği bu yeni düzene güncellenmedi (eski büyük oda); yerleşim için bu betik esastır.
IC_Y = 5.0
IC_X = 7.8
DK, DH = 0.25, 3.0                     # detayda duvarlar 3 m (blockout 2,6): üstüne kirişli tavan oturur
DIS_Y = IC_Y + DK
DIS_X = IC_X + DK
ORTA_R, ORTA_SANDALYE_R, ORTA_SANDALYE = 1.05, 1.65, 9
YAN_R, YAN_SANDALYE_R, YAN_SANDALYE = 0.75, 1.18, 4
# Yan masalar (ad, x, y). Doğuyu şömine köşesi kapladığı için üçüncü masa güneydoğuda, kapının yanında.
# Kuzeydeki masa tabure sırasına fazla yaklaşırsa kendiliğinden aşağı itilir.
YAN_YERLER = (('Masa_KuzeyBati', -4.9, 1.9), ('Masa_GuneyBati', -3.4, -2.8), ('Masa_GuneyDogu', 1.8, -3.4))
SOMINE_DUVAR, SOMINE_Y = 'dogu', -0.5   # şömine doğu duvarında (eğik kameradan önü görünsün); y: duvardaki merkezi
BAR_X = 5.0                            # bar (tezgâh ve arka raf) −BAR_X…+BAR_X arasında; iki ucu boş kalır (2026-10-15)
MUTFAK_X, MUTFAK_GEN = -6.6, 1.2       # barın solunda, kuzey (arka) duvarında mutfağa açılan kapı
SAHNE_R, SAHNE_H = 1.25, 0.3           # müzik sahnesi (barın sağındaki boşlukta, kuzeydoğu köşesi): yarıçap ve yükseklik
TOHUM = 7
YAN_KAYMA_X, YAN_KAYMA_Y = 0.6, 0.35
HALKA_DONME = 22
SANDALYE_DONME, SANDALYE_KAYMA = 9, 0.05
RAF_D, KORIDOR_D, TEZGAH_D = 0.4, 1.1, 0.6
TEZGAH_H = 1.05
TABURE_ARA, TABURE_R = 0.75, 0.19
YURUME = 0.5
KAPI_X, KAPI_GEN = 4.3, 2.6
SOMINE_GEN, SOMINE_H = 3.0, 1.8
MASA_Z = 0.80                          # masaların üst yüzü
DETAY = 2.0                            # yuvarlak parçaların inceliği: 1 = kaba, 2 = iki kat kenar + yumuşak profiller (site yorulursa düşür)

# Dokunun gerçek boyu (m): doku bu kadar alanda bir tekrar eder
UVS = {'M_Zemin': 2.0, 'M_Masa': 1.2, 'M_Ahsap': 1.0, 'M_Ahsap_Koyu': 1.0, 'M_Duvar': 2.5, 'M_Somine': 1.5, 'M_Deri': 0.5, 'M_Kul': 1.5}

# ───────── Koleksiyonlar ─────────
bpy.ops.wm.read_factory_settings(use_empty=True)
sahne = bpy.context.scene
def koleksiyon(ad, ust=None):
    c = bpy.data.collections.new(ad); (ust or sahne.collection).children.link(c); return c
K = koleksiyon('Taverna')
K_YAPI = koleksiyon('01_Yapi', K)
K_ZEMIN, K_DUVAR, K_KAPI = koleksiyon('Zemin', K_YAPI), koleksiyon('Duvarlar', K_YAPI), koleksiyon('Kapilar', K_YAPI)
K_BAR = koleksiyon('02_Bar', K)
K_TABURE = koleksiyon('Bar_Tabureleri', K_BAR)
K_RAF = koleksiyon('Bar_Raf_Siseler', K_BAR)
K_MASA = koleksiyon('03_Masalar', K)
K_SOM = koleksiyon('04_Somine', K)
K_ISIK = koleksiyon('05_Isik_Isaretleri', K)
K_SAB = koleksiyon('06_Sablonlar', K)
K_DEKOR = koleksiyon('07_Dekor', K)
K_TAVAN = koleksiyon('08_Tavan', K)            # tepeden bakan kamerada gizlenir (sitede kamera tavanın altında durur)
K_APLIK = koleksiyon('Aplikler', K_ISIK)
K_ONI = koleksiyon('99_Onizleme')

zar = random.Random(TOHUM)                     # blockout ile aynı sırayla çekilir: masalar aynı yere düşer
def oyna(en_cok): return zar.uniform(-en_cok, en_cok)
sus = random.Random(99)                        # süs eşyaları için ayrı "rastgele" (masaların yerini bozmasın)

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

M = {
    'zemin':  mat_doku('M_Zemin', 'zemin-ahsap'),
    'masa':   mat_doku('M_Masa', 'masa-ahsap'),
    'ahsap':  mat_doku('M_Ahsap', 'zemin-ahsap', carpan=(0.62, 0.50, 0.40), normal_guc=0.8),        # mobilya gövdesi
    'koyu':   mat_doku('M_Ahsap_Koyu', 'zemin-ahsap', carpan=(0.30, 0.24, 0.20), normal_guc=0.8),   # kirişler, direkler, kapı
    'duvar':  mat_doku('M_Duvar', 'duvar-tas', normal_guc=1.2),
    'somine': mat_doku('M_Somine', 'somine-tas', normal_guc=1.3),
    'kul':    mat_doku('M_Kul', 'somine-tas', carpan=(0.18, 0.16, 0.15), normal_guc=1.0),           # ocağın isli tabanı
    'deri':   mat_doku('M_Deri', 'deri'),
    'hali':   mat_doku('M_Hali', 'hali', puruz=False, puruz_sabit=0.95, alfa=True),
    'demir':  mat_duz('M_Demir', (0.035, 0.032, 0.03), 0.5, 0.85),
    'pirinc': mat_duz('M_Pirinc', (0.45, 0.30, 0.10), 0.32, 1.0),
    'kalay':  mat_duz('M_Kalay', (0.35, 0.34, 0.32), 0.42, 0.9),      # kupalar
    'mum':    mat_duz('M_Mum', (0.80, 0.70, 0.50), 0.45),
    'cam_y':  mat_duz('M_Cam_Yesil', (0.02, 0.08, 0.03), 0.12),
    'cam_k':  mat_duz('M_Cam_Kahve', (0.10, 0.03, 0.005), 0.12),
    'cam_s':  mat_duz('M_Cam_Saydam', (0.25, 0.25, 0.22), 0.08),
    'fener':  mat_duz('M_Fener_Cam', (0.12, 0.07, 0.03), 0.1, isik=(1.0, 0.52, 0.2), isik_guc=1.4),   # içinde mum yanan fener camı
    'bira':   mat_duz('M_Bira', (0.45, 0.22, 0.03), 0.15),
    'alev':   mat_duz('M_Alev', (0, 0, 0), 1.0, isik=(1.0, 0.45, 0.10), isik_guc=8.0),
    'kor':    mat_duz('M_Kor', (0.02, 0.01, 0.005), 0.9, isik=(1.0, 0.22, 0.03), isik_guc=2.5),
}

# ───────── Parça kurucular ─────────
# Her parça kendi geçici "bmesh"inde kurulur, malzemesi ve pahı verilir, sonra nesnenin bmesh'ine eklenir.
_GECICI = bpy.data.meshes.new('_gecici')

def b_kutu(x0, x1, y0, y1, z0, z1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 if v.co.x < 0 else x1; v.co.y = y0 if v.co.y < 0 else y1; v.co.z = z0 if v.co.z < 0 else z1
    return bm

def _n(n):
    """Yuvarlak parçaların kenar sayısı DETAY ile çarpılır."""
    return max(3, int(round(n * DETAY)))

def _yumusat(h):
    """Torna profilindeki her iki halka arasına yumuşak (Catmull-Rom) bir ara halka ekler: kıvrımlar yuvarlaklaşır."""
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
    bmesh.ops.create_cone(bm, cap_ends=True, segments=_n(n), radius1=r, radius2=r if r2 is None else r2, depth=d.length)
    q = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) / 2) @ q, verts=bm.verts)
    return bm

def b_torna(x, y, halkalar, n=12, ust=True, alt=True):
    """Dönen gövde: [(z, yarıçap)] halkaları (şişe, kupa, mum, fıçı, tornalı ayak)."""
    n = _n(n); halkalar = _yumusat(halkalar)
    bm = bmesh.new(); H = []
    for z, r in halkalar:
        H.append([bm.verts.new((x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n), z)) for i in range(n)])
    for a, b in zip(H, H[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    if ust: bm.faces.new(H[-1])
    if alt: bm.faces.new(H[0][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def dondur(bm, aci, merkez=(0, 0)):
    """Parçayı yukarıdan bakınca saat yönünde 'aci' derece döndürür."""
    cx, cy = merkez
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(cx, cy, 0), matrix=Matrix.Rotation(-math.radians(aci), 3, 'Z'))
    return bm

def P(hedef, bm, mi=0, pah=0.0, seg=1, yumusak=False):
    """Parçayı hedefe ekler. pah: keskin kenarları bu kadar yontar (m)."""
    for f in bm.faces:
        f.material_index = mi; f.smooth = yumusak
    if pah > 0:
        kenar = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(35)]
        if kenar:
            bmesh.ops.bevel(bm, geom=kenar, offset=pah, segments=seg + (1 if DETAY > 1 else 0), affect='EDGES', profile=0.5, clamp_overlap=True)
    bm.to_mesh(_GECICI); bm.free()
    hedef.from_mesh(_GECICI)

def nesne(ad, bm, mats, kol, konum=(0, 0, 0), aci=0.0, uv_ozel=None, koru=()):
    """bmesh'ten nesne kurar. Doku koordinatları (UV): her yüz baktığı yöne göre izdüşümlenir, malzemenin gerçek boyuna göre.
    koru: bu malzeme sıralarındaki yüzlerin UV'sine dokunulmaz (yaprak kartları kendi UV'siyle gelir)."""
    bm.normal_update()
    uvl = bm.loops.layers.uv.verify()
    olc = [UVS.get(m.name, 1.0) for m in mats]
    for f in bm.faces:
        if f.material_index in koru: continue
        n = f.normal; ax = max(range(3), key=lambda k: abs(n[k])); s = olc[min(f.material_index, len(olc) - 1)]
        for l in f.loops:
            p = l.vert.co
            u, v = (p.x, p.y) if ax == 2 else ((p.y, p.z) if ax == 0 else (p.x, p.z))
            l[uvl].uv = (u / s, v / s)
    if uv_ozel: uv_ozel(bm, uvl)
    me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    yumusak_var = any(p.use_smooth for p in me.polygons)
    if yumusak_var:
        try: me.set_sharp_from_angle(angle=math.radians(40))       # yumuşak yüzlerde 40°'den keskin kenarlar keskin kalsın
        except Exception: pass
    ob = bpy.data.objects.new(ad, me)
    ob.location = konum; ob.rotation_euler = (0, 0, -math.radians(aci)); kol.objects.link(ob)
    return ob

def bagla(cocuk, ebeveyn):
    bpy.context.view_layer.update()
    cocuk.parent = ebeveyn; cocuk.matrix_parent_inverse = ebeveyn.matrix_world.inverted()

def bos(ad, kol, x, y, z=0.0, boy=0.3, tur='PLAIN_AXES'):
    e = bpy.data.objects.new(ad, None); e.empty_display_type = tur; e.empty_display_size = boy
    e.location = (x, y, z); kol.objects.link(e); return e

def kopya(ad, sablon, kol, x, y, aci=0.0):
    ob = bpy.data.objects.new(ad, sablon.data); ob.location = (x, y, 0); ob.rotation_euler = (0, 0, -math.radians(aci))
    kol.objects.link(ob); return ob

# ───────── 01 Yapı ─────────
bm = bmesh.new(); P(bm, b_kutu(-DIS_X, DIS_X, -DIS_Y, DIS_Y, -0.05, 0.0)); nesne('Zemin', bm, [M['zemin']], K_ZEMIN)

K0, K1 = KAPI_X - KAPI_GEN / 2, KAPI_X + KAPI_GEN / 2
DUVARLAR = {
    'Duvar_Kuzey_Bati': (-DIS_X, MUTFAK_X - MUTFAK_GEN / 2, IC_Y, DIS_Y), 'Duvar_Kuzey_Dogu': (MUTFAK_X + MUTFAK_GEN / 2, DIS_X, IC_Y, DIS_Y),
    'Duvar_Bati': (-DIS_X, -IC_X, -DIS_Y, DIS_Y), 'Duvar_Dogu': (IC_X, DIS_X, -DIS_Y, DIS_Y),
    'Duvar_Guney_Bati': (-DIS_X, K0, -DIS_Y, -IC_Y), 'Duvar_Guney_Dogu': (K1, DIS_X, -DIS_Y, -IC_Y),
}
for ad, (x0, x1, y0, y1) in DUVARLAR.items():
    bm = bmesh.new()
    P(bm, b_kutu(x0, x1, y0, y1, 0, DH), 0)
    P(bm, b_kutu(x0 - 0.03, x1 + 0.03, y0 - 0.03, y1 + 0.03, DH, DH + 0.18), 1, pah=0.015)        # duvarın üstündeki ahşap kiriş
    P(bm, b_kutu(x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, 0, 0.14), 1, pah=0.01)                # süpürgelik
    nesne(ad, bm, [M['duvar'], M['koyu']], K_DUVAR)

# Ahşap direkler: duvar boyunca aralıklı, köşelerde ve kapı yanlarında (yarı ahşap iskelet)
bm = bmesh.new()
def direk(x, y):
    P(bm, b_kutu(x - 0.16, x + 0.16, y - 0.16, y + 0.16, 0, DH + 0.18), 0, pah=0.02)
_k = int((IC_X - 1.0) // 3.7)
DIREK_KUZEY = [i * 3.7 for i in range(-_k, _k + 1)]               # kuzey duvarı (barın arkası): 3,7 m arayla
DIREK_GUNEY = [-5.0, -2.0, 0.6]                                   # güney duvarı (kapının ve tabak rafının dışında)
DIREK_BATI = [-3.0, 0.0, 3.0]
DIREK_DOGU = [2.6]                                                # doğu duvarında şömine, kitaplık ve pano var: yalnızca bar ucunda
for x in [-IC_X + 0.1, IC_X - 0.1] + DIREK_KUZEY:
    direk(x, IC_Y - 0.06)
for x in [-IC_X + 0.1, IC_X - 0.1, K0 - 0.12, K1 + 0.12] + DIREK_GUNEY:
    direk(x, -IC_Y + 0.06)
for y in DIREK_BATI: direk(-IC_X + 0.06, y)
for y in DIREK_DOGU: direk(IC_X - 0.06, y)
nesne('Duvar_Direkleri', bm, [M['koyu']], K_DUVAR)

# Giriş kapısı: taş eşik, içeri açık iki kanat (dikey tahta + demir kuşak)
bm = bmesh.new(); P(bm, b_kutu(K0, K1, -DIS_Y, -IC_Y + 0.05, 0, 0.04), 0, pah=0.01); nesne('Kapi_Giris_Esik', bm, [M['somine']], K_KAPI)
# Kapının üstü: ahşap lento ve üstünde duvar (kapı boşluğu tavana kadar açık durmasın)
bm = bmesh.new()
P(bm, b_kutu(K0 - 0.2, K1 + 0.2, -DIS_Y - 0.02, -IC_Y + 0.04, 2.3, 2.5), 1, pah=0.015)
P(bm, b_kutu(K0, K1, -DIS_Y, -IC_Y, 2.5, DH), 0)
nesne('Kapi_Lento', bm, [M['duvar'], M['koyu']], K_KAPI)
# Kapının dışı: gece. Kapı boşluğundan bakınca boşluk değil, karanlık bir dış görünsün.
M_GECE = mat_duz('M_Gece', (0.004, 0.005, 0.008), 1.0, isik=(0.010, 0.012, 0.018), isik_guc=0.6)
bm = bmesh.new(); P(bm, b_kutu(K0 - 9, K1 + 9, -DIS_Y - 3.0, -DIS_Y - 2.9, -0.05, DH + 3.0), 0)
P(bm, b_kutu(K0 - 9, K1 + 9, -DIS_Y - 3.0, -DIS_Y, -0.06, -0.05), 0)
nesne('Kapi_Disari_Gece', bm, [M_GECE], K_KAPI)
kanat = KAPI_GEN / 2 - 0.05
for ad, x, yon in (('Kapi_Giris_Kanat_Bati', K0 + 0.05, 1), ('Kapi_Giris_Kanat_Dogu', K1 - 0.05, -1)):
    bm = bmesh.new()
    P(bm, b_kutu(-0.03, 0.03, 0, kanat, 0.02, 2.2), 0, pah=0.008)
    for z in (0.35, 1.85):
        P(bm, b_kutu(-0.045, 0.045, 0.05, kanat - 0.05, z, z + 0.07), 1)
    nesne(ad, bm, [M['koyu'], M['demir']], K_KAPI, konum=(x, -IC_Y, 0), aci=yon * 8)

# Mutfak kapısı: kuzey duvarında, barın solunda. Taş eşik, lento ve üstünde duvar, tavernaya doğru açık tek kanat.
# Arkasında karanlık bir mutfak girişi (zemin, arka ve yan duvar): kapıdan bakınca boşluk görünmesin. Tepeden bakan
# eğik kamerada kuzey duvarı bunu örter (2,25 m yüksekliğinde, duvarın 0,6 m gerisinde).
M0, M1 = MUTFAK_X - MUTFAK_GEN / 2, MUTFAK_X + MUTFAK_GEN / 2
bm = bmesh.new(); P(bm, b_kutu(M0, M1, IC_Y - 0.05, DIS_Y, 0, 0.04), 0, pah=0.01); nesne('Kapi_Mutfak_Esik', bm, [M['somine']], K_KAPI)
bm = bmesh.new()
P(bm, b_kutu(M0 - 0.15, M1 + 0.15, IC_Y - 0.04, DIS_Y + 0.02, 2.2, 2.38), 1, pah=0.015)
P(bm, b_kutu(M0, M1, IC_Y, DIS_Y, 2.38, DH), 0)
nesne('Kapi_Mutfak_Lento', bm, [M['duvar'], M['koyu']], K_KAPI)
bm = bmesh.new()
P(bm, b_kutu(-0.03, 0.03, -(MUTFAK_GEN - 0.08), 0, 0.02, 2.12), 0, pah=0.008)
for z in (0.35, 1.75):
    P(bm, b_kutu(-0.045, 0.045, -(MUTFAK_GEN - 0.12), -0.05, z, z + 0.07), 1)
nesne('Kapi_Mutfak_Kanat', bm, [M['koyu'], M['demir']], K_KAPI, konum=(M0 + 0.05, IC_Y, 0), aci=-20)
M_MUTFAK = mat_duz('M_Mutfak', (0.03, 0.018, 0.01), 1.0, isik=(0.05, 0.025, 0.01), isik_guc=0.4)   # loş, ateş renginde
bm = bmesh.new()
P(bm, b_kutu(M0 - 0.6, M1 + 0.6, DIS_Y, DIS_Y + 0.62, -0.05, 0.0), 0)          # zemin
P(bm, b_kutu(M0 - 0.6, M1 + 0.6, DIS_Y + 0.6, DIS_Y + 0.62, 0.0, 2.25), 0)    # arka
for x in (M0 - 0.6, M1 + 0.58):
    P(bm, b_kutu(x, x + 0.02, DIS_Y, DIS_Y + 0.62, 0.0, 2.25), 0)              # yanlar
nesne('Mutfak_Girisi', bm, [M_MUTFAK], K_KAPI)

# ───────── 06 Şablonlar: sandalye, tabure, koltuk ─────────
# Sandalye: önü kuzeyde (+y), merkez oturağın ortası ve yer seviyesi. Malzeme 0: ahşap, 1: deri.
bm = bmesh.new()
for sx in (-1, 1):
    P(bm, b_torna(sx * 0.23, 0.22, [(0, 0.020), (0.12, 0.026), (0.18, 0.019), (0.26, 0.026), (0.42, 0.024)], n=10), 0, yumusak=True)  # ön ayak (tornalı)
    P(bm, b_arasi((sx * 0.23, -0.21, 0), (sx * 0.23, -0.27, 0.95), 0.024, n=10), 0, yumusak=True)                                         # arka ayak (geriye eğik)
    P(bm, b_torna(sx * 0.23, -0.27, [(0.95, 0.026), (0.975, 0.03), (1.0, 0.012)], n=10, alt=False), 0, yumusak=True)                     # topuz
    P(bm, b_arasi((sx * 0.23, 0.22, 0.15), (sx * 0.23, -0.215, 0.15), 0.013, n=8), 0, yumusak=True)                                       # yan alt çubuk
P(bm, b_arasi((-0.23, 0.22, 0.2), (0.23, 0.22, 0.2), 0.013, n=8), 0, yumusak=True)                                                        # ön alt çubuk
P(bm, b_arasi((-0.23, -0.215, 0.2), (0.23, -0.215, 0.2), 0.013, n=8), 0, yumusak=True)                                                    # arka alt çubuk
P(bm, b_kutu(-0.27, 0.27, -0.25, 0.26, 0.41, 0.45), 0, pah=0.01)                                                                          # oturak tahtası
P(bm, b_kutu(-0.245, 0.245, -0.22, 0.235, 0.45, 0.49), 1, pah=0.018, seg=2)                                                               # deri minder
P(bm, b_kutu(-0.23, 0.23, -0.29, -0.255, 0.84, 0.93), 0, pah=0.008)                                                                      # arkalık üst çıtası
P(bm, b_kutu(-0.23, 0.23, -0.27, -0.245, 0.55, 0.59), 0, pah=0.006)                                                                      # arkalık alt çıtası
for x in (-0.11, 0.0, 0.11):
    P(bm, b_arasi((x, -0.258, 0.59), (x, -0.272, 0.84), 0.011, n=6), 0, yumusak=True)                                                     # dikey çubuklar
SANDALYE = nesne('Sandalye_Sablon', bm, [M['ahsap'], M['deri']], K_SAB, konum=(-DIS_X - 1.5, 1.0, 0))

# Bar taburesi: yuvarlak oturak (deri üst), dört açık ayak, ayak halkası
bm = bmesh.new()
P(bm, b_silindir(0, 0, TABURE_R, 0.70, 0.75, n=24), 0, pah=0.01)
P(bm, b_silindir(0, 0, TABURE_R - 0.02, 0.75, 0.77, n=24), 1, pah=0.008, yumusak=True)
for i in range(4):
    a = math.radians(45 + 90 * i)
    P(bm, b_arasi((0.11 * math.cos(a), 0.11 * math.sin(a), 0.70), (0.2 * math.cos(a), 0.2 * math.sin(a), 0.0), 0.018, n=8), 0, yumusak=True)
    b = math.radians(135 + 90 * i)
    P(bm, b_arasi((0.17 * math.cos(a), 0.17 * math.sin(a), 0.26), (0.17 * math.cos(b), 0.17 * math.sin(b), 0.26), 0.011, n=6), 0, yumusak=True)
TABURE = nesne('Tabure_Sablon', bm, [M['ahsap'], M['deri']], K_SAB, konum=(-DIS_X - 1.5, -1.0, 0))

# Koltuk (şömine önü): deri kaplı, yumuşak pahlı; önü kuzeyde
bm = bmesh.new()
for sx in (-1, 1):
    for sy in (-1, 1):
        P(bm, b_torna(sx * 0.32, sy * 0.32, [(0, 0.025), (0.09, 0.03)], n=10), 0, yumusak=True)                                           # kısa ayaklar
P(bm, b_kutu(-0.4, 0.4, -0.38, 0.4, 0.09, 0.40), 1, pah=0.04, seg=3)                                                                      # gövde
P(bm, b_kutu(-0.27, 0.27, -0.2, 0.38, 0.40, 0.50), 1, pah=0.045, seg=3)                                                                   # minder
P(bm, b_kutu(-0.4, 0.4, -0.4, -0.2, 0.40, 1.02), 1, pah=0.06, seg=3)                                                                      # arkalık
for sx in (-1, 1):
    P(bm, b_kutu(sx * 0.4 - (0.13 if sx > 0 else 0), sx * 0.4 + (0 if sx > 0 else 0.13), -0.25, 0.4, 0.40, 0.66), 1, pah=0.05, seg=3)   # kollar
KOLTUK = nesne('Koltuk_Sablon', bm, [M['ahsap'], M['deri']], K_SAB, konum=(-DIS_X - 1.5, -3.0, 0))

# Mum: pirinç tabak, mum, alev (ayrı nesne: site titretir)
def mum_kur(no, x, y, z, kol, ebeveyn=None):
    bm = bmesh.new()
    # Pirinç şamdan: geniş tabak, kalkık kenar, ortada mum yuvası
    P(bm, b_torna(0, 0, [(0, 0.05), (0.004, 0.058), (0.010, 0.060), (0.013, 0.056), (0.012, 0.045), (0.016, 0.03), (0.03, 0.027), (0.034, 0.03)], n=16), 0, yumusak=True)
    # Mum: hafif yamuk gövde, tepesinde erimiş çukur ve kenarından süzülen damlalar
    h = 0.11 + sus.uniform(0, 0.07)
    P(bm, b_torna(0, 0, [(0.02, 0.022), (h * 0.5, 0.0225), (h, 0.0215), (h + 0.006, 0.019), (h + 0.002, 0.012), (h - 0.002, 0.006)], n=14), 1, yumusak=True)
    for _ in range(3):
        a = sus.uniform(0, 2 * math.pi); boy = sus.uniform(0.015, 0.05)
        P(bm, b_arasi((0.021 * math.cos(a), 0.021 * math.sin(a), h + 0.004), (0.0225 * math.cos(a), 0.0225 * math.sin(a), h - boy), 0.0045, n=6, r2=0.0065), 1, yumusak=True)
    P(bm, b_arasi((0, 0, h - 0.004), (0.002, 0, h + 0.012), 0.0012, n=4), 2)                                 # fitil
    ob = nesne(f'Mum_{no}', bm, [M['pirinc'], M['mum'], M['demir']], kol, konum=(x, y, z))
    ust = h + 0.008                                                                                         # alevin tabanı
    bm = bmesh.new(); P(bm, b_torna(0, 0, [(0, 0.003), (0.008, 0.008), (0.02, 0.0105), (0.034, 0.008), (0.048, 0.004), (0.06, 0.0005)], n=10), 0, yumusak=True)
    alev = nesne(f'alev_mum_{no}', bm, [M['alev']], kol, konum=(x, y, z + ust))
    isaret = bos(f'isik_mum_{no}', kol, x, y, z + ust + 0.06, boy=0.08, tur='SPHERE')
    bagla(alev, ob); bagla(isaret, ob)
    if ebeveyn: bagla(ob, ebeveyn)
    return (x, y, z + ust + 0.06)

def kupa_kur(bm, x, y, z, aci=0):
    P(bm, b_torna(x, y, [(z, 0.04), (z + 0.01, 0.042), (z + 0.11, 0.045), (z + 0.12, 0.047)], n=14, ust=False), 0, yumusak=True)
    P(bm, b_torna(x, y, [(z + 0.10, 0.043)], n=14, alt=False), 1)
    a = math.radians(aci)
    P(bm, b_arasi((x + 0.045 * math.cos(a), y + 0.045 * math.sin(a), z + 0.09), (x + 0.075 * math.cos(a), y + 0.075 * math.sin(a), z + 0.06), 0.009, n=6), 0, yumusak=True)
    P(bm, b_arasi((x + 0.075 * math.cos(a), y + 0.075 * math.sin(a), z + 0.06), (x + 0.045 * math.cos(a), y + 0.045 * math.sin(a), z + 0.025), 0.009, n=6), 0, yumusak=True)

ISIKLAR = []                                   # (ad, x, y, z) önizleme ışıkları için
MUM_NO = [0]
def yeni_mum(x, y, z, kol, ebeveyn=None):
    MUM_NO[0] += 1
    p = mum_kur(MUM_NO[0], x, y, z, kol, ebeveyn)
    ISIKLAR.append((f'isik_mum_{MUM_NO[0]}', *p))

# ───────── 02 Bar ölçüleri (masalar tabure sırasına göre yerleşir) ─────────
RAF_Y0 = IC_Y - RAF_D
TEZ_Y1 = RAF_Y0 - KORIDOR_D
TEZ_Y0 = TEZ_Y1 - TEZGAH_D
TABURE_Y = TEZ_Y0 - 0.1 - TABURE_R

# ───────── 03 Masalar ─────────
SANDALYE_YARI = 0.43
def sandalye_yerleri(n, r, ilk_aci, donme, kayma):
    yer = []
    for i in range(n):
        a = ilk_aci + 360 * i / n + oyna(donme * 0.6)
        ra = math.radians(a); rr = r + oyna(kayma)
        yer.append((rr * math.sin(ra), rr * math.cos(ra), a + 180 + oyna(donme)))
    return yer

def masa_govde(ad, r, kol, konum):
    """Yuvarlak masa: pahlı kalın tabla, demir çember, ortada sekizgen ayak, dört kollu taban ve dört destek kolu."""
    bm = bmesh.new()
    P(bm, b_silindir(0, 0, r, MASA_Z - 0.08, MASA_Z, n=64), 0, pah=0.015, seg=2)
    P(bm, b_silindir(0, 0, r + 0.006, MASA_Z - 0.065, MASA_Z - 0.035, n=64), 2)                                 # demir çember
    ar = 0.13 if r > 0.9 else 0.09
    P(bm, b_silindir(0, 0, ar, 0.10, MASA_Z - 0.08, n=8), 1, pah=0.01)                                          # sekizgen ayak
    for i in range(4):
        b = b_kutu(0, r * 0.72, -0.05, 0.05, 0.0, 0.10); dondur(b, 45 + 90 * i); P(bm, b, 1, pah=0.012)        # taban kolları
        a = math.radians(45 + 90 * i)
        P(bm, b_arasi((ar * math.cos(a), ar * math.sin(a), 0.42), (r * 0.62 * math.cos(a), r * 0.62 * math.sin(a), MASA_Z - 0.085), 0.025, n=8), 1, yumusak=True)   # destek kolu
    return nesne(ad + '_Govde', bm, [M['masa'], M['ahsap'], M['demir']], kol, konum=konum)

def masa_kur(ad, x, y, r, yerler):
    kol = koleksiyon(ad, K_MASA)
    kok = bos(ad, kol, x, y, boy=r * 0.6, tur='CIRCLE')
    parcalar = [masa_govde(ad, r, kol, (x, y, 0))]
    for i, (dx, dy, aci) in enumerate(yerler):
        parcalar.append(kopya(f'{ad}_Sandalye_{i + 1}', SANDALYE, kol, x + dx, y + dy, aci))
    for p in parcalar: bagla(p, kok)
    return kok, kol

kok_orta, kol_orta = masa_kur('Masa_Orta', 0, 0, ORTA_R, sandalye_yerleri(ORTA_SANDALYE, ORTA_SANDALYE_R, 0, SANDALYE_DONME / 2, SANDALYE_KAYMA / 2))
for a in (70, 250):                             # oyun masasının kenarında iki mum (ortası zarlar için boş)
    ra = math.radians(a); yeni_mum(0.82 * math.sin(ra), 0.82 * math.cos(ra), MASA_Z, kol_orta, kok_orta)
YAN_MASALAR = []
for ad, x0, y0 in YAN_YERLER:
    yerler = sandalye_yerleri(YAN_SANDALYE, YAN_SANDALYE_R, 45 + oyna(HALKA_DONME), SANDALYE_DONME, SANDALYE_KAYMA)
    x = x0 + oyna(YAN_KAYMA_X); y = y0 + oyna(YAN_KAYMA_Y)
    if y0 > 0:
        y = min(y, TABURE_Y - TABURE_R - YURUME - max(dy for _, dy, _ in yerler) - SANDALYE_YARI)
    kok, kol = masa_kur(ad, x, y, YAN_R, yerler)
    YAN_MASALAR.append((ad, x, y, kok, kol))
    # Masanın üstü: ortada mum, kenarda iki kupa (masayla birlikte taşınır)
    yeni_mum(x + sus.uniform(-0.1, 0.1), y + sus.uniform(-0.1, 0.1), MASA_Z, kol, kok)
    bm = bmesh.new()
    for _ in range(2):
        a = sus.uniform(0, 2 * math.pi); rr = YAN_R * sus.uniform(0.45, 0.7)
        kupa_kur(bm, x + rr * math.cos(a), y + rr * math.sin(a), MASA_Z, sus.uniform(0, 360))
    bagla(nesne(f'{ad}_Kupalar', bm, [M['kalay'], M['bira']], kol), kok)

# ───────── 02 Bar ─────────
bm = bmesh.new()
P(bm, b_kutu(-BAR_X, BAR_X, TEZ_Y0 + 0.06, TEZ_Y1, 0.10, TEZGAH_H - 0.06), 0)                                      # ön panel (dikey tahtalar)
P(bm, b_kutu(-BAR_X, BAR_X, TEZ_Y0 + 0.12, TEZ_Y1, 0.0, 0.10), 1)                                                  # içeri çekik süpürgelik
P(bm, b_kutu(-BAR_X, BAR_X, TEZ_Y0 - 0.06, TEZ_Y1 + 0.03, TEZGAH_H - 0.07, TEZGAH_H), 2, pah=0.015, seg=2)        # tezgâh tablası (taşkın)
x = -BAR_X + 0.1
while x < BAR_X:                                                                                                  # ön paneldeki dikmeler
    P(bm, b_kutu(x - 0.05, x + 0.05, TEZ_Y0 + 0.02, TEZ_Y0 + 0.07, 0.10, TEZGAH_H - 0.07), 1, pah=0.01)
    x += 1.6
nesne('Bar_Tezgah', bm, [M['ahsap'], M['koyu'], M['masa']], K_BAR)
bm = bmesh.new()                                                                                                 # pirinç ayak çubuğu ve tutucuları
P(bm, b_arasi((-BAR_X + 0.1, TEZ_Y0 - 0.14, 0.2), (BAR_X - 0.1, TEZ_Y0 - 0.14, 0.2), 0.022, n=12), 0, yumusak=True)
x = -BAR_X + 0.6
while x < BAR_X:
    P(bm, b_arasi((x, TEZ_Y0 - 0.14, 0.2), (x, TEZ_Y0 + 0.06, 0.2), 0.012, n=8), 0, yumusak=True)
    x += 1.6
nesne('Bar_Ayak_Cubugu', bm, [M['pirinc']], K_BAR)

# Arka raf: alt dolap, üç raf tahtası, dikmeler
bm = bmesh.new()
P(bm, b_kutu(-BAR_X, BAR_X, RAF_Y0, IC_Y, 0, 0.9), 0)
P(bm, b_kutu(-BAR_X, BAR_X, RAF_Y0 - 0.03, IC_Y, 0.9, 0.95), 1, pah=0.01)
for z in (1.35, 1.75, 2.15):
    P(bm, b_kutu(-BAR_X, BAR_X, IC_Y - 0.32, IC_Y, z, z + 0.04), 1, pah=0.008)
x = -BAR_X + 0.05
while x < BAR_X:
    P(bm, b_kutu(x - 0.04, x + 0.04, IC_Y - 0.32, IC_Y, 0.95, 2.3), 1, pah=0.008)
    x += 2.4
nesne('Bar_Arka_Raf', bm, [M['ahsap'], M['koyu']], K_BAR)

# Raftaki şişeler ve kupalar (her raf ayrı nesne: kolay seçilsin)
CAMLAR = [M['cam_y'], M['cam_k'], M['cam_s']]
for ri, z in enumerate((0.95, 1.39, 1.79, 2.19)):
    bm = bmesh.new()
    x = -BAR_X + 0.15
    while x < BAR_X - 0.15:
        if sus.random() < 0.72:
            yy = IC_Y - 0.16 + sus.uniform(-0.04, 0.04)
            if sus.random() < 0.25:
                kupa_kur(bm, x, yy, z, sus.uniform(0, 360))
            else:
                h = sus.uniform(0.22, 0.32); r = sus.uniform(0.032, 0.045)
                P(bm, b_torna(x, yy, [(z, r * 0.9), (z + 0.005, r), (z + h * 0.62, r), (z + h * 0.75, r * 0.45), (z + h * 0.95, 0.013), (z + h, 0.014)], n=10),
                  2 + sus.randrange(3), yumusak=True)
        x += sus.uniform(0.11, 0.2)
    nesne(f'Bar_Raf_{ri + 1}', bm, [M['kalay'], M['bira']] + CAMLAR, K_RAF)

# Fıçı: tahta gövde, demir çemberler, kapak. dik=False: yatık (raf altında)
def fici(ad, kol, x, y, r=0.3, h=0.9, aci=0):
    bm = bmesh.new()
    P(bm, b_torna(0, 0, [(0, r * 0.86), (h * 0.15, r * 0.96), (h * 0.5, r), (h * 0.85, r * 0.96), (h, r * 0.86)], n=24), 0, yumusak=True)
    for zz in (h * 0.1, h * 0.3, h * 0.7, h * 0.9):
        rr = r * (0.94 if zz in (h * 0.1, h * 0.9) else 0.99) + 0.006
        P(bm, b_torna(0, 0, [(zz - 0.02, rr), (zz + 0.02, rr)], n=24, ust=False, alt=False), 1, yumusak=True)
    P(bm, b_silindir(0, 0, r * 0.8, h - 0.015, h + 0.005, n=24), 2)
    return nesne(ad, bm, [M['ahsap'], M['demir'], M['masa']], kol, konum=(x, y, 0), aci=aci)
for i, x in enumerate((-BAR_X + 0.45, BAR_X - 0.45)):
    fici(f'Bar_Fici_{i + 1}', K_BAR, x, (RAF_Y0 + TEZ_Y1) / 2, aci=sus.uniform(0, 90))

# Tezgâhın üstü: dört mum ve birkaç kupa
for x in (-0.77 * BAR_X, -2.0, 2.0, 0.77 * BAR_X):
    yeni_mum(x + sus.uniform(-0.2, 0.2), (TEZ_Y0 + TEZ_Y1) / 2 + sus.uniform(-0.08, 0.08), TEZGAH_H, K_BAR)
bm = bmesh.new()
for _ in range(9):
    kupa_kur(bm, sus.uniform(-BAR_X + 0.5, BAR_X - 0.5), (TEZ_Y0 + TEZ_Y1) / 2 + sus.uniform(-0.2, 0.2), TEZGAH_H, sus.uniform(0, 360))
nesne('Bar_Tezgah_Kupalar', bm, [M['kalay'], M['bira']], K_BAR)

# Tabureler: tezgâhın önünde boydan boya, biraz düzensiz
n_tab = int((2 * BAR_X - 0.8) // TABURE_ARA) + 1
bas = -(n_tab - 1) * TABURE_ARA / 2
kok_t = bos('Bar_Tabureleri', K_TABURE, 0, TABURE_Y, boy=0.4)
for i in range(n_tab):
    t = kopya(f'Bar_Tabure_{i + 1:02d}', TABURE, K_TABURE, bas + i * TABURE_ARA + sus.uniform(-0.06, 0.06),
              TABURE_Y + sus.uniform(-0.05, 0.05), sus.uniform(0, 90))
    bagla(t, kok_t)

# ───────── 04 Şömine (güney duvarının ortası) ─────────
SY = -IC_Y
G2, YD = SOMINE_GEN / 2, 0.95
bm = bmesh.new()
P(bm, b_kutu(-G2, -G2 + 0.5, SY, SY + YD, 0, SOMINE_H), 0, pah=0.02)                    # batı yanağı
P(bm, b_kutu(G2 - 0.5, G2, SY, SY + YD, 0, SOMINE_H), 0, pah=0.02)                      # doğu yanağı
P(bm, b_kutu(-G2, G2, SY, SY + 0.32, 0, DH), 0, pah=0.02)                               # arka duvar (bacaya kadar)
P(bm, b_kutu(-G2 + 0.2, G2 - 0.2, SY, SY + 0.45, SOMINE_H, DH), 0, pah=0.02)            # baca gövdesi (yalnızca ateşin arkasının üstü: tepeden ateş görünsün)
P(bm, b_kutu(-G2 - 0.3, G2 + 0.3, SY + YD, SY + YD + 0.6, 0, 0.08), 0, pah=0.015)        # önündeki taş eşik
nesne('Somine_Govde', bm, [M['somine']], K_SOM)
bm = bmesh.new()                                                                          # ahşap şömine rafı (kalın kiriş)
P(bm, b_kutu(-G2 - 0.12, G2 + 0.12, SY + YD - 0.12, SY + YD + 0.06, SOMINE_H - 0.02, SOMINE_H + 0.16), 0, pah=0.02, seg=2)
nesne('Somine_Raf', bm, [M['koyu']], K_SOM)
bm = bmesh.new(); P(bm, b_kutu(-G2 + 0.5, G2 - 0.5, SY + 0.32, SY + YD, 0, 0.03), 0); nesne('Somine_Ocak_Tabani', bm, [M['kul']], K_SOM)
# Kütükler, korlar, alevler (alevler ayrı nesne: site titretip boy attıracak)
bm = bmesh.new()
for p0, p1, r in (((-0.55, SY + 0.5, 0.08), (0.45, SY + 0.62, 0.08), 0.075), ((-0.35, SY + 0.75, 0.08), (0.6, SY + 0.48, 0.09), 0.07),
                  ((-0.1, SY + 0.45, 0.2), (0.25, SY + 0.78, 0.17), 0.06)):
    P(bm, b_arasi(p0, p1, r, n=10), 0, yumusak=True)
nesne('Somine_Kutukler', bm, [M['koyu']], K_SOM)
bm = bmesh.new()
for _ in range(26):
    b = b_kutu(-0.04, 0.04, -0.03, 0.03, 0.03, 0.03 + sus.uniform(0.015, 0.04)); dondur(b, sus.uniform(0, 180))
    bmesh.ops.translate(b, verts=b.verts, vec=(sus.uniform(-0.75, 0.75), SY + sus.uniform(0.4, 0.85), 0)); P(bm, b, 0)
nesne('korlar', bm, [M['kor']], K_SOM)
# Alevler: yassı, ucu kıvrık dil biçimleri (dümdüz koni "buz sarkıtı" gibi duruyordu). Şöminenin alevi mumunkinden daha turuncu ve daha az parlak.
M_ALEV_S = mat_duz('M_Alev_Somine', (0, 0, 0), 1.0, isik=(1.0, 0.36, 0.05), isik_guc=3.2)
for i in range(10):
    x = -0.6 + 1.2 * (i + sus.uniform(-0.3, 0.3)) / 9
    y = SY + sus.uniform(0.5, 0.75)
    h = sus.uniform(0.22, 0.6) * (1.15 - abs(x) / 1.2)            # ortadakiler daha uzun
    r = h * sus.uniform(0.18, 0.26)
    bm = bmesh.new()
    P(bm, b_torna(0, 0, [(0, r * 0.5), (h * 0.15, r), (h * 0.4, r * 0.85), (h * 0.65, r * 0.5), (h * 0.85, r * 0.2), (h, 0.002)], n=8), 0, yumusak=True)
    yon, buk = sus.uniform(0, 2 * math.pi), sus.uniform(0.04, 0.12)
    for v in bm.verts:                                              # yassılaştır, ucunu bir yana kıvır
        t = v.co.z / h
        v.co.y *= 0.6
        v.co.x += buk * t * t * math.cos(yon); v.co.y += buk * t * t * math.sin(yon) * 0.5
    nesne(f'alev_somine_{i + 1}', bm, [M_ALEV_S], K_SOM, konum=(x, y, 0.08))
ISIKLAR.insert(0, ('isik_somine', 0, SY + 0.6, 0.45))
bos('isik_somine', K_ISIK, 0, SY + 0.6, 0.45, boy=0.12, tur='SPHERE')

# Şömine önü oturma alanı: halı (resmin oranında), iki koltuk, alçak sehpa (üstünde mum ve kupa)
K_OTUR = koleksiyon('Somine_Oturma_Alani', K_SOM)
HALI_EN = 3.2; _h = resim('hali.png'); HALI_BOY = HALI_EN * _h.size[1] / _h.size[0]       # halı resminin oranında
OY = SY + YD + 0.6 + HALI_BOY / 2 + 0.02
kok_o = bos('Somine_Oturma_Alani', K_OTUR, 0, OY, boy=0.5)
def hali_uv(bm, uvl):                                   # halı resmi halının üstüne bir kez otursun
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (l.vert.co.x / HALI_EN + 0.5, l.vert.co.y / HALI_BOY + 0.5)
bm = bmesh.new(); P(bm, b_kutu(-HALI_EN / 2, HALI_EN / 2, -HALI_BOY / 2, HALI_BOY / 2, 0.0, 0.008))
oturma = [nesne('Somine_Hali', bm, [M['hali']], K_OTUR, konum=(0, OY, 0), aci=oyna(3), uv_ozel=hali_uv)]
for i, sx in enumerate((-1, 1)):
    kx, ky = sx * 1.15 + oyna(0.1), OY + 0.1 + oyna(0.1)
    yon = math.degrees(math.atan2(0 - kx, (SY + 0.5) - ky)) + oyna(6)
    oturma.append(kopya(f'Somine_Koltuk_{i + 1}', KOLTUK, K_OTUR, kx, ky, yon))
sx_ = oyna(0.1)
bm = bmesh.new()
P(bm, b_silindir(0, 0, 0.32, 0.40, 0.45, n=32), 0, pah=0.01, seg=2)
P(bm, b_silindir(0, 0, 0.05, 0.03, 0.40, n=8), 1)
P(bm, b_silindir(0, 0, 0.18, 0.0, 0.03, n=16), 1, pah=0.008)
oturma.append(nesne('Somine_Sehpa', bm, [M['masa'], M['ahsap']], K_OTUR, konum=(sx_, OY - 0.2, 0)))
for p in oturma: bagla(p, kok_o)
yeni_mum(sx_ - 0.08, OY - 0.2, 0.45, K_OTUR, kok_o)
SOMINE_ISIKLARI = {'isik_somine', ISIKLAR[-1][0]}       # şömineyle birlikte taşınacak ışık işaretleri (sehpadaki mum dahil)
bm = bmesh.new(); kupa_kur(bm, sx_ + 0.12, OY - 0.15, 0.45, 200); bagla(nesne('Somine_Sehpa_Kupa', bm, [M['kalay'], M['bira']], K_OTUR), kok_o)

# ───────── 07 Dekor: güneybatıda, güney duvarının dibinde fıçı ve sandık köşesi ─────────
fici('Dekor_Fici_1', K_DEKOR, -6.1, -IC_Y + 0.5, 0.32, 0.95, 10)
fici('Dekor_Fici_2', K_DEKOR, -5.45, -IC_Y + 0.45, 0.3, 0.9, 40)
fici('Dekor_Fici_3', K_DEKOR, -5.8, -IC_Y + 1.05, 0.28, 0.85, 70)
bm = bmesh.new()
P(bm, b_kutu(-0.3, 0.3, -0.3, 0.3, 0, 0.55), 0, pah=0.012)
for z in (0.0, 0.5):
    P(bm, b_kutu(-0.31, 0.31, -0.31, 0.31, z, z + 0.05), 1, pah=0.006)
nesne('Dekor_Sandik', bm, [M['ahsap'], M['koyu']], K_DEKOR, konum=(-4.8, -IC_Y + 0.45, 0), aci=8)

# ───────── 05 Duvar aplikleri: direklere asılı demir kollu fenerler (her biri bir ışık işareti) ─────────
def aplik(x, y, yon):
    """yon: fenerin odaya baktığı yön (kuzeyden saat yönünde derece). Fener direğin önünde, 1,9 m yükseklikte."""
    no = len([a for a in ISIKLAR if a[0].startswith('isik_aplik')]) + 1
    bm = bmesh.new()
    P(bm, b_kutu(-0.05, 0.05, -0.02, 0.0, 1.7, 2.05), 0)                                 # direğe çakılı demir plaka
    P(bm, b_arasi((0, 0, 1.95), (0, 0.22, 1.95), 0.012, n=6), 0, yumusak=True)          # kol
    P(bm, b_arasi((0, 0, 1.78), (0, 0.18, 1.95), 0.008, n=6), 0, yumusak=True)          # destek
    P(bm, b_silindir(0, 0.22, 0.075, 1.72, 1.74, n=12), 0)                               # fener tabanı
    P(bm, b_silindir(0, 0.22, 0.065, 1.74, 1.90, n=12), 1, yumusak=True)                 # cam
    P(bm, b_silindir(0, 0.22, 0.08, 1.90, 1.97, n=12, r2=0.02), 0)                       # külah
    P(bm, b_torna(0, 0.22, [(1.74, 0.018), (1.80, 0.018)], n=8), 2)                      # mum
    ob = nesne(f'Aplik_{no}', bm, [M['demir'], M['fener'], M['mum']], K_APLIK, konum=(x, y, 0), aci=yon)
    a = math.radians(yon); fx, fy = x + 0.22 * math.sin(a), y + 0.22 * math.cos(a)
    bm = bmesh.new(); P(bm, b_torna(0, 0, [(0, 0.005), (0.01, 0.009), (0.025, 0.006), (0.04, 0.001)], n=8), 0, yumusak=True)
    alev = nesne(f'alev_aplik_{no}', bm, [M['alev']], K_APLIK, konum=(fx, fy, 1.80))
    isaret = bos(f'isik_aplik_{no}', K_APLIK, fx, fy, 1.84, boy=0.08, tur='SPHERE')
    bagla(alev, ob); bagla(isaret, ob)
    ISIKLAR.append((f'isik_aplik_{no}', fx, fy, 1.84))
for y in DIREK_BATI:
    aplik(-IC_X + 0.22, y, 90)                         # batı duvarı direkleri, odaya (doğuya) bakar
for y in DIREK_DOGU:
    aplik(IC_X - 0.22, y, 270)                         # doğu duvarı
for x in DIREK_GUNEY:
    aplik(x, -IC_Y + 0.22, 0)                          # güney duvarı, kuzeye bakar

# ───────── 08 Tavan: tahta tavan ve kalın kirişler (tepeden bakan kamerada gizli) ─────────
bm = bmesh.new()
P(bm, b_kutu(-DIS_X, DIS_X, -DIS_Y, DIS_Y, DH + 0.18, DH + 0.24), 0)
x = -IC_X + 1.2
while x < IC_X:
    P(bm, b_kutu(x - 0.13, x + 0.13, -IC_Y, IC_Y, DH - 0.12, DH + 0.18), 1, pah=0.02)
    x += 2.2
nesne('Tavan', bm, [M['zemin'], M['koyu']], K_TAVAN)

# ───────── 09 Yeni parçalar (örnek fotoğraftan; yerleri 2026-10-15'te onaylandı, dokulu) ─────────
# Sarkıt fenerler, halka avize, kılıç-kalkanlar, tabela ve kalkanlar, görev panosu, harita, sancaklar, kitaplık,
# silah askısı, tabak rafı, trofe, ozan köşesi, erzak, odun yığını ve yeşillik (yaprak kartlarıyla).
import json
K_YENI = koleksiyon('09_Yeni', K)
K_SARKIT, K_AVIZE, K_SUS, K_PANO, K_EK, K_YESIL = (koleksiyon(a, K_YENI) for a in
                                                   ('Sarkit_Fenerler', 'Avize', 'Duvar_Susleri', 'Gorev_Panosu', 'Ek_Icerik', 'Yesillik'))
ETIKET = []                                    # (metin, x, y) tepeden önizlemedeki etiketler
TAVAN_Z = DH + 0.18                            # tavan tahtalarının alt yüzü
UVS.update({'M_Demir_Dovme': 0.3, 'M_Cuval': 0.4, 'M_Saksi': 0.4, 'M_Sarmasik': 0.5})
M.update({
    'dovme':   mat_doku('M_Demir_Dovme', 'demir', metal=0.75),
    'cuval':   mat_doku('M_Cuval', 'cuval'),
    'saksi':   mat_doku('M_Saksi', 'saksi-toprak'),
    'sarmasik': mat_doku('M_Sarmasik', 'sarmasik', normal_guc=1.2),
    'yaprak':  mat_doku('M_Yaprak', 'yaprak-kartlari', puruz=False, puruz_sabit=0.55, alfa=True),
    'kuru_ot': mat_doku('M_Kuru_Ot', 'yaprak-kartlari', carpan=(0.85, 0.62, 0.32), puruz=False, puruz_sabit=0.85, alfa=True),
    'kalkan1': mat_doku('M_Kalkan_1', 'kalkan-1', puruz=False, puruz_sabit=0.65, alfa=True),
    'kalkan2': mat_doku('M_Kalkan_2', 'kalkan-2', puruz=False, puruz_sabit=0.65, alfa=True),
    'tabela':  mat_doku('M_Tabela', 'tabela', puruz=False, puruz_sabit=0.6, alfa=True),
    'sancak':  mat_doku('M_Sancak', 'sancak', puruz=False, puruz_sabit=0.9, alfa=True),
    'harita':  mat_doku('M_Harita', 'harita'),
    'pano':    mat_doku('M_Gorev_Panosu', 'gorev-panosu'),
    'kitap':   mat_doku('M_Kitaplar', 'kitap-sirtlari'),
    'celik':   mat_duz('M_Celik', (0.55, 0.56, 0.58), 0.28, 1.0),
    'kemik':   mat_duz('M_Kemik', (0.62, 0.55, 0.42), 0.6),
    'toprak':  mat_duz('M_Toprak', (0.06, 0.045, 0.03), 1.0),
    'seramik': mat_duz('M_Seramik', (0.72, 0.67, 0.58), 0.35),
})
def oran(dosya):
    """Resmin eni / boyu (parçanın ölçüsü resme uysun)."""
    im = resim(dosya); return im.size[0] / im.size[1]

def uv_duz(mi_set, x0, x1, z0, z1):
    """Duvara asılan görsellerin UV'si: önden bakınca resim parçanın üstüne bir kez oturur (x → u, z → v)."""
    def f(bm, uvl):
        for fc in bm.faces:
            if fc.material_index in mi_set:
                for l in fc.loops:
                    l[uvl].uv = ((l.vert.co.x - x0) / (x1 - x0), (l.vert.co.z - z0) / (z1 - z0))
    return f

def b_levha(x0, x1, z0, z1, y=0.0):
    """Önü +y'ye bakan ince düz yüzey (görsel yapıştırmak için)."""
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1))]
    f = bm.faces.new(vs); f.normal_update()
    if f.normal.y < 0: f.normal_flip()                               # önü +y'ye baksın
    return bm

# ───────── Yaprak kartları ─────────
# Saydam yaprak dalı resmi yapıştırılmış ince düz yüzeyler. Oyunlarda bitkiler böyle yapılır: hafif ama gerçekçi.
# Atlas 3×3: 0–2 sarkan sarmaşık, 3–5 pothos (sarkan), 6–8 eğrelti (yukarı büyür). Kutular doku_hazirla.py'den.
KUTU = json.load(open(os.path.join(DOKU, 'yaprak-kartlari.json'), encoding='utf-8'))['kutular']

def b_kart(hucre, boy, ust, yon, egim, sarkan=True, ters=False):
    """hucre: atlas hücresi. boy: kartın boyu (m). ust: tutunduğu nokta. yon: kartın dışa baktığı yön (kuzeyden saat yönünde).
    egim: dikeyden dışarı yatıklık (derece). sarkan: dal tutunduğu yerden aşağı sarkar; değilse yukarı büyür.
    ters: resmi ters çevirir (kuru ot demetleri baş aşağı asılır)."""
    u0, v0, u1, v1 = KUTU[hucre]
    w = boy * (u1 - u0) / (v1 - v0)
    vu, va = (v0, v1) if not ters else (v1, v0)                      # resmin üst ve alt kenarı
    if sarkan: P_ = [(-w / 2, 0, 0, u0, va), (w / 2, 0, 0, u1, va), (w / 2, 0, -boy, u1, vu), (-w / 2, 0, -boy, u0, vu)]
    else:      P_ = [(-w / 2, 0, 0, u0, vu), (w / 2, 0, 0, u1, vu), (w / 2, 0, boy, u1, va), (-w / 2, 0, boy, u0, va)]
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap')
    f = bm.faces.new([bm.verts.new(p[:3]) for p in P_])
    for l, p in zip(f.loops, P_): l[uvl].uv = (p[3], p[4])
    T = Matrix.Translation(ust) @ Matrix.Rotation(-math.radians(yon), 4, 'Z') @ Matrix.Rotation(math.radians(egim) * (1 if sarkan else -1), 4, 'X')
    bmesh.ops.transform(bm, matrix=T, verts=bm.verts)
    return bm

def obek(bm, x, y, z, r, mi):
    """Yaprak öbeği: sarmaşık dokulu, hafif basık yuvarlak gövde (kartların içini doldurur)."""
    P(bm, b_torna(x, y, [(z - r * 0.75, r * 0.12), (z - r * 0.45, r * 0.85), (z, r), (z + r * 0.45, r * 0.8), (z + r * 0.75, r * 0.12)], n=10), mi, yumusak=True)

def saksi(ad, x, y, boy=1.3, r=0.28, z0=0.0, kart=10):
    """Saksı bitkisi: pişmiş toprak saksı, toprak, ortada yaprak öbeği, çevresinde yukarı büyüyen eğrelti ve saksıdan sarkan pothos."""
    bm = bmesh.new()
    P(bm, b_torna(0, 0, [(0, r * 0.72), (r * 1.3, r), (r * 1.38, r * 1.08), (r * 1.55, r * 1.08), (r * 1.55, r * 1.0)], n=16, ust=False), 0, yumusak=True)
    P(bm, b_silindir(0, 0, r * 0.98, r * 1.3, r * 1.36, n=16), 1)
    g = boy - r * 1.4
    obek(bm, 0, 0, r * 1.4 + g * 0.3, max(r * 0.8, g * 0.28), 2)
    for i in range(kart):
        a = 360 * i / kart + sus.uniform(-15, 15)
        if i % 3 == 2:                                                  # saksının kenarından sarkan pothos
            ra = math.radians(a); P(bm, b_kart(sus.choice((3, 4, 5)), sus.uniform(0.6, 1.0) * max(g, 0.25) * 0.8,
                                              (r * math.sin(ra), r * math.cos(ra), r * 1.5), a, sus.uniform(10, 25)), 3)
        else:                                                           # yukarı ve dışarı büyüyen eğrelti
            ra = math.radians(a); P(bm, b_kart(sus.choice((6, 7, 8)), sus.uniform(0.8, 1.1) * max(g, 0.25),
                                              (0.3 * r * math.sin(ra), 0.3 * r * math.cos(ra), r * 1.35), a, sus.uniform(15, 45), sarkan=False), 3)
    nesne(ad, bm, [M['saksi'], M['toprak'], M['sarmasik'], M['yaprak']], K_YESIL, konum=(x, y, z0), koru={3})

def sarkan_saksi(ad, x, y, z=2.3):
    """Tavandan üç zincirle sarkan saksı; kenarından aşağı dökülen sarmaşık ve pothos."""
    bm = bmesh.new()
    for i in range(3):
        a = 2 * math.pi * i / 3
        P(bm, b_arasi((0.17 * math.cos(a), 0.17 * math.sin(a), z + 0.18), (0, 0, z + 0.55), 0.004, n=4), 1)
    P(bm, b_arasi((0, 0, z + 0.55), (0, 0, TAVAN_Z), 0.006, n=4), 1)
    P(bm, b_torna(0, 0, [(z, 0.08), (z + 0.04, 0.14), (z + 0.17, 0.18), (z + 0.19, 0.18)], n=14, ust=False), 0, yumusak=True)
    obek(bm, 0, 0, z + 0.19, 0.2, 2)
    for i in range(8):
        a = 360 * i / 8 + sus.uniform(-15, 15); ra = math.radians(a)
        P(bm, b_kart(sus.choice((0, 1, 2, 3, 4)), sus.uniform(0.5, 0.95), (0.16 * math.sin(ra), 0.16 * math.cos(ra), z + 0.2), a, sus.uniform(4, 18)), 3)
    nesne(ad, bm, [M['saksi'], M['dovme'], M['sarmasik'], M['yaprak']], K_YESIL, konum=(x, y, 0), koru={3})

def sarmasik(ad, x, y, z0, z1, disari):
    """Ahşap direğe sarılan sarmaşık: direğin çevresinde sarmal yaprak öbekleri ve aralardan sarkan dallar.
    disari: odanın içine bakan yön (kartlar o yöne döner)."""
    bm = bmesh.new(); z, a = z0, sus.uniform(0, 6.28)
    while z < z1:
        r = sus.uniform(0.045, 0.07)                                   # küçük öbek (top gibi durmasın), çoğunluk yaprak kartı
        obek(bm, 0.19 * math.cos(a), 0.19 * math.sin(a), z, r, 0)
        if sus.random() < 0.85:
            P(bm, b_kart(sus.choice((0, 1, 2)), sus.uniform(0.3, 0.55), (0.2 * math.cos(a), 0.2 * math.sin(a), z + 0.05), disari + sus.uniform(-50, 50), sus.uniform(5, 20)), 1)
        z += sus.uniform(0.12, 0.2); a += sus.uniform(0.8, 1.3)
    nesne(ad, bm, [M['sarmasik'], M['yaprak']], K_YESIL, konum=(x, y, 0), koru={1})

# ───────── Sarkıt fenerler ─────────
def sarkit(ad, x, y, z_alt, kol):
    """Zincirle tavandan sarkan altıgen dövme demir fener: külah, altı dikme, içten parlayan camlar, mum ve alev."""
    bm = bmesh.new()
    P(bm, b_arasi((0, 0, z_alt + 0.46), (0, 0, TAVAN_Z), 0.007, n=4), 0)                     # zincir
    P(bm, b_torna(0, 0, [(z_alt + 0.44, 0.0), (z_alt + 0.46, 0.028), (z_alt + 0.5, 0.02)], n=8, alt=False), 0)   # askı halkası
    P(bm, b_silindir(0, 0, 0.14, z_alt + 0.32, z_alt + 0.44, n=3, r2=0.025), 0, pah=0.005)   # külah (altıgen)
    P(bm, b_silindir(0, 0, 0.14, z_alt, z_alt + 0.035, n=3), 0, pah=0.004)                    # taban
    for i in range(6):
        a = math.radians(60 * i)
        P(bm, b_arasi((0.125 * math.cos(a), 0.125 * math.sin(a), z_alt + 0.03), (0.125 * math.cos(a), 0.125 * math.sin(a), z_alt + 0.33), 0.009, n=4), 0)
    P(bm, b_silindir(0, 0, 0.118, z_alt + 0.035, z_alt + 0.32, n=3), 1)                       # camlar (içindeki mumla parlar)
    P(bm, b_silindir(0, 0, 0.02, z_alt + 0.035, z_alt + 0.12, n=8), 2)                        # mum
    nesne(ad, bm, [M['dovme'], M['fener'], M['mum']], kol, konum=(x, y, 0))
    bm = bmesh.new(); P(bm, b_torna(0, 0, [(0, 0.004), (0.01, 0.009), (0.025, 0.007), (0.04, 0.001)], n=8), 0, yumusak=True)
    nesne('alev_' + ad.lower(), bm, [M['alev']], kol, konum=(x, y, z_alt + 0.12))
    bos('isik_' + ad.lower(), kol, x, y, z_alt + 0.18, boy=0.08, tur='SPHERE')
    ISIKLAR.append(('isik_' + ad.lower(), x, y, z_alt + 0.18))

for i, x in enumerate((-(BAR_X - 1.2), -2.2, 2.2, BAR_X - 1.2)):
    sarkit(f'Sarkit_Bar_{i + 1}', x, (TEZ_Y0 + TEZ_Y1) / 2, 2.05, K_SARKIT)
for ad, x, y, kok, kol in YAN_MASALAR:
    sarkit(f'Sarkit_{ad}', x, y, 1.95, K_SARKIT)
ETIKET += [('Sarkıt fenerler (bar üstü, 4)', 0, TEZ_Y0 - 0.9)] + [('Sarkıt fener', x, y - 0.55) for _, x, y, _, _ in YAN_MASALAR]

# ───────── Halka avize (tepeden bakan kamerada gizli; göz hizasında görünür) ─────────
bm = bmesh.new(); AR, AZ = 0.65, 2.4
nokt = [(AR * math.cos(2 * math.pi * i / 24), AR * math.sin(2 * math.pi * i / 24)) for i in range(24)]
for i in range(24):
    (x0, y0), (x1, y1) = nokt[i], nokt[(i + 1) % 24]
    P(bm, b_arasi((x0, y0, AZ), (x1, y1, AZ), 0.022, n=8), 0, yumusak=True)                  # demir çember
for i in range(3):
    a = 2 * math.pi * i / 3
    P(bm, b_arasi((AR * math.cos(a), AR * math.sin(a), AZ), (0, 0, AZ + 0.55), 0.006, n=4), 0)
P(bm, b_arasi((0, 0, AZ + 0.55), (0, 0, TAVAN_Z), 0.009, n=4), 0)
MUMLAR_AVIZE = []
for i in range(6):
    a = 2 * math.pi * (i + 0.5) / 6; cx, cy = AR * math.cos(a), AR * math.sin(a)
    P(bm, b_torna(cx, cy, [(AZ, 0.04), (AZ + 0.012, 0.045), (AZ + 0.02, 0.028)], n=12), 0, yumusak=True)   # mum tablası
    h = sus.uniform(0.08, 0.14)
    P(bm, b_torna(cx, cy, [(AZ + 0.02, 0.019), (AZ + 0.02 + h, 0.019), (AZ + 0.026 + h, 0.016), (AZ + 0.022 + h, 0.009)], n=10), 1, yumusak=True)
    MUMLAR_AVIZE.append((cx, cy, AZ + 0.028 + h))
nesne('Avize_Orta', bm, [M['dovme'], M['mum']], K_AVIZE)
for i, (cx, cy, cz) in enumerate(MUMLAR_AVIZE):
    bm = bmesh.new(); P(bm, b_torna(0, 0, [(0, 0.003), (0.008, 0.007), (0.02, 0.009), (0.032, 0.006), (0.045, 0.0005)], n=8), 0, yumusak=True)
    nesne(f'alev_avize_{i + 1}', bm, [M['alev']], K_AVIZE, konum=(cx, cy, cz))
bos('isik_avize', K_AVIZE, 0, 0, AZ + 0.15, boy=0.1, tur='SPHERE'); ISIKLAR.append(('isik_avize', 0, 0, AZ + 0.15))
ETIKET.append(('(Avize tepeden gizli)', 0, AR + 0.35))

# ───────── Duvar süsleri ─────────
def duvar_parcasi(ad, kol, x, y, yon, kur, mats, uv=None):
    """Duvara asılan parça. Yerel düzen: duvar yüzü y=0, parça +y yönünde odaya bakar; yon ile döndürülür."""
    bm = bmesh.new(); kur(bm); return nesne(ad, bm, mats, kol, konum=(x, y, 0), aci=yon, uv_ozel=uv)

def kalkan_kilic(zc, r, kalkan):
    """Çapraz iki kılıç ve önlerinde yuvarlak kalkan. Malzeme: 0 çelik, 1 demir, 2 deri, 3 ahşap, 4 kalkan resmi."""
    def kur(bm):
        for aci in (-34, 34):
            parcalar = [(b_kutu(-0.022, 0.022, 0.02, 0.03, zc - 0.33, zc + 0.5), 0),        # namlu
                        (b_kutu(-0.13, 0.13, 0.012, 0.038, zc - 0.36, zc - 0.33), 1),       # balçak
                        (b_kutu(-0.018, 0.018, 0.014, 0.036, zc - 0.52, zc - 0.36), 2),     # kabza (deri sarılı)
                        (b_kutu(-0.03, 0.03, 0.01, 0.04, zc - 0.57, zc - 0.52), 1)]         # topuz
            for bb, mi in parcalar:
                bmesh.ops.rotate(bb, verts=bb.verts, cent=(0, 0, zc), matrix=Matrix.Rotation(math.radians(aci), 3, 'Y')); P(bm, bb, mi, pah=0.003)
        P(bm, b_arasi((0, 0.04, zc), (0, 0.085, zc), r * 0.99, n=32), 3)                    # kalkanın ahşap gövdesi
        P(bm, b_arasi((0, 0.085, zc), (0, 0.088, zc), r, n=32), 4)                          # boyalı yüz (resim)
        P(bm, b_arasi((0, 0.088, zc), (0, 0.13, zc), r * 0.2, n=16, r2=r * 0.07), 1, yumusak=True)   # ortadaki demir tümsek
    return kur, uv_duz({4}, -r, r, zc - r, zc + r), [M['celik'], M['dovme'], M['deri'], M['ahsap'], M[kalkan]]

kur, uv, mats = kalkan_kilic(2.4, 0.32, 'kalkan1')
duvar_parcasi('Kalkan_Kilic_Somine', K_SUS, 0, SY + 0.45, 0, kur, mats, uv)
kur, uv, mats = kalkan_kilic(1.9, 0.36, 'kalkan2')
duvar_parcasi('Kalkan_Kilic_Bati', K_SUS, -IC_X, -1.5, 90, kur, mats, uv)
ETIKET += [('Kılıç-kalkan (şömine bacası)', 0, SY + 1.15), ('Kılıç-kalkan (batı duvarı)', -IC_X + 1.6, 1.5)]
# Barın üstünde, duvarda 4 yuvarlak kalkan (iki desen sırayla)
for i, x in enumerate((-5.25, -1.85, 1.85, 5.7)):                 # kuzey duvarındaki direklerin arasında
    r = 0.26
    def kur(bm, r=r):
        P(bm, b_arasi((0, 0, 2.6), (0, 0.045, 2.6), r * 0.99, n=32), 0)
        P(bm, b_arasi((0, 0.045, 2.6), (0, 0.048, 2.6), r, n=32), 2)
        P(bm, b_arasi((0, 0.048, 2.6), (0, 0.085, 2.6), r * 0.2, n=16, r2=r * 0.07), 1, yumusak=True)
    duvar_parcasi(f'Kalkan_Bar_{i + 1}', K_SUS, x, IC_Y, 180, kur, [M['ahsap'], M['dovme'], M['kalkan1' if i % 2 == 0 else 'kalkan2']],
                  uv_duz({2}, -r, r, 2.6 - r, 2.6 + r))
# Taverna tabelası: barmen koridorunun üstünde, tavandan iki zincirle asılı; iki yüzünde de resim
TW = 1.6; TH = TW / oran('tabela.png'); TZ = 2.86 - TH
def tabela(bm):
    P(bm, b_kutu(-TW / 2 + 0.06, TW / 2 - 0.06, -0.015, 0.015, TZ + 0.05, TZ + TH - 0.05), 0)       # ahşap gövde
    P(bm, b_levha(-TW / 2, TW / 2, TZ, TZ + TH, 0.018), 2)                                          # ön yüz
    b = b_levha(-TW / 2, TW / 2, TZ, TZ + TH, 0.018); dondur(b, 180); P(bm, b, 3)                   # arka yüz
    for s in (-1, 1):
        P(bm, b_arasi((s * TW * 0.38, 0, TZ + TH - 0.03), (s * TW * 0.38, 0, TAVAN_Z), 0.006, n=4), 1)
def tabela_uv(bm, uvl):                         # arka yüzde resim ayna gibi ters görünmesin diye u tersine çevrilir
    for fc in bm.faces:
        if fc.material_index in (2, 3):
            for l in fc.loops:
                u = (l.vert.co.x + TW / 2) / TW
                l[uvl].uv = (u if fc.material_index == 2 else 1 - u, (l.vert.co.z - TZ) / TH)
duvar_parcasi('Tabela_Bar', K_SUS, 0, (RAF_Y0 + TEZ_Y1) / 2, 180, tabela, [M['koyu'], M['dovme'], M['tabela'], M['tabela']], tabela_uv)
ETIKET.append(('Tabela (asılı) + 4 kalkan (duvarda)', 0, IC_Y - 0.25))

# ───────── Görev panosu ve harita (doğu duvarı) ─────────
PW = 1.4; PH = PW / oran('gorev-panosu.jpg'); PZ = 0.95
def pano(bm):
    P(bm, b_kutu(-PW / 2, PW / 2, 0.0, 0.035, PZ, PZ + PH), 0)
    P(bm, b_levha(-PW / 2, PW / 2, PZ, PZ + PH, 0.036), 1)
    for x0, x1, z0, z1 in ((-PW / 2 - 0.06, PW / 2 + 0.06, PZ - 0.06, PZ), (-PW / 2 - 0.06, PW / 2 + 0.06, PZ + PH, PZ + PH + 0.06),
                           (-PW / 2 - 0.06, -PW / 2, PZ - 0.06, PZ + PH + 0.06), (PW / 2, PW / 2 + 0.06, PZ - 0.06, PZ + PH + 0.06)):
        P(bm, b_kutu(x0, x1, 0.0, 0.07, z0, z1), 0, pah=0.008)
    for s in (-1, 1):                                                                                 # küçük çatı
        b = b_kutu(min(0, s * (PW / 2 + 0.15)), max(0, s * (PW / 2 + 0.15)), 0.0, 0.24, PZ + PH + 0.06, PZ + PH + 0.1)
        bmesh.ops.rotate(b, verts=b.verts, cent=(0, 0, PZ + PH + 0.08), matrix=Matrix.Rotation(math.radians(-s * 22), 3, 'Y')); P(bm, b, 0, pah=0.006)
duvar_parcasi('Gorev_Panosu', K_PANO, IC_X, -IC_Y + 0.75, 270, pano, [M['koyu'], M['pano']], uv_duz({1}, -PW / 2, PW / 2, PZ, PZ + PH))
ETIKET.append(('Görev panosu', IC_X - 1.2, -4.0))
HW = 2.0; HH = HW / oran('harita.jpg'); HZ = 0.95
def harita(bm):
    P(bm, b_levha(-HW / 2, HW / 2, HZ, HZ + HH, 0.03), 1)
    P(bm, b_kutu(-HW / 2, HW / 2, 0.0, 0.028, HZ, HZ + HH), 0)
    for x0, x1, z0, z1 in ((-HW / 2 - 0.06, HW / 2 + 0.06, HZ + HH, HZ + HH + 0.06), (-HW / 2 - 0.06, HW / 2 + 0.06, HZ - 0.06, HZ),
                           (-HW / 2 - 0.06, -HW / 2, HZ - 0.06, HZ + HH + 0.06), (HW / 2, HW / 2 + 0.06, HZ - 0.06, HZ + HH + 0.06)):
        P(bm, b_kutu(x0, x1, 0.0, 0.055, z0, z1), 0, pah=0.008)
duvar_parcasi('Duvar_Haritasi', K_PANO, -IC_X, 1.5, 90, harita, [M['koyu'], M['harita']], uv_duz({1}, -HW / 2, HW / 2, HZ, HZ + HH))   # batı duvarı (doğuda şömine var)
ETIKET.append(('Büyük harita (batı duvarı)', -IC_X + 1.9, 1.95))

# ───────── Yeşillik ─────────
KIRISLER, _x = [], -IC_X + 1.2                   # tavan kirişlerinin x'leri (tavanla aynı hesap)
while _x < IC_X: KIRISLER.append(_x); _x += 2.2
sarkan_saksi('Bitki_Sarkan_Bati', -IC_X + 0.8, TEZ_Y0 - 0.9)
sarkan_saksi('Bitki_Sarkan_Dogu', IC_X - 0.8, TEZ_Y0 - 0.9)
sarkan_saksi('Bitki_Sarkan_Somine_Bati', -2.4, OY + 0.3, 2.25)
sarkan_saksi('Bitki_Sarkan_Somine_Dogu', 2.4, OY + 0.3, 2.25)
saksi('Bitki_Giris', K1 + 0.9, -IC_Y + 0.6, 1.55, 0.3, kart=12)
saksi('Bitki_Somine_Bati', -3.05, -IC_Y + 0.5, 1.3, kart=11)
saksi('Bitki_Kose_GB', -IC_X + 0.6, -IC_Y + 0.6, 1.6, 0.32, kart=12)
saksi('Bitki_Ozan', -IC_X + 0.55, -0.55, 1.0, 0.24)
for ad, x, y, kok, kol in YAN_MASALAR:
    saksi(f'Bitki_{ad}', x + 0.28, y - 0.12, 0.34, 0.07, z0=MASA_Z, kart=6)
for i, x in enumerate((-BAR_X + 0.5, BAR_X - 0.5)):
    saksi(f'Bitki_Tezgah_{i + 1}', x, (TEZ_Y0 + TEZ_Y1) / 2, 0.55, 0.1, z0=TEZGAH_H, kart=8)
sarmasik('Sarmasik_Kapi_Bati', K0 - 0.12, -IC_Y + 0.06, 0.2, DH, 0)
sarmasik('Sarmasik_Kapi_Dogu', K1 + 0.12, -IC_Y + 0.06, 0.2, DH, 0)
sarmasik('Sarmasik_Dogu', IC_X - 0.1, -IC_Y + 0.06, 0.3, DH, 315)            # güneydoğu köşe direği
for x in (-3.7, 3.7):
    sarmasik(f'Sarmasik_Bar_{"Bati" if x < 0 else "Dogu"}', x, IC_Y - 0.06, 2.3, DH, 180)
# Bar üstündeki kirişlerde sarmaşık: kiriş boyunca öbekler ve aralarından sarkan dallar (güneye, oyun masasına dönük)
for xk in [min(KIRISLER, key=lambda k: abs(k - h)) for h in (-6.0, -2.0, 2.0, 6.0)]:
    bm = bmesh.new(); y = TEZ_Y0 - 0.4
    while y < RAF_Y0:
        obek(bm, sus.uniform(-0.05, 0.05), y, DH - 0.16, sus.uniform(0.08, 0.13), 0)
        if sus.random() < 0.5:
            P(bm, b_kart(sus.choice((0, 1, 2, 3)), sus.uniform(0.4, 0.85), (0, y, DH - 0.18), sus.choice((180, 0)) + sus.uniform(-35, 35), sus.uniform(0, 12)), 1)
        y += sus.uniform(0.2, 0.32)
    nesne(f'Sarmasik_Kiris_{xk:+.1f}', bm, [M['sarmasik'], M['yaprak']], K_YESIL, konum=(xk, 0, 0), koru={1})
# Kuru ot demetleri: barmen koridorunun üstünde, kirişlerden baş aşağı (eğrelti kartları, kurumuş renkte)
bm = bmesh.new()
for xk in KIRISLER:
    if abs(xk) > IC_X - 0.6: continue
    for dy in (-0.25, 0.25):
        yy = (RAF_Y0 + TEZ_Y1) / 2 + dy + sus.uniform(-0.08, 0.08); boy = sus.uniform(0.3, 0.45)
        P(bm, b_arasi((0, yy, DH - 0.12), (0, yy, DH - 0.2), 0.005, n=4), 0)
        for k in range(3):
            P(bm, b_kart(sus.choice((6, 7, 8)), boy, (0, yy, DH - 0.18), 60 * k + sus.uniform(-20, 20), sus.uniform(2, 10), sarkan=True, ters=True), 1)
    nesne(f'Kuru_Ot_{xk:+.1f}', bm, [M['koyu'], M['kuru_ot']], K_YESIL, konum=(xk, 0, 0), koru={1}); bm = bmesh.new()
ETIKET += [('Bitki', -IC_X + 1.6, TEZ_Y0 - 1.4), ('Bitki', IC_X - 1.6, TEZ_Y0 - 1.4), ('Saksı', K1 + 0.9, -IC_Y + 1.25),
           ('Sarmaşık (kirişler)', 0, TEZ_Y1 + 0.35), ('Sarkan saksı', -2.4, OY + 0.85), ('Sarkan saksı', 2.4, OY + 0.85),
           ('Sarmaşık', K0 - 0.12, -IC_Y + 0.75), ('Sarmaşık', K1 + 0.12, -IC_Y + 0.75), ('Kuru ot demetleri (bar arkası)', -IC_X / 2, (RAF_Y0 + TEZ_Y1) / 2 + 0.6)]

# ───────── Ek içerik ─────────
def blok(ad, kur, mats, konum=(0, 0, 0), aci=0.0, uv=None):
    bm = bmesh.new(); kur(bm); return nesne(ad, bm, mats, K_EK, konum=konum, aci=aci, uv_ozel=uv)

def odun(bm):                                    # şöminenin doğu yanında, duvara dayalı üç sıra kütük
    for sira, adet in enumerate((5, 4, 3)):
        for i in range(adet):
            x = 0.07 + 0.14 * i + 0.07 * sira; z = 0.07 + 0.125 * sira
            P(bm, b_arasi((x, 0.0, z), (x + sus.uniform(-0.02, 0.02), 0.5, z), 0.066, n=10), 0, yumusak=True)
blok('Odun_Yigini', odun, [M['ahsap']], (G2 + 0.4, SY + 0.05, 0))
ETIKET.append(('Odun yığını', G2 + 0.95, SY + 0.85))

def kitaplik(bm):                                # şöminenin batı yanında: dört raf, deri ciltli kitaplar
    P(bm, b_kutu(-0.45, -0.42, 0.0, 0.36, 0.0, 1.9), 0, pah=0.006); P(bm, b_kutu(0.42, 0.45, 0.0, 0.36, 0.0, 1.9), 0, pah=0.006)
    P(bm, b_kutu(-0.45, 0.45, 0.0, 0.02, 0.0, 1.9), 0)
    for z in (0.0, 0.45, 0.9, 1.35, 1.86):
        P(bm, b_kutu(-0.45, 0.45, 0.0, 0.36, z, z + 0.04), 0, pah=0.005)
    for i, z in enumerate((0.04, 0.49, 0.94, 1.39)):
        P(bm, b_kutu(-0.42, 0.42, 0.04, 0.33, z, z + 0.33), 1)
def kitap_uv(bm, uvl):                           # her rafta resmin başka bir bölümü (aynı kitaplar alt alta görünmesin)
    for fc in bm.faces:
        if fc.material_index == 1:
            kat = min(3, int((fc.calc_center_median().z - 0.04) / 0.45))
            for l in fc.loops:
                p = l.vert.co
                l[uvl].uv = ((p.x + 0.42) / 0.84 * 0.62 + kat * 0.12, (p.z - (0.04 + 0.45 * kat)) / 0.33)
blok('Kitaplik', kitaplik, [M['ahsap'], M['kitap']], (-G2 - 0.95, SY, 0), uv=kitap_uv)
ETIKET.append(('Kitaplık', -G2 - 0.95, SY + 0.85))

def aski(bm):                                    # batı duvarında silah askısı: mızraklar, balta, küçük kalkan
    P(bm, b_kutu(-0.6, 0.6, 0.0, 0.05, 1.75, 1.85), 0, pah=0.006); P(bm, b_kutu(-0.6, 0.6, 0.0, 0.05, 0.25, 0.35), 0, pah=0.006)
    for x in (-0.42, -0.2):
        P(bm, b_arasi((x, 0.09, 0.3), (x, 0.09, 2.05), 0.017, n=8), 0, yumusak=True)
        P(bm, b_arasi((x, 0.09, 2.05), (x, 0.09, 2.3), 0.03, n=6, r2=0.002), 1)             # mızrak ucu
    P(bm, b_arasi((0.42, 0.09, 0.3), (0.42, 0.09, 1.75), 0.02, n=8), 0, yumusak=True)
    P(bm, b_kutu(0.43, 0.62, 0.075, 0.105, 1.45, 1.75), 1, pah=0.004)                      # balta ağzı
    P(bm, b_arasi((0.08, 0.06, 1.1), (0.08, 0.1, 1.1), 0.21, n=24), 3)                      # küçük kalkan gövdesi
    P(bm, b_arasi((0.08, 0.1, 1.1), (0.08, 0.103, 1.1), 0.215, n=24), 2)
duvar_parcasi('Silah_Askisi', K_EK, -IC_X, -4.0, 90, aski, [M['koyu'], M['celik'], M['kalkan2'], M['ahsap']], uv_duz({2}, 0.08 - 0.215, 0.08 + 0.215, 1.1 - 0.215, 1.1 + 0.215))
ETIKET.append(('Silah askısı (batı duvarı)', -IC_X + 1.9, -1.5))

def tabak_rafi(bm):                              # batı duvarında: iki raf, dik duran tabaklar ve toprak testiler
    for z in (1.5, 1.95):
        P(bm, b_kutu(-0.8, 0.8, 0.0, 0.25, z, z + 0.04), 0, pah=0.005)
        for x in (-0.7, 0.7):
            P(bm, b_kutu(x - 0.02, x + 0.02, 0.0, 0.2, z - 0.15, z), 0)                    # konsol
    for x in (-0.55, -0.2, 0.15):
        P(bm, b_arasi((x, 0.09, 1.68), (x, 0.12, 1.68), 0.13, n=24), 1, yumusak=True)
    for x in (0.45, 0.65):
        P(bm, b_torna(x, 0.12, [(1.54, 0.05), (1.6, 0.075), (1.68, 0.07), (1.74, 0.035), (1.78, 0.03)], n=14), 2, yumusak=True)
    for x in (-0.5, 0.0, 0.5):
        P(bm, b_torna(x, 0.12, [(1.99, 0.05), (2.03, 0.06), (2.1, 0.05), (2.14, 0.03)], n=12), 2, yumusak=True)
duvar_parcasi('Tabak_Rafi', K_EK, -0.9, -IC_Y, 0, tabak_rafi, [M['ahsap'], M['seramik'], M['saksi']])   # güney duvarı
ETIKET.append(('Tabak rafı (batı duvarı)', -IC_X + 1.8, -4.5))

bm = bmesh.new()                                 # boynuz trofesi: kapının içinde, lentonun üstündeki duvarda
P(bm, b_arasi((0, 0, 2.7), (0, 0.04, 2.7), 0.18, n=24), 0, pah=0.008)
for s in (-1, 1):
    P(bm, b_arasi((s * 0.05, 0.08, 2.75), (s * 0.35, 0.12, 2.95), 0.02, n=8, r2=0.012), 1, yumusak=True)
    P(bm, b_arasi((s * 0.22, 0.1, 2.86), (s * 0.3, 0.16, 3.0), 0.012, n=6, r2=0.005), 1, yumusak=True)
    P(bm, b_arasi((s * 0.3, 0.11, 2.92), (s * 0.48, 0.13, 2.97), 0.012, n=6, r2=0.005), 1, yumusak=True)
    P(bm, b_arasi((s * 0.12, 0.09, 2.8), (s * 0.18, 0.15, 2.66), 0.01, n=6, r2=0.004), 1, yumusak=True)
nesne('Boynuz_Trofe', bm, [M['koyu'], M['kemik']], K_EK, konum=(KAPI_X, -IC_Y, 0))
ETIKET.append(('Trofe (kapı üstü)', KAPI_X - 0.3, -3.4))

SW_ = 0.76; SH_ = SW_ / oran('sancak.png')
def sancak(bm):                                  # direkli kumaş sancak; kumaş hafif dalgalı
    P(bm, b_arasi((-0.45, 0.08, 2.75), (0.45, 0.08, 2.75), 0.02, n=8), 0, yumusak=True)
    for s in (-1, 1):
        P(bm, b_arasi((s * 0.45, 0.08, 2.75), (s * 0.49, 0.08, 2.75), 0.03, n=8), 1)                  # direğin uçlarındaki demir topuzlar
    b = bmesh.new(); uvl = b.loops.layers.uv.new('UVMap'); N_ = 10
    sat = []
    for j in range(N_ + 1):
        z = 2.74 - SH_ * j / N_; dy = 0.07 + 0.012 * math.sin(j * 1.3)
        sat.append([b.verts.new((-SW_ / 2, dy, z)), b.verts.new((SW_ / 2, dy, z))])
    for j in range(N_):
        f = b.faces.new((sat[j + 1][0], sat[j + 1][1], sat[j][1], sat[j][0]))
        for l in f.loops:
            l[uvl].uv = ((l.vert.co.x + SW_ / 2) / SW_, (l.vert.co.z - (2.74 - SH_)) / SH_)
    P(bm, b, 2)
for ad, x, y, yon in (('Sancak_Dogu', IC_X, 1.75, 270), ('Sancak_Guney', -IC_X + 1.5, -IC_Y, 0)):
    bm = bmesh.new(); sancak(bm); nesne(ad, bm, [M['koyu'], M['dovme'], M['sancak']], K_EK, konum=(x, y, 0), aci=yon, koru={2})
ETIKET += [('Sancak', IC_X - 1.0, -1.6), ('Sancak', -5.55, -IC_Y + 0.75)]

def ozan(bm):
    """Müzik sahnesi: yuvarlak, yükseltilmiş platform (SAHNE_R, SAHNE_H), önünde basamak, arkasında alçak korkuluk.
    Üstünde tabure, lavta, nota sehpası ve davul. Yerel düzende dinleyiciler tabureden nota sehpasına doğru (≈52°) taraftadır."""
    R, H = SAHNE_R, SAHNE_H
    P(bm, b_silindir(0, 0, R, 0.0, H, n=64), 0, pah=0.015, seg=2)                             # platform (tahta)
    P(bm, b_silindir(0, 0, R + 0.06, H - 0.08, H - 0.04, n=64), 4)                            # kenar çıtası
    ad = math.radians(52)
    for k in range(-3, 4):                                                                    # dinleyici tarafında yarım ay basamak
        a = ad + math.radians(14 * k)
        b = b_kutu(R - 0.05, R + 0.3, -0.24, 0.24, 0.0, H / 2); dondur(b, -math.degrees(a)); P(bm, b, 0, pah=0.01)
    ark = ad + math.pi                                                                        # arkada korkuluk
    nokt = [ark + math.radians(t) for t in range(-75, 76, 25)]
    for a in nokt:
        x, y = (R - 0.1) * math.cos(a), (R - 0.1) * math.sin(a)
        P(bm, b_arasi((x, y, H), (x, y, H + 0.8), 0.03, n=8), 1, yumusak=True)
    for a0, a1 in zip(nokt, nokt[1:]):
        P(bm, b_arasi(((R - 0.1) * math.cos(a0), (R - 0.1) * math.sin(a0), H + 0.78), ((R - 0.1) * math.cos(a1), (R - 0.1) * math.sin(a1), H + 0.78), 0.028, n=8), 1, yumusak=True)
    P(bm, b_silindir(0.1, -0.2, 0.17, H + 0.4, H + 0.45, n=20), 1, pah=0.006)                # tabure
    P(bm, b_silindir(0.1, -0.2, 0.15, H + 0.45, H + 0.47, n=20), 3, pah=0.006)
    for i in range(3):
        a = math.radians(120 * i + 30)
        P(bm, b_arasi((0.1 + 0.1 * math.cos(a), -0.2 + 0.1 * math.sin(a), H + 0.41), (0.1 + 0.16 * math.cos(a), -0.2 + 0.16 * math.sin(a), H), 0.016, n=8), 1, yumusak=True)
    P(bm, b_arasi((-0.25, 0.35, H), (-0.25, 0.3, H + 0.4), 0.015, n=6), 1)                     # lavta sehpası
    P(bm, b_torna(-0.25, 0.35, [(H + 0.35, 0.02), (H + 0.41, 0.13), (H + 0.53, 0.16), (H + 0.65, 0.13), (H + 0.73, 0.07), (H + 0.75, 0.04)], n=16), 2, yumusak=True)
    P(bm, b_arasi((-0.25, 0.35, H + 0.75), (-0.25, 0.35, H + 1.1), 0.022, n=8), 4, yumusak=True)   # sap
    P(bm, b_kutu(-0.29, -0.21, 0.32, 0.38, H + 1.1, H + 1.21), 4, pah=0.004)                 # burgu kafası
    P(bm, b_arasi((0.45, 0.25, H), (0.45, 0.25, H + 0.95), 0.012, n=6), 5)                    # nota sehpası
    P(bm, b_kutu(0.25, 0.65, 0.22, 0.25, H + 0.9, H + 1.2), 5)
    P(bm, b_torna(-0.55, -0.35, [(H, 0.2), (H + 0.05, 0.22), (H + 0.33, 0.22), (H + 0.36, 0.2)], n=24), 2, yumusak=True)   # davul gövdesi
    P(bm, b_silindir(-0.55, -0.35, 0.205, H + 0.36, H + 0.375, n=24), 3)                     # davul derisi
    for zz in (H + 0.06, H + 0.31):
        P(bm, b_torna(-0.55, -0.35, [(zz - 0.012, 0.226), (zz + 0.012, 0.226)], n=24, ust=False, alt=False), 5)   # demir çemberler
# Barın sağındaki boşlukta, kuzeydoğu köşesinde; dinleyicilere (odanın ortasına) dönük
SAHNE_X, SAHNE_Y = IC_X - SAHNE_R - 0.15, IC_Y - SAHNE_R - 0.25
_yon = math.degrees(math.atan2(-SAHNE_Y, -SAHNE_X)) - 52                  # yerel dinleyici yönünü odanın ortasına çevir
blok('Ozan_Kosesi', ozan, [M['zemin'], M['ahsap'], M['masa'], M['deri'], M['koyu'], M['dovme']], (SAHNE_X, SAHNE_Y, 0), aci=-_yon)
ETIKET.append(('Müzik sahnesi', SAHNE_X, SAHNE_Y - SAHNE_R - 0.3))

def erzak(bm):                                   # sancağın altında: üç çuval ve üst üste iki sandık
    for x, y, a in ((0.0, 0.0, 10), (0.55, -0.15, -25), (0.25, 0.4, 40)):
        b = b_torna(0, 0, [(0, 0.17), (0.12, 0.24), (0.32, 0.22), (0.45, 0.1), (0.52, 0.04), (0.56, 0.05)], n=14)
        for v in b.verts: v.co.y *= 0.75
        dondur(b, a); bmesh.ops.translate(b, verts=b.verts, vec=(x, y, 0)); P(bm, b, 0, yumusak=True)
    P(bm, b_kutu(-0.85, -0.25, -0.3, 0.3, 0.0, 0.5), 1, pah=0.012); P(bm, b_kutu(-0.8, -0.32, -0.25, 0.25, 0.5, 0.92), 1, pah=0.012)
    for z0 in (0.0, 0.45, 0.5, 0.87):
        P(bm, b_kutu(-0.86, -0.24, -0.31, 0.31, z0, z0 + 0.05), 2)
blok('Erzak_Kosesi', erzak, [M['cuval'], M['ahsap'], M['koyu']], (-IC_X + 0.75, -2.3, 0), aci=180)   # batı duvarı, kılıç-kalkanın altı
ETIKET.append(('Erzak', IC_X - 1.0, -0.15))

# ───────── Şömine doğu duvarına ─────────
# Şömine ve çevresi yukarıda güney duvarının ortasında kurulur; burada hepsi birlikte 90° döndürülüp doğu duvarına
# (SOMINE_Y noktasına, batıya bakacak şekilde) taşınır. Güney duvarındaki (x, −IC_Y + d) noktası → (IC_X − d, SOMINE_Y + x).
SOMINE_T = Matrix.Identity(4)
if SOMINE_DUVAR == 'dogu':
    SOMINE_T = Matrix.Translation((IC_X, SOMINE_Y, 0)) @ Matrix.Rotation(math.radians(90), 4, 'Z') @ Matrix.Translation((0, IC_Y, 0))
    bpy.context.view_layer.update()
    kume = set(K_SOM.all_objects) | {ob for ob in (bpy.data.objects.get(a) for a in (
        'isik_somine', 'Kalkan_Kilic_Somine', 'Kitaplik', 'Odun_Yigini', 'Bitki_Sarkan_Somine_Bati', 'Bitki_Sarkan_Somine_Dogu')) if ob}
    for o in kume:
        if o.parent not in kume: o.matrix_world = SOMINE_T @ o.matrix_world      # çocuklar ebeveynle birlikte gelir
    for i, (ad, x, y, z) in enumerate(ISIKLAR):
        if ad in SOMINE_ISIKLARI:
            p = SOMINE_T @ Vector((x, y, z)); ISIKLAR[i] = (ad, p.x, p.y, p.z)
def som(x, y, z): return tuple(SOMINE_T @ Vector((x, y, z)))

# ───────── 99 Önizleme: ışıklar ve kameralar ─────────
def isik(ad, konum, renk, guc, yaricap, golge=True):
    d = bpy.data.lights.new(ad, 'POINT'); d.color = renk; d.energy = guc; d.shadow_soft_size = yaricap; d.use_shadow = golge
    o = bpy.data.objects.new(ad, d); o.location = konum; K_ONI.objects.link(o)
isik('Onizleme_Somine', som(0, SY + 0.75, 0.55), (1.0, 0.42, 0.12), 700, 0.35)
isik('Onizleme_Somine_Oda', som(0, SY + 1.4, 1.1), (1.0, 0.5, 0.2), 500, 0.6)
GUC = {'aplik': 70, 'sarkit': 55, 'avize': 90}
for ad, x, y, z in ISIKLAR[1:]:
    tur = next((k for k in GUC if k in ad), None)               # fener ışıkları gölgesiz: fenerin kendi gövdesinden geçsin
    isik('Onizleme_' + ad, (x, y, z), (1.0, 0.58, 0.28), GUC.get(tur, 14), 0.03 if tur else 0.02, tur is None)
dunya = bpy.data.worlds.new('Dunya'); sahne.world = dunya
try: dunya.use_nodes = True
except Exception: pass
bg = dunya.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.06, 0.045, 0.03, 1); bg.inputs['Strength'].default_value = 1.6

sahne.render.engine = 'BLENDER_EEVEE'
ev = sahne.eevee
for ad, deger in (('use_raytracing', True), ('taa_render_samples', 48), ('use_shadows', True)):
    try: setattr(ev, ad, deger)
    except Exception: pass
try: sahne.view_settings.view_transform = 'Filmic'; sahne.view_settings.look = 'Medium High Contrast'
except Exception:
    try: sahne.view_settings.look = 'None'
    except Exception: pass
sahne.render.resolution_x, sahne.render.resolution_y = 1920, 1080
sahne.render.image_settings.file_format = 'PNG'

kam_u = bpy.data.cameras.new('Kamera_Ustten'); kam_u.type = 'ORTHO'; kam_u.ortho_scale = 2 * DIS_X; kam_u.clip_end = 60
cu = bpy.data.objects.new('Kamera_Ustten', kam_u); cu.location = (0, 0, 25); K_ONI.objects.link(cu)
# Göz hizası kameraları: oyun masasının çevresinden dört yöne (duvardaki süsler tepeden görünmediği için)
GOZ_KAMERALARI = {
    'kuzey': ((0.15, -ORTA_SANDALYE_R - 0.05, 1.18), (0.4, 3.2, 0.95)),     # bara doğru
    'guney': ((0.2, ORTA_SANDALYE_R + 0.1, 1.22), (KAPI_X - 2.0, -IC_Y, 1.45)),   # girişe ve tabak rafına doğru
    'dogu':  ((-1.6, -0.4, 1.25), (IC_X, SOMINE_Y, 1.3)),                        # şömineye doğru
    'bati':  ((-1.6, 0.3, 1.25), (-IC_X, 1.0, 1.6)),                         # batı duvarına doğru
}
kameralar = [(cu, USTTEN)]
for ad, (konum, bak) in GOZ_KAMERALARI.items():
    kd = bpy.data.cameras.new(f'Kamera_Goz_{ad}'); kd.lens = 24; kd.clip_start = 0.05
    ko = bpy.data.objects.new(f'Kamera_Goz_{ad.capitalize()}', kd); ko.location = konum; K_ONI.objects.link(ko)
    ko.rotation_euler = (Vector(bak) - Vector(konum)).to_track_quat('-Z', 'Y').to_euler()
    kameralar.append((ko, os.path.join(KOK, '3d', f'detay-goz-{ad}.png')))

for kam, yol in kameralar:
    K_TAVAN.hide_render = kam is cu                   # tepeden bakarken tavan görünmesin
    K_AVIZE.hide_render = kam is cu                   # avize de: tepeden oyun masasının üstünü kapatmasın (sitede de öyle)
    sahne.camera = kam; sahne.render.filepath = yol
    bpy.ops.render.render(write_still=True)
sahne.camera = cu; K_TAVAN.hide_render = False; K_AVIZE.hide_render = False

# Tepeden önizlemedeki etiketlerin yeri (0–1): blockout_etiketle.py okur
import json
with open(os.path.join(KOK, '3d', 'detay-etiketler.json'), 'w', encoding='utf-8') as f:
    json.dump({'etiketler': [{'metin': m, 'x': (x + DIS_X) / (2 * DIS_X), 'y': (DIS_Y - y) / (2 * DIS_Y)} for m, x, y in ETIKET],
               'oda_m': [round(2 * DIS_X, 2), round(2 * DIS_Y, 2)]}, f, ensure_ascii=False, indent=1)

for ekran in bpy.data.screens:
    for alan in ekran.areas:
        if alan.type == 'VIEW_3D':
            for sp in alan.spaces:
                if sp.type == 'VIEW_3D': sp.shading.type = 'MATERIAL'
bpy.data.meshes.remove(_GECICI)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True, relative_remap=True)
ucgen = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
print(f'Nesne: {len(bpy.data.objects)}, yüz (kopyalar dahil): {ucgen}, mum: {MUM_NO[0]}')
print('TAMAM')
