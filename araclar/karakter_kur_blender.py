# -*- coding: utf-8 -*-
"""
SKETCHFAB MODELİNDEN SİTE KARAKTERİ (2026-10-28; siteye yüklenmez, çıktısı yüklenir)
Kullanıcı "3D karakter referans modelleri/" klasörüne hazır modeller indirdi (Sketchfab, CC-BY; kaynaklar referanslar.txt).
Asıl istenen gorseller/3d karakterler/ içindeki karakter kâğıtlarındaki görünüş: bu betik hazır modeli alır, kâğıda benzetir
(dokuyu bölge bölge yeniden boyar, gereksiz parçaları siler, gözlük / tüy / anahtar gibi parçalar ekler), büyücünün kemik
adlarıyla bir iskelet kurar, poza sokar, hareketini ekler ve masa/ içine yazar.

Karakterler (komutun sonundaki ad):
  dm     "Meshy_AI_ Aurelian" (aliyaz01)          → kâğıt DM-human.jpg      → masa/dm-iskelet.glb / .js (oturur, zar_at)
  hanci  "The Noble Craftsman" (olmopotums)       → kâğıt hanci-dwarf.jpg   → masa/hanci.glb / .js (tezgâhın arkasında ayakta, bekle)

Aşamalar (ikinci ad; verilmezse ikisi sırayla):
  ham    modeli içe al, birleştir, kaideyi ve gereksiz parçaları sil, hafiflet; dokunun her pikselinin modelin neresine
         düştüğünü (konum haritası) pişir → 3d/karakter/<ad>-ham.blend, <ad>-konum.npy
  kur    ham dosyadan: dokuyu boya (karakter_boya.py), parça ekle, iskelet kur, poz, hareket, dışa aktar, önizleme

Çalıştırma (proje klasöründen):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --factory-startup --python araclar\\karakter_kur_blender.py -- dm
"""
import bpy, bmesh, math, base64, pathlib, sys
import numpy as np
from mathutils import Matrix, Vector

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
AD = ARGS[0] if ARGS else 'dm'
ASAMA = ARGS[1:] or ['ham', 'kur']
KOK = pathlib.Path.cwd()
REF = KOK / '3D karakter referans modelleri'
ARA = KOK / '3d' / 'karakter'                     # ara dosyalar ve önizlemeler (GitHub'a gitmez)
ARA.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(KOK / 'araclar'))

AYAR = {
    'dm': dict(girdi='dm.glb', yuz=32000, doku=2048,
               kes_alt=-0.903,                  # ayakların altındaki kaide
               sil_kutu=[((-0.2, 0.35), (-0.43, -0.015), (0.22, 0.66))],    # elindeki kitap (gövdeyle kaynaşık; renginden seçilir)
               koru='DM_KOL'),                  # sol ön kol (karakter_boya.DM_KOL): kitabın gölgesinde, silinmesin
    'garson_kiz': dict(girdi='kadın-garson.glb', yuz=24000, doku=2048, cikti_doku=1024),     # "Classic Maid Uniform" (restore50)
    'garson_erkek': dict(girdi='erkek-garson.glb', yuz=24000, doku=2048, cikti_doku=1024,   # "Medieval Peasant Warrior" (Azura_SQ)
                         sil_kutu=[((0.215, 0.37), (-0.08, 0.22), (-0.46, 0.22))]),   # sol kalçadaki kılıç ve kını
    'fighter': dict(girdi='archer-v1.glb', yuz=32000, doku=2048),   # "GA Free_251_The Shrewd Scoundrel" (Galaxy Abundant)
    'hanci': dict(girdi='hanci.glb', yuz=None, doku=2048, alcak=2800,   # alcak: büyücü gibi az çokgenli (üçgen sayısı), düz renkli
                  sil=('Anvil', 'Hammer', 'HotIron', 'Plane0', 'ShoulderPads')),   # örs, çekiç, kızgın demir, kıvılcımlar, omuz zırhı
}[AD]


def secili(obs, aktif=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active = aktif or obs[0]


def ham():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(REF / AYAR['girdi']))
    for o in list(bpy.context.scene.objects):
        if o.type == 'MESH' and any(k in o.name for k in AYAR.get('sil', ())):
            bpy.data.objects.remove(o, do_unlink=True)
    ms = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for o in ms:                                   # ebeveynlerden kurtar (dünyadaki yerleri kalsın)
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in list(bpy.context.scene.objects):
        if o.type != 'MESH': bpy.data.objects.remove(o, do_unlink=True)
    secili(ms)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if len(ms) > 1: bpy.ops.object.join()
    ob = bpy.context.active_object; ob.name = AD
    me = ob.data
    renk_uv(ob)
    while len(me.uv_layers) > 1: me.uv_layers.remove(me.uv_layers[-1])   # yalnızca ilk UV (renk_uv onu renk dokusuna göre doldurdu)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)              # parçalara bölünmüş modelin dikişleri
    if 'kes_alt' in AYAR:
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < AYAR['kes_alt']], context='VERTS')
    bm.to_mesh(me); bm.free()
    if AYAR['yuz'] and len(me.polygons) > AYAR['yuz']:
        md = ob.modifiers.new('az', 'DECIMATE'); md.ratio = AYAR['yuz'] / len(me.polygons)
        bpy.ops.object.modifier_apply(modifier=md.name)
    if 'sil_kutu' in AYAR: kutu_sil(ob)
    if AD == 'fighter': fighter_bas(ob)
    print('YUZ', len(me.polygons), 'KOSE', len(me.vertices))
    konum_pisir(ob)
    bpy.ops.wm.save_as_mainfile(filepath=str(ARA / f'{AD}-ham.blend'))


def renk_uv(ob):
    """Renk dokusunun gerçekten okuduğu UV katmanını ve glTF doku dönüşümünü (Mapping düğümü: ölçek, kaydırma) bulur, sonucu ilk
    UV katmanına yazar ve düğümleri kaldırır. (Meshy modellerinde doku beş UV katmanından birini, kimi zaman 16 kat büyütüp
    kaydırarak okuyor; bunu bilmeyince kadın garsonun dokusu yamalı görünüyordu.)"""
    me = ob.data
    for m in me.materials:
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m and m.use_nodes else None
        if not b or not b.inputs['Base Color'].is_linked: continue
        tx = b.inputs['Base Color'].links[0].from_node
        ad, olc, kay = me.uv_layers.active.name, (1, 1), (0, 0)
        v = tx.inputs['Vector'].links[0].from_node if tx.inputs['Vector'].is_linked else None
        if v and v.type == 'MAPPING':
            olc, kay = tuple(v.inputs['Scale'].default_value)[:2], tuple(v.inputs['Location'].default_value)[:2]
            v = v.inputs['Vector'].links[0].from_node if v.inputs['Vector'].is_linked else None
        if v and v.type == 'UVMAP' and v.uv_map: ad = v.uv_map
        uv = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers[ad].data.foreach_get('uv', uv); uv = uv.reshape(-1, 2)
        uv = uv * np.array(olc, np.float32) + np.array(kay, np.float32)
        me.uv_layers[0].data.foreach_set('uv', uv.ravel())
        for l in list(tx.inputs['Vector'].links): m.node_tree.links.remove(l)
        print('RENK_UV', ad, olc, kay)
        return


def doku_dizi(ob):
    """Modelin renk dokusu (H×W×3, 0…1; satır 0 = altta, Blender'daki gibi)."""
    for m in ob.data.materials:
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b and b.inputs['Base Color'].is_linked:
            im = b.inputs['Base Color'].links[0].from_node.image
            return np.array(im.pixels[:], np.float32).reshape(im.size[1], im.size[0], 4)[..., :3], im


def yuz_renk(ob):
    """Her yüzün UV ortasındaki doku rengi ve yüz ortaları (N×3)."""
    me = ob.data
    C, _ = doku_dizi(ob)
    uv = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers.active.data.foreach_get('uv', uv); uv = uv.reshape(-1, 2)
    bas = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', bas)
    say = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('loop_total', say)
    u = np.add.reduceat(uv, bas) / say[:, None]
    H, W = C.shape[:2]
    renk = C[np.clip((u[:, 1] % 1) * H, 0, H - 1).astype(int), np.clip((u[:, 0] % 1) * W, 0, W - 1).astype(int)]
    orta = np.zeros(len(me.polygons) * 3, np.float32); me.polygons.foreach_get('center', orta)
    return renk, orta.reshape(-1, 3)


def kutu_sil(ob):
    """Gövdeyle kaynaşık eşyalar (DM'in kitabı, erkek garsonun kılıcı): AYAR['sil_kutu'] kutularının içindeki doygun ya da koyu
    renkli yüzler silinir; ten (eller) ve az doygun kumaş (kollar) kalır. Sonra kopup kalan küçük kırıntılar da silinir."""
    import karakter_boya as kb
    renk, o = yuz_renk(ob)
    h, s, v = kb.hsv(renk)
    kutu = np.zeros(len(o), bool)
    for (x0, x1), (y0, y1), (z0, z1) in AYAR['sil_kutu']:
        kutu |= (o[:, 0] > x0) & (o[:, 0] < x1) & (o[:, 1] > y0) & (o[:, 1] < y1) & (o[:, 2] > z0) & (o[:, 2] < z1)
    ten = (h < 0.085) & (s > 0.2) & (s < 0.5) & (v > 0.55)
    kitap = kutu & ~ten & ((s > 0.3) | (v < 0.3))
    if 'koru' in AYAR:                                               # gölgede kalan kol kalır; avuçtaki kitap tahtası (doygun, koyu),
        kap = getattr(kb, AYAR['koru'])                              #   altın süs ve eldeki krem sayfalar gider (ölçüldü: ten s 0,3–0,5)
        altin = (h > 0.1) & (h < 0.18) & (s > 0.45)
        tahta = (s > 0.45) & (v < 0.5)
        sayfa = (o[:, 1] < -0.06) & (s < 0.25) & (v > 0.45)          # kolun önü (kol yeni geride, y > −0,06)
        kitap = np.where(kb.kapsul(o, kap), altin | tahta | sayfa, kitap)
    bm =bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in np.nonzero(kitap)[0]], context='FACES')
    kirinti_sil(bm, 400)
    bm.to_mesh(ob.data); bm.free()
    print('SILINDI', int(kitap.sum()), 'yüz')


