# -*- coding: utf-8 -*-
"""
NPR TAVERNA — SİTEYE AKTARMA (Blender betiği)
=============================================
NPR (Non-Photorealistic Rendering, "gerçekçi olmayan render"): sahne 3D'dir, site onu tarayıcıda canlı çizer ama sonuç
çizim gibi görünür: düz tonlu gölgelendirme (toon), mürekkep kenar çizgileri ve hafif fırça dokusu (index.html BÖLÜM 11b).

Bu betik 3d/taverna-detay.blend dosyasını açar, siteye gerekmeyenleri bırakır, dokuları küçültür ve tek dosya olarak
dışa aktarır. Asıl model ve 3d/dokular/ içindeki büyük dokular DEĞİŞMEZ (her şey yalnızca bu betiğin belleğinde).

Önce asıl model hazır olmalı (araclar/taverna_detay_blender.py).
Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --python araclar\\taverna_npr_aktar.py

Çıktılar:
  masa/taverna-npr.glb   sitenin yüklediği sahne (dokular içinde, WebP; şekiller Draco ile sıkıştırılmış)
  masa/taverna-npr.js    aynı dosyanın metin hâli: site bilgisayardan (file://) açılınca tarayıcı .glb okuyamaz, bunu okur

Duvar etiketi: duvarlar, direkler ve duvara asılı parçalar "duvar" bilgisi taşır (kuzey, guney, bati, dogu). Site kameranın
baktığı yöne göre öndeki duvarları alçaltır ve onlara asılı parçaları gizler (kesit görünümü). Böylece ileride yeni kamera
açıları eklenince kesit kendiliğinden doğru olur.
"""
import bpy, bmesh, os, base64, math
from mathutils import Vector

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(KOK, '3d', 'taverna-detay.blend')
GLB = os.path.join(KOK, 'masa', 'taverna-npr.glb')
JS = os.path.join(KOK, 'masa', 'taverna-npr.js')

# ───────── AYARLAR ─────────
DISARIDA_KOL = {'06_Sablonlar', '99_Onizleme'}
DISARIDA_AD = ('Masa_Orta_Sandalye_',)               # oyun masasının sandalyeleri: site koltuk sayısı kadar koyar
# Yalnızca göz hizasında (birinci şahıs) görünenler: tepeden bakan kamerada üstü kapatır ya da tavansız havada kalır.
# "pov" etiketi alırlar; site onları tepeden bakışta gizler.
POV_KOL = {'08_Tavan', 'Avize'}
POV_AD = ('Kapi_Disari_Gece', 'Sarmasik_Kiris_', 'Kuru_Ot_', 'Bitki_Sarkan_', 'Sarkit_Masa_')
WEBP_KALITE = 80
# Dokuların sitedeki en uzun kenarı (px). Yere yakın büyük yüzeyler keskin kalsın.
# (2026-10-16'ya kadar ikinci satırın başı bir açıklamanın içinde kalmıştı; kalkan, tabela, sancak ve harita 512 oluyordu.)
BOY = {'hali': 1024, 'post': 512, 'deri': 256, 'zemin-ahsap': 1024, 'duvar-tas': 1024, 'duvar-siva': 1024, 'masa-ahsap': 1024,
       'tas-altigen': 1024, 'tas-blok': 512, 'dis-zemin': 512,
       'kalkan-1': 256, 'kalkan-2': 256, 'tabela': 512, 'sancak': 256, 'harita': 512,
       'gorev-panosu': 512, 'kitap-sirtlari': 256, 'demir': 256, 'cuval': 256, 'saksi-toprak': 256}
VARSAYILAN = 512
SADELESTIR = {'Bar_Raf_': 0.3}                       # şişeler dosyanın yarısıydı; uzaktan kabalaşmaları fark edilmez
DUVAR_YAKIN = 0.7                                    # duvara bu kadar yakın parça "duvarda" sayılır (m)
HALI_R = 2.5                                         # oyun masasının altındaki yuvarlak halının yarıçapı (m)
OYUN_HALISI = False                                  # oyun masasının altına yuvarlak halı konsun mu? (2026-10-16: kullanıcının isteğiyle kaldırıldı)

bpy.ops.wm.open_mainfile(filepath=BLEND)
O = bpy.data.objects

