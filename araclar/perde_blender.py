# -*- coding: utf-8 -*-
"""
DM PERDESİNİN MODELİ (2026-10-29; siteye yüklenmez, çıktısı yüklenir: masa/perde.glb, perde.js)
Kullanıcının örnekleri (perde-1/2/3): yakma işi motifli tahta kanatlar, DM'e bakan yüzde çerçeveli kâğıtlar, kara demir
köşebent, perçin ve menteşeler. Üç kanat: ortada geniş (amblem), iki yanda dar (d20). Her kanat ayrı nesne (PerdeSol,
PerdeOrta, PerdeSag); site onları DM'in önünde bir yay üstüne dizer (index.html, tavKoltuklar) ve zarın fiziğinde duvar yapar.
Doku: araclar/perde_doku.py (3d/perde/perde-doku.png; ölçüler ve yerler oradan).

Yönler (Blender): x kanadın eni, +y oyunculara bakan ön yüz, −y DM'e bakan arka yüz, z yukarı; kanadın ortası kökte.
Çalıştırma (proje klasöründen; önce python araclar\\perde_doku.py):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --factory-startup --python araclar\\perde_blender.py
"""
import bpy, bmesh, math, base64, pathlib, sys
from mathutils import Vector, Matrix

KOK = pathlib.Path.cwd()
sys.path.insert(0, str(KOK / 'araclar'))
from perde_doku import PERDE, PX, SAYFA, YER                      # ölçüler ve doku sayfasındaki yerler

H, K, CW = PERDE['H'], PERDE['K'], PERDE['cerceve']
T = 0.005                                                           # çerçeve çıtalarının tahtadan çıkıntısı
DT = 0.0022                                                         # demir levhaların kalınlığı
AHSAP_PX = 1500                                                     # çerçeve ve kenarların dokusu: 1 m kaç piksel


def kutu(bm, x0, x1, y0, y1, z0, z1, rol, pah=0.0):
    g = bmesh.new(); bmesh.ops.create_cube(g, size=1.0)
    for v in g.verts:
        v.co = Vector((x0 if v.co.x < 0 else x1, y0 if v.co.y < 0 else y1, z0 if v.co.z < 0 else z1))
    if pah > 0:
        bmesh.ops.bevel(g, geom=list(g.edges), offset=pah, segments=1, affect='EDGES', profile=0.5, clamp_overlap=True)
    ekle(bm, g, rol)


def silindir(bm, merkez, eksen, r, boy, n, rol):
    g = bmesh.new()
    bmesh.ops.create_cone(g, cap_ends=True, segments=n, radius1=r, radius2=r, depth=boy)
    q = Vector(eksen).to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.transform(g, matrix=Matrix.Translation(merkez) @ q, verts=g.verts)
    ekle(bm, g, rol)


ROLLER = ['on', 'arka', 'ahsap', 'ahsap_d', 'demir']


def ekle(bm, g, rol):
    """g'yi bm'e ekler; yüzlerin rolü (doku sayfasının neresine eşleneceği) malzeme sırasında saklanır."""
    harita = {}
    for v in g.verts: harita[v] = bm.verts.new(v.co)
    for f in g.faces:
        try:
            yf = bm.faces.new([harita[v] for v in f.verts]); yf.material_index = ROLLER.index(rol)
        except ValueError:
            pass
    g.free()


