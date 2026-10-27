# -*- coding: utf-8 -*-
"""
YENİ HAN — ORTAK ÖLÇÜLER (2026-10-21)
=====================================
Blockout (han_blockout_blender.py) ve ayrıntılı model (han_detay_blender.py) yerleşimi buradan okur: bir ölçüyü
burada değiştirince ikisi de değişir. Blockout 3. sürümü kullanıcı onayladı (2026-10-21).

İki çeşit koordinat:
  • PLAN koordinatı (X, Y): ana gövdenin güneybatı köşesi (0, 0); 1 birim = 1 m. Aşağıdaki sayılar bunu kullanır.
  • DÜNYA koordinatı (x, y): (0, 0) = oyun masasının merkezi (sitenin kamerası buraya bakar). w(X, Y) çevirir.
  x doğuya, y kuzeye, z yukarı. z = 0: salonun zemini. Yukarıdaki seviye +0,60, kürsü +0,30.
"""

W, H = 24.0, 16.0                 # ana gövdenin iç sınırı (girinti ve çıkıntı hariç)
DK = 0.25                         # duvar kalınlığı
DH = 7.0                          # salon duvarlarının yüksekliği (galeri olduğu için iki kat)
DIS_Z = -0.45                     # dışarıdaki toprak (sundurmadan 2 basamakla inilir)
UST_Z = 0.60                      # yukarıdaki seviye (3 basamak × 0,20)
BAS_D = 0.40                      # basamak derinliği

# Yukarıdaki seviyenin sınırı (aşağı salona bakan kenarı; basamaklar buradan aşağı iner):
KANAT_X = 7.0                     # batı kanadının doğu kenarı (kanat X 0…7, Y KANAT_Y0…H)
KANAT_Y0 = 4.0                    # kanadın güney kenarı (altında giriş bölümü)
BANT_Y = 11.5                     # kuzey bandının güney kenarı (bar burada)
KD_X, KD_Y = 19.5, 8.0            # kuzeydoğu uzantısının batı ve güney kenarı
KAVIS_R = 2.0                     # bant ile uzantının birleştiği köşedeki basamak kavisinin yarıçapı

MASA = (14.0, 5.4)                # oyun masasının merkezi = dünyanın (0, 0)'ı
KURSU_R, KURSU_H = 2.5, 0.30      # kürsü: üst yarıçap ve yükseklik; çevresinde bir basamak (0,15)
ORTA_R, ORTA_SANDALYE_R, ORTA_SANDALYE = 1.05, 1.65, 9
YAN_MASALAR = [(9.8, 8.6), (10.0, 2.4), (19.6, 4.6), (17.6, 1.6)]
YAN_R, YAN_SANDALYE_R = 0.75, 1.18

# Bar (kuzey duvarı boyunca, düz; yukarıdaki seviyede, galerinin altında)
BAR_X = (11.5, 21.3)              # tezgâhın X aralığı (tezgâh Y TEZ_Y…TEZ_Y+0,6)
TEZ_Y = 13.8
RAF_D, TEZGAH_H = 0.45, 1.05      # arka dolap: derinlik; üstünde iki açık raf ve şişeler
MUTFAK = (16.0, 17.2)             # mutfak kapısı (kuzey duvarında)
PANO_X = (7.5, 9.5)               # görev panosu (kuzey duvarında, barın batısında)

# Giriş bölümü (güneybatı girintisi): GIRIS_X0…KANAT_X × GIRIS_Y0…KANAT_Y0
GIRIS_X0, GIRIS_Y0 = 1.5, 0.8
GIRIS_H = 3.4                     # giriş bölümünün tavanı (tek katlı)
KAPI_Y = (1.4, 3.4)               # kemerli çift kanatlı dış kapı (giriş bölümünün batı duvarında)
GECIT_Y = 1.3                     # giriş bölümünden salona açıklık: Y GECIT_Y…KANAT_Y0 (X = KANAT_X'te)

# Şömine (batı kanadında, kuzey duvarında); önünde temiz bir oturma yeri, gerisinde uzun masa
SOMINE_X = (2.5, 5.5)
# Merdiven: doğu duvarı boyunca kuzeye, galerinin doğu ucuna çıkar; çıkınca karşıda bir oda kapısı
MERDIVEN_X0, MERDIVEN_Y0 = 22.7, 8.0
# Galeri: kuzey duvarı boyunca, GALERI_X0'dan doğu duvarına (şöminenin üstüne gelmez)
GALERI_X0, GALERI_Y0 = 8.6, 13.8
GALERI_Z = UST_Z + 3.2
ODA_KAPILARI = [9.6, 12.2, 14.8, 17.4, 20.1, 22.85]       # kapıların batı kenarı (1 m); sonuncusu merdivenin tepesinde
ARALIK = {0: 35, 3: 25}                                   # aralık duran kapılar: sıra → açı (derece)

CIKINTI = (4.2, 3.0, 4.5)         # doğudaki yarım daire: merkez Y'si (X = W), yarıçapı, duvar yüksekliği
SAHNE_H = 0.30                    # ozan sahnesi: çıkıntının tamamını kaplar, önünde bir basamak

PENCERE_Z = (0.9, 2.4)
PENCERE_GUNEY = [(9.0, 10.4), (13.0, 14.4), (17.0, 18.4), (21.0, 22.4)]
PENCERE_KANAT = [(5.0, 6.4)]      # kanadın batı duvarında
PENCERE_DOGU_UST = (9.0, 10.6)    # doğu duvarında, galeri hizasında (Y aralığı)
PENCERE_CIKINTI = (2, 5, 9)       # çıkıntının 12 yay diliminden pencereli olanlar

# Sitenin eğik kamerası (index.html'deki TAV.yon, TAV.egim ve kesit yüksekliği TAV.kesik ile aynı)
YON, EGIM, KESIK = 30, 45, 0.95


def w(X, Y):
    """PLAN koordinatından DÜNYA koordinatına."""
    return X - MASA[0], Y - MASA[1]


def seviye(X, Y):
    """Bir noktanın zemin yüksekliği (yukarıdaki seviye mi, salon mu)."""
    return UST_Z if (X < KANAT_X and Y > KANAT_Y0) or Y > BANT_Y or (X > KD_X and Y > KD_Y) else 0.0
