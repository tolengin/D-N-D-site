"""buyuler_ham.json + araclar/buyu/tr.json -> sitenin masa/buyuler.js dosyası (SRD 5.2.1 büyüleri, Türkçe açıklamalar; 2026-11-12).
Türkçe ad ve açıklamalar tr.json'da (kendi sözlerimiz); değiştirmek için orayı düzelt, bu betiği yeniden çalıştır.
Çalıştır: python -I -X utf8 araclar/buyu_yaz.py <buyuler_ham.json> masa/buyuler.js (ham dosyayı buyu_ayikla.py üretir)"""
import json, re, sys, pathlib
D = pathlib.Path(__file__).parent
B = json.load(open(sys.argv[1], encoding='utf-8'))
T = json.load(open(D / 'buyu' / 'tr.json', encoding='utf-8'))
OKUL = {'Abjuration': 'abj', 'Conjuration': 'con', 'Divination': 'div', 'Enchantment': 'enc', 'Evocation': 'evo', 'Illusion': 'ill', 'Necromancy': 'nec', 'Transmutation': 'tra'}
SINIF = {'Bard': 'B', 'Cleric': 'C', 'Druid': 'D', 'Paladin': 'P', 'Ranger': 'R', 'Sorcerer': 'S', 'Warlock': 'W', 'Wizard': 'Z'}
AB = {'Strength': 'str', 'Dexterity': 'dex', 'Constitution': 'con', 'Intelligence': 'int', 'Wisdom': 'wis', 'Charisma': 'cha'}
HT = 'Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder'
OZEL_SURE = {
    'Bonus Action, which you take immediately after hitting a target with a Melee weapon or an Unarmed Strike': 'Bonus eylem (yakından vurunca)',
    'Bonus Action, which you take immediately after hitting a creature with a Melee weapon or an Unarmed Strike': 'Bonus eylem (yakından vurunca)',
    'Bonus Action, which you take immediately after hitting a creature with a weapon': 'Bonus eylem (silahla vurunca)',
    'Reaction, which you take when you see a creature within 60 feet of yourself casting a spell with Verbal, Somatic, or Material components': 'Tepki (biri büyü yaparken)',
    'Reaction, which you take when you or a creature you can see within 60 feet of you falls': 'Tepki (biri düşerken)',
    'Reaction, which you take in response to taking damage from a creature that you can see within 60 feet of yourself': 'Tepki (hasar alınca)',
    'Reaction, which you take when you are hit by an attack roll or targeted by the Magic Missile spell': 'Tepki (saldırı isabet edince)',
    'Action (Overgrowth) or 8 hours (Enrichment)': 'Eylem ya da 8 saat',
}
def birim(s):
    s = re.sub(r'\b(\d+) rounds?\b', r'\1 tur', s)
    s = re.sub(r'\b(\d+) minutes?\b', r'\1 dakika', s)
    s = re.sub(r'\b(\d+) hours?\b', r'\1 saat', s)
    s = re.sub(r'\b(\d+) days?\b', r'\1 gün', s)
    return s
def sure(s):
    r = s.endswith(' or Ritual')
    if r: s = s[:-len(' or Ritual')]
    if s in OZEL_SURE: return OZEL_SURE[s], r
    s = {'Action': 'Eylem', 'Bonus Action': 'Bonus eylem', 'Reaction': 'Tepki'}.get(s, s)
    return birim(s), r
def menzil(s):
    s = {'Self': 'Kendin', 'Touch': 'Dokunma', 'Sight': 'Görüş', 'Special': 'Özel', 'Unlimited': 'Sınırsız'}.get(s, s)
    s = re.sub(r'\b(\d[\d,]*) feet\b', r'\1 ft', s)
    s = re.sub(r'\b(\d+) miles?\b', r'\1 mil', s)
    return s
def dur(s):
    c = s.startswith('Concentration')
    s = re.sub(r'^Concentration,? +up to +', 'en çok ', s)
    s = {'Instantaneous': 'Anında', 'Until dispelled': 'Bozulana dek', 'Until dispelled or triggered': 'Bozulana ya da tetiklenene dek', 'Special': 'Özel'}.get(s, s)
    s = re.sub(r'^Up to ', 'en çok ', s)
    return birim(s), c
