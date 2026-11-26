# -*- coding: utf-8 -*-
"""
YENİ HAN — DIŞ CEPHEYİ SİTEYE AKTARMA (Blender betiği)  (2026-11-26)
====================================================================
3d/han/han-dis.blend'den (araclar/han_dis_blender.py kurar) yalnızca dış kabuğu ('10_Dis') ve çevreyi ('11_Cevre') alır,
dokuları küçültür ve tek dosya olarak dışa aktarır: masa/han-dis.glb + han-dis.js (bilgisayardan açılınca, HAN_DIS_GLB).
Asıl dosyalar DEĞİŞMEZ. Alacakaranlığın ışığı pişirilir (aşağıda IŞIK PİŞİRME; ~10–20 dk); sonuna "-- canli" eklenirse pişirmeden.
Önizleme sisi, ışıklar ve kameralar alınmaz.

Site (index.html BÖLÜM 11d) bunu yalnızca açılış için yükler. Nesnelerin 'dis' etiketi (userData.dis):
  'zemin'  çayır, toprak avlu, yollar: açılıştan sonra da kalır (içerinin eski taş döşemesinin yerine)
  'kabuk'  bina dışı, ağaçlar, eşyalar: yalnızca açılışta görünür, sonra bellekten atılır
Malzemelerdeki renk çarpanı (Dis_Tas: daha gri taş, Dis_Yol: koyu toprak, Dis_Yaprak) glTF'e geçmediği için resmin içine işlenir.

Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --python araclar\\han_dis_aktar.py
"""
import bpy, os, sys, math, time, base64
import numpy as np

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLB, JS = os.path.join(KOK, 'masa', 'han-dis.glb'), os.path.join(KOK, 'masa', 'han-dis.js')
BOY = 512                                              # dokuların en büyük kenarı (px)
ZEMIN = ('Cevre_Cayir', 'Cevre_Cayir_Yakin', 'Cevre_Avlu', 'Cevre_Yol')

bpy.ops.wm.open_mainfile(filepath=os.path.join(KOK, '3d', 'han', 'han-dis.blend'))
def kolda(o, adlar):
    return any(c.name in adlar or any(c.name in p.children for p in bpy.data.collections if p.name in adlar) for c in o.users_collection)
secim = [o for o in bpy.data.objects if o.type == 'MESH' and kolda(o, ('10_Dis', '11_Cevre')) and not o.name.startswith('Onizleme_')]
for o in bpy.data.objects: o.select_set(False)
for o in secim:
    o.select_set(True); o['dis'] = 'zemin' if o.name in ZEMIN else 'kabuk'
print('Nesne:', len(secim), ', yüz:', sum(len(o.data.polygons) for o in secim))

