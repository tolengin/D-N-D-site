# Nano Banana referansları (2. yöntem): masa/ figürü ile ham görsel arasındaki dönüşüm (ölçek + dönüş + kayma)
# ayırt edici noktalar (SIFT) eşleştirilerek bulunur. Sonra ham görsel bu dönüşümle masa/ çerçevesine, ama
# yüksek çözünürlükte (ölçek kadar büyük) çevrilir ve masa/ figürünün kesim maskesi büyütülerek uygulanır.
# Orijinal dosyalara yazılmaz; çıktı yalnızca gorseller/tekli/.
import os, sys, json
import numpy as np
import cv2
from PIL import Image, ImageFilter

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # proje klasörü (araclar/ bir üstü)
OUT = os.path.join(SITE, 'gorseller', 'tekli')
os.makedirs(OUT, exist_ok=True)
CLASSES = ['barbarian', 'bard', 'cleric', 'druid', 'fighter', 'monk', 'paladin', 'ranger', 'rogue', 'sorcerer', 'warlock', 'wizard', 'sinifsiz']
JOBS = []
for c in CLASSES:
    JOBS.append((f'{c}-f', c, f'{c}-kadin'))
    JOBS.append((f'{c}-m', c, f'{c}-erkek'))
JOBS += [('dm', 'dm', 'dm'), ('garson-dolu', 'garson', 'garson-dolu'), ('garson-bos', 'garson', 'garson-bos')]
only = sys.argv[1:]
sift = cv2.SIFT_create(nfeatures=6000)

def estimate(tpl_rgba, raw_rgb):
    t = np.asarray(tpl_rgba); a = t[..., 3]
    tg = cv2.cvtColor(np.ascontiguousarray(t[..., :3]), cv2.COLOR_RGB2GRAY)
    tg = cv2.resize(tg, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)   # küçük şablonda daha çok nokta
    am = cv2.resize((a > 200).astype(np.uint8) * 255, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    rg = cv2.cvtColor(raw_rgb, cv2.COLOR_RGB2GRAY)
    k1, d1 = sift.detectAndCompute(tg, am)
    k2, d2 = sift.detectAndCompute(rg, None)
    m = cv2.BFMatcher().knnMatch(d1, d2, k=2)
    good = [p[0] for p in m if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]
    src = np.float32([k1[g.queryIdx].pt for g in good]) / 2                # masa pikseli
    dst = np.float32([k2[g.trainIdx].pt for g in good])                    # ham piksel
    M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=6)
    return M, int(inl.sum()) if inl is not None else 0, len(good)

report = []
for key, rawname, outname in JOBS:
    if only and outname not in only: continue
    tpl = Image.open(os.path.join(SITE, 'masa', key + '.webp')).convert('RGBA')
    raw_im = Image.open(os.path.join(SITE, 'gorseller', rawname + '.jpg')).convert('RGB')
    raw = np.asarray(raw_im)
    M, ninl, ngood = estimate(tpl, raw)
    s = float(np.hypot(M[0, 0], M[1, 0])); ang = float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
    # masa çerçevesini s kat büyüterek ham görselden örnekle: hedef (u,v) -> masa (u/s, v/s) -> ham M·(u/s, v/s)
    tw, th = tpl.size
    W, H = int(round(tw * s)), int(round(th * s))
    A = M.copy(); A[:, :2] = M[:, :2] / s                                   # hedef pikselden ham piksele
    hi = cv2.warpAffine(raw, A, (W, H), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 0, 255))
    # Benzerlik: yüksek çözünürlüklü sonucu masa boyutuna küçültüp masa/ figürüyle karşılaştır (yalnızca figürün içi)
    lo = cv2.resize(hi, (tw, th), interpolation=cv2.INTER_AREA).astype(np.float32)
    tt = np.asarray(tpl).astype(np.float32); mk = tt[..., 3] > 200
    diff = np.abs(lo - tt[..., :3])[mk].mean()
    # Kesim maskesi: masa/ saydamlığı büyütülür; kenar yarım piksel içeri çekilir ki ham zeminin rengi sızmasın
    a = tpl.getchannel('A').filter(ImageFilter.MinFilter(3)).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(max(0.6, s * 0.3)))
    fig = Image.fromarray(hi)
    bb = a.point(lambda v: 255 if v > 8 else 0).getbbox()                   # figürün kendi sınırı (masa tuvalindeki boşluk atılır)
    fig, a = fig.crop(bb), a.crop(bb)
    W, H = fig.size
    side = int(max(W, H) * 1.16)                                            # kare tuval, çevrede ~%8 boşluk; figür küçültülmez
    canvas = Image.new('RGB', (side, side), (255, 0, 255))
    canvas.paste(fig, ((side - W) // 2, (side - H) // 2), a)
    p = os.path.join(OUT, outname + '.jpg')
    canvas.save(p, 'JPEG', quality=95, subsampling=0)
    cx = M[0, 2] + M[0, 0] * tw / 2 + M[0, 1] * th / 2
    half = 'tek' if rawname == 'dm' else ('sol' if cx < raw_im.width / 2 else 'sağ')
    report.append(dict(dosya=outname + '.jpg', kaynak=rawname + '.jpg', yari=half, olcek=round(s, 3), donus=round(ang, 2),
                       nokta=ninl, ort_fark=round(float(diff), 1), boyut=side, kb=os.path.getsize(p) // 1024))
    print(f'{outname:16s} <- {rawname}.jpg {half:4s} ölçek {s:.3f} dönüş {ang:+.2f}° nokta {ninl}/{ngood} ort.renk farkı {diff:5.1f}  tuval {side}  {report[-1]["kb"]} KB')
json.dump(report, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tekli-rapor.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