# 1) Malzemeler: normal ve pürüz haritaları çıkar (toon gölgelendirmede işe yaramaz, dosyayı büyütür)
for m in bpy.data.materials:
    if not m.use_nodes: continue
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type == 'NORMAL_MAP': nt.nodes.remove(n)
    b = nt.nodes.get('Principled BSDF')
    if b:
        for ad in ('Roughness', 'Metallic'):
            for l in list(b.inputs[ad].links): nt.links.remove(l)
for img in bpy.data.images:                        # kalan renk dokularını küçült (yalnızca bellekte)
    if not img.filepath or img.size[0] == 0: continue
    ad = os.path.splitext(os.path.basename(img.filepath))[0]
    k = BOY.get(ad, VARSAYILAN) / max(img.size)
    if k < 1: img.scale(max(1, round(img.size[0] * k)), max(1, round(img.size[1] * k)))

# 2) Oyun halısı (OYUN_HALISI açıksa) ve dış zemin
if OYUN_HALISI:
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, radius=HALI_R, segments=72)
    uvk = bm.loops.layers.uv.new()
    for f in bm.faces:
        for l in f.loops: l[uvk].uv = (0.5 + l.vert.co.x / (2 * HALI_R) * 0.56, 0.5 + l.vert.co.y / (2 * HALI_R))
    me = bpy.data.meshes.new('Oyun_Halisi'); bm.to_mesh(me); bm.free(); me.materials.append(bpy.data.materials.get('M_Hali'))
    hal = bpy.data.objects.new('Oyun_Halisi', me); hal.location = (0, 0, 0.004); hal.rotation_euler.z = math.radians(12)
    bpy.context.scene.collection.objects.link(hal)
# Dış zeminin dokusu: varsa kendi dokusu (dis-zemin, 2026-10-16), yoksa eski taş duvar dokusu (duvarlar artık sıva)
_dz = next((p for p in (os.path.join(KOK, '3d', 'dokular', a + '.jpg') for a in ('dis-zemin', 'duvar-tas')) if os.path.exists(p)), None)
tas = bpy.data.images.load(_dz) if _dz else None
if tas and tas.size[0] > 512: tas.scale(512, round(tas.size[1] * 512 / tas.size[0]))
mz = bpy.data.materials.new('M_Dis_Zemin'); mz.use_nodes = True                # renk tonunu site verir (serin, morumsu)
if tas:
    tx = mz.node_tree.nodes.new('ShaderNodeTexImage'); tx.image = tas
    mz.node_tree.links.new(tx.outputs['Color'], mz.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30)
uvk = bm.loops.layers.uv.new()
for f in bm.faces:
    for l in f.loops: l[uvk].uv = (l.vert.co.x / 1.4, l.vert.co.y / 1.4)            # taş 1,4 m'de bir tekrar
me = bpy.data.meshes.new('Dis_Zemin'); bm.to_mesh(me); bm.free(); me.materials.append(mz)
dz = bpy.data.objects.new('Dis_Zemin', me); dz.location = (0, 0, -0.06); bpy.context.scene.collection.objects.link(dz)

