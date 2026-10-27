# -*- coding: utf-8 -*-
"""
YENİ HAN — SİTEYE AKTARMA (Blender betiği)
==========================================
3d/han/han-detay.blend dosyasını açar, siteye gerekmeyenleri bırakır, dokuları küçültür ve tek dosya olarak dışa aktarır.
Asıl model ve 3d/dokular/ DEĞİŞMEZ (her şey yalnızca bu betiğin belleğinde). Eski tavernanın aktarıcısı taverna_npr_aktar.py.

İki sürüm (Yeni Han adım 4: ışık denemesi):
  canlı  (varsayılan)  masa/han.glb + han.js           ışığı site canlı hesaplar (eski taverna gibi)
  pişmiş ("pismis")    masa/han-pismis.glb + .js       ışık Blender'da (Cycles) hesaplanır, her köşeye renk olarak yazılır
                                                      ("vertex color"); site duvara, zemine, eşyaya ışık hesaplamaz

Pişmiş ışık nasıl saklanır: her köşenin "Isik" renginde
  RGB = şöminenin dışındaki bütün ışıklar (avize, aplik, fener, mum, oda, dolgu, gök), karekökü alınmış ve K'ye bölünmüş
  A   = yalnızca şömine (gücü); site bunu titreterek ekler. K, Kb ve şöminenin rengi "Isik_Ayar" nesnesinde.
Karekök: karanlık yerlerde de ayrım kalsın diye (renk 0–1 arası saklanır, karanlık tonlar sıkışmasın).

Önce asıl model hazır olmalı (araclar/han_detay_blender.py).
Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --python araclar\\han_aktar.py
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --python araclar\\han_aktar.py -- pismis
Site: adresin sonuna ?sahne=han ya da ?sahne=han-pismis (index.html BÖLÜM 11b, SAHNE).
"""
import bpy, bmesh, os, sys, base64, math, time
import numpy as np

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(KOK, '3d', 'han', 'han-detay.blend')
PISMIS = 'pismis' in sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else False
AD = 'han-pismis' if PISMIS else 'han'
GLOB = 'HAN_PISMIS_GLB' if PISMIS else 'HAN_GLB'                 # .js dosyasının doldurduğu değişken (index.html: SAHNE)
GLB, JS = os.path.join(KOK, 'masa', AD + '.glb'), os.path.join(KOK, 'masa', AD + '.js')

# ───────── AYARLAR ─────────
DISARIDA_KOL = {'08_Sablonlar', '99_Onizleme'}
DISARIDA_AD = ('Masa_Orta_Sandalye_',)              # oyun masasının sandalyeleri: site koltuk sayısı kadar koyar
POV_KOL = {'Tavan', 'Avize'}                         # yalnızca göz hizasında görünenler (tepeden bakışta gizli)
POV_AD = ('Sundurma_Sacak',)
WEBP_KALITE = 80
BOY = {'hali': 1024, 'post': 512, 'deri': 256, 'zemin-ahsap': 1024, 'duvar-siva': 1024, 'masa-ahsap': 1024,
       'tas-altigen': 1024, 'tas-blok': 512, 'dis-zemin': 512, 'kalkan-1': 256, 'kalkan-2': 256, 'tabela': 512, 'sancak': 256,
       'harita': 512, 'gorev-panosu': 512, 'kitap-sirtlari': 256, 'demir': 256, 'cuval': 256, 'saksi-toprak': 256}
VARSAYILAN = 512
# Pişirme
ORNEK = 256                                           # her köşede kaç ışın (az olursa lekeli)
SIK = 0.45                                            # büyük yüzler bu boydan (m) uzun kenar kalmayana dek bölünür (ışık köşelerde saklanır)
SOMINE_ISIK = ('Onizleme_isik_somine', 'Onizleme_Somine_Oda')

bpy.ops.wm.open_mainfile(filepath=BLEND)
O = bpy.data.objects

def kolda_mi(ob, adlar):
    for kol in ob.users_collection:
        k = kol
        while k:
            if k.name in adlar: return True
            k = next((p for p in bpy.data.collections if k.name in p.children), None)
    return False
secim = [ob for ob in O if ob.type in {'MESH', 'EMPTY'} and not ob.name.startswith(DISARIDA_AD) and not kolda_mi(ob, DISARIDA_KOL)]
meshler = [ob for ob in secim if ob.type == 'MESH']