def alcak_poli(ob, ucgen, renk_sayisi=16, hucre=16, temizle=3):
    """Büyücü gibi az çokgenli (2026-10-28, kullanıcı: "low poly çeksek bu sanatla uyuşur mu"): model ucgen kadar üçgene iner,
    her yüz düz tek renk olur. Renk, boyanmış yüksek çözünürlüklü modelde o yüzün altına düşen küçük yüzlerin ortancası;
    renkler renk_sayisi kadar palete toplanır (k-ortalama); sonra her yüz komşularının çoğunluk rengini alır (temizle kez: dokudaki
    pişmiş ışık-gölge yüzden yüze alaca bir görünüm veriyordu, büyücüde her parça tek renk), palet büyücünün peopleColors'u gibi küçük bir dokuda (8×8 hücre,
    hücre başına hucre px: uzaktan bakınca komşu hücre karışmasın), her yüzün UV'si kendi hücresinin ortasında."""
    from mathutils.kdtree import KDTree
    renk, orta = yuz_renk(ob)                                       # boyanmış dokudan (yüksek çözünürlük)
    kd = KDTree(len(orta))
    for i, c in enumerate(orta): kd.insert(c, i)
    kd.balance()
    md = ob.modifiers.new('az', 'DECIMATE'); md.ratio = min(1.0, ucgen / sum(len(p.vertices) - 2 for p in ob.data.polygons))
    md.use_collapse_triangulate = True
    secili([ob]); bpy.ops.object.modifier_apply(modifier=md.name)
    me = ob.data
    V = np.array([v.co[:] for v in me.vertices], np.float32)
    yr = np.zeros((len(me.polygons), 3), np.float32)
    for p in me.polygons:                                           # yüzün ortası ve köşelere doğru üç nokta: altındaki küçük yüzlerin ortancası
        c = np.array(p.center[:], np.float32); nokta = [c] + [c + (V[i] - c) * 0.6 for i in p.vertices]
        yr[p.index] = np.median([renk[kd.find(q)[1]] for q in nokta], 0)
    rng = np.random.default_rng(5); mer = yr[rng.choice(len(yr), renk_sayisi, replace=False)]
    for _ in range(25):                                             # k-ortalama
        es = np.argmin(((yr[:, None] - mer[None]) ** 2).sum(-1), 1)
        for k in range(renk_sayisi):
            if (es == k).any(): mer[k] = yr[es == k].mean(0)
    es = np.argmin(((yr[:, None] - mer[None]) ** 2).sum(-1), 1)
    komsu = [[] for _ in me.polygons]                               # kenar komşuları
    kenar = {}
    for p in me.polygons:
        for e in p.edge_keys: kenar.setdefault(e, []).append(p.index)
    for fs in kenar.values():
        for a in fs:
            komsu[a] += [b for b in fs if b != a]
    for _ in range(temizle):                                        # çoğunluk süzgeci (kendisi 1,5 oy)
        yeni = es.copy()
        for i, ks in enumerate(komsu):
            oy = np.bincount(es[ks], minlength=renk_sayisi).astype(np.float32) if ks else np.zeros(renk_sayisi, np.float32)
            oy[es[i]] += 1.5; yeni[i] = int(np.argmax(oy))
        es = yeni
    for k in range(renk_sayisi):
        if (es == k).any(): mer[k] = np.median(yr[es == k], 0)
    n = 8 * hucre
    im = bpy.data.images.new('alcakRenkler', n, n)
    px = np.ones((n, n, 4), np.float32)
    for k in range(renk_sayisi):
        r_, c_ = divmod(k, 8); px[r_ * hucre:(r_ + 1) * hucre, c_ * hucre:(c_ + 1) * hucre, :3] = mer[k]
    im.pixels.foreach_set(px.ravel()); im.pack()
    uv = np.zeros((len(me.loops), 2), np.float32)
    for p in me.polygons:
        r_, c_ = divmod(int(es[p.index]), 8)
        uv[list(p.loop_indices)] = ((c_ + 0.5) / 8, (r_ + 0.5) / 8)
        p.use_smooth = False; p.material_index = 0
    me.uv_layers.active.data.foreach_set('uv', uv.ravel())
    m = me.materials[0]
    tx = next(nd for nd in m.node_tree.nodes if nd.type == 'TEX_IMAGE'); tx.image = im; tx.interpolation = 'Closest'
    while len(me.materials) > 1: me.materials.pop()
    print('ALCAK', len(me.polygons), 'yüz', renk_sayisi, 'renk')


def uv_kapsam(ob, n):
    """Dokunun (n×n, satır 0 altta) UV üçgenlerinin içine düşen pikselleri (doku parçaları; arası kenar payı)."""
    me = ob.data
    uv = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers.active.data.foreach_get('uv', uv); uv = (uv.reshape(-1, 2) % 1) * n - 0.5
    M = np.zeros((n, n), bool)
    for p in me.polygons:
        ls = list(p.loop_indices)
        for k in range(1, len(ls) - 1):
            a, b, c = uv[ls[0]], uv[ls[k]], uv[ls[k + 1]]
            x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int); x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int)
            x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, n - 1), min(y1, n - 1)
            if x1 < x0 or y1 < y0: continue
            X, Y = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
            d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(d) < 1e-9: continue
            l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / d
            l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / d
            ic = (l1 >= -0.02) & (l2 >= -0.02) & (1 - l1 - l2 >= -0.02)
            M[Y[ic], X[ic]] = True
    print('KAPSAM', round(M.mean(), 3))
    return M


def kirinti_sil(bm, en_az):
    """en_az yüzden küçük kopuk parçaları siler."""
    bm.faces.ensure_lookup_table()
    gor = set(); sil = []
    for f in bm.faces:
        if f.index in gor: continue
        st = [f]; gor.add(f.index); par = []
        while st:
            g = st.pop(); par.append(g)
            for e in g.edges:
                for k in e.link_faces:
                    if k.index not in gor: gor.add(k.index); st.append(k)
        if len(par) < en_az: sil += par
    if sil: bmesh.ops.delete(bm, geom=sil, context='FACES')
    print('KIRINTI', len(sil))


def parcalar(ob):
    """Modelin kopuk parçaları (birbirine kenarla bağlı yüz kümeleri): yüz → parça no (0 en büyüğü)."""
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table()
    no = np.full(len(bm.faces), -1, np.int32); kumeler = []
    for f in bm.faces:
        if no[f.index] >= 0: continue
        st = [f]; no[f.index] = len(kumeler); kume = []
        while st:
            g = st.pop(); kume.append(g.index)
            for e in g.edges:
                for k in e.link_faces:
                    if no[k.index] < 0: no[k.index] = len(kumeler); st.append(k)
        kumeler.append(kume)
    sira = np.argsort([-len(k) for k in kumeler]); yeni = np.empty_like(sira); yeni[sira] = np.arange(len(sira))
    no = yeni[no]
    orta = np.zeros(len(bm.faces) * 3, np.float32); ob.data.polygons.foreach_get('center', orta); orta = orta.reshape(-1, 3)
    for i in range(min(len(kumeler), 40)):
        m = no == i
        print('PARCA %2d yüz=%5d  x[%6.1f %6.1f] y[%6.1f %6.1f] z[%6.1f %6.1f]' % (i, m.sum(), *[f(orta[m][:, j]) for j in range(3) for f in (np.min, np.max)]))
    bm.free()
    return no


def pisir(ob, n, dugum_kur):
    """Modelin dokusuna (UV) bir değer pişirir: dugum_kur(nt) yayılacak rengi veren çıkışı döndürür. Pişmeyen pikseller −1."""
    im = bpy.data.images.new('pisir', n, n, float_buffer=True, alpha=True)
    im.pixels.foreach_set(np.full(n * n * 4, -1, np.float32))
    mat = bpy.data.materials.new('pisir'); mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    em = nt.nodes.new('ShaderNodeEmission'); out = nt.nodes.new('ShaderNodeOutputMaterial')
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = im; nt.nodes.active = tx
    nt.links.new(dugum_kur(nt), em.inputs['Color']); nt.links.new(em.outputs[0], out.inputs['Surface'])
    eski = list(ob.data.materials)
    ob.data.materials.clear(); ob.data.materials.append(mat)
    sah = bpy.context.scene
    sah.render.engine = 'CYCLES'; sah.cycles.samples = 1; sah.cycles.device = 'CPU'
    sah.render.bake.margin = 0
    secili([ob])
    bpy.ops.object.bake(type='EMIT')
    a = np.array(im.pixels[:], np.float32).reshape(n, n, 4)
    ob.data.materials.clear()
    for m in eski: ob.data.materials.append(m)
    bpy.data.materials.remove(mat); bpy.data.images.remove(im)
    return a


def konum_pisir(ob):
    """Dokunun her pikseline düşen 3D noktayı (P, metre ya da modelin birimi) ve parçanın numarasını (parca) pişirir:
    boyama bölgeleri buna göre seçilir."""
    n = AYAR['doku']
    a = pisir(ob, n, lambda nt: nt.nodes.new('ShaderNodeTexCoord').outputs['Generated'])   # sınır kutusunda 0…1
    mn = np.array([min((ob.matrix_world @ Vector(c))[i] for c in ob.bound_box) for i in range(3)])
    mx = np.array([max((ob.matrix_world @ Vector(c))[i] for c in ob.bound_box) for i in range(3)])
    P = mn + a[..., :3] * (mx - mn)
    maske = a[..., 0] > -0.5
    no = parcalar(ob)                                             # parça numarası köşe rengi olarak (no + 0,5) / 1000
    ca = ob.data.color_attributes.new('parca', 'FLOAT_COLOR', 'CORNER')
    say = np.zeros(len(ob.data.polygons), np.int32); ob.data.polygons.foreach_get('loop_total', say)
    r = np.repeat((no + 0.5) / 1000, say).astype(np.float32)
    ca.data.foreach_set('color', np.stack([r, r * 0, r * 0, r * 0 + 1], -1).ravel())
    def oznitelik(nt):
        at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'parca'; return at.outputs['Color']
    b = pisir(ob, n, oznitelik)
    ob.data.color_attributes.remove(ob.data.color_attributes['parca'])
    parca = np.where(b[..., 0] > -0.5, np.floor(b[..., 0] * 1000), -1).astype(np.int16)
    np.savez_compressed(ARA / f'{AD}-konum.npz', P=P.astype(np.float32), maske=maske, parca=parca)
    print('KONUM', maske.mean().round(3), mn, mx)


# ---------------------------------------------------------------- İSKELET
# Kemikler büyücünün adlarıyla (site ve zar_hareket.py bu adları kullanır): (ad, ebeveyn, baş eklemi, uç eklemi)
KEMIKLER = [
    ('bip Pelvis_02', None, 'legen', 'bel'),
    ('bip Spine_03', 'bip Pelvis_02', 'bel', 'gogus'),
    ('bip Spine1_04', 'bip Spine_03', 'gogus', 'boyun'),
    ('bip Neck_05', 'bip Spine1_04', 'boyun', 'bas'),
    ('bip Head_06', 'bip Neck_05', 'bas', 'tepe'),
]
for t, n in (('L', (7, 8, 9, 10, 11, 12, 13, 14, 23, 24, 25, 26)), ('R', (15, 16, 17, 18, 19, 20, 21, 22, 27, 28, 0, 29))):
    k = t.lower()
    ad = lambda tur, i: f'bip {t} {tur}_0{n[i]}'                     # büyücüdeki gibi: Clavicle_07, Hand_010, Foot_00
    KEMIKLER += [
        (ad('Clavicle', 0), 'bip Spine1_04', f'kprc_{k}', f'omuz_{k}'),
        (ad('UpperArm', 1), ad('Clavicle', 0), f'omuz_{k}', f'dirsek_{k}'),
        (ad('Forearm', 2), ad('UpperArm', 1), f'dirsek_{k}', f'bilek_{k}'),
        (ad('Hand', 3), ad('Forearm', 2), f'bilek_{k}', f'bogum_{k}'),
        (ad('Finger0', 4), ad('Hand', 3), f'bas0_{k}', f'bas1_{k}'),          # başparmak
        (ad('Finger01', 5), ad('Finger0', 4), f'bas1_{k}', f'bas2_{k}'),
        (ad('Finger1', 6), ad('Hand', 3), f'bogum_{k}', f'parmak_{k}'),       # dört parmak birlikte
        (ad('Finger11', 7), ad('Finger1', 6), f'parmak_{k}', f'uc_{k}'),
        (ad('Thigh', 8), 'bip Pelvis_02', f'kalca_{k}', f'diz_{k}'),
        (ad('Calf', 9), ad('Thigh', 8), f'diz_{k}', f'ayak_{k}'),
        (ad('Foot', 10), ad('Calf', 9), f'ayak_{k}', f'tarak_{k}'),
        (ad('Toe0', 11), ad('Foot', 10), f'tarak_{k}', f'parmakuc_{k}'),
    ]

