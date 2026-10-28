# -*- coding: utf-8 -*-
"""
3d/modeller/ İÇİNDEKİ BİR KARAKTERİ SİTEYE GÖNDERİR (2026-10-28; siteye yüklenmez, çıktısı yüklenir)
Kullanıcı karakteri Blender'da açıp elle düzeltince (3d/modeller/<ad>.blend), bu betik onu sitenin okuduğu masa/<dosya>.glb
ve .js olarak dışa aktarır (karakter_kur_blender.py'nin dışa aktarmasıyla aynı ayarlar).

  dm            → masa/dm-iskelet.glb        fighter       → masa/fighter-iskelet.glb
  hanci         → masa/hanci.glb             garson-kiz    → masa/garson-kiz.glb      garson-erkek → masa/garson-erkek.glb

Çalıştırma (proje klasöründen; Blender açıksa önce dosyayı kaydet):
  & "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Blender\\blender.exe" --background --python araclar\\model_aktar_blender.py -- hanci

Dikkat: iskeletin adı "Iskelet", kemik adları ve hareketlerin adları (zar_at, bekle, sil, sise, yuru) değişmemeli; site
onları adıyla arar. karakter_kur_blender.py yeniden çalışırsa 3d/modeller/<ad>.blend'i yeniler, elle değiştirilmişse önce
<ad>-elle-<tarih>.blend olarak yedekler.
"""
import bpy, base64, pathlib, sys

AD = (sys.argv[sys.argv.index('--') + 1:] or ['dm'])[0]
KOK = pathlib.Path.cwd()
CIKTI = {'dm': ('dm-iskelet', 'DM_ISKELET_GLB', 'İskeletli DM'), 'fighter': ('fighter-iskelet', 'FIGHTER_ISKELET_GLB', 'İskeletli fighter'),
         'hanci': ('hanci', 'HANCI_GLB', 'Hancı'), 'garson-kiz': ('garson-kiz', 'GARSON_KIZ_GLB', 'Garson'),
         'garson-erkek': ('garson-erkek', 'GARSON_ERKEK_GLB', 'Garson')}[AD]

bpy.ops.wm.open_mainfile(filepath=str(KOK / '3d' / 'modeller' / f'{AD}.blend'))
arm = bpy.data.objects['Iskelet']
if bpy.context.object and bpy.context.object.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
for o in [arm] + [o for o in arm.children if o.type == 'MESH']: o.select_set(True)
bpy.context.view_layer.objects.active = arm
for h in bpy.data.actions: h.use_fake_user = True                  # bütün hareketler dışa aktarılsın
bpy.context.scene.frame_set(0)
cikti = KOK / 'masa' / f'{CIKTI[0]}.glb'
secenek = dict(filepath=str(cikti), export_format='GLB', use_selection=True, export_yup=True, export_apply=False,
               export_animations=True, export_skins=True, export_extras=True)
try: bpy.ops.export_scene.gltf(**secenek, export_image_format='JPEG', export_image_quality=82)
except TypeError: bpy.ops.export_scene.gltf(**secenek, export_image_format='JPEG')
veri = base64.b64encode(cikti.read_bytes()).decode('ascii')
cikti.with_suffix('.js').write_text(f'// {CIKTI[2]} (3d/modeller/{AD}.blend, araclar/model_aktar_blender.py -- {AD} üretir). Site bilgisayardan açılınca .glb yerine bu okunur.\nwindow.{CIKTI[1]} = "' + veri + '";\n', encoding='utf-8')
print('YAZILDI', cikti, cikti.stat().st_size)