def kanat(ad, W, menteseler, arka):
    """Bir kanat: gövde tahtası, iki yüzde çerçeve, önde köşebent ve perçinler, menteşeli kenarlar, arkada raptiyeler ve ayaklar.
    menteseler: menteşenin olduğu kenarlar (−1 sol, +1 sağ; x yönünde). arka: DM'e bakan kâğıdın doku yeri."""
    bm = bmesh.new()
    w2, h2, k2 = W / 2, H / 2, K / 2
    # gövde: ön ve arka yüz kendi resminde, kenarlar tahta
    g = bmesh.new(); bmesh.ops.create_cube(g, size=1.0)
    for v in g.verts: v.co = Vector((w2 if v.co.x > 0 else -w2, k2 if v.co.y > 0 else -k2, h2 if v.co.z > 0 else -h2))
    harita = {v: bm.verts.new(v.co) for v in g.verts}
    for f in g.faces:
        f.normal_update(); n = f.normal
        rol = 'on' if n.y > 0.9 else 'arka' if n.y < -0.9 else 'ahsap'
        bm.faces.new([harita[v] for v in f.verts]).material_index = ROLLER.index(rol)
    g.free()
    # çerçeve: önde ve arkada dört çıta (yanlar dikey damarlı)
    for y0, y1 in ((k2, k2 + T), (-k2 - T, -k2)):
        kutu(bm, -w2, w2, y0, y1, h2 - CW, h2, 'ahsap', 0.0018)
        kutu(bm, -w2, w2, y0, y1, -h2, -h2 + CW, 'ahsap', 0.0018)
        for s in (-1, 1):
            xa, xb = sorted((s * w2, s * (w2 - CW)))
            kutu(bm, xa, xb, y0, y1, -h2 + CW, h2 - CW, 'ahsap_d', 0.0018)
    on = k2 + T                                                     # ön çerçevenin yüzü
    # köşebentler: L biçimli demir, üç perçin
    kol, gen = 0.052, 0.015
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * w2, sz * h2
            kutu(bm, *sorted((cx, cx - sx * kol)), on, on + DT, *sorted((cz, cz - sz * gen)), 'demir')
            kutu(bm, *sorted((cx, cx - sx * gen)), on, on + DT, *sorted((cz - sz * gen, cz - sz * kol)), 'demir')
            for px, pz in ((gen * 0.5, gen * 0.5), (kol - 0.009, gen * 0.5), (gen * 0.5, kol - 0.009)):
                silindir(bm, Vector((cx - sx * px, on + DT + 0.0012, cz - sz * pz)), (0, 1, 0), 0.0034, 0.0024, 6, 'demir')
    # menteşeler: kenarda kayış ve topuz (iki kanadın topuzu birleşir)
    for s in menteseler:
        ex = s * w2
        for zz in (-H * 0.27, H * 0.27):
            kutu(bm, *sorted((ex, ex - s * 0.036)), on, on + DT, zz - 0.009, zz + 0.009, 'demir')
            for px in (0.012, 0.027):
                silindir(bm, Vector((ex - s * px, on + DT + 0.0012, zz)), (0, 1, 0), 0.0028, 0.0024, 6, 'demir')
            silindir(bm, Vector((ex, on + 0.004, zz)), (0, 0, 1), 0.0058, 0.036, 8, 'demir')
    # arka: kâğıdı tutan dört raptiye, iki ayak (perde dik dursun)
    ark = -k2 - T
    for sx in (-1, 1):
        for sz in (-1, 1):
            silindir(bm, Vector((sx * (w2 - CW - 0.012), -k2 - 0.0012, sz * (h2 - CW - 0.012))), (0, 1, 0), 0.0042, 0.0026, 6, 'demir')
        kutu(bm, sx * W * 0.32 - 0.016, sx * W * 0.32 + 0.016, ark - 0.034, ark, -h2, -h2 + 0.028, 'ahsap', 0.003)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # UV: her yüz rolüne göre doku sayfasındaki yerine
    uvl = bm.loops.layers.uv.new('UVMap')
    SW, SH = SAYFA

    def yer(ad, fx, fy):                                             # fx, fy: o yerin içinde 0…1 (fy aşağı doğru)
        x0, y0, w, h = YER[ad]
        return ((x0 + fx * w) / SW, 1 - (y0 + fy * h) / SH)
    on_yer = 'on_orta' if 'Orta' in ad else 'on_yan'
    bm.normal_update()
    for f in bm.faces:
        rol = ROLLER[f.material_index]; n = f.normal
        for l in f.loops:
            p = l.vert.co
            if rol == 'on':
                l[uvl].uv = yer(on_yer, (w2 - p.x) / W, (h2 - p.z) / H)       # önden bakınca solu +x
            elif rol == 'arka':
                l[uvl].uv = yer(arka, (p.x + w2) / W, (h2 - p.z) / H)
            elif rol in ('ahsap', 'ahsap_d'):
                ax = max(range(3), key=lambda k: abs(n[k]))
                a, b = ((p.y + 0.06), (h2 - p.z)) if ax == 0 else (((p.x + w2), (p.y + 0.06)) if ax == 2 else ((p.x + w2), (h2 - p.z)))
                if rol == 'ahsap_d': a, b = b, a                       # dikey çıtada damar boyuna
                x0, y0, w, h = YER['ahsap']
                l[uvl].uv = ((x0 + min(a * AHSAP_PX, w - 2)) / SW, 1 - (y0 + min(b * AHSAP_PX, h - 2)) / SH)
            else:
                x0, y0, w, h = YER['demir']
                l[uvl].uv = ((x0 + 20 + ((p.x + w2) / W) * (w - 40)) / SW, 1 - (y0 + 20 + ((h2 - p.z) / H) * (h - 40)) / SH)
    for f in bm.faces: f.material_index = 0
    me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free()
    me.materials.append(MAL)
    ob = bpy.data.objects.new(ad, me); bpy.context.scene.collection.objects.link(ob)
    ob['W'], ob['H'], ob['K'] = round(W, 4), round(H, 4), round(K + 2 * T, 4)   # site: yay ve zarın duvarı
    print('KANAT', ad, len(me.polygons), 'yüz')
    return ob