# ───────── PİŞİRME (yalnızca pişmiş sürüm) ─────────
if PISMIS:
    t0 = time.time()
    sahne = bpy.context.scene
    for k in bpy.data.collections: k.hide_render = k.name == '08_Sablonlar'
    for ob in O: ob.hide_render = False; ob.hide_set(False)
    # Kendi ışığını saçan yüzler (alev, kor, fener camı) pişirmede kapalı: ışıkları zaten ışık işaretleri veriyor; yoksa
    # mumların alevi şöminenin ayrı pişirmesine de karışır. Dışa aktarmadan önce geri açılır.
    parlak = []
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
        if b and b.inputs['Emission Strength'].default_value > 0:
            parlak.append((b.inputs['Emission Strength'], b.inputs['Emission Strength'].default_value))
            b.inputs['Emission Strength'].default_value = 0
    # Paylaşılan şekiller (aynı sandalyenin kopyaları) ayrılır: her kopya kendi yerindeki ışığı alsın
    paylasilan = {}
    for ob in meshler:
        if ob.data.users > 1:
            if ob.data.name in paylasilan: ob.data = ob.data.copy()
            else: paylasilan[ob.data.name] = 1
    # Büyük yüzler bölünür (ışık köşelerde saklandığı için: 6 m'lik duvarın yalnızca 4 köşesi olsa ışık lekesi görünmez)
    eklenen = 0
    for ob in meshler:
        if ob.name.startswith('Dis_'): continue
        s = ob.matrix_world.to_scale(); sk = max(abs(s.x), abs(s.y), abs(s.z))
        bm = bmesh.new(); bm.from_mesh(ob.data); n0 = len(bm.faces)
        for _ in range(7):
            uzun = [e for e in bm.edges if e.calc_length() * sk > SIK]
            if not uzun: break
            bmesh.ops.subdivide_edges(bm, edges=uzun, cuts=1, use_grid_fill=True)
        if len(bm.faces) != n0: bm.to_mesh(ob.data); eklenen += len(bm.faces) - n0
        bm.free()
    print(f'  bölünen yüzler: +{eklenen}')
    # Cycles: ekran kartıyla (yoksa işlemciyle)
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
    sahne.cycles.samples = ORNEK
    sahne.cycles.max_bounces = 4; sahne.cycles.diffuse_bounces = 3
    isiklar = [o for o in O if o.type == 'LIGHT']
    print(f'  ışık: {len(isiklar)}, şekil: {len(meshler)}')
    for ob in meshler:
        for a in list(ob.data.color_attributes): ob.data.color_attributes.remove(a)
    def pis(katman, yanik):
        """Yalnızca 'yanik' ışıklar açıkken dağınık ışığı (renksiz: yalnızca ışık) her köşeye yazar."""
        for L in isiklar: L.hide_render = L not in yanik
        for ob in meshler:
            a = ob.data.color_attributes.new(katman, 'FLOAT_COLOR', 'CORNER')
            ob.data.color_attributes.active_color = a
        bpy.ops.object.select_all(action='DESELECT')
        for ob in meshler: ob.select_set(True)
        bpy.context.view_layer.objects.active = meshler[0]
        bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, target='VERTEX_COLORS')
    somine = [o for o in isiklar if o.name in SOMINE_ISIK]
    dunya = sahne.world.node_tree.nodes.get('Background').inputs['Strength']; gok = dunya.default_value
    pis('Isik_A', [o for o in isiklar if o not in somine])
    print(f'  1. pişirme bitti ({time.time() - t0:.0f} sn)')
    dunya.default_value = 0
    pis('Isik_B', somine)
    dunya.default_value = gok
    for g, v in parlak: g.default_value = v
    print(f'  2. pişirme bitti ({time.time() - t0:.0f} sn)')
    # İki katman tek renge: RGB = √(A / K), A(alfa) = √(şömine gücü / Kb)
    def oku(me, ad):
        a = np.empty(len(me.loops) * 4, np.float32); me.color_attributes[ad].data.foreach_get('color', a); return a.reshape(-1, 4)
    hepA = np.concatenate([oku(ob.data, 'Isik_A')[:, :3] for ob in meshler])
    hepB = np.concatenate([oku(ob.data, 'Isik_B')[:, :3] for ob in meshler])
    lumB = hepB @ np.array([0.2126, 0.7152, 0.0722])
    K = float(np.percentile(hepA.max(1), 99.5)) or 1.0
    Kb = float(np.percentile(lumB, 99.5)) or 1.0
    renkB = (hepB.sum(0) / max(lumB.sum(), 1e-6)).tolist()             # şömine ışığının ortalama rengi (gücü 1 olacak biçimde)
    for ob in meshler:
        me = ob.data; A, B = oku(me, 'Isik_A'), oku(me, 'Isik_B')
        c = np.empty_like(A)
        c[:, :3] = np.sqrt(np.clip(A[:, :3] / K, 0, 1))
        c[:, 3] = np.sqrt(np.clip((B[:, :3] @ np.array([0.2126, 0.7152, 0.0722])) / Kb, 0, 1))
        for ad in ('Isik_A', 'Isik_B'): me.color_attributes.remove(me.color_attributes[ad])
        hedef = me.color_attributes.new('Isik', 'FLOAT_COLOR', 'CORNER'); hedef.data.foreach_set('color', c.ravel())
        me.color_attributes.active_color = hedef; me.color_attributes.render_color_index = 0
    ayar = bpy.data.objects.new('Isik_Ayar', None); bpy.context.scene.collection.objects.link(ayar)
    ayar['K'], ayar['Kb'], ayar['renkB'] = K, Kb, renkB
    secim.append(ayar)
    print(f'  K {K:.3f}, Kb {Kb:.3f}, şömine rengi {[round(v, 2) for v in renkB]}')

