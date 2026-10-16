# Macentayı saydamlığa çevirir (POV elleriyle aynı yöntem): "ne kadar pembe" ölçüsünden saydamlık, renk ayrıştırma,
# kenardaki pembe tonun temizlenmesi; strong=True ise (hareket bulanıklığı) pembe-mor-bordo tonlar kahveye çekilir.
import numpy as np
from PIL import Image

def key_out(im, strong=False):
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    c = np.concatenate([a[:40, :40].reshape(-1, 3), a[:40, -40:].reshape(-1, 3)])
    K = np.median(c, axis=0)
    Kd = min(K[0] - K[1], K[2] - K[1])
    d = np.minimum(a[..., 0] - a[..., 1], a[..., 2] - a[..., 1])
    t0 = 12.0
    alpha = np.clip((Kd - d) / (Kd - t0), 0, 1)
    alpha[alpha < 0.03] = 0
    alpha[alpha > 0.985] = 1
    al = np.maximum(alpha, 1e-3)[..., None]
    F = np.clip((a - (1 - alpha[..., None]) * K) / al, 0, 255)
    m = np.clip(np.minimum(F[..., 0] - F[..., 1], F[..., 2] - F[..., 1]), 0, None)[..., None]
    F[..., 0:1] -= m; F[..., 2:3] -= m
    semi = (alpha > 0) & (alpha < 0.97)
    w = np.clip((1 - alpha) * 1.6, 0, 1)
    R, G, B = F[..., 0], F[..., 1], F[..., 2]
    B2 = np.minimum(B, G); R2 = np.minimum(R, G + 45 * (1 - w))
    Y = 0.3 * R2 + 0.59 * G + 0.11 * B2
    warm = np.dstack([Y * 1.08, Y, Y * 0.86])
    clean = np.dstack([R2, G, B2]) * (1 - w[..., None] * 0.7) + warm * (w[..., None] * 0.7)
    F = np.where(semi[..., None], clean, F)
    if strong:
        R, G, B = F[..., 0], F[..., 1], F[..., 2]
        mx, mn = F.max(axis=2), F.min(axis=2)
        sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-3), 0)
        hue = (np.degrees(np.arctan2(np.sqrt(3) * (G - B), 2 * R - G - B)) + 360) % 360
        dist = np.minimum(np.abs(hue - 330), 360 - np.abs(hue - 330))
        wt = np.clip((48 - dist) / 30, 0, 1) * np.clip(sat * 3, 0, 1) * (alpha < 0.999)   # yalnızca yarı saydam iz
        Y = 0.3 * R + 0.59 * G + 0.11 * B
        brown = np.dstack([Y * 1.18, Y * 0.97, Y * 0.78])
        F = F * (1 - wt[..., None]) + brown * wt[..., None]
    F[alpha == 0] = 0
    return Image.fromarray(np.dstack([np.clip(F, 0, 255), alpha * 255]).astype(np.uint8), 'RGBA')
