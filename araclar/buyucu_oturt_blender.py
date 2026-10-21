# -*- coding: utf-8 -*-
"""
BÜYÜCÜYÜ MASAYA OTURTUR (siteye yüklenmez; çıktısı yüklenir)
Kullanıcının getirdiği poly-art_wizard_medieval_fantasy.glb (Denys Almaral, Sketchfab, CC-BY-4.0) T duruşundadır,
animasyonu yoktur. Bu betik iskeletin kemiklerini çevirerek onu sandalyede oturur hâle getirir (uyluklar öne, baldırlar
aşağı, kollar aşağı ve önkollar masaya), pozu modele işler (iskelet kalkar, düz bir model kalır) ve dışa aktarır:
  masa/buyucu.glb   (site https:// üzerinden açılınca)
  masa/buyucu.js    (site bilgisayardan açılınca: aynı veri metin olarak, taverna-npr.js gibi)
  3d/buyucu-onizleme-on/arka/yan.png   (kontrol için)
Ölçü ve yer: oturağın ortası (0, 0, 0) zemin; leğen kemiği oturak yüksekliğinde. Yüzü −y'ye bakar (glTF'te +z);
site (BÖLÜM 11b, tavBuyucu) onu sandalyeye göre 180° çevirir.
Asası (staff) masaya batmasın diye şimdilik çıkarılır.
Çalıştırma (proje klasöründen):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --factory-startup --python araclar\\buyucu_oturt_blender.py
Pozu değiştirmek için aşağıdaki POZ tablosundaki açılar değiştirilip betik yeniden çalıştırılır.
"""
import bpy, math, base64, pathlib
from mathutils import Matrix, Vector

KOK = pathlib.Path(bpy.path.abspath('//')).resolve() if bpy.data.filepath else pathlib.Path.cwd()
GIRDI = KOK / 'poly-art_wizard_medieval_fantasy.glb'
CIKTI = KOK / 'masa' / 'buyucu.glb'
BOY = 1.80            # ayakta, şapka dahil boy (m)
OTURAK = 0.50         # leğen kemiğinin (oturan) yerden yüksekliği (m)
LEGEN_Y = -0.02       # leğenin oturağın ortasına göre yeri (+y: masaya doğru)

# Dünya eksenlerinde dönüşler (derece), sırayla uygulanır (açıların yönü önizlemeyle denendi):
# x ekseninde eksi açı aşağı bakan bir kemiği karakterin önüne kaldırır.
POZ = [
    ('bip Spine_03',      'X',  6),     # gövde hafif öne
    ('bip L Thigh_023',   'X', -88),    # uyluklar öne (oturur)
    ('bip R Thigh_027',   'X', -88),
    ('bip L Calf_024',    'X',  84),    # baldırlar yine aşağı
    ('bip R Calf_028',    'X',  84),
    ('bip L UpperArm_08', 'Y',  70),    # kollar T duruşundan aşağı
    ('bip R UpperArm_016','Y', -70),
    ('bip L UpperArm_08', 'X', -28),    # biraz öne
    ('bip R UpperArm_016','X', -28),
    ('bip L Forearm_09',  'X', -72),    # önkollar masaya
    ('bip R Forearm_017', 'X', -72),
    ('bip L Forearm_09',  'Z', -22),    # eller içe
    ('bip R Forearm_017', 'Z',  22),
]
EKSEN = {'X': Vector((1, 0, 0)), 'Y': Vector((0, 1, 0)), 'Z': Vector((0, 0, 1))}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(GIRDI))
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']

