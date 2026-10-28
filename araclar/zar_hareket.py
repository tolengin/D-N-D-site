# -*- coding: utf-8 -*-
"""
ZAR ATMA HAREKETİ (ortak; 2026-10-28'de buyucu_oturt_blender.py'den ayrıldı, karakter_kur_blender.py de kullanır).
Oturan karakterin sağ koluyla zarı avuçlayıp sallaması ve masaya savurması. Kemik adları büyücünün iskeletindeki gibidir
("bip R Hand_018" …); başka modeller aynı adlarla kurulur ki site (index.html, tavKolAt / tavAvuc) hepsini aynı biçimde oynatsın.
"""
import math
from mathutils import Matrix, Vector

EKSEN = {'X': Vector((1, 0, 0)), 'Y': Vector((0, 1, 0)), 'Z': Vector((0, 0, 1))}

# Zar atma hareketi: kare (30 kare = 1 sn) → oturma duruşundan dönüşler (dünya eksenlerinde, kemiğin başı çevresinde).
# Karakterin yüzü −y'de, sağ eli −x tarafında. X: eksi kemiği öne / yukarı kaldırır, artı geri / aşağı indirir; Z: artı sağ eli içe alır.
# Parmaklar (Finger1 = birleşik dört parmak, Finger0 = başparmak): X artı avuca kıvırır.
YUMRUK = [('bip R Finger1_021', 'X', 55), ('bip R Finger11_022', 'X', 70), ('bip R Finger0_019', 'Z', -25), ('bip R Finger01_020', 'Z', -30)]
SALLA_UST = [('bip R UpperArm_016', 'Z', 5), ('bip R Forearm_017', 'X', -42), ('bip R Hand_018', 'X', -30)] + YUMRUK
SALLA_ALT = [('bip R UpperArm_016', 'Z', 5), ('bip R Forearm_017', 'X', -8), ('bip R Hand_018', 'X', 28)] + YUMRUK
ZAR_AT = [
    (0,  []),                                                                     # oturuş
    (4,  [('bip R UpperArm_016', 'Z', 5), ('bip R Forearm_017', 'X', -20)] + YUMRUK),    # zarı avuçlar
    (8, SALLA_UST), (11, SALLA_ALT),                                             # bir kez sallar (göğüs önünde; 2026-10-28'e kadar üç kez, zar geç geliyordu)
    (15, [('bip Spine1_04', 'X', -3), ('bip R UpperArm_016', 'X', 8), ('bip R UpperArm_016', 'Z', 5),
          ('bip R Forearm_017', 'X', -40), ('bip R Hand_018', 'X', -38)] + YUMRUK),            # bileği geri büker
    (20, [('bip Spine1_04', 'X', 9), ('bip R UpperArm_016', 'X', -25), ('bip R UpperArm_016', 'Z', 10),
          ('bip R Forearm_017', 'X', 32), ('bip R Hand_018', 'X', 22),
          ('bip R Finger1_021', 'X', -12), ('bip R Finger0_019', 'Z', 15)]),                      # masaya savurur, el açılır: zar çıkar
    (26, [('bip Spine1_04', 'X', 8), ('bip R UpperArm_016', 'X', -32), ('bip R UpperArm_016', 'Z', 10),
          ('bip R Forearm_017', 'X', 38), ('bip R Hand_018', 'X', 10), ('bip R Finger1_021', 'X', -8)]),   # el masanın üstünde kalır
    (42, []),                                                                     # oturuşa döner
]
BIRAK = 18                                    # zarın çıktığı kare (0,6 sn): el savururken açılıyor; 20'de el masaya iniyor, zar oradan
                                              # çıkınca masaya gömülüyordu
ANIM_KEMIK = ['bip Spine1_04', 'bip R Clavicle_015', 'bip R UpperArm_016', 'bip R Forearm_017', 'bip R Hand_018',
              'bip R Finger0_019', 'bip R Finger01_020', 'bip R Finger1_021', 'bip R Finger11_022']


