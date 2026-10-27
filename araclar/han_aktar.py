# -*- coding: utf-8 -*-
"""
YENİ HAN — SİTEYE AKTARMA (Blender betiği)
==========================================
3d/han/han-detay.blend dosyasını açar, siteye gerekmeyenleri bırakır, dokuları küçültür ve tek dosya olarak dışa aktarır.
Asıl model ve 3d/dokular/ DEĞİŞMEZ (her şey yalnızca bu betiğin belleğinde). Eski tavernanın aktarıcısı taverna_npr_aktar.py.

İki sürüm (Yeni Han adım 4: ışık denemesi):
  canlı  (varsayılan)  masa/han.glb + han.js           ışığı site canlı hesaplar (eski taverna gibi)
  pişmiş ("pismis")    masa/han-pismis.glb + .js       ışık Blender'da (Cycles) "ışık haritasına" (resim) pişirilir;
                                                      site duvara, zemine, eşyaya ışık hesaplamaz
  "-- pismis deneme": küçük haritalar ve az ışınla hızlı deneme (süre ölçmek için)

Pişmiş ışık nasıl saklanır (2026-10-27'den beri ışık haritası; önce köşe rengiydi, gölgeler lekeli çıkıyordu):
  Her nesneye ikinci bir UV haritası ("Isik", sitede uv1) açılır; bütün nesneler tek resimde kendi yerini alır.
  isik-a (HARITA px) = titremeyen ışıklar (aplik, fener, oda, dolgu, gök), √(ışık / K)
  isik-b / -c / -d (HARITA_B px, gri) = yalnızca şömine / avize / mumlar (KUMELER), √(güç / Kx); site her birini ayrı titretir.
  K, Kb…Kd ve kümelerin rengi (renkB…renkD) "Isik_Ayar"da (2026-10-27: avize ve mumlar da titresin diye ayrıldı).
  Resimler .glb'ye gizli kartların (Isik_Harita_A…D) parlama dokusu olarak girer; PNG kopyaları 3d/han/isik/.
Karekök: karanlık yerlerde de ayrım kalsın diye (resim 8 bit, karanlık tonlar sıkışmasın).

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
       'harita': 512, 'gorev-panosu': 512, 'kitap-sirtlari': 256, 'demir': 256, 'cuval': 256, 'saksi-toprak': 256,
       'isik-a': 4096, 'isik-b': 4096, 'isik-c': 4096, 'isik-d': 4096}              # ışık haritaları küçültülmez (boyları pişirmede belli)
VARSAYILAN = 512
# Pişirme (ışık haritası, 2026-10-27: köşe renginde gölgeler lekeli ve 45 cm'den küçükleri yok oluyordu)
DENEME = 'deneme' in sys.argv                         # "-- pismis deneme": küçük ve hızlı (süre ölçmek için)
ORNEK = 24 if DENEME else 192                         # her pikselde kaç ışın (az olursa tanecikli; YUMUSAK siler)
HARITA = 1024 if DENEME else 2048                     # şömine dışındaki ışığın haritası (px, kare)
HARITA_B = 512 if DENEME else 1024                    # yalnızca şöminenin haritası (yumuşak ışık: yarı boy yeter)
PAY = 0.003                                           # UV parçaları arası boşluk (haritanın payı; 2048'de ~6 px)
KENAR = 4                                             # pişirmede parçaların kenarından dışarı taşırılan px (dikiş görünmesin)
YUMUSAK = 1.2                                         # gürültü silme bulanıklığı (px, A haritasında)
ISIK_KLASOR = os.path.join(KOK, '3d', 'han', 'isik')  # pişen resimlerin PNG kopyası (siteye .glb içinde gider)
# Ayrı pişen (site titretir) ışık kümeleri: harf → Blender ışığının adı ona uyuyor mu. Her biri kendi gri resmi (isik-b, -c, -d):
# tek resmin kanallarına sığdırılmaz, çünkü .glb'deki WEBP rengi yarım çözünürlükte saklar, kanallar birbirine karışır.
KUMELER = {'b': lambda ad: ad in ('Onizleme_isik_somine', 'Onizleme_Somine_Oda'),   # şömine
           'c': lambda ad: ad == 'Onizleme_isik_avize',                             # oyun masasının avizesi
           'd': lambda ad: ad.startswith('Onizleme_isik_mum_')}                     # mumlar (masalar, şamdanlar)

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
    # Paylaşılan şekiller (aynı sandalyenin kopyaları) ayrılır: her kopya ışık haritasında kendi yerini alsın
    for ob in meshler:                                      # şablonlarla (08_Sablonlar, dışa aktarılmaz) paylaşılanlar da ayrılır
        if ob.data.users > 1: ob.data = ob.data.copy()
    # Ölçek uygulanır: ışık haritasında her yüzün payı gerçek (metre) alanıyla orantılı olsun (yalnızca bu betiğin belleğinde)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in meshler: ob.select_set(True)
    bpy.context.view_layer.objects.active = meshler[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # İkinci UV haritası "Isik": dokular birinci haritayı (UVMap) kullanmaya devam eder, ışık haritası ikincisini.
    # Sitede TEXCOORD_1 = uv1 olur; birinci harita yoksa boş bir tane açılır ki ışık haritası hep ikinci sırada kalsın.
    for ob in meshler:
        uv = ob.data.uv_layers
        if not len(uv): uv.new(name='UVMap')
        ilk = uv[0]
        isik = uv.new(name='Isik')
        uv.active = isik; ilk.active_render = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.average_islands_scale()                       # her parçanın payı metre alanıyla orantılı (bütün nesneler birlikte)
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=PAY, shape_method='CONVEX')
    bpy.ops.object.mode_set(mode='OBJECT')
    uvler = np.concatenate([np.array([d.uv[:] for d in ob.data.uv_layers['Isik'].data]) for ob in meshler])
    print(f'  ışık haritası UV hazır ({time.time() - t0:.0f} sn): {len(uvler)} köşe, '
          f'u {uvler[:, 0].min():.3f}–{uvler[:, 0].max():.3f}, v {uvler[:, 1].min():.3f}–{uvler[:, 1].max():.3f}')
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
    # Pişirme hedefi: her malzemeye bağlantısız bir resim düğümü (etkin düğüm). Bütün nesneler aynı resme, kendi UV yerine pişer.
    gri = None                                              # malzemesi olmayan yüz kalmasın (pişirme "etkin resim yok" der)
    for ob in meshler:
        mats = ob.data.materials
        if not len(mats) or any(m is None for m in mats):
            if gri is None: gri = bpy.data.materials.new('Isik_Gri'); gri.use_nodes = True
            if not len(mats): mats.append(gri)
            for i, m in enumerate(mats):
                if m is None: mats[i] = gri
    dugumsuz = {m.name for ob in meshler for m in ob.data.materials if m and not m.use_nodes}
    if dugumsuz: print('  UYARI düğümsüz malzeme (pişirilemez):', sorted(dugumsuz))
    malzemeler = {m for ob in meshler for m in ob.data.materials if m and m.use_nodes}
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
        """Yalnızca 'yanik' ışıklar açıkken dağınık ışığı (renksiz: yalnızca ışık) ışık haritasına yazar."""
        for L in isiklar: L.hide_render = L not in yanik
        img = hedef_resim(ad, boy)
        bpy.ops.object.select_all(action='DESELECT')
        for ob in meshler: ob.select_set(True)
        bpy.context.view_layer.objects.active = meshler[0]
        bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, target='IMAGE_TEXTURES',
                            margin=KENAR, margin_type='EXTEND', use_clear=True)
        a = np.empty(boy * boy * 4, np.float32); img.pixels.foreach_get(a)
        a = a.reshape(boy, boy, 4)[:, :, :3]
        print(f'  {ad}: dolu piksel %{100 * (a.max(2) > 1e-5).mean():.1f}, en çok {a.max():.2f}')
        return a
    kume = {h: [o for o in isiklar if f(o.name)] for h, f in KUMELER.items()}
    print('  ayrı pişen ışıklar:', {h: len(v) for h, v in kume.items()})
    dunya = sahne.world.node_tree.nodes.get('Background').inputs['Strength']; gok = dunya.default_value
    A = pis('Isik_A', HARITA, [o for o in isiklar if not any(o in v for v in kume.values())])
    print(f'  1. pişirme bitti ({time.time() - t0:.0f} sn)')
    dunya.default_value = 0
    T = {}
    for h, v in kume.items():
        T[h] = pis('Isik_' + h.upper(), HARITA_B, v)
        print(f'  {h} pişti ({time.time() - t0:.0f} sn)')
    dunya.default_value = gok
    for g, v in parlak: g.default_value = v
    for m in malzemeler:                                    # pişirme düğümleri çıkar (dışa aktarılmasın)
        for ad in ('Isik_Hedef', 'Isik_UV'):
            n = m.node_tree.nodes.get(ad)
            if n: m.node_tree.nodes.remove(n)
    print(f'  bütün pişirmeler bitti ({time.time() - t0:.0f} sn)')
    # Gürültü: az ışınla pişen resim tanecikli olur; küçük bir Gauss bulanıklığı tanecikleri siler, gölge kenarı yerinde kalır
    def bulanik(x, s):
        if s <= 0: return x
        r = int(3 * s); k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2); k /= k.sum()
        for eksen in (0, 1):
            x = sum(np.roll(x, i - r, axis=eksen) * k[i] for i in range(len(k)))
        return x
    A = bulanik(A, YUMUSAK)
    # Saklama: RGB = √(ışık / K) (karanlıkta da ayrım kalsın). Her küme ayrı resim (gri): √(güç / Kx); rengi renkX.
    dolu = A.max(2) > 1e-5
    K = float(np.percentile(A.max(2)[dolu], 99.7)) if dolu.any() else 1.0
    gri = {}
    for h, X in T.items():
        X = bulanik(X, YUMUSAK * HARITA_B / HARITA)
        lum = X @ np.array([0.2126, 0.7152, 0.0722])
        Kx = float(np.percentile(lum[lum > 1e-5], 99.7)) if (lum > 1e-5).any() else 1.0
        renk = (X.reshape(-1, 3).sum(0) / max(lum.sum(), 1e-6)).tolist()   # kümenin ışığının ortalama rengi (gücü 1 olacak biçimde)
        gri[h] = (np.sqrt(np.clip(lum / Kx, 0, 1)), Kx, renk)
    os.makedirs(ISIK_KLASOR, exist_ok=True)
    def kaydet(ad, rgb):
        boy = rgb.shape[0]
        img = bpy.data.images.new(ad, boy, boy, alpha=False)
        img.colorspace_settings.name = 'Non-Color'                  # ham değer (site karekökü kendisi açar)
        px = np.ones((boy, boy, 4), np.float32); px[:, :, :3] = rgb
        img.pixels.foreach_set(px.ravel())
        img.filepath_raw = os.path.join(ISIK_KLASOR, ad + '.png'); img.file_format = 'PNG'
        img.save()                                          # (renk ayarını burada yeniden yazma: Blender resmi boşaltıp siyah kaydediyordu)
        g = np.empty(boy * boy * 4, np.float32); img.pixels.foreach_get(g)
        print(f'  {ad}.png kaydedildi: ortalama {g.reshape(-1, 4)[:, :3].mean():.3f} (kaydedilen {rgb.mean():.3f})')
        return img
    imA = kaydet('isik-a', np.sqrt(np.clip(A / K, 0, 1)))
    imX = {h: kaydet('isik-' + h, np.repeat(g[:, :, None], 3, 2)) for h, (g, _, _) in gri.items()}
    # Resimler .glb'ye gizli iki küçük kartın "parlama dokusu" olarak girer (site kartları gizler, dokuyu ışık haritası yapar)
    def kart(ad, img):
        me = bpy.data.meshes.new(ad); me.from_pydata([(0, 0, -5), (0.1, 0, -5), (0.1, 0.1, -5)], [], [(0, 1, 2)])
        me.uv_layers.new(name='UVMap')
        m = bpy.data.materials.new(ad); m.use_nodes = True
        nt = m.node_tree; b = nt.nodes.get('Principled BSDF'); t = nt.nodes.new('ShaderNodeTexImage'); t.image = img
        nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.0
        me.materials.append(m)
        ob = bpy.data.objects.new(ad, me); bpy.context.scene.collection.objects.link(ob)
        secim.append(ob)
    kart('Isik_Harita_A', imA)
    for h, im in imX.items(): kart('Isik_Harita_' + h.upper(), im)
    ayar = bpy.data.objects.new('Isik_Ayar', None); bpy.context.scene.collection.objects.link(ayar)
    ayar['K'] = K
    for h, (_, Kx, renk) in gri.items(): ayar['K' + h], ayar['renk' + h.upper()] = Kx, renk
    secim.append(ayar)
    print(f'  K {K:.3f}', {h: (round(Kx, 3), [round(v, 2) for v in renk]) for h, (_, Kx, renk) in gri.items()})

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
ayar.update(export_vertex_color='NONE')
if PISMIS: ayar.update(export_draco_texcoord_quantization=14)   # ışık haritası UV'si (uv1) 2048 px'te piksel hassasiyetinde kalsın
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
