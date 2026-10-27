# -*- coding: utf-8 -*-
"""
MASA GÖRÜNÜMÜ TEST DÜZENEĞİ (siteye yüklenmez)
index.html'in bir kopyasını (araclar/test/test.html) sahte bir DM ve oyuncularla açılacak şekilde hazırlar.
Asıl siteye dokunmaz. Görünmez Edge ile fotoğraf çekmek için:
  powershell -File araclar\\test\\dene.ps1 -out d.png                       (5 kişi, yakın bakış)
  powershell -File araclar\\test\\dene.ps1 -out d.png -n 9 -extra "&all=1"  (9 kişi, bütün taverna)
  powershell -File araclar\\test\\dene.ps1 -cfg '{"seatR":1.7}'             (çizilmiş taverna ayarlarını denemek: TAV'a eklenir)
Adresin # kısmı: n (kişi sayısı, DM dahil), solo=1 (masaya bağlı değil, tek başına), all=1, s/x/y (görünüm), dbg=1 (koltuk listesi), nolog=1, cfg.
cdp.ps1 adım adım komut da çalıştırır: -steps @('wait:800', "js:TT.showRoll({...},{})", 'shot:zar.png')
"""
import sys, pathlib
KOK = pathlib.Path(__file__).resolve().parents[2]            # proje klasörü (araclar/test'in iki üstü)
OUT = pathlib.Path(sys.argv[0]).parent / 'test.html'
s = (KOK / 'index.html').read_text(encoding='utf-8')
s = s.replace('<head>', '<head>\n<base href="../../">', 1)          # göreli: dosyadan da, http sunucusundan da proje köküne gider
snip = r'''
;(function(){
  const q = new URLSearchParams(location.hash.slice(1));
  const N = +q.get('n') || 4;
  const log = document.createElement('pre'); log.id = 'testlog';
  log.style.cssText = 'position:fixed;left:30vw;top:0;z-index:99999;color:#0f0;background:#000c;font:12px monospace;margin:0;max-width:70vw;white-space:pre-wrap';
  if (q.get('nolog')) log.style.display = 'none';
  document.body.appendChild(log);
  const L = m => { log.textContent += m + '\n'; };
  window.addEventListener('error', e => L('HATA: ' + e.message + ' @' + e.lineno));
  window.addEventListener('unhandledrejection', e => L('PROMISE: ' + (e.reason && (e.reason.stack || e.reason.message) || e.reason)));
  const ow = console.warn; console.warn = (...a) => { L('WARN: ' + a.map(x => x && x.stack || String(x)).join(' ')); ow(...a); };
  const oe = console.error; console.error = (...a) => { L('ERR: ' + a.map(x => x && x.stack || String(x)).join(' ')); oe(...a); };
  if (q.get('cfg')) Object.assign(TAV, JSON.parse(q.get('cfg')));
  window.TT = { meSeat, renderMe, tvLayout, olAc, showRoll, stopNet, tavOverview, tavSetView, tavMasaBakis, tavTepe, tavSoloKoltuk, tavZoom, tav, tavKolAt, tavKolVar, zarVitrin, zarSekil, zarAt3, zarSon, zarMasa, renderTable, net, store, setMode, setNet, renderNetUI, playerReceive, showChar, SES, ses, sesBaslat, sesAyar, sesSeviye, sesDisari, acilisGoster, SAVAS, npcler, hedefUI, hasarAl, koltukAc, renderNpcs, savasBaslat, siraIleri, savasBitir, renderSira, renderDus, dmReceive, siraAl, rollExpr, rollD20, rollDeath, hasarBekle, renderBekleyen, ACTIONS, buyutUI, povGoster, ustUI, tavKick, svRender, SV, npcHazir: k => ACTIONS["npc-hazir"]({dataset:{k}}), get C() { return C; }, get mode() { return mode; } };
  store.tavCanli = q.get('canli') === '1';                 // görünmez Edge'de ekran kartı yok: sürekli çizim çok yavaş (canli=1 ile açılır)
  if (q.get('goz') === '0') store.tavGoz = false;
  store.welcomed = true;
  if (!q.get('acilis')) { $('#acilis').hidden = true; sesDisari(20000, 1, 0, 0); }   // açılış perdesi fotoğrafları kapatmasın (acilis=1 ile görünür)
  const solo = !!q.get('solo');                            // solo=1: masaya bağlı değil, tek başına (ana ekran)
  if (solo) stopNet(true);                                 // önceki denemeden kalan masa kaydını sil (test profili localStorage'ı hatırlar)
  else { store.net.role = 'dm'; store.net.name = 'Usta'; store.net.code = 'ABCDEF'; net.status = 'open'; }
  const cls = ['fighter','wizard','cleric','rogue','bard','druid','barbarian','ranger'];
  for (let i = 0; !solo && i < N - 1; i++) net.players.set('p' + i, { pid: 'p' + i, name: 'Oyuncu ' + (i + 1), seat: 'sabcd' + i, char: normalize({ name: 'Kahraman ' + (i + 1), cls: cls[i], look: i % 2 ? 'f' : 'm', hp: { cur: 10, max: 12 } }), online: true, face: '' });   // normalize: gerçek kağıt gibi eksik alanlar tamamlanır (yoksa DM ekranı çöker)
  setMode('table');
  const t0 = performance.now();
  const iv = setInterval(() => {
    if (tav.state === 'on' || tav.state === 'fail' || performance.now() - t0 > 150000) {
      clearInterval(iv);
      L('tav: ' + tav.state + ' ' + Math.round(performance.now() - t0) + 'ms');
      if (q.get('all')) tavOverview(true);
      if (q.get('s')) tavSetView(+q.get('s'), +(q.get('x') || 0), +(q.get('y') || 0));
      if (q.get('dbg')) seatLayoutTav(N).seats.forEach((o, i) => L(i + ': k=' + o.k + ' x=' + o.x.toFixed(1) + ' y=' + o.y.toFixed(1) + ' arka=' + o.back));
      setTimeout(() => { document.title = 'HAZIR'; }, 900);
    }
  }, 200);
})();
'''
i = s.rindex('})();')
s = s[:i] + snip + s[i:]
OUT.write_text(s, encoding='utf-8')
print(OUT)


