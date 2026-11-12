"""SRD 5.2.1 metninden (pypdf ile çıkarılmış .txt, sayfa başlarında "=== SAYFA n ===") büyüleri ayıklar -> buyuler_ham.json (2026-11-12).
Ad: sınıf listelerindeki doğru yazım (PDF'te bazı adlar küçük-büyük harf karışık). Sınıflar: büyünün kendi başlığı (SRD tablolarında
Phantasmal Force ve Sorcerer'da Mind Spike eksik). Çalıştır: python -I -X utf8 araclar/buyu_ayikla.py srd521.txt buyuler_ham.json"""
import re, json, pathlib, sys
GIR, CIK = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
T = GIR.read_text(encoding='utf-8').split('\n')
# sayfa başlıklarını at
temiz = []
i = 0
while i < len(T):
    s = T[i]
    if s.startswith('=== SAYFA'):
        i += 1
        if i < len(T) and T[i].startswith('System Reference Document'): i += 1
        if i < len(T) and T[i].strip().isdigit(): i += 1
        continue
    temiz.append(s); i += 1
T = temiz

# 1) Sınıf listeleri (tablolar) -> doğru adlar
OKUL = 'Abjuration|Conjuration|Divination|Enchantment|Evocation|Illusion|Necromancy|Transmutation'
dogru = {}
sinif_liste = {}
bas = None
for s in T:
    m = re.match(r'^(?:Cantrips \(Level 0 (\w+) Spells\)|Level (\d) (\w+) Spells)$', s.strip())
    if m:
        if m.group(1): bas = (m.group(1), 0)
        else: bas = (m.group(3), int(m.group(2)))
        continue
    if bas:
        m2 = re.match(r'^(.+) (' + OKUL + r') ([—–CRM, ]+)$', s.strip())
        if m2 and m2.group(1) != 'Spell':
            ad = m2.group(1).strip()
            dogru[ad.lower()] = ad
            sinif_liste.setdefault(bas[0], {}).setdefault(ad, bas[1])
        elif s.strip() in ('Spell School Special',):
            pass
        elif not m2 and s.strip() and not s.strip().startswith('Spell School'):
            bas = None

# 2) Açıklamalar
bas_i = T.index('Spell Descriptions')
son_i = T.index('Rules Glossary', bas_i)
B = T[bas_i + 1:son_i]
kafa = re.compile(r'^(?:Level (\d) (' + OKUL + r')|(' + OKUL + r') Cantrip) \((.*)$')
buyuler = []
j = 0
while j < len(B):
    m = kafa.match(B[j].strip())
    if m and j > 0:
        ad_ham = B[j - 1].strip()
        sin = m.group(4)
        k = j
        while ')' not in sin:
            k += 1; sin += ' ' + B[k].strip()
        sin = sin.split(')')[0]
        b = {'ad': dogru.get(ad_ham.lower(), ad_ham), 'sv': int(m.group(1)) if m.group(1) else 0,
             'okul': m.group(2) or m.group(3), 'sinif': [x.strip() for x in sin.split(',') if x.strip()], 'i': j, 'k': k}
        buyuler.append(b)
        j = k + 1; continue
    j += 1
for n, b in enumerate(buyuler):
    son = buyuler[n + 1]['i'] - 1 if n + 1 < len(buyuler) else len(B)
    sat = B[b['k'] + 1:son]
    alan = {}
    metin = []
    cur = None
    for s in sat:
        m = re.match(r'^(Casting Time|Range|Components?|Duration): (.*)$', s.strip())
        if m and len(metin) == 0:
            cur = m.group(1).replace('Component', 'Components').replace('Componentss', 'Components'); alan[cur] = m.group(2).strip(); continue
        if cur and cur != 'Duration' and 'Duration' not in alan:
            a = alan[cur]
            alan[cur] = (a[:-2] + s.strip()) if a.endswith(' -') else (a + ' ' + s.strip()); continue
        if cur == 'Duration' and not metin and alan.get('Duration', '').endswith(','):
            alan[cur] += ' ' + s.strip(); continue
        metin.append(s)
    tx = ''
    for s in metin:
        s = s.rstrip()
        if s.startswith(' '): tx += '\n' + s.strip()
        elif tx.endswith('-') and not tx.endswith(' -'): tx = tx[:-1] + s
        elif tx.endswith(' -'): tx = tx[:-2] + s
        else: tx += (' ' if tx and not tx.endswith('\n') else '') + s
    tx = re.sub(r'[ \t]+', ' ', tx).strip()
    b['sure'] = alan.get('Casting Time', ''); b['menzil'] = alan.get('Range', '')
    b['bil'] = alan.get('Components', ''); b['dur'] = alan.get('Duration', '')
    b['metin'] = tx
    del b['i'], b['k']

# kontrol: sınıf listeleriyle karşılaştır
adlar = {b['ad'] for b in buyuler}
eksik = [a for a in dogru.values() if a not in adlar]
print(len(buyuler), 'büyü; tabloda olup açıklamada olmayan:', eksik, file=sys.stderr)
for c, l in sinif_liste.items():
    for a, sv in l.items():
        b = next((x for x in buyuler if x['ad'] == a), None)
        if not b: continue
        if c not in b['sinif']: print('sınıf farkı', c, a, b['sinif'], file=sys.stderr)
        if b['sv'] != sv: print('seviye farkı', c, a, sv, b['sv'], file=sys.stderr)
for b in buyuler:
    for c in b['sinif']:
        if b['ad'] not in sinif_liste.get(c, {}): print('tabloda yok', c, b['ad'], file=sys.stderr)
CIK.write_text(json.dumps(buyuler, ensure_ascii=False, indent=0), encoding='utf-8')
