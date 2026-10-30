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
        if ek == 'YON':                                           # kemik dünyada aci yönüne bakar (başı çevresinde; el: parmaklar o yöne)
            su = (pb.tail - pb.head).normalized(); ist = (inv @ Vector(aci)).normalized()
            M = pb.matrix.copy(); bas = M.translation.copy()
            pb.matrix = Matrix.Translation(bas) @ su.rotation_difference(ist).to_matrix().to_4x4() @ Matrix.Translation(-bas) @ M
            bpy.context.view_layer.update(); continue
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


# Boşta (2026-10-29, kullanıcı: "her karaktere nefes alma, 10–15 saniyede bir özel hareket"). Site "nefes"i hep oynatır (döngü),
# "ozel"i ara sıra bir kez. Nefes zar_at'ın ve özel hareketlerin kemiklerine dokunmaz (aynı anda oynarlar, karışmasınlar):
# göğsün altı, boyun ve köprücük kemikleri. 4 sn: 1,6 sn nefes alır (göğüs dikleşir, omuzlar kalkar), 2,4 sn verir.
NEFES = [(0, []),
         (48, [('bip Spine_03', 'X', -2.5), ('bip Neck_05', 'X', 2.5), ('bip L Clavicle_07', 'Y', -3.5), ('bip R Clavicle_015', 'Y', 3.5)]),
         (120, [])]
NEFES_KEMIK = ['bip Spine_03', 'bip Neck_05', 'bip L Clavicle_07', 'bip R Clavicle_015']
SAG_EL, SOL_EL = 'bip R Hand_018', 'bip L Hand_010'
OZEL_KEMIK = ['bip Spine1_04', 'bip Head_06'] + [f'bip {t} {k}' for t, ks in
              (('R', ('UpperArm_016', 'Forearm_017', 'Hand_018', 'Finger0_019', 'Finger01_020', 'Finger1_021', 'Finger11_022')),
               ('L', ('UpperArm_08', 'Forearm_09', 'Hand_010', 'Finger0_011', 'Finger01_012', 'Finger1_013', 'Finger11_014'))) for k in ks]


def yuz(arm):
    """Yüzdeki noktalar (iskeletin içinde, duruşta): baş kemiğinden; ölçüler 0,23 m'lik başa göre (DM'de ölçüldü)."""
    b = arm.data.bones['bip Head_06']
    H = b.head_local.copy(); yuk = (b.tail_local - b.head_local); k = yuk.length / 0.23; yuk.normalize()
    on = Vector((0, -1, 0)); on = (on - yuk * on.dot(yuk)).normalized(); sag = on.cross(yuk).normalized()   # sag: karakterin sağı (−x)
    P = lambda o, y, s=0.0: H + on * o * k + yuk * y * k + sag * s * k
    return dict(cene=P(0.10, 0.01), burun=P(0.115, 0.105), kulak=P(0.0, 0.11, 0.085), alin=P(0.10, 0.17), on=on, yuk=yuk, sag=sag, k=k)