# 3) Duvar ölçüleri ve direklerin duvarlara ayrılması
bpy.context.view_layer.update()
def kutu(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([min(v[i] for v in bb) for i in range(3)]), Vector([max(v[i] for v in bb) for i in range(3)])
IC_X = kutu(O['Duvar_Dogu'])[0].x + 0.03; IC_Y = kutu(O['Duvar_Kuzey_Dogu'])[0].y + 0.03   # iç yüzler (süpürgelik payı)
def duvari(c):                                          # bir noktanın en yakın duvarı ve uzaklığı
    d = {'kuzey': IC_Y - c.y, 'guney': c.y + IC_Y, 'dogu': IC_X - c.x, 'bati': c.x + IC_X}
    k = min(d, key=d.get); return k, d[k]

dir_ = O['Duvar_Direkleri']; mw = dir_.matrix_world
bm = bmesh.new(); bm.from_mesh(dir_.data); bm.verts.ensure_lookup_table()
parcalar, gorulen = [], set()
for v in bm.verts:
    if v.index in gorulen: continue
    yigin, p = [v], []; gorulen.add(v.index)
    while yigin:
        w = yigin.pop(); p.append(w.index)
        for e in w.link_edges:
            u = e.other_vert(w)
            if u.index not in gorulen: gorulen.add(u.index); yigin.append(u)
    parcalar.append(p)
gruplar = {}
for p in parcalar:
    c = sum((mw @ bm.verts[i].co for i in p), Vector()) / len(p)
    gruplar.setdefault(duvari(c)[0], set()).update(p)
for ad, kume in gruplar.items():
    b2 = bm.copy(); b2.verts.ensure_lookup_table()
    bmesh.ops.delete(b2, geom=[b2.verts[i] for i in range(len(b2.verts)) if i not in kume], context='VERTS')
    me = bpy.data.meshes.new(f'Direk_{ad}'); b2.to_mesh(me); b2.free()
    for m in dir_.data.materials: me.materials.append(m)
    ob = bpy.data.objects.new(f'Direk_{ad.capitalize()}', me); ob.matrix_world = mw.copy()
    for k in dir_.users_collection: k.objects.link(ob)
    ob['duvar'] = ad
bm.free(); bpy.data.objects.remove(dir_)
for ad, d in (('Duvar_Kuzey_Bati', 'kuzey'), ('Duvar_Kuzey_Dogu', 'kuzey'), ('Duvar_Bati', 'bati'), ('Duvar_Dogu', 'dogu'),
              ('Duvar_Guney_Bati', 'guney'), ('Duvar_Guney_Dogu', 'guney'), ('Kapi_Lento', 'guney'), ('Kapi_Mutfak_Lento', 'kuzey')):
    O[ad]['duvar'] = d

# 4) Siteye gidecek nesneler; duvara asılı ya da duvar boyu uzanan parçalar etiketlenir
def kolda_mi(ob, adlar):
    for kol in ob.users_collection:
        k = kol
        while k:
            if k.name in adlar: return True
            k = next((p for p in bpy.data.collections if k.name in p.children), None)
    return False
bpy.ops.object.select_all(action='DESELECT')
secilen, etiket, pov = 0, 0, 0
for ob in bpy.data.objects:
    if ob.type not in {'MESH', 'EMPTY'} or ob.name.startswith(DISARIDA_AD) or kolda_mi(ob, DISARIDA_KOL): continue
    ob.hide_set(False); ob.select_set(True); secilen += 1
    if ob.name.startswith(POV_AD) or kolda_mi(ob, POV_KOL): ob['pov'] = 1; pov += 1
    oran = next((v for k, v in SADELESTIR.items() if ob.name.startswith(k)), None)
    if oran and ob.type == 'MESH': ob.modifiers.new('Sadelestir', 'DECIMATE').ratio = oran
    if 'duvar' in ob.keys() or ob.name.startswith(('Zemin', 'Dis_Zemin', 'Oyun_Halisi')): continue
    if ob.type == 'MESH':
        mn, mx = kutu(ob); c = (mn + mx) / 2
        yer, uz = duvari(Vector((c.x, c.y, 0)))
        kalinlik = {'kuzey': mx.y - mn.y, 'guney': mx.y - mn.y, 'dogu': mx.x - mn.x, 'bati': mx.x - mn.x}[yer]
        if uz - kalinlik / 2 < DUVAR_YAKIN and kalinlik < 1.2 and (mn.z > 0.15 or mx.z > 1.6):
            ob['duvar'] = yer; etiket += 1
    else:                                                # ışık işaretleri: duvardaki aplikler duvarla birlikte söner
        p = ob.matrix_world.translation; yer, uz = duvari(p)
        if uz < 0.5 and p.z > 1.0: ob['duvar'] = yer
print(f'  seçilen nesne: {secilen}, duvar etiketli: {etiket}, yalnızca göz hizası: {pov}')

# 5) Dışa aktar (custom property'ler "extras" olarak gider; site userData.duvar diye okur)
ayar = dict(filepath=GLB, export_format='GLB', use_selection=True, export_extras=True,
            export_image_format='WEBP', export_image_quality=WEBP_KALITE,
            export_cameras=False, export_lights=False, export_yup=True,
            export_apply=True, export_texcoords=True, export_normals=True, export_tangents=False,
            export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12)
try:
    bpy.ops.export_scene.gltf(**ayar)
except TypeError as e:
    print('AYAR HATASI:', e); raise SystemExit(1)
veri = open(GLB, 'rb').read()
with open(JS, 'w', encoding='utf-8') as f:
    f.write('/* NPR taverna (araclar/taverna_npr_aktar.py üretir; elle değiştirme). Site bilgisayardan açılınca .glb yerine bu okunur. */\n')
    f.write('window.TAVERNA_NPR="' + base64.b64encode(veri).decode('ascii') + '";\n')
print(f'  {GLB}: {len(veri) / 1024 / 1024:.2f} MB')
print('TAMAM')