# DM'in eklemleri (modelin kendi duruşunda, metre; önizlemelerdeki ızgaradan okundu: 3d/karakter). Kitabı tutan eller havada.
DM_EKLEM = dict(
    legen=(0, 0.16, 0.06), bel=(0, 0.16, 0.14), gogus=(0, 0.16, 0.36), boyun=(0, 0.14, 0.64), bas=(0.01, 0.13, 0.70), tepe=(0.03, 0.12, 0.93),
    kprc_l=(0.03, 0.13, 0.60), omuz_l=(0.165, 0.16, 0.60), dirsek_l=(0.225, 0.07, 0.33), bilek_l=(0.15, -0.195, 0.345),
    bogum_l=(0.08, -0.27, 0.385), parmak_l=(0.045, -0.29, 0.405), uc_l=(0.015, -0.30, 0.42),
    bas0_l=(0.13, -0.225, 0.365), bas1_l=(0.11, -0.245, 0.395), bas2_l=(0.09, -0.255, 0.43),
    kprc_r=(-0.03, 0.13, 0.60), omuz_r=(-0.165, 0.16, 0.60), dirsek_r=(-0.24, 0.10, 0.36), bilek_r=(-0.215, -0.09, 0.54),
    bogum_r=(-0.16, -0.16, 0.60), parmak_r=(-0.15, -0.205, 0.625), uc_r=(-0.14, -0.25, 0.645),
    bas0_r=(-0.19, -0.12, 0.545), bas1_r=(-0.155, -0.15, 0.555), bas2_r=(-0.105, -0.17, 0.58),
    kalca_l=(0.09, 0.16, 0.04), diz_l=(0.11, 0.14, -0.44), ayak_l=(0.19, 0.21, -0.82), tarak_l=(0.21, 0.08, -0.885), parmakuc_l=(0.215, 0.03, -0.89),
    kalca_r=(-0.09, 0.16, 0.04), diz_r=(-0.10, 0.14, -0.44), ayak_r=(-0.185, 0.21, -0.82), tarak_r=(-0.20, 0.08, -0.885), parmakuc_r=(-0.205, 0.03, -0.89),
)
# Başparmak eklemlerini ızgaradan kestirmek zor: eşlemeden sonra eller kendi ekseni çevresinde bu kadar (derece) daha çevrilir
# (önizlemede avuçlar yukarı bakıyordu; büyücüde başparmak yukarıda, avuç içe dönük)
DM_BURGU = {'bip R Hand_018': -90, 'bip L Hand_010': 90}
DM_BAS = [('bip Neck_05', 'X', -8), ('bip Head_06', 'X', -16)]   # eksi X: baş yukarı
OTURAK, LEGEN_Y = 0.50, -0.02          # büyücüyle aynı: leğen oturağın 50 cm üstünde, ortasının 2 cm önünde (buyucu_oturt_blender.py)


# Fighter'ın eklemleri (archer-v1, kollar açık duruş, boy 1,8 m; ızgaralı önizlemelerden). Sol eli +x, yüzü −y.
FIGHTER_EKLEM = dict(legen=(0, -0.01, 0.98), bel=(0, -0.01, 1.06), gogus=(0, 0.0, 1.28), boyun=(0, 0.0, 1.52), bas=(0, -0.01, 1.58),
                     tepe=(0, -0.01, 1.79))
for _k, _sx in (('l', 1), ('r', -1)):
    FIGHTER_EKLEM.update({k: (x * _sx, y, z) for k, (x, y, z) in {
        f'kprc_{_k}': (0.03, 0.0, 1.47), f'omuz_{_k}': (0.18, 0.0, 1.43), f'dirsek_{_k}': (0.345, 0.0, 1.235), f'bilek_{_k}': (0.50, -0.06, 1.08),
        f'bogum_{_k}': (0.545, -0.09, 1.0), f'parmak_{_k}': (0.555, -0.10, 0.95), f'uc_{_k}': (0.565, -0.11, 0.90),
        f'bas0_{_k}': (0.505, -0.10, 1.04), f'bas1_{_k}': (0.50, -0.12, 1.0), f'bas2_{_k}': (0.495, -0.13, 0.965),
        f'kalca_{_k}': (0.10, -0.01, 0.93), f'diz_{_k}': (0.13, -0.02, 0.55), f'ayak_{_k}': (0.15, 0.03, 0.10),
        f'tarak_{_k}': (0.15, -0.07, 0.03), f'parmakuc_{_k}': (0.15, -0.13, 0.02)}.items()})
FIGHTER_BURGU = {}


def fighter_bas(ob):
    """Kâğıttaki fighter'ın başı açık, saçı kısa ve kırçıl; modelin (archer) başında yeşil bir kapüşon var. Kapüşonun noktaları
    kafa elipsine (karakter_boya.FIGHTER_KAFA, 9 mm dışına) yapıştırılır: kafayı saran bir saç olur (karakter_boya.fighter saç gibi boyar);
    boyna doğru geçiş yumuşak (omuz pelerini zincir yaka olarak kalır). Arkadaki uzun pelerinin bel altı silinir: oturunca
    sandalyenin içine girerdi; üstü kırmızı tabarın arkası olur."""
    import karakter_boya as kb
    C, _ = doku_dizi(ob)
    h, s, v = kb.hsv(kose_renk(ob, C))
    me = ob.data
    V = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', V); V = V.reshape(-1, 3)
    yesil = (h > 0.17) & (h < 0.5) & (s > 0.1)
    c, r = (np.array(a, np.float32) for a in kb.FIGHTER_KAFA)
    d = (V - c) / r; n = np.linalg.norm(d, axis=1)
    astar = (v < 0.3) & ~((h < 0.1) & (s > 0.25))                    # kapüşonun koyu iç astarı (şakaklarda dışarı taşıyordu)
    tenv = (h < 0.1) & (s > 0.22) & (s < 0.68) & (v > 0.3)
    yuzb = (d[:, 1] / np.maximum(n, 1e-6) < -0.55) & (V[:, 2] > 1.56) & (V[:, 2] < 1.735) & (np.abs(V[:, 0]) < 0.075) & (V[:, 1] > -0.125)   # gözler, kaşlar (kapüşonun sivri ucu daha önde)
    kapus = (yesil | astar | (~tenv & ~yuzb)) & (V[:, 2] > 1.5) & (n < 3)   # kapüşonun açık renkli ön kenarı da (alnın önünde sivri kalıyordu)
    w = np.clip((V[:, 2] - 1.5) / 0.1, 0, 1); w = w * w * (3 - 2 * w)
    tutam = kb.gurultu(V, 45, 31) * 0.6 + kb.gurultu(V, 110, 32) * 0.4      # kısa saç tutamları: yüzey 0…1,4 cm kabarır
    hedef = c + d / np.maximum(n, 1e-6)[:, None] * r * (1 + (0.004 + 0.014 * tutam[:, None]) / r.mean())
    V[kapus] = V[kapus] * (1 - w[kapus, None]) + hedef[kapus] * w[kapus, None]
    me.vertices.foreach_set('co', V.ravel()); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    pelerin = yesil & (V[:, 1] > 0.06) & (V[:, 2] < 0.95)
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in np.nonzero(pelerin)[0]], context='VERTS')
    kirinti_sil(bm, 200)
    bm.to_mesh(me); bm.free()
    print('KAPUSON', int(kapus.sum()), 'PELERIN', int(pelerin.sum()))


def _hanci_eklem():
    """Hancının eklemleri (modelin kendi biriminde, boy 54): kollar modelin içindeki boş nesnelerden (Base Human_L_Upperarm …),
    boyun, baş, bacaklar ve parmaklar önizleme ızgarasından. Eller yumruk (çekiç ve kızgın demir tutuyordu)."""
    e = dict(legen=(0, 2.2, 20.5), bel=(0, 2.3, 23.0), gogus=(0, 0.9, 33.7), boyun=(0, 2.0, 43.0), bas=(0, 1.5, 45.5), tepe=(0, 1.0, 54.0))
    kol = {'l': ((9.29, 0.45, 39.85), (13.46, 3.6, 39.46), (19.65, 2.17, 31.87), (19.77, -8.21, 26.53)),
           'r': ((-9.29, 0.45, 39.85), (-13.83, 2.72, 38.51), (-19.99, 2.23, 30.79), (-23.63, -6.61, 24.09))}
    for k, (kp, om, di, bi) in kol.items():
        kp, om, di, bi = map(Vector, (kp, om, di, bi))
        d = (bi - di).normalized(); ic = Vector((-1 if k == 'l' else 1, 0, 0))
        e.update({f'kprc_{k}': Vector((kp.x * 0.3, kp.y, kp.z)), f'omuz_{k}': om, f'dirsek_{k}': di, f'bilek_{k}': bi,
                  f'bogum_{k}': bi + d * 3.5, f'parmak_{k}': bi + d * 5.0, f'uc_{k}': bi + d * 6.5,
                  f'bas0_{k}': bi + d * 1.2 + ic * 1.6 + Vector((0, 0, 1)), f'bas1_{k}': bi + d * 2.6 + ic * 2.0 + Vector((0, 0, 1)),
                  f'bas2_{k}': bi + d * 4.0 + ic * 2.2 + Vector((0, 0, 0.8))})
        sx = 1 if k == 'l' else -1
        e.update({f'kalca_{k}': (5.5 * sx, 2.2, 18.5), f'diz_{k}': (6.5 * sx, 1.5, 8.5), f'ayak_{k}': (6.8 * sx, 2.0, 2.5),
                  f'tarak_{k}': (7.0 * sx, -2.5, 0.6), f'parmakuc_{k}': (7.0 * sx, -5.0, 0.4)})
    return {k: tuple(v) for k, v in e.items()}


HANCI_EKLEM = _hanci_eklem()
HANCI_KOLLAR = [k[0] for k in KEMIKLER if any(t in k[0] for t in ('Clavicle', 'UpperArm', 'Forearm', 'Hand'))]   # yalnızca kollar
TEZGAH = 1.05                         # tezgâhın yüksekliği (han_plan.TEZGAH_H): hancının yumrukları bunun üstüne konar (alçak bir basamakta durur)
# Tezgâh arkasında bekleme (döngü, 30 kare = 1 sn): hafif nefes, başını çevirip salona bakar
BEKLE = [
    (0, []),
    (50, [('bip Spine1_04', 'X', 2), ('bip Head_06', 'Z', 9)]),
    (100, [('bip Spine1_04', 'X', 0), ('bip Head_06', 'Z', 2), ('bip Head_06', 'X', 4)]),
    (150, [('bip Spine1_04', 'X', 2), ('bip Head_06', 'Z', -9)]),
    (200, [('bip Spine1_04', 'X', 0), ('bip Head_06', 'Z', -2)]),
    (240, []),
]
BEKLE_KEMIK = ['bip Spine1_04', 'bip Head_06']

# Hancının işleri (2026-10-28, kullanıcının isteği: "15–20 sn'de bir arkasını dönüp şişe alsın, 10 sn'de bir bardak silsin, yer
# değiştirsin"). Sırayı ve yer değiştirmeyi site verir (index.html, tavHanciGuncelle); burada yalnızca hareketler.
# Elde beliren eşyalar kendi kemiklerinde (hanci_esyalar), boyu 0 iken görünmez: Sise ve BezEl sağ elde, Bardak sol elde;
# üçü de tezgâhtan alınıp tezgâha bırakılır (omuzdaki havluya kol yetişmiyor: omuzdan bileğe ~54 cm).
# Eller 'IK' ile bileğin gideceği noktaya uzanır (iskeletin içinde, metre: kök leğenin altında yerde, yüzü −y, sol eli +x;
# duruşta bilekler (±0,42, −0,41, 1,06), omuzlar (±0,35, −0,04, 1,18), tezgâh 1,05); öteki dönüşler dünya eksenlerinde
# (zar_hareket.ZAR_AT gibi). Leğenin dönüşü ve geri adımı listenin sonunda: önce kollar, sonra bütün gövde onlarla döner.
_L, _R = (lambda k: {'UpperArm': 'bip L UpperArm_08', 'Forearm': 'bip L Forearm_09', 'Hand': 'bip L Hand_010'}[k],
          lambda k: {'UpperArm': 'bip R UpperArm_016', 'Forearm': 'bip R Forearm_017', 'Hand': 'bip R Hand_018'}[k])
PELVIS = 'bip Pelvis_02'
SOL, SAG = 'bip L Hand_010', 'bip R Hand_018'


def gor(sise=0, bardak=0, bez=0):
    return [('Sise', 'S', sise), ('Bardak', 'S', bardak), ('BezEl', 'S', bez)]


KALK = [(SOL, 'IK', (0.38, -0.42, 1.12)), (SAG, 'IK', (-0.38, -0.42, 1.12))]       # yumruklar tezgâhtan biraz kalkar
SOL_TEZ, SAG_TEZ = (SOL, 'IK', (0.28, -0.46, 1.07)), (SAG, 'IK', (-0.26, -0.47, 1.07))   # tezgâhtan kupayı / bezi alır, bırakır
SOL_KUPA = (SOL, 'IK', (0.13, -0.37, 1.13))                                         # kupa göğsün önünde (kupanın ortası ~(0,05, −0,41))
SAG_SIL = lambda dx=0.0, dy=0.0: (SAG, 'IK', (-0.01 + dx, -0.40 + dy, 1.24))          # bezli el kupanın ağzında
SIL = [(0, gor()), (10, [SOL_TEZ, SAG_TEZ] + gor()), (12, [SOL_TEZ, SAG_TEZ] + gor(bardak=1, bez=1)),
       (30, [SOL_KUPA, SAG_SIL()] + gor(bardak=1, bez=1))]