# ───────── IŞIK PİŞİRME (2026-11-26, kullanıcının seçimi: karma) ─────────
# Bina kabuğu, avlu, yollar, yakın çayır, yakın ağaçlar ve eşyalar: alacakaranlığın ışığı (batan güneş, gök, ışıyan pencereler,
# içerinin kapıdan sızan ışıkları) "Isik" UV'sine (sitede uv1) pişer → isik-a (2048 px); dört fener ayrı → isik-b (1024 px, gri,
# site titretir). Uzak çayır ve uzak ağaçlar canlı ışıkta kalır (ışık haritasında yer yutmasınlar). Yöntem içerinin aynısı
# (araclar/han_aktar.py): √(ışık / K) saklanır, resimler gizli kartların (Isik_Harita_A / B) parlama dokusu, katsayılar Isik_Ayar'da.
# İçerideki duvarlar ve eşyalar sahnede kalır (gölge düşürür, ışık yansıtır) ama pişmez. "-- canli": pişirmeden hızlı aktarım.
CANLI = 'canli' in sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else False
PIS_YOK = ('Cevre_Cayir', 'Cevre_Agac_Uzak')
FENER = ('Dis_Fener', 'Cevre_Fener')                       # ayrı pişen (titreyen) ışıklar
HARITA, HARITA_B, ORNEK, KENAR, PAY, YUMUSAK = 2048, 1024, 128, 4, 0.003, 1.2
ISIK_KLASOR = os.path.join(KOK, '3d', 'han', 'isik-dis')
kartlar = []
if not CANLI:
    t0 = time.time(); sahne = bpy.context.scene
    for k in bpy.data.collections: k.hide_render = k.name == '08_Sablonlar'
    for ob in bpy.data.objects: ob.hide_render = ob.name in ('Onizleme_Sis', 'Onizleme_Dolgu')   # sis kutusu ve içerinin tepe dolgu ışığı yok
    pisen = [o for o in secim if o.name not in PIS_YOK]
    # Kendi ışığını saçanlar: dışarının pencereleri ışısın (duvara sıcak ışık vurur); alevler, fener camları kapalı (ışıkları var)
    parlak = []
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
        if b and b.inputs['Emission Strength'].default_value > 0 and m.name != 'Dis_Pencere':
            parlak.append((b.inputs['Emission Strength'], b.inputs['Emission Strength'].default_value)); b.inputs['Emission Strength'].default_value = 0
    for ob in pisen:
        if ob.data.users > 1: ob.data = ob.data.copy()
    bpy.ops.object.select_all(action='DESELECT')
    for ob in pisen: ob.select_set(True)
    bpy.context.view_layer.objects.active = pisen[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for ob in pisen:
        uv = ob.data.uv_layers
        if not len(uv): uv.new(name='UVMap')
        uv[0].active_render = True; isik = uv.new(name='Isik'); uv.active = isik
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.select_all(action='SELECT'); bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=PAY, shape_method='CONVEX')
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f'  ışık haritası UV hazır ({time.time() - t0:.0f} sn), pişen nesne {len(pisen)}')
    sahne.render.engine = 'CYCLES'
    try:
        pr = bpy.context.preferences.addons['cycles'].preferences
        for tur in ('OPTIX', 'CUDA'):
            try:
                pr.compute_device_type = tur; pr.get_devices()
                if any(d.type == tur for d in pr.devices):
                    for d in pr.devices: d.use = d.type == tur
                    sahne.cycles.device = 'GPU'; print('  Cycles:', tur); break
            except TypeError: pass
    except Exception as e: print('  Cycles ekran kartı yok, işlemci:', e)
    sahne.cycles.samples = ORNEK; sahne.cycles.max_bounces = 4; sahne.cycles.diffuse_bounces = 3
    isiklar = [o for o in bpy.data.objects if o.type == 'LIGHT' and not o.hide_render]
    fener = [o for o in isiklar if o.name.startswith(FENER)]
    malzemeler = {s_.material for ob in pisen for s_ in ob.material_slots if s_.material and s_.material.node_tree}
    def hedef_resim(ad, boy):
        img = bpy.data.images.new(ad, boy, boy, alpha=False, float_buffer=True)
        for m in malzemeler:
            nt = m.node_tree
            n = nt.nodes.get('Isik_Hedef') or nt.nodes.new('ShaderNodeTexImage'); n.name = 'Isik_Hedef'
            u = nt.nodes.get('Isik_UV') or nt.nodes.new('ShaderNodeUVMap'); u.name = 'Isik_UV'; u.uv_map = 'Isik'
            if not n.inputs['Vector'].links: nt.links.new(u.outputs['UV'], n.inputs['Vector'])
            n.image = img; nt.nodes.active = n
        return img
    def pis(ad, boy, yanik):
        for L in isiklar: L.hide_render = L not in yanik
        img = hedef_resim(ad, boy)
        bpy.ops.object.select_all(action='DESELECT')
        for ob in pisen: ob.select_set(True)
        bpy.context.view_layer.objects.active = pisen[0]
        bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, target='IMAGE_TEXTURES', margin=KENAR, margin_type='EXTEND', use_clear=True)
        a = np.empty(boy * boy * 4, np.float32); img.pixels.foreach_get(a)
        a = a.reshape(boy, boy, 4)[:, :, :3]
        print(f'  {ad}: dolu piksel %{100 * (a.max(2) > 1e-5).mean():.1f}, en çok {a.max():.2f} ({time.time() - t0:.0f} sn)')
        return a
    A = pis('Isik_A', HARITA, [o for o in isiklar if o not in fener])
    dunya = sahne.world.node_tree.nodes.get('Background').inputs['Strength']; gok = dunya.default_value; dunya.default_value = 0
    pen = bpy.data.materials.get('Dis_Pencere').node_tree.nodes['Principled BSDF'].inputs['Emission Strength']; pg = pen.default_value; pen.default_value = 0
    B = pis('Isik_B', HARITA_B, fener)
    dunya.default_value = gok; pen.default_value = pg
    for g, v in parlak: g.default_value = v
    for m in malzemeler:
        for ad in ('Isik_Hedef', 'Isik_UV'):
            n = m.node_tree.nodes.get(ad)
            if n: m.node_tree.nodes.remove(n)
    def bulanik(x, s):
        r = int(3 * s); k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2); k /= k.sum()
        for eksen in (0, 1): x = sum(np.roll(x, i - r, axis=eksen) * k[i] for i in range(len(k)))
        return x
    A = bulanik(A, YUMUSAK); B = bulanik(B, YUMUSAK * HARITA_B / HARITA)
    dolu = A.max(2) > 1e-5
    K = float(np.percentile(A.max(2)[dolu], 99.7)) if dolu.any() else 1.0
    lum = B @ np.array([0.2126, 0.7152, 0.0722])
    Kb = float(np.percentile(lum[lum > 1e-5], 99.7)) if (lum > 1e-5).any() else 1.0
    renkB = (B.reshape(-1, 3).sum(0) / max(lum.sum(), 1e-6)).tolist()
    os.makedirs(ISIK_KLASOR, exist_ok=True)
    def kaydet(ad, rgb):
        boy = rgb.shape[0]; img = bpy.data.images.new(ad, boy, boy, alpha=False); img.colorspace_settings.name = 'Non-Color'
        px = np.ones((boy, boy, 4), np.float32); px[:, :, :3] = rgb; img.pixels.foreach_set(px.ravel())
        img.filepath_raw = os.path.join(ISIK_KLASOR, ad + '.png'); img.file_format = 'PNG'; img.save()
        return img
    imA = kaydet('isik-a', np.sqrt(np.clip(A / K, 0, 1)))
    imB = kaydet('isik-b', np.repeat(np.sqrt(np.clip(lum / Kb, 0, 1))[:, :, None], 3, 2))
    def kart(ad, img):
        me = bpy.data.meshes.new(ad); me.from_pydata([(0, 0, -5), (0.1, 0, -5), (0.1, 0.1, -5)], [], [(0, 1, 2)]); me.uv_layers.new(name='UVMap')
        m = bpy.data.materials.new(ad); m.use_nodes = True
        nt = m.node_tree; b = nt.nodes.get('Principled BSDF'); t = nt.nodes.new('ShaderNodeTexImage'); t.image = img
        nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.0
        me.materials.append(m); ob = bpy.data.objects.new(ad, me); bpy.context.scene.collection.objects.link(ob); ob['dis'] = 'isik'
        kartlar.append(ob)
    kart('Isik_Harita_A', imA); kart('Isik_Harita_B', imB)
    ayar = bpy.data.objects.new('Isik_Ayar', None); bpy.context.scene.collection.objects.link(ayar)
    ayar['K'], ayar['Kb'], ayar['renkB'], ayar['dis'] = K, Kb, renkB, 'isik'; kartlar.append(ayar)
    print(f'  K {K:.3f}, Kb {Kb:.3f}, renkB {[round(v, 2) for v in renkB]}; pişirme {time.time() - t0:.0f} sn')

