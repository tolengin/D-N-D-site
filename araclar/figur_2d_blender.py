# -*- coding: utf-8 -*-
"""
2D TAVERNA FİGÜRLERİ (Blender betiği) — şimdilik BLOCKOUT (gri manken)
Her figür, tavernayla AYNI kamera açısından 16 yöne dönük çekilir (22,5°'de bir). Site her koltuk için masaya bakan
yöne en yakın kareyi seçer. İleride gerçek karakterler de aynı yolla eklenecek: model 'yap_<ad>' işleviyle kurulur,
aşağıdaki FIGURLER listesine eklenir.

Kamera açısı aşağıdaki KAM ayarındadır; sitedeki NPR kamerasıyla (index.html, TAV.yon ve TAV.egim) aynı olmalı.
Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --factory-startup --python araclar\\figur_2d_blender.py
Sonra:  python araclar\\figur_2d_hazirla.py   (.webp; masa/fig2d/ klasörüne)

Kurallar (yeni karakter eklerken de):
  • Koltuğun ortası (oturağın altındaki yer noktası) dünyanın (0, 0, 0) noktasıdır; figür +y yönüne (masaya) bakar.
    Sandalye figürle birlikte çekilir; masanın kenarı +y yönünde ~0,55 m ötededir (eller oraya uzanır).
  • Resmin ortası her zaman (0, 0, 0) noktasıdır: site resmi koltuğun yer noktasına ortalayarak koyar.
  • Kare k: figür, kuzeyden (+y) saat yönünün tersine k × 22,5° dönmüş hâlde. k = 0 → kuzeye bakar.
"""
import bpy, bmesh, math, os, json
from mathutils import Vector, Matrix

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIKTI = os.path.join(KOK, '3d', 'fig2d')
KAM = {'yon': 30.0, 'egim': 45.0}               # kamera açısı: index.html'deki TAV.yon, TAV.egim ile AYNI olmalı
YON_SAYISI = 16
KARE_M = 2.6                                   # resmin kapladığı alan (m, kare)
PX_M = 235.3                                   # keskinlik (piksel / metre): sitede yakın bakışta 1 m ≈ 225 piksel
CIZGI = 2.8                                    # mürekkep çizgisinin kalınlığı (piksel)

os.makedirs(CIKTI, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sahne = bpy.context.scene

def mat(ad, renk, puruz=0.8):
    m = bpy.data.materials.new(ad); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*renk, 1); b.inputs['Roughness'].default_value = puruz
    return m
M_AHSAP = mat('M_Ahsap', (0.20, 0.11, 0.05))
M_GRI = mat('M_Manken', (0.42, 0.44, 0.50))
M_DM = mat('M_Manken_DM', (0.36, 0.10, 0.08))
M_DERI = mat('M_Deri', (0.25, 0.14, 0.07))

def kutu(bm, x0, x1, y0, y1, z0, z1):
    r = bmesh.ops.create_cube(bm, size=1)['verts']
    for v in r: v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0), (z0 + z1) / 2 + v.co.z * (z1 - z0)))
def cubuk(bm, a, b, r, seg=12):                  # iki nokta arasında silindir
    a, b = Vector(a), Vector(b); d = b - a
    v = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)['verts']
    T = Matrix.Translation((a + b) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=T, verts=v)
def kure(bm, c, r):
    v = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=r)['verts']
    bmesh.ops.translate(bm, vec=Vector(c), verts=v)
def nesne(ad, kur, m):
    bm = bmesh.new(); kur(bm)
    for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(ad, me); sahne.collection.objects.link(o); return o

# Sandalye (blockout): arkalık −y'de, oturak 0,45 m
def sandalye(bm):
    for x in (-0.2, 0.2):
        for y in (-0.2, 0.2): cubuk(bm, (x, y, 0), (x, y, 0.45), 0.025, 8)
    kutu(bm, -0.23, 0.23, -0.23, 0.23, 0.43, 0.48)
    for x in (-0.2, 0.2): cubuk(bm, (x, -0.21, 0.48), (x, -0.24, 1.0), 0.025, 8)
    kutu(bm, -0.21, 0.21, -0.25, -0.21, 0.62, 0.96)
def minder(bm): kutu(bm, -0.2, 0.2, -0.2, 0.2, 0.48, 0.51)

# Oturan manken: masaya (+y) dönük, kollar masanın kenarına uzanır
def manken(bm, boy=1.0):
    s = boy
    kutu(bm, -0.18, 0.18, -0.12, 0.30, 0.50, 0.64)                    # kalça ve uyluklar
    for x in (-0.1, 0.1):
        cubuk(bm, (x, 0.28, 0.58), (x, 0.36, 0.06), 0.06)              # baldırlar
        kutu(bm, x - 0.05, x + 0.05, 0.30, 0.46, 0.0, 0.07)             # ayaklar
    cubuk(bm, (0, -0.04, 0.62), (0, 0.04, 0.62 + 0.48 * s), 0.17, 16)  # gövde (öne hafif eğik)
    kure(bm, (0, 0.04, 0.62 + 0.48 * s), 0.17)                          # omuzlar yuvarlak
    cubuk(bm, (0, 0.05, 1.16 * s), (0, 0.06, 1.24 * s), 0.05)         # boyun
    kure(bm, (0, 0.07, 1.33 * s), 0.11)                                 # baş
    for x in (-1, 1):
        o = (0.21 * x, 0.02, 1.04 * s); d = (0.24 * x, 0.20, 0.86); e = (0.14 * x, 0.46, 0.83)
        cubuk(bm, o, d, 0.055); cubuk(bm, d, e, 0.05); kure(bm, e, 0.06)

