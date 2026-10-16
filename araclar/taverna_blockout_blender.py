# -*- coding: utf-8 -*-
"""
YENİ TAVERNA — BLOCKOUT (kaba taslak) Blender betiği
=====================================================
Blockout: dokusuz, düz renkli, basit kutu ve silindirlerle yerleşimi ve oranları kurmak.
Ayrıntı ve malzeme sonra gelir. Bu betik her çalıştığında her şeyi sıfırdan kurar.

Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --factory-startup --python araclar\\taverna_blockout_blender.py
  python araclar\\blockout_etiketle.py          (önizlemenin etiketli kopyası)

Çıktılar:
  3d/taverna-blockout.blend              kaynak dosya
  3d/blockout-onizleme.png               tam tepeden önizleme
  3d/blockout-etiketler.json             etiketlerin resimdeki yeri (blockout_etiketle.py okur)

Yerleşim (kuzey = ekranın üstü):
  • Ortada büyük yuvarlak oyun masası, kameranın tam ortasında. 9 sandalye (DM kuzeyde + 8 oyuncu).
  • Üç çaprazda (KB, KD, GB) birer küçük yuvarlak masa, her birinde 4 sandalye.
  • Kuzey duvarı boyunca baştan sona bar: arka raf, tezgâh, önünde boydan boya tabureler.
  • Güney duvarının ortasında şömine; sağ altta (eski GD masasının yerinde) geniş giriş kapısı.

Ölçüler METRE cinsindendir. Oda merkezi (0, 0) = ortadaki masanın merkezi = kameranın ortası.
  x doğuya (sağa), y kuzeye (yukarı) artar, z yukarı. Kameranın gördüğü alan 16:9'dur ve odayı (duvarlar dahil) tam kaplar.
  Aşağıdaki "AYARLAR" bölümündeki sayıları değiştirip betiği yeniden çalıştırmak yerleşimi değiştirmeye yeter.

Blender'daki düzen (Outliner):
  Taverna
  ├─ 01_Yapi          Zemin, Duvarlar, Kapilar
  ├─ 02_Bar           tezgâh, raf, fıçılar; Bar_Tabureleri alt klasöründe tabureler
  ├─ 03_Masalar       her masa kendi alt klasöründe; masa ve sandalyeleri o masanın boş nesnesine (empty) bağlı
  ├─ 04_Somine
  ├─ 05_Isik_Isaretleri   mumlar ve ışığın olacağı yerler (isik_somine, isik_mum_…); ışığın kendisini site koyar
  └─ 06_Sablonlar     tek sandalye ve tek tabure modeli (hepsi bunların bağlı kopyası: şablonu değiştirince hepsi değişir)
  99_Onizleme         kamera ve önizleme ışıkları (yalnızca resim için)
"""
import bpy, bmesh, math, os, json, random

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(KOK, '3d', 'taverna-blockout.blend')
ONIZLEME = os.path.join(KOK, '3d', 'blockout-onizleme.png')
ETIKETLER = os.path.join(KOK, '3d', 'blockout-etiketler.json')
os.makedirs(os.path.join(KOK, '3d'), exist_ok=True)

# ───────── AYARLAR (metre) ─────────
IC_Y = 6.0                       # odanın iç yarı yüksekliği (merkezden kuzey/güney duvarına)
DK, DH = 0.25, 2.6               # duvar kalınlığı, duvar yüksekliği
DIS_Y = IC_Y + DK                # kameranın gördüğü alanın yarı yüksekliği
DIS_X = DIS_Y * 16 / 9           # … ve yarı genişliği (16:9)
IC_X = DIS_X - DK                # odanın iç yarı genişliği

ORTA_R, ORTA_SANDALYE_R, ORTA_SANDALYE = 1.05, 1.65, 9      # oyun masası: yarıçap, sandalyelerin uzaklığı, sayısı
YAN_R, YAN_SANDALYE_R, YAN_SANDALYE = 0.75, 1.18, 4         # çapraz masalar
YAN_X, YAN_Y = 6.0, 1.9                                     # çapraz masaların merkezden (yaklaşık) uzaklığı