bpy.ops.wm.read_factory_settings(use_empty=True)
img = bpy.data.images.load(str(KOK / '3d' / 'perde' / 'perde-doku.png'))
MAL = bpy.data.materials.new('Perde'); MAL.use_nodes = True
b = MAL.node_tree.nodes['Principled BSDF']
tx = MAL.node_tree.nodes.new('ShaderNodeTexImage'); tx.image = img
MAL.node_tree.links.new(tx.outputs['Color'], b.inputs['Base Color'])
b.inputs['Roughness'].default_value = 0.85
Wy, Wo = PERDE['W_yan'], PERDE['W_orta']
kanatlar = [kanat('PerdeSol', Wy, [1], 'arka_sol'), kanat('PerdeOrta', Wo, [-1, 1], 'arka_orta'), kanat('PerdeSag', Wy, [-1], 'arka_sag')]

# dışa aktar (kanatlar kökte, üst üste; site yerleştirir) ve .js kopyası
CIKTI = KOK / 'masa' / 'perde.glb'
for o in bpy.context.scene.objects: o.select_set(o in kanatlar)
secenek = dict(filepath=str(CIKTI), export_format='GLB', use_selection=True, export_yup=True, export_apply=True, export_extras=True)
try: bpy.ops.export_scene.gltf(**secenek, export_image_format='JPEG', export_image_quality=86)
except TypeError: bpy.ops.export_scene.gltf(**secenek, export_image_format='JPEG')
CIKTI.with_suffix('.js').write_text('// DM perdesi (araclar/perde_blender.py üretir). Site bilgisayardan açılınca .glb yerine bu okunur.\nwindow.PERDE_GLB = "'
                                    + base64.b64encode(CIKTI.read_bytes()).decode('ascii') + '";\n', encoding='utf-8')
print('YAZILDI', CIKTI, CIKTI.stat().st_size)

# önizleme: sitedeki gibi yayda (DM'in önünde, D = 0,75 m), önden (oyuncular), arkadan (DM), yukarıdan
D, ara = 0.75, 1.03
xs, top = [], 0.0
gen = [o['W'] for o in kanatlar]
toplam = sum(gen) * ara
for o, w in zip(kanatlar, gen):
    a = (top + w * ara / 2 - toplam / 2) / D; top += w * ara
    o.location = (math.sin(a) * D, -math.cos(a) * D + D, H / 2); o.rotation_euler = (0, 0, a)   # +y oyunculara; DM kökün −y yanında
sah = bpy.context.scene
sah.render.engine = 'BLENDER_WORKBENCH'; sah.display.shading.light = 'STUDIO'; sah.display.shading.color_type = 'TEXTURE'
sah.render.resolution_x, sah.render.resolution_y = 900, 450
sah.world = bpy.data.worlds.new('d'); sah.world.color = (0.12, 0.1, 0.08)
cam = bpy.data.objects.new('kam', bpy.data.cameras.new('kam')); sah.collection.objects.link(cam); sah.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 0.95
hedef = Vector((0, 0.15, H / 2))
for yon, yer_ in (('on', (0, 2.5, 0.35)), ('arka', (0, -2.5, 0.35)), ('ust', (0.6, 2.0, 1.6)), ('yakin', (0.25, 1.2, 0.2))):
    if yon == 'yakin': cam.data.ortho_scale = 0.4
    cam.location = Vector(yer_) + Vector((0, 0.15, 0)); cam.rotation_euler = (hedef - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sah.render.filepath = str(KOK / '3d' / 'perde' / f'perde-{yon}.png'); bpy.ops.render.render(write_still=True)
print('BITTI')