# İçe aktarılan modelin boyu (birimi cm ya da m olabilir): ölçek buna göre
bpy.context.view_layer.update()
zler = [(o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices]
ham_boy = max(zler) - min(zler)
# Asa: masaya batmasın diye şimdilik çıkar
for o in list(meshes):
    if 'staff' in o.name.lower() or 'staff' in o.data.name.lower():
        bpy.data.objects.remove(o, do_unlink=True); meshes.remove(o)

# Poz: kemiği başının çevresinde, dünya ekseninde çevir (çocukları da onunla döner)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
inv = arm.matrix_world.inverted().to_3x3()
for ad, ek, aci in POZ:
    pb = arm.pose.bones.get(ad)
    if not pb:
        print('KEMİK YOK:', ad, [b.name for b in arm.pose.bones]); continue
    eks = (inv @ EKSEN[ek]).normalized()
    M = pb.matrix.copy(); bas = M.translation.copy()
    pb.matrix = Matrix.Translation(bas) @ Matrix.Rotation(math.radians(aci), 4, eks) @ Matrix.Translation(-bas) @ M
    bpy.context.view_layer.update()
legen = arm.matrix_world @ arm.pose.bones['bip Pelvis_02'].head
bpy.ops.object.mode_set(mode='OBJECT')

# Pozu modele işle, iskeleti kaldır, parçaları birleştir
for o in meshes:
    bpy.context.view_layer.objects.active = o
    for md in [m for m in o.modifiers if m.type == 'ARMATURE']:
        bpy.ops.object.modifier_apply(modifier=md.name)
for o in meshes:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
bpy.data.objects.remove(arm, do_unlink=True)
for o in list(bpy.context.scene.objects):
    if o.type == 'EMPTY': bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
bz = bpy.context.active_object; bz.name = 'Buyucu'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Ölçü (ayakta boyu, T duruşundaki yükseklikten) ve yer: leğen oturağın üstünde, yüz +y'ye
s = BOY / ham_boy
bz.scale = (s, s, s)
bz.location = (0, 0, 0)
bpy.context.view_layer.update()
lg = legen * s                                                   # leğen, ölçeklenince
bz.location = (-lg.x, LEGEN_Y - lg.y, OTURAK - lg.z)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
print('BOYUT', tuple(round(d, 3) for d in bz.dimensions), 'en alt', round(min((bz.matrix_world @ v.co).z for v in bz.data.vertices), 3))

# Dışa aktar (iskeletsiz, animasyonsuz) ve bilgisayardan açılış için .js kopyası
CIKTI.parent.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT'); bz.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(CIKTI), export_format='GLB', use_selection=True, export_yup=True, export_apply=True, export_animations=False, export_skins=False)
veri = base64.b64encode(CIKTI.read_bytes()).decode('ascii')
(CIKTI.with_suffix('.js')).write_text('// Büyücü modeli (araclar/buyucu_oturt_blender.py üretir). Site bilgisayardan açılınca .glb yerine bu okunur.\nwindow.BUYUCU_GLB = "' + veri + '";\n', encoding='utf-8')
print('YAZILDI', CIKTI, CIKTI.stat().st_size)

# Önizleme: önden ve yandan, düz ışıkla
sah = bpy.context.scene
sah.render.engine = 'BLENDER_WORKBENCH'; sah.display.shading.light = 'STUDIO'; sah.display.shading.color_type = 'TEXTURE'
sah.render.resolution_x, sah.render.resolution_y = 600, 700
sah.world = bpy.data.worlds.new('d'); sah.world.color = (0.12, 0.1, 0.08)
cam = bpy.data.objects.new('kam', bpy.data.cameras.new('kam')); sah.collection.objects.link(cam); sah.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.0
zemin = bpy.data.meshes.new('oturak'); zemin.from_pydata([(-.22, -.22, .47), (.22, -.22, .47), (.22, .22, .47), (-.22, .22, .47)], [], [(0, 1, 2, 3)])
sah.collection.objects.link(bpy.data.objects.new('oturak', zemin))
(KOK / '3d').mkdir(exist_ok=True)
for ad, yer, don in [('on', (0, -4, 0.8), (math.radians(90), 0, 0)), ('arka', (0, 4, 0.8), (math.radians(90), 0, math.radians(180))), ('yan', (4, 0, 0.8), (math.radians(90), 0, math.radians(90)))]:
    cam.location = yer; cam.rotation_euler = don
    sah.render.filepath = str(KOK / '3d' / f'buyucu-onizleme-{ad}.png')
    bpy.ops.render.render(write_still=True)
print('BITTI')