# Dağınıklık: masalar ve sandalyeler tam düzenli durmasın. Sayılar en fazla ne kadar kayacaklarını verir.
# TOHUM "rastgele"nin başlangıcıdır: aynı sayı hep aynı dağınıklığı verir; başka bir sayı yazınca başka bir dağınıklık çıkar.
TOHUM = 7
YAN_KAYMA_X, YAN_KAYMA_Y = 0.6, 0.35                        # yan masaların yerinden kayması (m)
HALKA_DONME = 22                                            # yan masaların sandalye halkasının dönmesi (derece)
SANDALYE_DONME, SANDALYE_KAYMA = 9, 0.05                    # her sandalyenin kendi dönmesi (derece) ve kayması (m); oyun masasında yarısı

RAF_D, KORIDOR_D, TEZGAH_D = 0.4, 1.1, 0.6                  # bar: arka raf, barmen koridoru, tezgâh derinliği
TEZGAH_H = 1.05
TABURE_ARA, TABURE_R = 0.75, 0.19                           # taburelerin arası ve oturağın yarıçapı
YURUME = 0.5                                                # tabureler ile kuzeydeki masaların sandalyeleri arasında en az bu kadar yol

KAPI_X, KAPI_GEN = 6.0, 2.6                                 # giriş kapısı: güney duvarında, merkezi ve genişliği
SOMINE_GEN, SOMINE_H = 3.0, 1.8                             # şömine: güney duvarının ortasında

# ───────── Koleksiyonlar (Outliner'daki klasörler) ─────────
bpy.ops.wm.read_factory_settings(use_empty=True)
sahne = bpy.context.scene
def koleksiyon(ad, ust=None):
    c = bpy.data.collections.new(ad)
    (ust or sahne.collection).children.link(c)
    return c
K = koleksiyon('Taverna')
K_YAPI = koleksiyon('01_Yapi', K)
K_ZEMIN, K_DUVAR, K_KAPI = koleksiyon('Zemin', K_YAPI), koleksiyon('Duvarlar', K_YAPI), koleksiyon('Kapilar', K_YAPI)
K_BAR = koleksiyon('02_Bar', K)
K_TABURE = koleksiyon('Bar_Tabureleri', K_BAR)
K_MASA = koleksiyon('03_Masalar', K)
K_SOM = koleksiyon('04_Somine', K)
K_ISIK = koleksiyon('05_Isik_Isaretleri', K)
K_SAB = koleksiyon('06_Sablonlar', K)
K_ONI = koleksiyon('99_Onizleme')

# ───────── Blockout malzemeleri: düz renk, türüne göre ayrı ─────────
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
    m.diffuse_color = (*renk, 1)            # Blender'ın düz (Solid) görünümündeki renk
    return m
M_ZEMIN  = malzeme('BO_Zemin',   (0.20, 0.19, 0.18))
M_DUVAR  = malzeme('BO_Duvar',   (0.42, 0.40, 0.38))
M_KAPI   = malzeme('BO_Kapi',    (0.30, 0.20, 0.12))
M_MASA   = malzeme('BO_Masa',    (0.45, 0.30, 0.18))
M_ORTA   = malzeme('BO_Masa_Orta', (0.52, 0.34, 0.18))
M_SAND   = malzeme('BO_Sandalye', (0.35, 0.23, 0.14))
M_BAR    = malzeme('BO_Bar',     (0.28, 0.17, 0.10))
M_TAS    = malzeme('BO_Tas',     (0.33, 0.32, 0.31))
M_MUM    = malzeme('BO_Mum',     (0.85, 0.80, 0.68))
M_ATES   = malzeme('BO_Ates',    (1.00, 0.35, 0.06), isik=4.0)
M_KOLTUK = malzeme('BO_Koltuk',  (0.42, 0.13, 0.08))
M_HALI   = malzeme('BO_Hali',    (0.30, 0.08, 0.06))
zar = random.Random(TOHUM)                    # dağınıklık için "rastgele" sayılar (TOHUM aynıysa hep aynı)
def oyna(en_cok): return zar.uniform(-en_cok, en_cok)