# ───────── Malzemeler ve dokular ─────────
for m in bpy.data.materials:                        # normal ve pürüz haritaları çıkar (sitede işe yaramaz, dosyayı büyütür)
    if not m.use_nodes: continue
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type == 'NORMAL_MAP': nt.nodes.remove(n)
    b = nt.nodes.get('Principled BSDF')
    if b:
        for ad in ('Roughness', 'Metallic'):
            for l in list(b.inputs[ad].links): nt.links.remove(l)
for img in bpy.data.images:
    if not img.filepath or img.size[0] == 0: continue
    ad = os.path.splitext(os.path.basename(img.filepath))[0]
    k = BOY.get(ad, VARSAYILAN) / max(img.size)
    if k < 1: img.scale(max(1, round(img.size[0] * k)), max(1, round(img.size[1] * k)))

# ───────── Seçim ve etiketler (duvar etiketleri han_detay_blender.py'de kondu) ─────────
bpy.ops.object.select_all(action='DESELECT')
pov = 0
for ob in secim:
    ob.hide_set(False); ob.select_set(True)
    if ob.name.startswith(POV_AD) or kolda_mi(ob, POV_KOL): ob['pov'] = 1; pov += 1
print(f'  seçilen nesne: {len(secim)}, duvar etiketli: {sum(1 for o in secim if "duvar" in o.keys())}, yalnızca göz hizası: {pov}')

# ───────── Dışa aktar ─────────
ayar = dict(filepath=GLB, export_format='GLB', use_selection=True, export_extras=True,
            export_image_format='WEBP', export_image_quality=WEBP_KALITE,
            export_cameras=False, export_lights=False, export_yup=True,
            export_apply=True, export_texcoords=True, export_normals=True, export_tangents=False,
            export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12)
if PISMIS: ayar.update(export_vertex_color='ACTIVE', export_draco_color_quantization=10)
else: ayar.update(export_vertex_color='NONE')
try:
    bpy.ops.export_scene.gltf(**ayar)
except TypeError as e:
    print('AYAR HATASI:', e)
    print('  geçerli ayarlar:', sorted(p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties))
    raise SystemExit(1)
veri = open(GLB, 'rb').read()
with open(JS, 'w', encoding='utf-8') as f:
    f.write('/* Yeni han (araclar/han_aktar.py üretir; elle değiştirme). Site bilgisayardan açılınca .glb yerine bu okunur. */\n')
    f.write(f'window.{GLOB}="' + base64.b64encode(veri).decode('ascii') + '";\n')
print(f'  {GLB}: {len(veri) / 1024 / 1024:.2f} MB')
print('TAMAM')