def cevir(arm, liste):
    """Kemikleri sırayla, başlarının çevresinde dünya ekseninde çevirir (çocukları da onunla döner).
    Ek türleri (2026-10-28, hancının hareketleri): 'L' kemiği dünyada (dx, dy, dz) metre taşır, 'S' boyunu verir (0: görünmez;
    şişe, kupa, havlu elde belirip kaybolur)."""
    import bpy
    inv = arm.matrix_world.inverted().to_3x3()
    for ad, ek, aci in liste:
        pb = arm.pose.bones.get(ad)
        if not pb:
            print('KEMİK YOK:', ad, [b.name for b in arm.pose.bones]); continue
        if ek == 'L':
            pb.matrix = Matrix.Translation(inv @ Vector(aci)) @ pb.matrix; bpy.context.view_layer.update(); continue
        if ek == 'S':
            pb.scale = (max(aci, 1e-3),) * 3; bpy.context.view_layer.update(); continue
        if ek == 'IK':                                            # el (bileği) iskeletin içinde aci noktasına uzanır; Blender'ın IK'sı
            on, ust = pb.parent, pb.parent.parent                 #   önkolu ve üst kolu çevirir, elin dünyadaki yönü değişmez
            yon = pb.matrix.to_3x3().copy()
            hedef = bpy.data.objects.new('ik_hedef', None); bpy.context.scene.collection.objects.link(hedef)
            hedef.location = arm.matrix_world @ Vector(aci)
            c = on.constraints.new('IK'); c.target = hedef; c.chain_count = 2
            bpy.context.view_layer.update()
            Mu, Mo = ust.matrix.copy(), on.matrix.copy()
            on.constraints.remove(c); bpy.data.objects.remove(hedef)
            ust.matrix = Mu; bpy.context.view_layer.update(); on.matrix = Mo; bpy.context.view_layer.update()
            pb.matrix = Matrix.Translation(pb.matrix.translation) @ yon.to_4x4(); bpy.context.view_layer.update()
            continue
        eks = (inv @ EKSEN[ek]).normalized()
        M = pb.matrix.copy(); bas = M.translation.copy()
        pb.matrix = Matrix.Translation(bas) @ Matrix.Rotation(math.radians(aci), 4, eks) @ Matrix.Translation(-bas) @ M
        bpy.context.view_layer.update()


def hareket_kur(arm, ad='zar_at', tablo=None, kemikler=None, birak=BIRAK):
    """arm'ın şu anki duruşundan (dinlenme) tablo'daki anahtar kareleri kaydeder; site için 'birak' ve 'sure' (sn) yazar."""
    import bpy
    tablo = tablo or ZAR_AT; kemikler = kemikler or ANIM_KEMIK
    sah = bpy.context.scene
    sah.render.fps = 30; sah.frame_start = 0; sah.frame_end = tablo[-1][0]
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    if not arm.animation_data: arm.animation_data_create()
    arm.animation_data.action = bpy.data.actions.new(ad)
    arm.animation_data.action.use_fake_user = True                # birden çok hareket (garsonda bekle + yuru) dışa aktarımda kalsın
    onceki = {}
    tasinan = {a for _, l in tablo for a, e, _ in l if e == 'L'}     # bunların yeri de, şunların boyu da her karede kaydedilir
    boylu = {a for _, l in tablo for a, e, _ in l if e == 'S'}
    for kare, liste in tablo:
        for pb in arm.pose.bones:
            pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
        bpy.context.view_layer.update()
        cevir(arm, liste)
        for kad in kemikler:
            pb = arm.pose.bones[kad]
            if kad not in tasinan: pb.location = (0, 0, 0)
            q = pb.rotation_quaternion.copy()
            if kad in onceki and onceki[kad].dot(q) < 0: q.negate()  # kısa yoldan dönsün
            pb.rotation_quaternion = q; onceki[kad] = q
            pb.keyframe_insert('rotation_quaternion', frame=kare)
            if kad in tasinan: pb.keyframe_insert('location', frame=kare)
            if kad in boylu: pb.keyframe_insert('scale', frame=kare)
    if birak is not None: arm['birak'] = round(birak / sah.render.fps, 3)      # site: zar elden bu saniyede çıkar
    arm['sure'] = round(tablo[-1][0] / sah.render.fps, 3)
    bpy.ops.object.mode_set(mode='OBJECT')