for _i, _k in enumerate(range(40, 140, 8)):                                         # bezle kupanın içinde küçük daireler, kupa döner
    _a = _i * math.pi / 2
    SIL.append((_k, [SOL_KUPA, (SOL, 'Z', 14 * math.sin(_a)), SAG_SIL(0.025 * math.cos(_a), 0.025 * math.sin(_a))] + gor(bardak=1, bez=1)))
SIL += [(150, [SOL_KUPA, SAG_SIL()] + gor(bardak=1, bez=1)), (168, [SOL_TEZ, SAG_TEZ] + gor(bardak=1, bez=1)),
        (170, [SOL_TEZ, SAG_TEZ] + gor()), (186, gor())]

DONUK = lambda aci, geri=0.0: [(PELVIS, 'Z', aci), (PELVIS, 'L', (0, geri, 0))]   # arkasına döner (180) ve rafa doğru geri adım (+y)
GERI = 0.62                                                                        # tezgâhın arkası leğenden 0,92 m geride (han_plan)
EGIL = ('bip Spine1_04', 'X', 14)
UZAN = [EGIL, (SAG, 'IK', (-0.2, -0.6, 1.16))]                                    # dönükken önündeki rafa (dolabın üstündeki şişeler)
SISE_TUT = (SAG, 'IK', (-0.2, -0.36, 1.2))                                         # şişe göğsün önünde, dik
DOK = [(SAG, 'IK', (-0.13, -0.40, 1.31)), (SAG, 'Y', 100)]                        # kupaya döker (ağzı sola, kupanın üstüne)
ALTA = (SAG, 'IK', (-0.3, -0.22, 0.95))                                            # şişeyi tezgâhın altındaki rafa bırakır
_ad = lambda a, b: [('bip L Thigh_023', 'X', a), ('bip L Calf_024', 'X', -a * 1.6 if a < 0 else 0), ('bip R Thigh_027', 'X', b), ('bip R Calf_028', 'X', -b * 1.6 if b < 0 else 0)]
SISE = [(0, gor()), (10, KALK + gor()),
        (22, KALK + _ad(-18, 8) + DONUK(90, 0.25) + gor()), (34, KALK + _ad(8, -18) + DONUK(180, GERI - 0.05) + gor()), (42, KALK + DONUK(180, GERI) + gor()),
        (58, UZAN + DONUK(180, GERI) + gor()), (64, UZAN + DONUK(180, GERI) + gor(sise=1)),
        (80, [SISE_TUT, KALK[0]] + DONUK(180, GERI) + gor(sise=1)),
        (92, [SISE_TUT, KALK[0]] + _ad(-18, 8) + DONUK(90, 0.3) + gor(sise=1)), (104, [SISE_TUT, KALK[0]] + _ad(8, -18) + DONUK(0, 0.03) + gor(sise=1)),
        (110, [SISE_TUT, KALK[0]] + gor(sise=1)),
        (120, [SISE_TUT, SOL_TEZ] + gor(sise=1)), (122, [SISE_TUT, SOL_TEZ] + gor(sise=1, bardak=1)),   # kupayı tezgâhtan alır
        (136, [SISE_TUT, SOL_KUPA] + gor(sise=1, bardak=1)), (152, DOK + [SOL_KUPA] + gor(sise=1, bardak=1)),
        (182, DOK[:1] + [(SAG, 'Y', 92), SOL_KUPA] + gor(sise=1, bardak=1)), (196, [SISE_TUT, SOL_KUPA] + gor(sise=1, bardak=1)),
        (212, [ALTA, SOL_KUPA] + gor(sise=1, bardak=1)), (214, [ALTA, SOL_KUPA] + gor(bardak=1)),
        (228, [KALK[1], SOL_TEZ] + gor(bardak=1)), (230, [KALK[1], SOL_TEZ] + gor()), (244, gor())]

# Bar boyunca yürüme (döngü, 32 kare): kollar tezgâhtan kalkık, sallanır; site hancıyı yürüdüğü yöne çevirip taşır
_YK = lambda a, b, k: _ad(a, b) + [(SOL, 'IK', (0.36, -0.28 - k / 200, 1.0)), (SAG, 'IK', (-0.36, -0.28 + k / 200, 1.0)), ('bip Spine_03', 'Z', k / 4)]
HANCI_YURU = [(0, _YK(-20, 14, 12) + gor()), (8, _YK(-4, -6, 0) + gor()), (16, _YK(14, -20, -12) + gor()), (24, _YK(-6, -4, 0) + gor()), (32, _YK(-20, 14, 12) + gor())]
HANCI_ESYA = ['Sise', 'Bardak', 'BezEl']
HANCI_KEMIK = [PELVIS, 'bip Spine_03', 'bip Spine1_04', 'bip Head_06'] + [f(k) for f in (_L, _R) for k in ('UpperArm', 'Forearm', 'Hand')] + \
              ['bip L Thigh_023', 'bip L Calf_024', 'bip R Thigh_027', 'bip R Calf_028'] + HANCI_ESYA

# Garsonların eklemleri (modelin kendi duruşunda, metre; ızgaralı önizlemeden ve bacak kesitlerinden). Kız adım atar gibi duruyor:
# sağ bacağı önde, sol bacağı arkada (topuklu); kollar aşağıda, sağ elinde bez.
KIZ_EKLEM = dict(
    legen=(0, -0.06, -0.02), bel=(0, -0.06, 0.06), gogus=(0, -0.07, 0.28), boyun=(0, -0.07, 0.51), bas=(0, -0.07, 0.57), tepe=(0, -0.06, 0.95),
    kprc_l=(0.03, -0.07, 0.48), omuz_l=(0.165, -0.06, 0.465), dirsek_l=(0.21, -0.05, 0.175), bilek_l=(0.23, -0.08, -0.06),
    bogum_l=(0.235, -0.10, -0.12), parmak_l=(0.235, -0.11, -0.15), uc_l=(0.235, -0.12, -0.18),
    bas0_l=(0.215, -0.10, -0.08), bas1_l=(0.21, -0.115, -0.105), bas2_l=(0.205, -0.125, -0.13),
    kprc_r=(-0.03, -0.07, 0.48), omuz_r=(-0.165, -0.06, 0.465), dirsek_r=(-0.205, -0.05, 0.175), bilek_r=(-0.24, -0.09, -0.075),
    bogum_r=(-0.245, -0.11, -0.14), parmak_r=(-0.245, -0.12, -0.17), uc_r=(-0.245, -0.13, -0.20),
    bas0_r=(-0.225, -0.11, -0.095), bas1_r=(-0.22, -0.125, -0.12), bas2_r=(-0.215, -0.135, -0.145),
    kalca_r=(-0.085, -0.07, -0.04), diz_r=(-0.045, -0.11, -0.46), ayak_r=(0.0, -0.10, -0.84), tarak_r=(0.01, -0.20, -0.92), parmakuc_r=(0.015, -0.25, -0.945),
    kalca_l=(0.085, -0.05, -0.04), diz_l=(0.047, 0.07, -0.45), ayak_l=(0.0, 0.21, -0.82), tarak_l=(-0.005, 0.12, -0.925), parmakuc_l=(-0.005, 0.07, -0.945),
)
ERKEK_EKLEM = dict(legen=(0, 0.03, 0.0), bel=(0, 0.03, 0.10), gogus=(0, 0.03, 0.35), boyun=(0, 0.03, 0.62), bas=(0, 0.03, 0.68), tepe=(0, 0.02, 0.95))
for _k, _sx in (('l', 1), ('r', -1)):
    ERKEK_EKLEM.update({
        f'kprc_{_k}': (0.03 * _sx, 0.03, 0.58), f'omuz_{_k}': (0.19 * _sx, 0.04, 0.56), f'dirsek_{_k}': (0.285 * _sx, 0.05, 0.33),
        f'bilek_{_k}': (0.265 * _sx, 0.04, 0.04), f'bogum_{_k}': (0.265 * _sx, 0.03, -0.06), f'parmak_{_k}': (0.265 * _sx, 0.02, -0.10),
        f'uc_{_k}': (0.265 * _sx, 0.01, -0.14), f'bas0_{_k}': (0.245 * _sx, 0.0, 0.0), f'bas1_{_k}': (0.235 * _sx, -0.015, -0.04),
        f'bas2_{_k}': (0.23 * _sx, -0.025, -0.07), f'kalca_{_k}': (0.10 * _sx, 0.03, -0.02), f'diz_{_k}': (0.12 * _sx, 0.03, -0.48),
        f'ayak_{_k}': (0.13 * _sx, 0.07, -0.86), f'tarak_{_k}': (0.13 * _sx, -0.06, -0.93), f'parmakuc_{_k}': (0.13 * _sx, -0.15, -0.94)})

# Garsonun duruşu (dünya yönleri; yüzü −y): bacaklar dik, sağ kol yanda, sol el omuz hizasında tepsiyi taşır (dirsek yana,
# önkol yukarı, el avuç yukarı)
GARSON_YON = {
    'bip L Thigh_023': (0, 0.02, -1), 'bip L Calf_024': (0, 0.05, -1), 'bip L Foot_025': (0, -0.85, -0.5),
    'bip R Thigh_027': (0, 0.02, -1), 'bip R Calf_028': (0, 0.05, -1), 'bip R Foot_00': (0, -0.85, -0.5),
    'bip R UpperArm_016': (-0.2, 0.03, -1), 'bip R Forearm_017': (-0.08, -0.2, -1), 'bip R Hand_018': (-0.03, -0.05, -1),
    'bip L UpperArm_08': (0.8, -0.2, -0.55), 'bip L Forearm_09': (0.05, -0.3, 0.95), 'bip L Hand_010': (-0.35, -0.2, 0.25),
}
# Erkek garson tepsiyi bel hizasında taşır (üst kol yanda, önkol önde): gömleğinin kolu yeleğin kol oyuğuna kaynaşık, kol omuz
# hizasına kalkınca oyuk yırtılıyordu
GARSON_YON_ERKEK = dict(GARSON_YON, **{'bip L UpperArm_08': (0.18, 0.05, -1), 'bip L Forearm_09': (0.12, -1, 0.12), 'bip L Hand_010': (0.05, -1, 0.0)})
# Yürüme (döngü, 32 kare = 1,07 sn; bir adım 0,55 m: site garsonu saniyede ~1 m ilerletir). Sol kol (tepsi) kımıldamaz.
_ADIM = lambda on, arka, a, b: [(on[0], 'X', a[0]), (on[1], 'X', a[1]), (arka[0], 'X', b[0]), (arka[1], 'X', b[1])]
_SOL, _SAG = ('bip L Thigh_023', 'bip L Calf_024'), ('bip R Thigh_027', 'bip R Calf_028')
YURU = [
    (0, _ADIM(_SOL, _SAG, (-22, 6), (18, 12)) + [('bip R UpperArm_016', 'X', -14), ('bip Spine_03', 'Z', 4)]),
    (8, _ADIM(_SOL, _SAG, (-4, 4), (-12, 48)) + [('bip R UpperArm_016', 'X', 0)]),
    (16, _ADIM(_SAG, _SOL, (-22, 6), (18, 12)) + [('bip R UpperArm_016', 'X', 14), ('bip Spine_03', 'Z', -4)]),
    (24, _ADIM(_SAG, _SOL, (-4, 4), (-12, 48)) + [('bip R UpperArm_016', 'X', 0)]),
    (32, _ADIM(_SOL, _SAG, (-22, 6), (18, 12)) + [('bip R UpperArm_016', 'X', -14), ('bip Spine_03', 'Z', 4)]),
]
YURU_KEMIK = list(_SOL + _SAG) + ['bip R UpperArm_016', 'bip Spine_03']
GARSON_BEKLE = [
    (0, []),
    (60, [('bip Spine1_04', 'X', 2), ('bip Head_06', 'Z', 12)]),
    (120, [('bip Spine1_04', 'X', 0), ('bip Head_06', 'Z', 0), ('bip Head_06', 'X', 5)]),
    (180, [('bip Spine1_04', 'X', 2), ('bip Head_06', 'Z', -12)]),
    (240, []),
]


