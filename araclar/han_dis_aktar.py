# -*- coding: utf-8 -*-
"""
YENİ HAN — DIŞ CEPHEYİ SİTEYE AKTARMA (Blender betiği)  (2026-11-26)
====================================================================
3d/han/han-dis.blend'den (araclar/han_dis_blender.py kurar) yalnızca dış kabuğu ('10_Dis') ve çevreyi ('11_Cevre') alır,
dokuları küçültür ve tek dosya olarak dışa aktarır: masa/han-dis.glb + han-dis.js (bilgisayardan açılınca, HAN_DIS_GLB).
Asıl dosyalar DEĞİŞMEZ. Işık pişirilmez (şimdilik; sitede canlı ışık). Önizleme sisi, ışıklar ve kameralar alınmaz.

Site (index.html BÖLÜM 11d) bunu yalnızca açılış için yükler. Nesnelerin 'dis' etiketi (userData.dis):
  'zemin'  çayır, toprak avlu, yollar: açılıştan sonra da kalır (içerinin eski taş döşemesinin yerine)
  'kabuk'  bina dışı, ağaçlar, eşyalar: yalnızca açılışta görünür, sonra bellekten atılır
Malzemelerdeki renk çarpanı (Dis_Tas: daha gri taş, Dis_Yol: koyu toprak, Dis_Yaprak) glTF'e geçmediği için resmin içine işlenir.

Çalıştırma (proje klasöründe, PowerShell):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --python araclar\\han_dis_aktar.py
"""
import bpy, os, base64
import numpy as np

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLB, JS = os.path.join(KOK, 'masa', 'han-dis.glb'), os.path.join(KOK, 'masa', 'han-dis.js')
BOY = 512                                              # dokuların en büyük kenarı (px)
ZEMIN = ('Cevre_Cayir', 'Cevre_Avlu', 'Cevre_Yol')

bpy.ops.wm.open_mainfile(filepath=os.path.join(KOK, '3d', 'han', 'han-dis.blend'))
def kolda(o, adlar):
    return any(c.name in adlar or any(c.name in p.children for p in bpy.data.collections if p.name in adlar) for c in o.users_collection)
secim = [o for o in bpy.data.objects if o.type == 'MESH' and kolda(o, ('10_Dis', '11_Cevre')) and not o.name.startswith('Onizleme_')]
for o in bpy.data.objects: o.select_set(False)
for o in secim:
    o.select_set(True); o['dis'] = 'zemin' if o.name in ZEMIN else 'kabuk'
print('Nesne:', len(secim), ', yüz:', sum(len(o.data.polygons) for o in secim))

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

ayar = dict(filepath=GLB, export_format='GLB', use_selection=True, export_extras=True,
            export_image_format='WEBP', export_image_quality=80,
            export_cameras=False, export_lights=False, export_yup=True,
            export_apply=True, export_texcoords=True, export_normals=True, export_tangents=False, export_vertex_color='NONE',
            export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12)
bpy.ops.export_scene.gltf(**ayar)
veri = open(GLB, 'rb').read()
open(JS, 'w', encoding='ascii').write('window.HAN_DIS_GLB="' + base64.b64encode(veri).decode('ascii') + '";\n')
print(f'Yazıldı: {GLB} ({len(veri) / 1e6:.2f} MB), {JS}')
print('TAMAM')