def yap_oyuncu():
    return [nesne('Sandalye', sandalye, M_AHSAP), nesne('Minder', minder, M_DERI), nesne('Manken', manken, M_GRI)]
def yap_dm():
    def kitap(bm): kutu(bm, -0.16, 0.16, 0.40, 0.62, 0.80, 0.86)     # DM'in önünde açık kitap (masanın kenarında)
    return [nesne('Sandalye', sandalye, M_AHSAP), nesne('Minder', minder, M_DERI),
            nesne('Manken', lambda bm: manken(bm, 1.04), M_DM), nesne('Kitap', kitap, mat('M_Kitap', (0.85, 0.78, 0.6)))]
def yap_sandalye():
    return [nesne('Sandalye', sandalye, M_AHSAP), nesne('Minder', minder, M_DERI)]

FIGURLER = [('blockout-oyuncu', yap_oyuncu), ('blockout-dm', yap_dm), ('sandalye', yap_sandalye)]

# Işık: tavernanın sıcak ortamına uysun (üstten sıcak, yandan serin dolgu)
d = bpy.data.lights.new('Sicak', 'SUN'); d.energy = 2.6; d.color = (1.0, 0.72, 0.45); d.angle = math.radians(20)
o = bpy.data.objects.new('Sicak', d); o.rotation_euler = (math.radians(35), 0, math.radians(150)); sahne.collection.objects.link(o)
d = bpy.data.lights.new('Serin', 'SUN'); d.energy = 0.7; d.color = (0.6, 0.66, 1.0)
o = bpy.data.objects.new('Serin', d); o.rotation_euler = (math.radians(60), 0, math.radians(-40)); sahne.collection.objects.link(o)
dunya = bpy.data.worlds.new('Dunya'); sahne.world = dunya
try: dunya.use_nodes = True
except Exception: pass
bg = dunya.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value = (0.16, 0.11, 0.07, 1); bg.inputs['Strength'].default_value = 1.0

# Kamera: tavernadakiyle aynı yön, ortası (0, 0, 0)
th, ph = math.radians(KAM['yon']), math.radians(KAM['egim'])
BAK = Vector((math.sin(th) * math.cos(ph), math.cos(th) * math.cos(ph), -math.sin(ph)))
kd = bpy.data.cameras.new('Kamera'); kd.type = 'ORTHO'; kd.ortho_scale = KARE_M; kd.clip_end = 60
kam = bpy.data.objects.new('Kamera', kd); sahne.collection.objects.link(kam); sahne.camera = kam
kam.rotation_euler = (math.radians(90 - KAM['egim']), 0, -th); kam.location = -BAK * 20

r = sahne.render
r.engine = 'BLENDER_EEVEE'; r.film_transparent = True
r.resolution_x = r.resolution_y = round(KARE_M * PX_M)
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'
sahne.view_settings.view_transform = 'Filmic'
try: sahne.view_settings.look = 'Medium High Contrast'
except Exception: pass
try: sahne.eevee.taa_render_samples = 32
except Exception: pass
r.use_freestyle = True; r.line_thickness_mode = 'ABSOLUTE'; r.line_thickness = CIZGI
fs = sahne.view_layers[0].freestyle_settings; fs.crease_angle = math.radians(140)
ls = fs.linesets[0] if fs.linesets else fs.linesets.new('Cizgi')
ls.select_silhouette = ls.select_border = ls.select_crease = ls.select_external_contour = True
lst = ls.linestyle or bpy.data.linestyles.new('Murekkep'); ls.linestyle = lst
lst.color = (0.07, 0.045, 0.03); lst.alpha = 0.85; lst.caps = 'ROUND'

kok = bpy.data.objects.new('Kok', None); sahne.collection.objects.link(kok)
for ad, yap in FIGURLER:
    parcalar = yap()
    for p in parcalar: p.parent = kok
    for k in range(YON_SAYISI):
        kok.rotation_euler = (0, 0, math.radians(k * 360 / YON_SAYISI))
        r.filepath = os.path.join(CIKTI, f'{ad}-{k:02d}.png')
        bpy.ops.render.render(write_still=True)
    for p in parcalar: bpy.data.objects.remove(p)
    print('çekildi:', ad)
json.dump({'yon_sayisi': YON_SAYISI, 'kare_m': KARE_M, 'figurler': [a for a, _ in FIGURLER]},
          open(os.path.join(CIKTI, 'figurler.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('TAMAM')