def iskelet_yap(eklem, olcek):
    arm = bpy.data.objects.new('Iskelet', bpy.data.armatures.new('Iskelet'))
    bpy.context.scene.collection.objects.link(arm)
    secili([arm]); bpy.ops.object.mode_set(mode='EDIT')
    for ad, ebe, a, b in KEMIKLER:
        eb = arm.data.edit_bones.new(ad)
        eb.head = Vector(eklem[a]) * olcek; eb.tail = Vector(eklem[b]) * olcek
        if ebe: eb.parent = arm.data.edit_bones[ebe]
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm


def gerilen_sil(ob, once, kat=3.0, en_az=0.03):
    """Poz verilince çok gerilen yüzleri siler: Meshy modellerinde el, değdiği eteğe kaynaşık; kol kalkınca aradan ince bir
    perde geriliyordu. Bir kenarı eskisinin kat katından ve en_az metreden uzun olan yüz gider."""
    me = ob.data
    E = np.zeros(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', E); E = E.reshape(-1, 2)
    simdi = np.array([v.co[:] for v in me.vertices])
    l0 = np.linalg.norm(once[E[:, 0]] - once[E[:, 1]], axis=1); l1 = np.linalg.norm(simdi[E[:, 0]] - simdi[E[:, 1]], axis=1)
    kotu = set(map(tuple, np.sort(E[(l1 > l0 * kat) & (l1 > en_az)], 1).tolist()))
    bm = bmesh.new(); bm.from_mesh(me)
    sil = [f for f in bm.faces if any(tuple(sorted((e.verts[0].index, e.verts[1].index))) in kotu for e in f.edges)]
    bmesh.ops.delete(bm, geom=sil, context='FACES'); bm.to_mesh(me); bm.free()
    print('GERILEN', len(sil), 'yüz silindi')


def kose_renk(ob, C):
    """Her köşenin asıl dokudaki rengi (köşenin UV'lerinin ortalaması; C satır 0 altta)."""
    me = ob.data
    uv = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers.active.data.foreach_get('uv', uv); uv = uv.reshape(-1, 2)
    vi = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', vi)
    H, W = C.shape[:2]
    c = C[np.clip((uv[:, 1] % 1) * H, 0, H - 1).astype(int), np.clip((uv[:, 0] % 1) * W, 0, W - 1).astype(int)]
    top = np.zeros((len(me.vertices), 3), np.float32); np.add.at(top, vi, c)
    return top / np.maximum(np.bincount(vi, minlength=len(me.vertices)), 1)[:, None]


def kol_izni(V, renk):
    """Garsonlarda kol kemiklerinin oynatabileceği köşeler (V modelin kendi ölçüsünde). Kollar elbiseye / tuniğe değecek kadar
    yakın duruyor: uzaklığa göre ağırlıkta kol kaldırılınca eteğin ve önlüğün yanı da kalkıyordu. İzin: ten, kol yeni, elde tutulan."""
    import karakter_boya as kb
    h, s_, v = kb.hsv(renk)
    x, z = V[:, 0], V[:, 2]
    ax = np.abs(x)
    ten = (h < 0.1) & (s_ > 0.2) & (s_ < 0.7) & (v > 0.28)
    if AD == 'garson_kiz':
        kol = (ax > 0.13) & (z > 0.26)                                 # kısa kollar
        bez = (h > 0.45) & (h < 0.62) & (s_ > 0.3) & (v > 0.4)
        return (ten & (ax > 0.17) & (z < 0.45)) | kol | (bez & (ax > 0.17))
    teal = (h > 0.42) & (h < 0.62) & (s_ > 0.15)                     # erkek: gömlek kolları, omuz başı
    return (ten & (ax > 0.19) & (z < 0.3)) | (teal & (ax > 0.17) & (z > 0.15)) | ((ax > 0.2) & (z > 0.4))


def agirlik_ver(ob, arm, us=4.0, yumusat=4, kol_izin=None):
    """Her köşe en yakın kemiklere (kemik çizgisine uzaklığın ters üssü) bağlanır, en çok 3 kemik; sonra ağırlıklar model
    boyunca yumuşatılır. (Blender'ın kemik ısısı bu modellerde çalışmadı: saç, ceket ve gövde iç içe ayrı kabuklar; ısı iç
    kabuktaki kemiği göremiyor, ensedeki saç geride kalıyor, baldırlar bükülmüyordu.)"""
    me = ob.data
    V = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', V); V = V.reshape(-1, 3)
    adlar = [b.name for b in arm.data.bones]
    A = np.array([b.head_local[:] for b in arm.data.bones], np.float32); B = np.array([b.tail_local[:] for b in arm.data.bones], np.float32)
    AB = B - A
    t = np.clip(((V[:, None, :] - A[None]) * AB[None]).sum(-1) / (AB ** 2).sum(-1)[None], 0, 1)
    D = np.linalg.norm(V[:, None, :] - (A[None] + t[..., None] * AB[None]), axis=-1)
    W = (1 / np.maximum(D, 0.004)) ** us
    if kol_izin is not None:                                         # kol kemikleri yalnızca izin verilen köşeleri oynatır
        kolk = np.array([any(t in n for t in ('Arm', 'Forearm', 'Hand', 'Finger')) for n in adlar])
        W[np.ix_(~kol_izin, kolk)] = 0
    en = np.argsort(-W, 1)[:, 3:]
    np.put_along_axis(W, en, 0, 1)                                  # en yakın 3 kemik
    W /= W.sum(1, keepdims=True)
    E = np.zeros(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', E); E = E.reshape(-1, 2)
    say = np.bincount(E.ravel(), minlength=len(V)).astype(np.float32)[:, None]
    for _ in range(yumusat):                                        # komşuların ortalamasına yaklaştır (keskin geçişler yumuşar)
        T = np.zeros_like(W); np.add.at(T, E[:, 0], W[E[:, 1]]); np.add.at(T, E[:, 1], W[E[:, 0]])
        W = np.where(say > 0, 0.5 * W + 0.5 * T / np.maximum(say, 1), W)
    en = np.argsort(-W, 1)[:, 4:]
    np.put_along_axis(W, en, 0, 1)                                  # glTF: en çok 4 kemik
    W[W < 0.01] = 0
    W /= W.sum(1, keepdims=True)
    for bi, n in enumerate(adlar):
        g = ob.vertex_groups.new(name=n)
        idx = np.nonzero(W[:, bi])[0]
        for i, w in zip(idx.tolist(), W[idx, bi].tolist()): g.add([i], w, 'REPLACE')
    print('AGIRLIK', len(V), 'köşe', len(adlar), 'kemik')


def hedef_duruş():
    """Büyücünün oturur iskeletindeki (masa/buyucu-iskelet.glb, dinlenme duruşu) eklem yerleri: yeni karakterin kemikleri bu
    yönlere çevrilir ki zar_at hareketi ve sitenin avuç hesabı (tavAvuc) aynı çalışsın."""
    once, once_h = set(bpy.data.objects), set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(KOK / 'masa' / 'buyucu-iskelet.glb'))
    yeni = [o for o in bpy.data.objects if o not in once]
    a = next(o for o in yeni if o.type == 'ARMATURE')
    bpy.context.view_layer.update()
    bas = {b.name: (a.matrix_world @ b.head_local).copy() for b in a.data.bones}
    for o in yeni: bpy.data.objects.remove(o, do_unlink=True)
    for h in set(bpy.data.actions) - once_h: bpy.data.actions.remove(h)   # büyücünün zar_at'ı modele karışıp dışa aktarılıyordu
    return bas


def ana_cocuk():
    """Her kemiğin yönünü veren çocuğu (ilk çocuk; elde dört parmak)."""
    cocuk = {}
    for ad, ebe, a, b in KEMIKLER:
        if ebe and ebe not in cocuk: cocuk[ebe] = ad
    cocuk.update({'bip L Hand_010': 'bip L Finger1_013', 'bip R Hand_018': 'bip R Finger1_021'})
    return cocuk


def yon_hedef(arm, yonler):
    """Elle verilen kemik yönlerinden (dünya ekseninde) yon_ver'in istediği hedef eklem yerleri."""
    cocuk, h = ana_cocuk(), {}
    for ad, ebe, a, b in KEMIKLER:
        if ad in yonler:
            if ad not in h: h[ad] = arm.data.bones[ad].head_local.copy()
            h[cocuk[ad]] = h[ad] + Vector(yonler[ad]).normalized() * 0.1
    return h


def yon_ver(arm, hedef, burgu=None, yalniz=None):
    """Kemikleri (ebeveynden çocuğa) hedef iskeletteki yönlerine çevirir; ellerde başparmağın tarafı da eşlenir."""
    secili([arm]); bpy.ops.object.mode_set(mode='POSE')
    cocuk = ana_cocuk()

    def dondur(pb, R):
        M = pb.matrix.copy(); h = M.translation.copy()
        pb.matrix = Matrix.Translation(h) @ R.to_4x4() @ Matrix.Translation(-h) @ M
        bpy.context.view_layer.update()

    for ad, ebe, a, b in KEMIKLER:
        c = cocuk.get(ad)
        if not ebe or not c or ad not in hedef or c not in hedef or (yalniz and ad not in yalniz): continue
        pb, pc = arm.pose.bones[ad], arm.pose.bones[c]
        su = (pc.head - pb.head).normalized(); ist = (hedef[c] - hedef[ad]).normalized()
        dondur(pb, su.rotation_difference(ist).to_matrix())
        bp = ad.replace('Hand_010', 'Finger0_011').replace('Hand_018', 'Finger0_019')
        if 'Hand' in ad and bp in hedef:                          # başparmak tarafı (bilek ekseni çevresinde)
            ek = (pc.head - pb.head).normalized()
            def yan(v): v = v - ek * v.dot(ek); return v.normalized()
            s1 = yan(arm.pose.bones[bp].head - pb.head); s2 = yan(hedef[bp] - hedef[ad])
            aci = s1.angle(s2); isaret = 1 if ek.dot(s1.cross(s2)) > 0 else -1
            dondur(pb, Matrix.Rotation(aci * isaret + math.radians((burgu or {}).get(ad, 0)), 3, ek))
    bpy.ops.object.mode_set(mode='OBJECT')


def kur():
    import karakter_boya as kb
    from zar_hareket import hareket_kur, cevir
    DM, GARSON, OTUR = AD == 'dm', AD.startswith('garson'), AD in ('dm', 'fighter')   # oturanlar: masada zar atar
    bpy.ops.wm.open_mainfile(filepath=str(ARA / f'{AD}-ham.blend'))
    ob = bpy.data.objects[AD]
    # 1) doku: kâğıda göre yeniden boya (konum haritası pişirilirken olduğu gibi satır 0 altta)
    C, im = doku_dizi(ob)
    izin = kol_izni(np.array([v.co[:] for v in ob.data.vertices]), kose_renk(ob, C)) if GARSON else None   # boyamadan önce: asıl renkler
    if im.size[0] != AYAR['doku']:                                 # hancının dokusu 4096: konum haritasının boyuna (ve web'e uygun boya) indir
        im.scale(AYAR['doku'], AYAR['doku']); C, im = doku_dizi(ob)
    d = np.load(ARA / f'{AD}-konum.npz')
    kb.KAPSAM = uv_kapsam(ob, C.shape[0])
    Y = getattr(kb, AD)(C, d['P'], d['parca'] if 'parca' in d else None)
    Y = kb.tasir(Y, kb.KAPSAM, 16)                               # kenar payı da yeni renkte (uzaktan bakınca küçük dokuda da çatlak olmasın)
    im.pixels.foreach_set(np.concatenate([Y, np.ones(Y.shape[:2] + (1,), np.float32)], -1).ravel())
    im.update(); im.pack()                                         # yeni pikseller hem dışa aktarıma hem .blend'e gitsin
    for m in ob.data.materials:                                   # site yalnızca renk dokusunu kullanır (toon); ötekiler dosyayı büyütür
        nt = m.node_tree
        for n in list(nt.nodes):
            if n.type in ('NORMAL_MAP', 'SEPARATE_COLOR', 'UVMAP') or (n.type == 'TEX_IMAGE' and n.image != im): nt.nodes.remove(n)
    if AYAR.get('cikti_doku'):                                     # garsonlar küçük görünür: doku dosyası küçülsün
        im.scale(AYAR['cikti_doku'], AYAR['cikti_doku']); im.pack()
    if AYAR.get('alcak'): alcak_poli(ob, AYAR['alcak'])
    # 2) ölçü: DM ayakta 1,80 m; hancı (cüce) 1,35 m; garsonlar (genç) 1,62 ve 1,74 m
    s = {'dm': 1.80, 'fighter': 1.80, 'hanci': 1.35, 'garson_kiz': 1.62, 'garson_erkek': 1.74}[AD] / ob.dimensions.z
    ob.scale = (s, s, s); secili([ob]); bpy.ops.object.transform_apply(scale=True)
    # 3) iskelet, ağırlıklar
    arm = iskelet_yap({'dm': DM_EKLEM, 'fighter': FIGHTER_EKLEM, 'hanci': HANCI_EKLEM, 'garson_kiz': KIZ_EKLEM, 'garson_erkek': ERKEK_EKLEM}[AD], s)
    agirlik_ver(ob, arm, kol_izin=izin)
    ob.parent = arm
    md = next((m for m in ob.modifiers if m.type == 'ARMATURE'), None) or ob.modifiers.new('Iskelet', 'ARMATURE')
    md.object = arm
    # 4) kâğıttaki ekler: DM gözlük ve tüy; hancı örgü, anahtar halkası, havlu
    ekler = dm_ekler(ob, s) if DM else [] if OTUR else garson_kulak(ob, s) if AD == 'garson_erkek' else [] if GARSON else hanci_ekler(ob, s)
    # 5) duruş: kemikler büyücünün oturuşuna çevrilir (hancıda yalnızca kollar: yumruklar tezgâhta), poz modele işlenir,
    #    iskeletin yeni duruşu olur
    if GARSON:                                                     # garsonlar ayakta: bacaklar dik, sol elde tepsi
        yonler = GARSON_YON_ERKEK if AD == 'garson_erkek' else GARSON_YON
        yon_ver(arm, yon_hedef(arm, yonler), None, list(yonler))
    else:
        yon_ver(arm, hedef_duruş(), DM_BURGU if DM else FIGHTER_BURGU if OTUR else None, None if OTUR else HANCI_KOLLAR)
    if DM:
        secili([arm]); bpy.ops.object.mode_set(mode='POSE')
        cevir(arm, DM_BAS)                                         # model kitaba bakıyordu: başı kaldır (yukarıdan yüzü görünsün)
        bpy.ops.object.mode_set(mode='OBJECT')
    once = np.array([v.co[:] for v in ob.data.vertices])
    for o in [ob] + ekler:
        secili([o]); bpy.ops.object.modifier_apply(modifier=next(m.name for m in o.modifiers if m.type == 'ARMATURE'))
    if GARSON: gerilen_sil(ob, once)
    secili([arm]); bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')
    # 6) yer. DM: leğen büyücününki gibi oturağın üstünde. Hancı: yumrukları tezgâhın üstünde; ayaklarının yerden yüksekliği
    #    modelde "basamak" (m): site hancıyı yere koyar, cüce tezgâhın arkasında o kadar yüksek bir kasanın üstünde durur
    if OTUR:
        legen = arm.data.bones['bip Pelvis_02'].head_local
        T = Matrix.Translation((-legen.x, LEGEN_Y - legen.y, OTURAK - legen.z))
    elif GARSON:                                                   # ayakları yerde, leğeni kökün üstünde
        legen = arm.data.bones['bip Pelvis_02'].head_local
        T = Matrix.Translation((-legen.x, -legen.y, -min(v.co.z for v in ob.data.vertices)))
    else:
        eller = [arm.data.bones[n].tail_local for n in ('bip L Hand_010', 'bip R Hand_018')]
        yumruk = min(e.z for e in eller) - 0.04
        orta = (eller[0] + eller[1]) / 2
        legen = arm.data.bones['bip Pelvis_02'].head_local          # kök leğenin altında (yürürken ve dönerken kendi çevresinde döner);
        T = Matrix.Translation((-legen.x, -legen.y, TEZGAH - yumruk))   # site yumruk_on kadar geride kurar: yumruklar tezgâhta
        arm['yumruk_on'] = round(legen.y - orta.y, 3)
        print('YUMRUK_ON', arm['yumruk_on'])
        arm['basamak'] = round(TEZGAH - yumruk + min(v.co.z for v in ob.data.vertices), 3)
        print('BASAMAK', arm['basamak'])
    for o in [arm, ob] + ekler:
        o.parent = None; o.matrix_world = T @ o.matrix_world
    secili([arm, ob] + ekler, ob); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if GARSON: ekler += garson_tepsi(ob, arm)                       # tepsi (ve kızda uzun etek) duruştan sonra: tepsi yatay dursun
    if AD == 'hanci': ekler += hanci_esyalar(ob, arm)        # şişe, kupa, el bezi (kendi kemiklerinde)
    secili([ob] + ekler, ob); bpy.ops.object.join()
    ob.parent = arm
    md = ob.modifiers.new('Iskelet', 'ARMATURE'); md.object = arm
    if AYAR.get('alcak'):                                          # eklenen parçalar da köşeli
        for f in ob.data.polygons: f.use_smooth = False
    print('BOYUT', tuple(round(v, 3) for v in ob.dimensions), 'en alt', round(min(v.co.z for v in ob.data.vertices), 3))
    # 7) hareket, dışa aktar
    if OTUR:
        bas_ayir(ob, arm)
        hareket_kur(arm)
        disa_aktar(arm, ob, KOK / 'masa' / f'{AD}-iskelet.glb', f'{AD.upper()}_ISKELET_GLB', 'İskeletli ' + {'dm': 'DM', 'fighter': 'fighter'}[AD])
    elif GARSON:
        hareket_kur(arm, 'bekle', GARSON_BEKLE, BEKLE_KEMIK, None)
        hareket_kur(arm, 'yuru', YURU, YURU_KEMIK, None)            # son kurulan önizlemede oynar
        ad = AD.replace('_', '-')
        disa_aktar(arm, ob, KOK / 'masa' / f'{ad}.glb', AD.upper() + '_GLB', 'Garson')
    else:
        for ad, tablo, kem in (('yuru', HANCI_YURU, HANCI_KEMIK), ('sise', SISE, HANCI_KEMIK), ('sil', SIL, HANCI_KEMIK),
                               ('bekle', [(k, l + gor()) for k, l in BEKLE], BEKLE_KEMIK + HANCI_ESYA)):
            hareket_kur(arm, ad, tablo, kem, None)
            arm['sure_' + ad] = arm['sure']
        disa_aktar(arm, ob, KOK / 'masa' / 'hanci.glb', 'HANCI_GLB', 'Hancı')
    bpy.context.scene.frame_set(0)
    bpy.ops.wm.save_as_mainfile(filepath=str(ARA / f'{AD}-kur.blend'))
    modeller_kopya()
    if AD == 'hanci': hanci_onizle(arm, ob)
    else: onizle(arm, ob)


def garson_kulak(ob, s):
    """Yarı-elf erkek garsonun sivri kulak uçları: kulağın üstünden yukarı ve geriye ince koni (ten rengi). Kulak yüze ışın
    atılarak bulunur."""
    arm = ob.parent
    parca = []
    for sx in (-1, 1):
        kulak = isin(ob, (sx * 2, 0.02 * s, 0.775 * s), (-sx, 0, 0)) or Vector((sx * 0.075 * s, 0.02 * s, 0.775 * s))
        kok = kulak + Vector((-sx * 0.006, 0.006, 0.018)) * (s / 0.95)
        uc = kok + Vector((sx * 0.012, 0.03, 0.045)) * (s / 0.95)
        d = uc - kok
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.011 * s / 0.95, radius2=0.0008, depth=d.length, location=(kok + uc) / 2)
        k = bpy.context.active_object
        k.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); k.scale = (0.45, 1, 1)
        k.data.materials.append(malzeme('Kulak', '#c69276'))
        vg = k.vertex_groups.new(name='bip Head_06'); vg.add(range(len(k.data.vertices)), 1.0, 'REPLACE')
        k.parent = arm; md = k.modifiers.new('Iskelet', 'ARMATURE'); md.object = arm
        parca.append(k)
    return parca


