# Önden figürler (gorseller/on) -> masa/<ad>-on.webp: macenta silinir, figüre bağlı olmayan parçalar (DM'in havadaki kitap kapağı,
# garsonun tepsisi yanındaki bulanık iz) atılır, hepsi aynı tuvale konur ve alt kesimleri aynı çizgiye oturur.
# Ayrıca panoramalar (pov-kuzey, pov-guney) 16:9 webp'ye çevrilir. Orijinallere yazılmaz.
import os, glob, sys
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keyout import key_out

SITE = r'C:\Users\PC\Desktop\DnD-dort element-site'
SRC, DST = os.path.join(SITE, 'gorseller', 'on'), os.path.join(SITE, 'masa')
OUTW = 640                                          # son tuval genişliği (piksel)
ascii_name = lambda n: n.replace('ı', 'i').replace('İ', 'I')

# 1) Panoramalar: 2752x1536 -> iki yandan kırpılıp tam 16:9, 1920x1080
for n in ['pov-kuzey', 'pov-guney']:
    p = os.path.join(SITE, 'gorseller', n + '.jpg')
    if not os.path.exists(p): print(n, 'YOK'); continue
    im = Image.open(p).convert('RGB')
    w = round(im.height * 16 / 9); l = (im.width - w) // 2
    im.crop((l, 0, l + w, im.height)).resize((1920, 1080), Image.LANCZOS).save(os.path.join(DST, n + '.webp'), 'WEBP', quality=82, method=6)
    print(n, os.path.getsize(os.path.join(DST, n + '.webp')) // 1024, 'KB  kırpma', l)

# 2) Önden figürler
figs = {}
for f in sorted(glob.glob(os.path.join(SRC, '*.jpg'))):
    name = ascii_name(os.path.basename(f)[:-4])
    src = Image.open(f).convert('RGB')
    im = key_out(src, strong=name.startswith('garson-dolu'))
    a = np.asarray(im).copy()
    A = a[..., 3]
    # İçeriyi koru: mor ve eflatun kumaşlar (bard, warlock) macentaya yakın olduğu için yarı saydam sayılıyordu.
    # Saf zeminden 6 pikselden fazla içeride kalan ve çoğunlukla opak olan pikseller tam opak olur ve özgün rengine döner;
    # macenta temizliği yalnızca dış kenar şeridinde çalışır.
    # (kenar sayılan yer: yarıdan saydam bir piksele 10 pikselden yakın her şey; saç telleri gibi ince yerler de kenarda kalır)
    sure_bg = (A < 100).astype(np.uint8)
    dist = cv2.distanceTransform(1 - sure_bg, cv2.DIST_L2, 5)
    inner = dist > 10
    fix = inner & (A > 140)
    a[fix, :3] = np.asarray(src)[fix]; A[fix] = 255
    if name.startswith('garson-dolu'):
        A[inner & (A < 150)] = 0                                        # tepsi yanındaki bulanık izden kalan soluk şerit
    # figüre bağlı olmayan parçaları at: en büyük parçaya değmeyen her şey (biraz genişletilmiş maskeyle bakılır ki saç teli gibi ince bağlar kopmasın)
    solid = (A > 20).astype(np.uint8)
    grown = cv2.dilate(solid, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(grown, 8)
    keep = 1 + int(np.argmax(st[1:, 4]))
    removed = int(((lab != keep) & (solid > 0)).sum())
    A[lab != keep] = 0
    # tuvalin alt kenarındaki zayıf saydamlık (zemin geçişi) atılır
    A[A < 40] = 0
    rows = np.where((A > 128).sum(1) > 50)[0]
    base = int(rows.max())                                              # alt kesim: son dolu satır
    ys, xs = np.where(A > 0)
    top, left, right = int(ys.min()), int(xs.min()), int(xs.max())
    A[base + 1:] = 0                                                    # alt kesimin altında kalan kırıntılar
    figs[name] = dict(img=Image.fromarray(a, 'RGBA'), base=base, top=top, left=left, right=right, removed=removed)
    print(f'{name:22s} alt kesim {base}  üst {top}  sol-sağ {left}-{right}  atılan ayrı parça {removed} px')

# ortak tuval: en yüksek figür + en geniş figür, yatayda figürün kutusu ortalanır, alt kesim aynı çizgide
H = max(v['base'] - v['top'] for v in figs.values()) + 1
W = max(v['right'] - v['left'] for v in figs.values()) + 1
pad = int(W * 0.02)
CW, CH = W + 2 * pad, H + pad
k = OUTW / CW
print('ortak tuval', CW, 'x', CH, '-> ', OUTW, 'x', round(CH * k), '  alt çizgi tuvalin', CH - 1, 'satırında (en altta)')
for name, v in figs.items():
    canvas = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    cx = (v['left'] + v['right']) / 2
    ox = int(round(CW / 2 - cx)); oy = (CH - 1) - v['base']
    canvas.paste(v['img'], (ox, oy), v['img'])
    out = canvas.convert('RGBa').resize((OUTW, round(CH * k)), Image.LANCZOS).convert('RGBA')
    if name == 'garson-dolu-on':
        # Tepsinin sağ altında, elbiseye değen ve bu yüzden ayrı parça sayılmayan bulanık iz: mor tonlu pikseller ve
        # çevreleri (12 px) silinir; yalnızca elbisenin dışında (yüzde 61'den sağda) ve tepsinin altında (yüzde 64'ten aşağıda).
        o = np.asarray(out).copy(); R, G, B, Al = [o[..., i].astype(int) for i in range(4)]
        pur = ((R - G > 18) & (B - G > 18) & (Al > 0)).astype(np.uint8)
        zone = np.zeros_like(pur); zone[int(o.shape[0] * .64):, int(o.shape[1] * .61):] = 1
        kill = cv2.dilate(pur * zone, np.ones((25, 25), np.uint8)) & zone
        o[kill > 0, 3] = 0
        print('garson-dolu: silinen iz pikseli', int(kill.sum()))
        out = Image.fromarray(o, 'RGBA')
    p = os.path.join(DST, name + '.webp')
    q = 84
    while True:
        out.save(p, 'WEBP', quality=q, method=6, alpha_quality=85)
        if os.path.getsize(p) < 70 * 1024 or q <= 60: break
        q -= 6
    print(f'{name + ".webp":28s} {out.size[0]}x{out.size[1]}  {os.path.getsize(p) // 1024} KB  kalite {q}')