out = []
for b in B:
    ad = b['ad'].replace('’', "'")
    tr = T[ad]
    sr, r = sure(b['sure'])
    du, c = dur(b['dur'])
    bil = b['bil'].replace('’', "'")
    mat = ''
    m = re.search(r'M \((.*)\)\s*$', bil)
    if m: mat = re.sub(r' - ', '', m.group(1)).replace('materi - als', 'materials')
    t = b['metin']
    ust = re.search(r'(Using a Higher-Level Spell Slot\.|Cantrip Upgrade\.)(.*)', t, re.S)
    ana = t[:ust.start()] if ust else t
    o = {'a': ad, 't': tr[0], 's': b['sv'], 'o': OKUL[b['okul']], 'k': ''.join(SINIF[x] for x in b['sinif']),
         'sr': sr, 'mz': menzil(b['menzil']), 'b': re.sub(r'\s*\(.*', '', bil).replace(' ', ''), 'd': du, 'x': tr[1]}
    if c: o['c'] = 1
    if r: o['r'] = 1
    if mat: o['m'] = mat
    if re.search(r'worth|consumes', mat): o['mp'] = 1                    # değerli / tükenen malzeme
    sv = re.search(r'(' + '|'.join(AB) + r') saving throw', ana)
    if sv: o['sv'] = AB[sv.group(1)]
    if re.search(r'melee spell attack', ana, re.I): o['at'] = 'y'
    elif re.search(r'ranged spell attack', ana, re.I): o['at'] = 'u'
    h = []
    for m in re.finditer(r'(\d+d\d+(?: ?\+ ?\d+)?) (' + HT + r') damage', ana):
        v = m.group(1).replace(' ', '') + ' ' + m.group(2).lower()
        if v not in h: h.append(v)
    for m in re.finditer(r'(' + HT + r') damage equal to (\d+d\d+) plus your spellcasting ability modifier', ana):
        v = m.group(2) + '+mod ' + m.group(1).lower()
        if v not in h: h.insert(0, v)
    if h: o['h'] = ' + '.join(h[:2])
    iy = re.search(r'regains?(?: a number of)? Hit Points equal to (\d+d\d+) plus your spellcasting ability modifier', ana)
    if iy: o['iy'] = iy.group(1) + '+mod'
    if ust:
        u = ust.group(2)
        m = re.search(r'increases? by (\d+d\d+) for (?:each|every) (?:spell )?slot level above', u)
        if m and b['sv'] > 0: o['up'] = '+' + m.group(1)
    out.append(o)
satir = ',\n'.join(json.dumps(o, ensure_ascii=False, separators=(',', ':')) for o in out)
js = ('/* SRD 5.2.1 büyüleri (Wizards of the Coast, CC-BY-4.0; 2024 kuralları). 339 büyü.\n'
      '   Ad, seviye, okul, sınıflar, süre, menzil, bileşen ve süre SRD\'den; açıklamalar kendi Türkçe sözlerimizle kısaltıldı.\n'
      '   Elle değiştirilmez: araclar/buyu_yaz.py üretir (2026-11-12).\n'
      '   a: İngilizce ad · t: Türkçe ad · s: seviye (0 = cantrip) · o: okul · k: sınıflar (B Bard, C Cleric, D Druid, P Paladin,\n'
      '   R Ranger, S Sorcerer, W Warlock, Z Wizard) · sr: yapılış süresi · mz: menzil · b: bileşenler · d: süre · c: konsantrasyon\n'
      '   r: ritüel · m: malzeme (SRD metni) · mp: değerli ya da tükenen malzeme · x: açıklama · sv: kurtarma zarı · at: büyü saldırısı\n'
      '   (y yakın, u menzilli) · h: hasar · iy: iyileştirme · up: üst yuvada seviye başına eklenen zar */\n'
      'window.SRD_BUYU = [\n' + satir + '\n];\n')
p = pathlib.Path(sys.argv[2])
p.write_bytes(js.encode('utf-8'))
print(len(out), 'büyü,', len(js.encode('utf-8')), 'bayt')