# Dokular: Temel Renk'e bağlı resmi (doğrudan ya da çarpan düğümünden) küçült, çarpanı piksellere işle, doğrudan bağla
yapilan = {}
for m in {s.material for o in secim for s in o.material_slots if s.material}:
    nt = m.node_tree; b = nt.nodes.get('Principled BSDF')
    if not b or not b.inputs['Base Color'].is_linked: continue
    kay = b.inputs['Base Color'].links[0].from_node; carp = np.ones(3)
    if kay.type == 'MIX':
        carp = np.array(kay.inputs[7].default_value[:3]); kay = kay.inputs[6].links[0].from_node if kay.inputs[6].is_linked else None
    if not kay or kay.type != 'TEX_IMAGE' or not kay.image: continue
    anah = (kay.image.name, tuple(np.round(carp, 3)))
    if anah not in yapilan:
        img = kay.image.copy(); img.name = 'dis-' + os.path.splitext(kay.image.name)[0] + ('' if (carp == 1).all() else '-k')
        w, h = img.size; k = BOY / max(w, h)
        if k < 1: img.scale(max(1, round(w * k)), max(1, round(h * k)))
        if not (carp == 1).all():
            px = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32); img.pixels.foreach_get(px)
            px = px.reshape(-1, 4); px[:, :3] *= carp; img.pixels.foreach_set(px.ravel())
        img.pack(); yapilan[anah] = img
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = yapilan[anah]
    if kay.inputs['Vector'].is_linked: nt.links.new(kay.inputs['Vector'].links[0].from_socket, t.inputs['Vector'])
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    if m.name == 'Dis_Pencere':                         # ışıma sitede verilir (doku × sıcak renk); düğüm zinciri glTF'e geçmez
        for l in list(b.inputs['Emission Color'].links): nt.links.remove(l)
        b.inputs['Emission Strength'].default_value = 0.0
    # normal ve pürüz haritaları sitede kullanılmıyor: dosyayı büyütmesin
    for inp in ('Normal', 'Roughness'):
        for l in list(b.inputs[inp].links): nt.links.remove(l)
print('Doku:', len(yapilan))

bpy.ops.object.select_all(action='DESELECT')
for o in secim + kartlar: o.select_set(True)
ayar = dict(filepath=GLB, export_format='GLB', use_selection=True, export_extras=True,
            export_image_format='WEBP', export_image_quality=80,
            export_cameras=False, export_lights=False, export_yup=True,
            export_apply=True, export_texcoords=True, export_normals=True, export_tangents=False, export_vertex_color='NONE',
            export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12 if CANLI else 14)   # ışık haritası UV'si piksel hassasiyetinde
bpy.ops.export_scene.gltf(**ayar)
veri = open(GLB, 'rb').read()
open(JS, 'w', encoding='ascii').write('window.HAN_DIS_GLB="' + base64.b64encode(veri).decode('ascii') + '";\n')
print(f'Yazıldı: {GLB} ({len(veri) / 1e6:.2f} MB), {JS}')
print('TAMAM')