# ───────── Şekil kurucular (metre): her nesnenin merkezi tabanının ortasındadır ─────────
def _nesne(ad, bm, mat, kol, konum, aci=0.0):
    me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free()
    if mat: me.materials.append(mat)
    ob = bpy.data.objects.new(ad, me)
    ob.location = konum; ob.rotation_euler = (0, 0, -math.radians(aci))   # aci: yukarıdan bakınca saat yönünde derece
    kol.objects.link(ob)
    return ob

def kutu(ad, kol, x, y, w, d, h, z0=0.0, mat=None, aci=0.0):
    """(x, y) merkezli, w (doğu-batı) × d (kuzey-güney) × h kutu."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= w; v.co.y *= d; v.co.z = (v.co.z + 0.5) * h
    return _nesne(ad, bm, mat, kol, (x, y, z0), aci)

def kutu_kenar(ad, kol, x0, x1, y0, y1, h, z0=0.0, mat=None):
    """Köşeleriyle verilen kutu (duvarlar ve bar için kolay)."""
    return kutu(ad, kol, (x0 + x1) / 2, (y0 + y1) / 2, abs(x1 - x0), abs(y1 - y0), h, z0, mat)

def silindir(ad, kol, x, y, r, h, z0=0.0, mat=None, n=24, r_ust=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=(r if r_ust is None else r_ust), depth=h)
    for v in bm.verts: v.co.z += h / 2
    return _nesne(ad, bm, mat, kol, (x, y, z0))

def bagla(cocuk, ebeveyn):
    """Nesneyi bir boş nesneye bağlar (dünyadaki yeri değişmez). Ebeveyni taşıyınca hepsi birlikte taşınır."""
    bpy.context.view_layer.update()          # yeni nesnelerin dünyadaki yeri hesaplansın
    cocuk.parent = ebeveyn
    cocuk.matrix_parent_inverse = ebeveyn.matrix_world.inverted()

def bos(ad, kol, x, y, z=0.0, boy=0.3, tur='PLAIN_AXES'):
    e = bpy.data.objects.new(ad, None); e.empty_display_type = tur; e.empty_display_size = boy
    e.location = (x, y, z); kol.objects.link(e); return e

def kopya(ad, sablon, kol, x, y, aci=0.0):
    """Şablonun bağlı kopyası (aynı şekli paylaşır). aci: önünün baktığı yön, kuzeyden saat yönünde derece."""
    ob = bpy.data.objects.new(ad, sablon.data)
    ob.location = (x, y, 0); ob.rotation_euler = (0, 0, -math.radians(aci))
    kol.objects.link(ob)
    return ob

ETIKET = []                                   # (metin, x, y) — önizlemedeki etiketler
def etiket(metin, x, y): ETIKET.append((metin, x, y))

# ───────── 01 Yapı: zemin, duvarlar, kapı ─────────
kutu('Zemin', K_ZEMIN, 0, 0, 2 * DIS_X, 2 * DIS_Y, 0.05, z0=-0.05, mat=M_ZEMIN)
kutu_kenar('Duvar_Kuzey', K_DUVAR, -DIS_X, DIS_X, IC_Y, DIS_Y, DH, mat=M_DUVAR)
kutu_kenar('Duvar_Bati', K_DUVAR, -DIS_X, -IC_X, -DIS_Y, DIS_Y, DH, mat=M_DUVAR)
kutu_kenar('Duvar_Dogu', K_DUVAR, IC_X, DIS_X, -DIS_Y, DIS_Y, DH, mat=M_DUVAR)
K0, K1 = KAPI_X - KAPI_GEN / 2, KAPI_X + KAPI_GEN / 2
kutu_kenar('Duvar_Guney_Bati', K_DUVAR, -DIS_X, K0, -DIS_Y, -IC_Y, DH, mat=M_DUVAR)
kutu_kenar('Duvar_Guney_Dogu', K_DUVAR, K1, DIS_X, -DIS_Y, -IC_Y, DH, mat=M_DUVAR)
kutu_kenar('Kapi_Giris_Esik', K_KAPI, K0, K1, -DIS_Y, -IC_Y, 0.03, mat=M_KAPI)
kanat = KAPI_GEN / 2 - 0.05                      # iki kanat, içeri doğru açık duruyor
kutu('Kapi_Giris_Kanat_Bati', K_KAPI, K0 + 0.04, -IC_Y + kanat / 2, 0.06, kanat, 2.2, mat=M_KAPI)
kutu('Kapi_Giris_Kanat_Dogu', K_KAPI, K1 - 0.04, -IC_Y + kanat / 2, 0.06, kanat, 2.2, mat=M_KAPI)
etiket('Giriş kapısı', KAPI_X, -IC_Y + 0.35)

# ───────── 06 Şablonlar: sandalye ve tabure ─────────
# Sandalyenin önü (masaya bakan yüzü) kuzeyde. Merkez: oturağın ortası, yer seviyesi. 0,6 × 0,6 m.
SW = SD = 0.6
B = 0.06                                     # ayak kalınlığı
bm = bmesh.new()
def _parca(bm, x0, x1, y0, y1, z0, z1, mi=0):
    m = bmesh.ops.create_cube(bm, size=1.0)
    for f in {f for v in m['verts'] for f in v.link_faces}: f.material_index = mi   # mi=1: arkalık (koyu, yönü belli olsun)
    for v in m['verts']:
        v.co.x = x0 if v.co.x < 0 else x1
        v.co.y = y0 if v.co.y < 0 else y1
        v.co.z = z0 if v.co.z < 0 else z1
for sx in (-1, 1):
    x0, x1 = (SW / 2 - B, SW / 2) if sx > 0 else (-SW / 2, -SW / 2 + B)
    _parca(bm, x0, x1, SD / 2 - B, SD / 2, 0, 0.45)                 # ön ayak
    _parca(bm, x0, x1, -SD / 2, -SD / 2 + B, 0, 0.92, 1)            # arka ayak (arkalığın direği)
_parca(bm, -SW / 2, SW / 2, -SD / 2, SD / 2, 0.40, 0.47)             # oturak
_parca(bm, -SW / 2 + B, SW / 2 - B, -SD / 2, -SD / 2 + B, 0.62, 0.92, 1)   # arkalık
SANDALYE = _nesne('Sandalye_Sablon', bm, M_SAND, K_SAB, (-DIS_X - 1.5, 1.0, 0))   # odanın dışında durur
SANDALYE.data.materials.append(M_BAR)

bm = bmesh.new()
for r1, r2, z0, z1 in ((0.17, 0.17, 0.0, 0.03), (0.04, 0.04, 0.03, 0.70), (TABURE_R, TABURE_R, 0.70, 0.76), (0.13, 0.13, 0.25, 0.28)):
    m = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=r1, radius2=r2, depth=z1 - z0)
    for v in m['verts']: v.co.z += (z0 + z1) / 2                    # taban, direk, oturak, ayak halkası
TABURE = _nesne('Tabure_Sablon', bm, M_SAND, K_SAB, (-DIS_X - 1.5, -1.0, 0))

# Koltuk (şömine önü): kollu, geniş, alçak. Önü kuzeyde. 0,8 × 0,8 m.
KW = 0.8
bm = bmesh.new()
_parca(bm, -KW / 2, KW / 2, -KW / 2, KW / 2, 0.0, 0.40)                       # gövde ve oturak
_parca(bm, -KW / 2, KW / 2, -KW / 2, -KW / 2 + 0.18, 0.40, 0.95, 1)          # arkalık
_parca(bm, -KW / 2, -KW / 2 + 0.14, -KW / 2 + 0.18, KW / 2, 0.40, 0.62, 1)   # sol kol
_parca(bm, KW / 2 - 0.14, KW / 2, -KW / 2 + 0.18, KW / 2, 0.40, 0.62, 1)     # sağ kol
KOLTUK = _nesne('Koltuk_Sablon', bm, M_KOLTUK, K_SAB, (-DIS_X - 1.5, -3.0, 0))
KOLTUK.data.materials.append(M_BAR)

# ───────── 02 Bar: ölçüler (masalar tabure sırasına göre yerleşeceği için önce hesaplanır) ─────────
RAF_Y0 = IC_Y - RAF_D
TEZ_Y1 = RAF_Y0 - KORIDOR_D                    # tezgâhın arka kenarı
TEZ_Y0 = TEZ_Y1 - TEZGAH_D                     # tezgâhın ön kenarı (müşteri tarafı)
TABURE_Y = TEZ_Y0 - 0.1 - TABURE_R              # tabureler tezgâhın önünde, boydan boya

# ───────── 03 Masalar ─────────
SANDALYE_YARI = 0.43                           # sandalyenin merkezinden en uzak köşesi (0,6 m kare, biraz dönebilir)
def sandalye_yerleri(n, r, ilk_aci, donme, kayma):
    """Sandalyelerin masaya göre yeri ve yönü: [(dx, dy, aci)]. donme/kayma: dağınıklık."""
    yer = []
    for i in range(n):
        a = ilk_aci + 360 * i / n + oyna(donme * 0.6)          # masadaki yeri (kuzeyden saat yönünde)
        ra = math.radians(a); rr = r + oyna(kayma)
        yer.append((rr * math.sin(ra), rr * math.cos(ra), a + 180 + oyna(donme)))   # önü masaya dönük, biraz yamuk
    return yer

def masa_kur(ad, x, y, r, yerler, mat, ayak_r):
    """Yuvarlak masa + çevresinde sandalyeler. Hepsi masanın boş nesnesine bağlı (tutamak): onu taşıyınca hepsi gelir."""
    kol = koleksiyon(ad, K_MASA)
    kok = bos(ad, kol, x, y, boy=r * 0.6, tur='CIRCLE')
    parcalar = [
        silindir(f'{ad}_Ust', kol, x, y, r, 0.06, z0=0.72, mat=mat, n=48),
        silindir(f'{ad}_Ayak', kol, x, y, ayak_r, 0.66, z0=0.06, mat=mat, n=16),
        silindir(f'{ad}_Taban', kol, x, y, ayak_r * 2.6, 0.06, z0=0.0, mat=mat, n=24),
    ]
    for i, (dx, dy, aci) in enumerate(yerler):
        parcalar.append(kopya(f'{ad}_Sandalye_{i + 1}', SANDALYE, kol, x + dx, y + dy, aci))
    for p in parcalar: bagla(p, kok)
    return kok

# Oyun masası: kameranın tam ortasında kalır; DM kuzeyde (bara bakan tarafta). Sandalyeleri yalnızca biraz yamuk.
masa_kur('Masa_Orta', 0, 0, ORTA_R, sandalye_yerleri(ORTA_SANDALYE, ORTA_SANDALYE_R, 0, SANDALYE_DONME / 2, SANDALYE_KAYMA / 2), M_ORTA, 0.15)
etiket('Masa_Orta (oyun masası, 9 koltuk)', 0, 0)
# Çapraz masalar: yerleri, sandalye halkasının açısı ve her sandalye biraz farklı
YAN_MASALAR, MASA_KOK = [], {}
for ad, sx, sy in (('Masa_KuzeyBati', -1, 1), ('Masa_KuzeyDogu', 1, 1), ('Masa_GuneyBati', -1, -1)):
    yerler = sandalye_yerleri(YAN_SANDALYE, YAN_SANDALYE_R, 45 + oyna(HALKA_DONME), SANDALYE_DONME, SANDALYE_KAYMA)
    x = sx * YAN_X + oyna(YAN_KAYMA_X)
    y = sy * YAN_Y + oyna(YAN_KAYMA_Y)
    if sy > 0:                                 # kuzeydekiler: sandalyeleri tabure sırasına yaklaşmasın
        y = min(y, TABURE_Y - TABURE_R - YURUME - max(dy for _, dy, _ in yerler) - SANDALYE_YARI)
    MASA_KOK[ad] = masa_kur(ad, x, y, YAN_R, yerler, M_MASA, 0.11)
    YAN_MASALAR.append((ad, x, y))
    etiket(ad, x, y)

# ───────── 02 Bar: kuzey duvarı boyunca baştan sona ─────────
kutu_kenar('Bar_Arka_Raf', K_BAR, -IC_X, IC_X, RAF_Y0, IC_Y, 2.0, mat=M_BAR)
kutu_kenar('Bar_Tezgah', K_BAR, -IC_X, IC_X, TEZ_Y0, TEZ_Y1, TEZGAH_H, mat=M_BAR)
kutu_kenar('Bar_Ayaklik', K_BAR, -IC_X, IC_X, TEZ_Y0 - 0.06, TEZ_Y0, 0.25, z0=0.2, mat=M_BAR)   # tezgâh dibinde ayak dayama çıtası
for i, x in enumerate((-IC_X + 0.45, IC_X - 0.45)):
    silindir(f'Bar_Fici_{i + 1}', K_BAR, x, (RAF_Y0 + TEZ_Y1) / 2, 0.3, 0.9, mat=M_BAR, n=20)   # barmen koridorunun iki ucunda
etiket('Bar_Tezgah', 0, (TEZ_Y0 + TEZ_Y1) / 2)
etiket('Bar_Arka_Raf', IC_X / 3, (RAF_Y0 + IC_Y) / 2)

n_tab = int((2 * IC_X - 0.8) // TABURE_ARA) + 1
bas = -(n_tab - 1) * TABURE_ARA / 2
kok_t = bos('Bar_Tabureleri', K_TABURE, 0, TABURE_Y, boy=0.4)
for i in range(n_tab):
    bagla(kopya(f'Bar_Tabure_{i + 1:02d}', TABURE, K_TABURE, bas + i * TABURE_ARA, TABURE_Y), kok_t)
etiket(f'Bar tabureleri ({n_tab})', IC_X / 2, TABURE_Y)

# ───────── 04 Şömine: güney duvarının ortası ─────────
SY = -IC_Y                                     # şöminenin dayandığı duvar
G2, YD = SOMINE_GEN / 2, 0.95                  # yarı genişlik, yan duvarların derinliği
kutu_kenar('Somine_Arka', K_SOM, -G2, G2, SY, SY + 0.3, SOMINE_H, mat=M_TAS)
kutu_kenar('Somine_Yan_Bati', K_SOM, -G2, -G2 + 0.45, SY, SY + YD, SOMINE_H, mat=M_TAS)
kutu_kenar('Somine_Yan_Dogu', K_SOM, G2 - 0.45, G2, SY, SY + YD, SOMINE_H, mat=M_TAS)
kutu_kenar('Somine_Ust_Kemer', K_SOM, -G2, G2, SY + YD - 0.25, SY + YD, 0.35, z0=SOMINE_H - 0.35, mat=M_TAS)   # ağzın üstündeki taş kemer
kutu_kenar('Somine_Esik', K_SOM, -G2 - 0.25, G2 + 0.25, SY + YD, SY + YD + 0.6, 0.06, mat=M_TAS)
kutu_kenar('Somine_Ates', K_SOM, -G2 + 0.6, G2 - 0.6, SY + 0.35, SY + 0.8, 0.35, mat=M_ATES)
etiket('Şömine', 0, SY + 0.6)

# Şömine önünde oturma alanı: halı, ateşe dönük iki koltuk ve aralarında alçak sehpa
K_OTUR = koleksiyon('Somine_Oturma_Alani', K_SOM)
OY = SY + YD + 0.6 + 0.95                      # oturma alanının ortası (eşiğin 0,95 m önü)
kok_o = bos('Somine_Oturma_Alani', K_OTUR, 0, OY, boy=0.5)
oturma = [kutu('Somine_Hali', K_OTUR, 0, OY, 3.6, 1.9, 0.015, mat=M_HALI, aci=oyna(3))]
for i, sx in enumerate((-1, 1)):
    kx, ky = sx * 1.2 + oyna(0.1), OY + 0.15 + oyna(0.1)
    yon = math.degrees(math.atan2(0 - kx, (SY + 0.5) - ky)) + oyna(6)        # ateşe dönük
    oturma.append(kopya(f'Somine_Koltuk_{i + 1}', KOLTUK, K_OTUR, kx, ky, yon))
oturma.append(silindir('Somine_Sehpa', K_OTUR, oyna(0.1), OY - 0.15, 0.32, 0.45, mat=M_MASA, n=24))
for p in oturma: bagla(p, kok_o)
etiket('Şömine önü oturma alanı', 3.4, OY)

# ───────── 05 Işık işaretleri (+ mumlar) ─────────
isaretler = [('isik_somine', 0, SY + 0.6, 0.45)]
mumlar = [(x, y, 0.78, MASA_KOK[ad]) for ad, x, y in YAN_MASALAR]                  # masadaki mum masaya bağlı: masayla taşınır
mumlar += [(x, (TEZ_Y0 + TEZ_Y1) / 2, TEZGAH_H, None) for x in (-6.0, -2.0, 2.0, 6.0)]    # bar tezgâhındaki mumlar
for i, (x, y, z, kok) in enumerate(mumlar):
    mum = silindir(f'Mum_{i + 1}', K_ISIK, x, y, 0.04, 0.12, z0=z, mat=M_MUM, n=12)
    alev = silindir(f'Mum_{i + 1}_Alev', K_ISIK, x, y, 0.02, 0.07, z0=z + 0.12, mat=M_ATES, n=8, r_ust=0.0)
    isaret = bos(f'isik_mum_{i + 1}', K_ISIK, x, y, z + 0.2, boy=0.12, tur='SPHERE')
    bagla(alev, mum); bagla(isaret, mum)
    if kok: bagla(mum, kok)
for ad, x, y, z in isaretler:
    bos(ad, K_ISIK, x, y, z, boy=0.12, tur='SPHERE')
isaretler += [(f'isik_mum_{i + 1}', x, y, z + 0.2) for i, (x, y, z, _) in enumerate(mumlar)]   # önizleme ışıkları için

# ───────── 99 Önizleme: kamera (ortadaki masanın tam üstü) ve geçici ışıklar ─────────
cam_d = bpy.data.cameras.new('Kamera'); cam_d.type = 'ORTHO'; cam_d.ortho_scale = 2 * DIS_X; cam_d.clip_end = 60
cam = bpy.data.objects.new('Kamera', cam_d); cam.location = (0, 0, 25); K_ONI.objects.link(cam)
sahne.camera = cam
sahne.render.resolution_x, sahne.render.resolution_y = 1920, 1080

def isik(ad, konum, renk, guc, yaricap, golge=True):
    d = bpy.data.lights.new(ad, 'POINT'); d.color = renk; d.energy = guc; d.shadow_soft_size = yaricap; d.use_shadow = golge
    o = bpy.data.objects.new(ad, d); o.location = konum; K_ONI.objects.link(o)
isik('Onizleme_Somine', (0, SY + 1.05, 0.7), (1.0, 0.45, 0.15), 1300, 0.4)
for ad, x, y, z in isaretler[1:]:
    isik('Onizleme_' + ad, (x, y, z), (1.0, 0.55, 0.25), 7, 0.03, False)
dunya = bpy.data.worlds.new('Dunya'); sahne.world = dunya
try: dunya.use_nodes = True
except Exception: pass
bg = dunya.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.09, 0.07, 0.05, 1); bg.inputs['Strength'].default_value = 3.0

sahne.render.engine = 'BLENDER_EEVEE'
try: sahne.view_settings.view_transform = 'Filmic'
except Exception: pass
sahne.render.filepath = ONIZLEME
sahne.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)

# Etiketlerin resimdeki yeri (0–1): blockout_etiketle.py okur
with open(ETIKETLER, 'w', encoding='utf-8') as f:
    json.dump({'etiketler': [{'metin': m, 'x': (x + DIS_X) / (2 * DIS_X), 'y': (DIS_Y - y) / (2 * DIS_Y)} for m, x, y in ETIKET],
               'oda_m': [round(2 * DIS_X, 2), round(2 * DIS_Y, 2)]}, f, ensure_ascii=False, indent=1)

# Blender açılınca ekranda düz renkli (Solid) görünüm, malzeme renkleriyle
for ekran in bpy.data.screens:
    for alan in ekran.areas:
        if alan.type == 'VIEW_3D':
            for sp in alan.spaces:
                if sp.type == 'VIEW_3D': sp.shading.color_type = 'MATERIAL'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True)
print(f'Oda (duvarlar dahil): {2 * DIS_X:.1f} x {2 * DIS_Y:.1f} m, tabure: {n_tab}')
print('TAMAM')