def garson_tepsi(ob, arm):
    """Sol elde yuvarlak tahta tepsi, üstünde iki köpüklü kupa (kâğıtlardaki gibi); kızda dizden aşağı uzun kahverengi etek
    (modelin kısa elbisesinin eteğinden bileğe, kıvrımlı). Duruş işlendikten sonra kurulur: tepsi yatay; ağırlıkları elle."""
    parca = []
    el = arm.data.bones['bip L Hand_010']
    m = (el.head_local + el.tail_local) / 2 + Vector((0, 0, 0.045))
    def bag(o, agir):
        for kemik, w in agir:
            vg = o.vertex_groups.get(kemik) or o.vertex_groups.new(name=kemik); vg.add(range(len(o.data.vertices)), w, 'REPLACE')
        parca.append(o)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.014, vertices=28, location=m)
    t = bpy.context.active_object; t.data.materials.append(malzeme('Tepsi', '#6b4a2f'))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.165, minor_radius=0.009, major_segments=28, minor_segments=5, location=m + Vector((0, 0, 0.012)))
    k = bpy.context.active_object; k.data.materials.append(malzeme('Tepsi', '#6b4a2f'))
    secili([t, k]); bpy.ops.object.join(); t = bpy.context.active_object; t.name = 'Tepsi'
    bag(t, [('bip L Hand_010', 1.0)])
    for dx, dy in ((-0.06, 0.03), (0.06, -0.03)):
        c = m + Vector((dx, dy, 0.007 + 0.05))
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.1, vertices=12, location=c)
        g = bpy.context.active_object; g.data.materials.append(malzeme('Kupa', '#7a5434'))
        bpy.ops.mesh.primitive_torus_add(major_radius=0.036, minor_radius=0.004, major_segments=12, minor_segments=4, location=c + Vector((0, 0, 0.025)))
        b = bpy.context.active_object; b.data.materials.append(malzeme('Cember', '#5a5a5e'))
        bpy.ops.mesh.primitive_torus_add(major_radius=0.02, minor_radius=0.006, major_segments=10, minor_segments=4, location=c + Vector((0.04, 0, 0)))
        sap = bpy.context.active_object; sap.rotation_euler = (math.radians(90), 0, 0); sap.data.materials.append(malzeme('Kupa', '#7a5434'))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.036, segments=12, ring_count=6, location=c + Vector((0, 0, 0.05)))
        kp = bpy.context.active_object; kp.scale = (1, 1, 0.45); kp.data.materials.append(malzeme('Kopuk', '#efe6cf'))
        secili([g, b, sap, kp]); bpy.ops.object.join(); g = bpy.context.active_object; g.name = 'Kupa'
        bag(g, [('bip L Hand_010', 1.0)])
    if AD == 'garson_kiz': parca.append(uzun_etek(ob, arm))
    return parca


