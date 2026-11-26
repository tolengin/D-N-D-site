# -*- coding: utf-8 -*-
"""
IZGARALI ÖNİZLEME, BLENDER KISMI (2026-11-26, R5; siteye yüklenmez). Hazır bir modelin eklem yerlerini (omuz, dirsek, bilek,
kalça, diz, ayak), silinecek parçaların (miğfer, pelerin, kılıç) ve başın yerini okumak için: modeli önden / yandan / arkadan
ortografik çizer; ızgarayı araclar/izgara_ciz.py ekler (Blender'ın Python'unda Pillow yok). Ölçüler modelin kendi biriminde.
Örnek (proje klasöründen):
  blender -b --factory-startup --python araclar/izgara_blender.py -- "3D karakter referans modelleri/paladin-v2.glb" 3d/karakter/iz/paladin --yuz 120000 --don -90 --bolge ust:-0.26,0.26,0.12,0.50,-0.2,0.24 --adim 0.02 --px 900
  python araclar/izgara_ciz.py 3d/karakter/iz/paladin           (→ 3d/karakter/iz/paladin-ust.png)
glb verilirse birleştirir, azaltır (--yuz), döndürür (--don, derece; model −y'ye baksın), <onek>.blend kaydeder; .blend verilirse
(ör. 3d/karakter/<ad>-ham.blend) olduğu gibi çizer. --bolge ad:x0,x1,z0,z1[,y0,y1] (birden çok olabilir), --adim ızgara aralığı.
Önde +x sağda, yanda +y sağda, arkada −x sağda.
"""
import bpy, sys, math, json
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index('--') + 1:]
girdi, cik = a[0], a[1]
import pathlib
cik = str(pathlib.Path(cik).resolve())                                     # tam yol (Blender göreli yolu açılan .blend'e göre yorumlar)
pathlib.Path(cik).parent.mkdir(parents=True, exist_ok=True)               # çıktı klasörü yoksa açılır
opt = {'yuz': 0, 'don': 0.0, 'adim': 0.02, 'px': 1000}
bolgeler = []
i = 2
while i < len(a):
    k = a[i][2:]
    if k == 'bolge':
        ad, v = a[i + 1].split(':'); bolgeler.append((ad, [float(t) for t in v.split(',')]))
    else:
        opt[k] = float(a[i + 1])
    i += 2
if girdi.endswith('.blend'):
    bpy.ops.wm.open_mainfile(filepath=girdi)
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=girdi)
    ms = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for o in ms:
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in list(bpy.context.scene.objects):
        if o.type != 'MESH': bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in ms: o.select_set(True)
    bpy.context.view_layer.objects.active = ms[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if len(ms) > 1: bpy.ops.object.join()
    ob = bpy.context.active_object; ob.name = 'model'
    if opt['don']:
        ob.data.transform(Matrix.Rotation(math.radians(opt['don']), 4, 'Z')); ob.data.update()
    if opt['yuz'] and len(ob.data.polygons) > opt['yuz']:
        md = ob.modifiers.new('az', 'DECIMATE'); md.ratio = opt['yuz'] / len(ob.data.polygons)
        bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.ops.wm.save_as_mainfile(filepath=cik + '.blend')
ms = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.visible_get()]
bpy.context.view_layer.update()
mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
for o in ms:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
print('BOUNDS', tuple(round(v, 4) for v in mn), tuple(round(v, 4) for v in mx), 'YUZ', sum(len(o.data.polygons) for o in ms))
if not bolgeler: bolgeler = [('tum', [mn.x, mx.x, mn.z, mx.z, mn.y, mx.y])]
sah = bpy.context.scene
for c in [o for o in sah.objects if o.type == 'CAMERA']: bpy.data.objects.remove(c)
sah.render.engine = 'BLENDER_WORKBENCH'; sah.display.shading.light = 'STUDIO'; sah.display.shading.color_type = 'TEXTURE'
sah.world = bpy.data.worlds.new('d'); sah.world.color = (0.55, 0.55, 0.55)
cam = bpy.data.objects.new('kam', bpy.data.cameras.new('kam')); sah.collection.objects.link(cam); sah.camera = cam
cam.data.type = 'ORTHO'; cam.data.clip_end = 100
bilgi = []
for ad, b in bolgeler:
    x0, x1, z0, z1 = b[:4]
    y0, y1 = (b[4], b[5]) if len(b) > 5 else (mn.y, mx.y)
    for yon, d, (u0, u1), isaret in (('on', Vector((0, -1, 0)), (x0, x1), 1), ('yan', Vector((1, 0, 0)), (y0, y1), 1), ('arka', Vector((0, 1, 0)), (x0, x1), -1)):
        gw, gh = u1 - u0, z1 - z0
        olc = max(gw, gh)
        px = int(opt['px'])
        sah.render.resolution_x = int(px * gw / olc); sah.render.resolution_y = int(px * gh / olc)
        cam.data.ortho_scale = olc
        uc, zc = (u0 + u1) / 2, (z0 + z1) / 2
        c = Vector((0, uc, zc)) if yon == 'yan' else Vector((uc, 0, zc))
        cam.location = c + d * 20; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
        yol = f'{cik}-{ad}-{yon}.png'
        sah.render.filepath = yol; bpy.ops.render.render(write_still=True)
        bilgi.append(dict(ad=ad, yon=yon, yol=yol, u0=u0, u1=u1, z0=z0, z1=z1, isaret=isaret))
json.dump(dict(adim=opt['adim'], bilgi=bilgi), open(cik + '-izgara.json', 'w'))