def ozel_tablo(arm, tur):
    """Karakterin ara sıra yaptığı hareket (kare tablosu). Eller 'IK' ile yüzdeki noktalara gider, parmaklar 'YON' ile hedefe bakar.
    tur: sakal (büyücü: sakalını sıvazlar), gozluk (DM: gözlüğünü iter, sonra notlarına eğilir), boyun (fighter: boynunu esnetir,
    parmaklarını çıtlatır), sac (kız garson: saçını kulağının arkasına atar), alin (oğlan garson: alnının terini siler)."""
    Y = yuz(arm); on, yuk, sag, k = Y['on'], Y['yuk'], Y['sag'], Y['k']
    t = lambda v: tuple(v)
    inis = [(SAG_EL, 'IK', t(Y['cene'] - yuk * 0.32 * k + on * 0.14 * k + sag * 0.10 * k))]   # dönüşte el önce göğsün önüne iner
                                                                    #   (yoksa kol yüzden dinlenmeye dönerken yana savruluyordu)
    def uzan(nokta, geri=0.13, ek=(), yan=0.0):
        """Sağ el noktaya: bilek altta ve önde (yan: karakterin sağına doğru; avuç yüzü kapatmasın), parmaklar noktaya bakar."""
        b = nokta - (yuk * 0.75 - on * 0.35 - sag * yan).normalized() * geri * k
        return [(SAG_EL, 'IK', t(b)), (SAG_EL, 'YON', t(nokta - b))] + list(ek)
    if tur == 'sakal':
        c = Y['cene']
        sv = lambda d: uzan(c - yuk * d * k, 0.12, [('bip Head_06', 'X', -5), ('bip Head_06', 'Z', -8)])
        return [(0, []), (16, sv(0.0)), (28, sv(0.07)), (38, sv(0.0)), (50, sv(0.08)), (60, sv(0.0)), (72, sv(0.08)),
                (86, inis + [('bip Head_06', 'Z', -4)]), (108, [])]
    if tur == 'gozluk':
        b = Y['burun']
        it = lambda d: uzan(b - on * d * k + yuk * d * 0.4 * k + sag * 0.012 * k, 0.15, [('bip Head_06', 'X', -6)], yan=0.9)
        egil = [('bip Spine1_04', 'X', 9), ('bip Head_06', 'X', 16)]
        return [(0, []), (14, it(0.03)), (22, it(0.0)), (30, it(0.0)), (40, it(0.04)), (48, inis), (58, []), (68, egil), (96, egil + [('bip Head_06', 'Z', 6)]),
                (114, [])]
    if tur == 'boyun':
        g = arm.data.bones['bip Spine1_04'].tail_local                  # göğsün üstü
        el2 = lambda d: [(SAG_EL, 'IK', t(g + on * (0.30 + d) * k - yuk * 0.16 * k - sag * 0.03 * k)),
                         (SOL_EL, 'IK', t(g + on * (0.30 + d) * k - yuk * 0.16 * k + sag * 0.03 * k)),
                         ('bip R Finger1_021', 'X', 40), ('bip L Finger1_013', 'X', 40)]
        return [(0, []), (14, [('bip Head_06', 'Y', 30)]), (24, [('bip Head_06', 'Y', 30)]), (40, [('bip Head_06', 'Y', -30)]),
                (50, [('bip Head_06', 'Y', -30)]), (62, [('bip Head_06', 'X', -6)]), (74, el2(0.0)), (82, el2(0.07) + [('bip Spine1_04', 'X', -4)]),
                (88, el2(0.03)), (94, el2(0.08) + [('bip Spine1_04', 'X', -4)]), (110, [])]
    if tur == 'sac':
        # 2026-10-30: el kulağın arkasına (0,04–0,06 geri) uzanınca dirsek ~175° katlanıyor, önkol iki karede 130° burulup
        # takla atıyordu (kullanıcı: "eli 360 atıyor"). Artık şakaktan kulağın üstüne kayar, bilek dışarıda (yan).
        q = Y['kulak']
        sv = lambda o, y, bas: uzan(q + on * o * k + yuk * y * k, 0.12, [('bip Head_06', 'Y', bas)], yan=0.7)
        return [(0, []), (14, sv(0.05, 0.03, -10)), (26, sv(0.01, 0.02, -12)), (34, sv(-0.01, -0.02, -8)), (46, inis), (60, []), (72, [])]
    if tur == 'alin':
        a = Y['alin']
        sil = lambda s: uzan(a + sag * s * k, 0.12, [('bip Head_06', 'X', -8)])
        return [(0, []), (14, sil(-0.06)), (26, sil(0.06)), (32, sil(0.07)), (42, inis + [('bip Head_06', 'X', -4)]), (58, []), (72, [])]
    raise ValueError(tur)


def bosta_kur(arm, tur):
    """nefes (döngü) ve ozel (bir kez) hareketleri; zar_at'tan sonra çağrılır (birak / sure değişmez)."""
    sure = arm.get('sure')
    hareket_kur(arm, 'nefes', NEFES, NEFES_KEMIK, None)
    if tur: hareket_kur(arm, 'ozel', ozel_tablo(arm, tur), OZEL_KEMIK, None)
    if sure is not None: arm['sure'] = sure


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