def uzun_etek(ob, arm, n=56):
    """Kızın kısa elbisesinin eteğinden bileğe uzun etek. Üst halka eteğin ucunun çevresine oturur (her açıda modelin o
    yükseklikteki en dış noktası); aşağı doğru açılır, dikey kıvrımları var. Üstü leğene, altı yakın bacağa bağlı (yürürken sallanır)."""
    legen = arm.data.bones['bip Pelvis_02'].head_local
    V = np.array([v.co[:] for v in ob.data.vertices])
    ust_z = legen.z - 0.15                                          # kısa eteğin içinden başlar (ucu leğenin ~24 cm altı): arada aralık kalmasın
    alt_z = 0.10
    dilim = V[np.abs(V[:, 2] - ust_z) < 0.015]
    a = np.arctan2(dilim[:, 1] - legen.y, dilim[:, 0] - legen.x); rr = np.hypot(dilim[:, 1] - legen.y, dilim[:, 0] - legen.x)
    R0 = np.full(n, 0.15)
    for i in range(n):
        th = -np.pi + 2 * np.pi * i / n
        fark = np.abs((a - th + np.pi) % (2 * np.pi) - np.pi)
        sec = rr[(fark < 2 * np.pi / n * 1.5) & (rr < 0.3)]
        if len(sec): R0[i] = sec.max() - 0.012
    halka = 9
    kv, yz = [], []
    for j in range(halka):
        t = j / (halka - 1); z = ust_z + 0.01 - (ust_z + 0.01 - alt_z) * t
        for i in range(n):
            th = -np.pi + 2 * np.pi * i / n
            r = R0[i] + 0.21 * t ** 1.1 + 0.012 * t * np.sin(th * 11) + 0.006 * t * np.sin(th * 23 + 1.3)
            kv.append((legen.x + r * np.cos(th), legen.y + r * np.sin(th), z))
    for j in range(halka - 1):
        for i in range(n):
            a0, a1 = j * n + i, j * n + (i + 1) % n
            yz.append((a0, a1, a1 + n, a0 + n))
    me = bpy.data.meshes.new('Etek'); me.from_pydata(kv, [], yz)
    for f in me.polygons: f.use_smooth = True
    et = bpy.data.objects.new('Etek', me); bpy.context.scene.collection.objects.link(et)
    et.data.materials.append(malzeme('Etek', '#6a5241'))
    gl, gr, gp = (et.vertex_groups.new(name=k) for k in ('bip L Thigh_023', 'bip R Thigh_027', 'bip Pelvis_02'))
    for idx, (x, y, z) in enumerate(kv):
        t = (ust_z - z) / (ust_z - alt_z)
        sol = min(1.0, max(0.0, 0.5 + (x - legen.x) / 0.16))
        wl, wr = 0.7 * t * sol, 0.7 * t * (1 - sol)
        gl.add([idx], wl, 'REPLACE'); gr.add([idx], wr, 'REPLACE'); gp.add([idx], 1 - wl - wr, 'REPLACE')
    return et


def hanci_esyalar(ob, arm):
    """Hancının elinde beliren eşyalar (duruştan sonra; metre): sağ elde yeşil şişe ve el bezi, sol elde kupa (yumruk kulpunu
    tutar). Her biri kendi kemiğinde (boyu 0: görünmez; hareketler belirtir)."""
    secili([arm]); bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    yr = (eb['bip R Hand_018'].head + eb['bip R Hand_018'].tail) / 2
    yl = (eb['bip L Hand_010'].head + eb['bip L Hand_010'].tail) / 2
    kupa = yl + Vector((-0.055, 0, 0.01))                          # kulp yumrukta, kupa içeride
    for ad, ebe, bas in (('Sise', 'bip R Hand_018', yr), ('BezEl', 'bip R Hand_018', yr), ('Bardak', 'bip L Hand_010', kupa)):
        b = eb.new(ad); b.head = bas; b.tail = bas + Vector((0, 0, 0.06)); b.parent = eb[ebe]
    bpy.ops.object.mode_set(mode='OBJECT')
    parca = []

    def topla(obs, ad, kemik):
        secili(obs); bpy.ops.object.join(); o = bpy.context.active_object; o.name = ad
        o.vertex_groups.new(name=kemik).add(range(len(o.data.vertices)), 1.0, 'REPLACE'); parca.append(o)

    def silindir(r, boy, yer, mat, n=14):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=boy, vertices=n, location=yer)
        o = bpy.context.active_object; o.data.materials.append(mat); return o
    cam, mantar = malzeme('SiseCam', '#2f5a33'), malzeme('Mantar', '#9a7348')
    topla([silindir(0.034, 0.17, yr, cam), silindir(0.013, 0.09, yr + Vector((0, 0, 0.125)), cam, 10),
           silindir(0.0145, 0.025, yr + Vector((0, 0, 0.18)), mantar, 10)], 'Sise', 'Sise')
    k = [silindir(0.04, 0.11, kupa, malzeme('Kupa', '#7a5434'))]
    for dz in (-0.03, 0.03):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.041, minor_radius=0.004, major_segments=14, minor_segments=4, location=kupa + Vector((0, 0, dz)))
        k.append(bpy.context.active_object); k[-1].data.materials.append(malzeme('Cember', '#5a5a5e'))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.024, minor_radius=0.007, major_segments=10, minor_segments=4, location=kupa + Vector((0.045, 0, 0)))
    k.append(bpy.context.active_object); k[-1].rotation_euler = (math.radians(90), 0, 0); k[-1].data.materials.append(malzeme('Kupa', '#7a5434'))
    topla(k, 'Bardak', 'Bardak')
    bpy.ops.mesh.primitive_cube_add(size=1, location=yr + Vector((0, 0, -0.06)))     # yumruktan sarkan bez: silerken kupanın içine girer
    b = bpy.context.active_object; b.scale = (0.08, 0.012, 0.12); b.data.materials.append(malzeme('Havlu', '#d8ccb0'))
    bpy.ops.object.transform_apply(scale=True)
    topla([b], 'BezEl', 'BezEl')
    return parca


def hanci_onizle(arm, ob):
    """Her hareketin birkaç karesi önden, yandan ve sitenin kamerasına yakın yukarıdan (3d/karakter/hanci-<hareket>-<kare>-<yön>.png)."""
    sah = bpy.context.scene
    sah.render.engine = 'BLENDER_WORKBENCH'; sah.display.shading.light = 'STUDIO'; sah.display.shading.color_type = 'MATERIAL'
    sah.render.resolution_x, sah.render.resolution_y = 360, 360
    sah.world = bpy.data.worlds.new('d'); sah.world.color = (0.12, 0.1, 0.08)
    cam = bpy.data.objects.new('kam', bpy.data.cameras.new('kam')); sah.collection.objects.link(cam); sah.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 1.25
    on = arm['yumruk_on']                                          # tezgâh ve arkadaki dolap (sitedeki yerleri)
    for ad, y0, y1, z0, z1 in (('tezgah', -0.41 - on, 0.28 - on, TEZGAH - 0.05, TEZGAH), ('dolap', 1.4 - on, 1.85 - on, 0, 1.0)):   # han_plan: tezgâh ve arka dolap
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, (y0 + y1) / 2, (z0 + z1) / 2)); k = bpy.context.active_object
        k.scale = (1.6, y1 - y0, z1 - z0); k.name = ad
    hedef = Vector((0, 0.0, 1.2))
    for hareket, kareler in (('sil', [12, 30, 56, 96, 168]), ('sise', [22, 42, 64, 80, 104, 136, 170, 212]), ('yuru', [0, 16]), ('bekle', [0])):
        arm.animation_data.action = bpy.data.actions[hareket]
        for k in kareler:
            sah.frame_set(k)
            for yon, yer in (('on', (0, -4, 1.2)), ('yan', (-4, 0.1, 1.2)), ('ust', (0, -3.4, 4.0))):
                cam.location = yer; cam.rotation_euler = (hedef - Vector(yer)).to_track_quat('-Z', 'Y').to_euler()
                sah.render.filepath = str(ARA / f'hanci-{hareket}-{k:03d}-{yon}.png'); bpy.ops.render.render(write_still=True)
    print('BITTI')


def hanci_ekler(ob, s):
    """Kâğıttaki ense örgüsü (kızıl, uçta pirinç halka), sağ kalçada anahtar halkası, sol omuzda havlu. Ölçüler modelin
    kendi biriminde (boy 54) verilir, s ile metreye çevrilir."""
    arm = ob.parent
    V = lambda *p: Vector(p) * s
    parca = []

    def bag(o, kemik):
        vg = o.vertex_groups.new(name=kemik); vg.add(range(len(o.data.vertices)), 1.0, 'REPLACE')
        o.parent = arm; md = o.modifiers.new('Iskelet', 'ARMATURE'); md.object = arm
        parca.append(o)

    def katil(obs, ad, mat):
        for o in obs: o.data.materials.clear(); o.data.materials.append(mat)
        secili(obs); bpy.ops.object.join(); o = bpy.context.active_object; o.name = ad
        return o

    # örgü: ensenin arkasından sırta inen, sağa sola kayan basık küreler
    yol = [V(0, 7.6, 47), V(0, 10.2, 43), V(0, 12.0, 38.5), V(0, 12.6, 34), V(0, 12.4, 30.5)]
    toplar = []
    n = 16
    for i in range(n):
        t = i / (n - 1) * (len(yol) - 1); k = min(int(t), len(yol) - 2); f = t - k
        c = yol[k].lerp(yol[k + 1], f) + Vector(((-1) ** i * 0.45 * s, 0, 0))
        r = (1.9 - 0.8 * i / (n - 1)) * s
        sg, rc = (6, 4) if AYAR.get('alcak') else (10, 6)            # az çokgenlide köşeli düğümler
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=sg, ring_count=rc, location=c)
        b = bpy.context.active_object; b.scale = (1, 0.75, 0.62); toplar.append(b)
    org = katil(toplar, 'Orgu', malzeme('Orgu', '#a5482a'))
    bpy.ops.mesh.primitive_torus_add(major_radius=1.25 * s, minor_radius=0.35 * s, location=yol[-1] + V(0, 0.2, 1.3), major_segments=12, minor_segments=5)
    halka = bpy.context.active_object; halka.rotation_euler = (math.radians(90) + math.atan2(1, 6), 0, 0)
    halka = katil([halka], 'OrguHalka', malzeme('Pirinc', '#b8913f'))
    bag(org, 'bip Head_06'); bag(halka, 'bip Head_06')
    # anahtar halkası: kemerden (sağ kalça önü) sarkan halka ve dört anahtar
    merkez = V(-8.5, -9.6, 20.5)
    obs = []
    bpy.ops.mesh.primitive_torus_add(major_radius=2.0 * s, minor_radius=0.22 * s, location=merkez, major_segments=16, minor_segments=5)
    obs.append(bpy.context.active_object); obs[-1].rotation_euler = (math.radians(90), 0, math.radians(15))
    for i, aci in enumerate((-28, -9, 9, 28)):
        a = math.radians(aci)
        ust = merkez + V(math.sin(a) * 1.6, -0.3, -math.cos(a) * 1.6)
        alt = ust + V(math.sin(a) * 1.2, -0.2, -4.2)
        d = alt - ust
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22 * s, depth=d.length, vertices=6, location=(ust + alt) / 2)
        c = bpy.context.active_object; c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); obs.append(c)
        bpy.ops.mesh.primitive_cube_add(size=1, location=alt + V(0.45, 0, 0.6))
        c = bpy.context.active_object; c.scale = (0.9 * s, 0.25 * s, 0.6 * s); obs.append(c)       # anahtarın dişi
        bpy.ops.mesh.primitive_torus_add(major_radius=0.6 * s, minor_radius=0.18 * s, location=ust + V(0, 0, -0.5), major_segments=10, minor_segments=4)
        c = bpy.context.active_object; c.rotation_euler = (math.radians(90), 0, 0); obs.append(c)
    bag(katil(obs, 'Anahtarlar', malzeme('Pirinc', '#b8913f')), 'bip Pelvis_02')
    # havlu: sol omuzun (+x) önünden üstünden arkasına sarkan bez (lekeli krem); kalınlığı olan bir şerit
    yol = [V(10.0, -7.6, 33.5), V(10.6, -7.0, 38.5), V(11.2, -3.6, 43.0), V(11.4, 2.0, 44.6), V(11.0, 7.4, 42.0), V(10.4, 10.6, 36.0), V(10.0, 11.2, 32.0)]
    gen = 2.8 * s; kal = 0.3 * s                                     # göğse ve sırta yaslı (önce önlüğün önünde tahta gibi duruyordu)
    kv, yz = [], []
    for i, p in enumerate(yol):
        ileri = (yol[min(i + 1, len(yol) - 1)] - yol[max(i - 1, 0)]).normalized()
        dis = ileri.cross(Vector((1, 0, 0))).normalized()
        if dis.dot(Vector((0, 0, 1))) < 0 and abs(ileri.z) < 0.7: dis = -dis
        for sx in (-1, 1):
            for sd in (-1, 1): kv.append(p + Vector((sx * gen, 0, 0)) + dis * sd * kal)
    for i in range(len(yol) - 1):
        a, b = 4 * i, 4 * i + 4
        yz += [(a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3), (a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2)]
    son = 4 * (len(yol) - 1); yz += [(0, 1, 3, 2), (son, son + 2, son + 3, son + 1)]
    me = bpy.data.meshes.new('Havlu'); me.from_pydata([tuple(v) for v in kv], [], yz)
    hv = bpy.data.objects.new('Havlu', me); bpy.context.scene.collection.objects.link(hv)
    hv.data.materials.append(malzeme('Havlu', '#d8ccb0'))
    bag(hv, 'bip L Clavicle_07')
    return parca


