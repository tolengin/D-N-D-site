# -*- coding: utf-8 -*-
"""
IZGARALI ÖNİZLEME, ÇİZİM KISMI (2026-11-26; araclar/izgara_blender.py'nin çizdiklerine ızgara ve sayılar ekler, Pillow).
  python araclar/izgara_ciz.py <onek>        → <onek>-<bölge>.png (önden, yandan, arkadan yan yana)
"""
import sys, json, math
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype('arial.ttf', 18)
J = json.load(open(sys.argv[1] + '-izgara.json')); st = J['adim']
gruplar = {}
for b in J['bilgi']:
    im = Image.open(b['yol']).convert('RGB'); dr = ImageDraw.Draw(im)
    u0, u1, z0, z1, isaret = b['u0'], b['u1'], b['z0'], b['z1'], b['isaret']
    W, H = im.size; s = W / (u1 - u0)
    X = lambda u: ((u - u0) if isaret > 0 else (u1 - u)) * s
    Z = lambda z: (z1 - z) * s
    k = math.ceil(u0 / st - 1e-9)
    while k * st <= u1 + 1e-9:
        u = k * st; x = X(u)
        dr.line([(x, 0), (x, H)], fill=(255, 70, 70) if abs(u) < 1e-9 else (70, 70, 70))
        if k % 2 == 0: dr.text((x + 2, 2), f'{u:+.2f}', fill=(255, 255, 0), font=F)
        k += 1
    k = math.ceil(z0 / st - 1e-9)
    while k * st <= z1 + 1e-9:
        z = k * st; y = Z(z)
        dr.line([(0, y), (W, y)], fill=(70, 70, 70))
        if k % 2 == 0: dr.text((2, y + 1), f'{z:.2f}', fill=(0, 255, 255), font=F)
        k += 1
    dr.text((W // 2 - 40, H - 24), b['yon'] + (' +x>' if b['yon'] == 'on' else ' +y>' if b['yon'] == 'yan' else ' -x>'), fill=(255, 140, 0), font=F)
    gruplar.setdefault(b['ad'], []).append(im)
for ad, ps in gruplar.items():
    T = Image.new('RGB', (sum(p.width for p in ps) + 20, max(p.height for p in ps)), (30, 30, 30))
    x = 0
    for p in ps: T.paste(p, (x, 0)); x += p.width + 10
    T.save(f'{sys.argv[1]}-{ad}.png'); print(ad, T.size)