def malzeme(ad, hex_):
    m = bpy.data.materials.new(ad); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*[(int(hex_[i:i + 2], 16) / 255) ** 2.2 for i in (1, 3, 5)], 1)
    b.inputs['Roughness'].default_value = 0.6
    m.diffuse_color = b.inputs['Base Color'].default_value             # önizlemede (Workbench) de görünsün
    return m


def basa_bagla(o, arm):
    vg = o.vertex_groups.new(name='bip Head_06'); vg.add(range(len(o.data.vertices)), 1.0, 'REPLACE')
    o.parent = arm; md = o.modifiers.new('Iskelet', 'ARMATURE'); md.object = arm


def isin(ob, bas, yon):
    """ob'a (dünya ekseninde) ışın: çarptığı nokta ya da None."""
    inv = ob.matrix_world.inverted()
    ok, p, n, i = ob.ray_cast(inv @ Vector(bas), (inv.to_3x3() @ Vector(yon)).normalized())
    return (ob.matrix_world @ p) if ok else None


def dm_ekler(ob, s):
    """Kâğıttaki yuvarlak gözlük ve sağ kulağın arkasındaki tüy. Baş kitaba doğru eğik ve dönük olduğu için yerleri yüze
    ışın atılarak bulunur. s: ham modelden (karakter_boya.DM_YUZ ölçüleri) şimdiki ölçüye çarpan."""
    import karakter_boya as kb
    arm = ob.parent
    gozler = [kb._yuz(p)[0] * s for p in ((262, 282), (350, 290))]       # yakın çekimde göz bebekleri (x, z); [0] sağ göz (−x)
    on_isin = lambda x, z: isin(ob, (x, -2, z), (0, 1, 0))
    yuzey = [on_isin(gx, gz) for gx, gz in gozler]
    orta = (gozler[0] + gozler[1]) / 2
    alin, cene = on_isin(orta[0], orta[1] + 0.06 * s), on_isin(orta[0], orta[1] - 0.10 * s)
    # yüzün eksenleri: x (sağ gözden sola), yuk (çeneden alına), on (yüzden dışarı)
    xek = (yuzey[1] - yuzey[0]).normalized()
    yuk = alin - cene; yuk = (yuk - xek * yuk.dot(xek)).normalized()
    on = yuk.cross(xek).normalized()
    if on.y > 0: on = -on
    R = 0.0165 * s
    parca = []
    merkez = [p + on * 0.011 * s for p in yuzey]
    for m in merkez:
        bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=0.0016 * s, major_segments=24, minor_segments=6)
        t = bpy.context.active_object
        t.matrix_world = Matrix.Translation(m) @ Matrix((xek, yuk, xek.cross(yuk))).transposed().to_4x4()
        parca.append(t)

    def cubuk(p, q, r=0.0013 * s):
        d = q - p
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=6)
        c = bpy.context.active_object
        c.matrix_world = Matrix.Translation((p + q) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        parca.append(c)
    kopru = (merkez[0] + merkez[1]) / 2 + on * 0.003 * s + yuk * 0.004 * s
    cubuk(merkez[0] + xek * R, kopru); cubuk(kopru, merkez[1] - xek * R)
    for m, sgn in ((merkez[0], -1), (merkez[1], 1)):                 # saplar: çerçevenin yanından kulağa
        u = m + xek * sgn * R
        cubuk(u, u - on * 0.095 * s - yuk * 0.01 * s + xek * sgn * 0.006 * s)
    for o in parca: o.data.materials.append(malzeme('Gozluk', '#4a3a26'))
    secili(parca); bpy.ops.object.join(); gz = bpy.context.active_object; gz.name = 'Gozluk'
    basa_bagla(gz, arm)
    # tüy: sağ kulağın (−x) arkasından yukarı ve geriye; ince, kıvrık bir yaprak
    kulak = isin(ob, (-2, yuzey[0].y - on.y * 0.08 * s, yuzey[0].z), (1, 0, 0)) or (yuzey[0] - xek * 0.07 * s)
    kok = kulak - on * 0.01 * s + yuk * 0.02 * s - xek * 0.025 * s   # saçın dışında dursun (gür saçta kayboluyordu)
    boy, en = 0.19 * s, 0.026 * s
    yonu = (yuk * 0.85 - on * 0.5 - xek * 0.15).normalized()
    yan = xek.cross(yonu).normalized()
    kv = []
    n = 12
    for i in range(n + 1):
        t = i / n
        c = kok + yonu * boy * t - on * 0.025 * s * t * t - xek * 0.012 * s * t
        w = en * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.7 * (0.25 if t < 0.12 else 1)
        kv += [c - yan * w * 0.4, c + yan * w * 0.6]
    me = bpy.data.meshes.new('Tuy'); me.from_pydata([tuple(v) for v in kv], [], [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(n)])
    tuy = bpy.data.objects.new('Tuy', me); bpy.context.scene.collection.objects.link(tuy)
    tuy.data.materials.append(malzeme('Tuy', '#ddd6c6'))
    basa_bagla(tuy, arm)
    return [gz, tuy]


def bas_ayir(ob, arm, R=0.21, alt=0.025):
    """Baş (saç, yüz, sakal, gözlük, tüy) ayrı bir "Bas" parçası olur: site POV'da kendi başını bütünüyle gizler. (Büyücüde
    baş kemiği küçültülüyordu; bu modelde ensedeki saç boyna da bağlı olduğu için küçülmüyor, gözün önünde saç kütlesi
    kalıyordu.) Kesik kenardaki köşelerin ağırlıkları iki yanda aynı: hareket ederken aralık açılmaz."""
    h, n = arm.data.bones['bip Head_06'], arm.data.bones['bip Neck_05']
    yuk = (h.tail_local - n.head_local).normalized()
    c = h.head_local + (h.tail_local - h.head_local) * 0.45
    me = ob.data
    taban = n.head_local - yuk * alt                                 # boynun biraz altı: göz hizasında boyun kesiti görünmesin
    ek = {i for i, m in enumerate(me.materials) if m and m.name.split('.')[0] in ('Gozluk', 'Tuy')}
    secili([ob]); bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(me)
    for e in list(bm.verts) + list(bm.edges) + list(bm.faces): e.select = False
    for f in bm.faces:                                             # yüzün ortasına göre (sivri saç uçları da gitsin)
        o = f.calc_center_median()
        f.select = f.material_index in ek or ((o - c).length < R and (o - taban).dot(yuk) > 0)
    bm.select_flush_mode(); bmesh.update_edit_mesh(me)
    bpy.ops.mesh.separate(type='SELECTED'); bpy.ops.object.mode_set(mode='OBJECT')
    bas = next(o for o in bpy.context.selected_objects if o != ob); bas.name = 'Bas'; bas.data.name = 'Bas'
    print('BAS', len(bas.data.polygons), 'yüz ayrıldı')


MODELLER = KOK / '3d' / 'modeller'   # kullanıcının Blender'da açıp bakacağı / düzelteceği son hâller (araclar/model_aktar_blender.py siteye gönderir)


def modeller_kopya():
    """Son hâlin kopyası 3d/modeller/<ad>.blend olur. Kullanıcı o dosyayı Blender'da değiştirdiyse (betiğin yazdığı andan sonra
    kaydedilmişse) üzerine yazılmaz: önce <ad>-elle-<tarih>.blend olarak yedeklenir."""
    import json, shutil, time
    MODELLER.mkdir(parents=True, exist_ok=True)
    ad = AD.replace('_', '-'); hedef = MODELLER / f'{ad}.blend'; kayit = MODELLER / '.betik.json'
    k = json.loads(kayit.read_text(encoding='utf-8')) if kayit.exists() else {}
    if hedef.exists() and abs(hedef.stat().st_mtime - k.get(ad, 0)) > 2:
        yedek = MODELLER / f'{ad}-elle-{time.strftime("%Y%m%d-%H%M")}.blend'
        shutil.copy2(hedef, yedek); print('YEDEK', yedek)
    bpy.ops.wm.save_as_mainfile(filepath=str(hedef), copy=True)
    k[ad] = hedef.stat().st_mtime; kayit.write_text(json.dumps(k), encoding='utf-8')
    print('MODEL', hedef)


def disa_aktar(arm, ob, cikti, glob, aciklama):
    secili([arm] + [o for o in arm.children if o.type == 'MESH'], ob)
    secenek = dict(filepath=str(cikti), export_format='GLB', use_selection=True, export_yup=True, export_apply=False,
                   export_animations=True, export_skins=True, export_extras=True)
    try: bpy.ops.export_scene.gltf(**secenek, export_image_format='JPEG', export_image_quality=82)
    except TypeError: bpy.ops.export_scene.gltf(**secenek, export_image_format='JPEG')
    veri = base64.b64encode(cikti.read_bytes()).decode('ascii')
    cikti.with_suffix('.js').write_text(f'// {aciklama} (araclar/karakter_kur_blender.py -- {AD} üretir). Site bilgisayardan açılınca .glb yerine bu okunur.\nwindow.{glob} = "' + veri + '";\n', encoding='utf-8')
    print('YAZILDI', cikti, cikti.stat().st_size)


def onizle(arm, ob):
    sah = bpy.context.scene
    sah.render.engine = 'BLENDER_WORKBENCH'; sah.display.shading.light = 'STUDIO'; sah.display.shading.color_type = 'TEXTURE'
    sah.render.resolution_x, sah.render.resolution_y = 500, 500
    sah.world = bpy.data.worlds.new('d'); sah.world.color = (0.12, 0.1, 0.08)
    cam = bpy.data.objects.new('kam', bpy.data.cameras.new('kam')); sah.collection.objects.link(cam); sah.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 1.6
    if AD in ('dm', 'fighter'):                                    # masa (76 cm) ve oturanın kolları
        y0, y1, mz, hedef = -0.40, -1.4, 0.76, Vector((0, -0.25, 0.75))
    elif AD == 'hanci':                                            # tezgâh (TEZGAH) ve hancının üst gövdesi
        y0, y1, mz, hedef = -0.25, -0.85, TEZGAH, Vector((0, -0.1, 1.45))
    else:                                                          # garson: yer
        y0, y1, mz, hedef = 1.0, -1.0, 0.0, Vector((0, 0, 0.95))
    masa = bpy.data.meshes.new('masa'); masa.from_pydata([(-.7, y0, mz), (.7, y0, mz), (.7, y1, mz), (-.7, y1, mz)], [], [(0, 1, 2, 3)])
    sah.collection.objects.link(bpy.data.objects.new('masa', masa))
    for ad, yer, kareler in [('on', (0, -4, 0.9), [0, 8, 20]), ('yan', (-4, -0.3, 0.8), [0, 20]), ('ust', (-2.0, -3.2, 3.2), [0]), ('arka', (0, 4, 0.9), [0])]:
        yer = Vector(yer) + Vector((0, 0, hedef.z - 0.75))
        if AD == 'hanci': kareler = [0, 75] if ad == 'on' else [0]
        elif AD not in ('dm', 'fighter'): kareler = [0, 8, 16] if ad in ('on', 'yan') else [0]
        cam.location = yer; cam.rotation_euler = (hedef - Vector(yer)).to_track_quat('-Z', 'Y').to_euler()
        for k in kareler:
            sah.frame_set(k)
            sah.render.filepath = str(ARA / f'{AD}-{ad}-{k:02d}.png')
            bpy.ops.render.render(write_still=True)
    print('BITTI')


if 'ham' in ASAMA: ham()
if 'kur' in ASAMA: kur()
