---
name: Dört Element
description: D&D 2024 için Türkçe açıklamalı karakter defteri ve elle boyanmış bir tavernada oynanan çevrim içi masa.
colors:
  ember-orange: "#ff7a33"
  ember-gold: "#ffc857"
  tide-cyan: "#38c6ec"
  moss-green: "#a3c94f"
  sky-indigo: "#5566e8"
  hearth-black: "#120807"
  ash-white: "#fcefe7"
  ember-dust: "#d3aa99"
  ember-ink: "#1d0a03"
  luck-green: "#4ecb8f"
  wound-red: "#ff6464"
  lamp-amber: "#f5b942"
  tavern-floor: "#1a120b"
  tavern-candle: "#f6ead8"
  tavern-dust: "#d6c3a6"
  chalkboard: "#2a3036"
  board-oak: "#6b4a2a"
  nameplate-ink: "#2a1c10"
  brass: "#c9a45c"
typography:
  display:
    fontFamily: "Grenze, 'Palatino Linotype', 'Book Antiqua', Georgia, serif"
    fontSize: "clamp(28px, 3.4vw, 44px)"
    fontWeight: 600
    lineHeight: 1.1
  numeral:
    fontFamily: "Grenze, 'Palatino Linotype', Georgia, serif"
    fontSize: "40px"
    fontWeight: 600
    lineHeight: 1
  headline:
    fontFamily: "Grenze, 'Palatino Linotype', Georgia, serif"
    fontSize: "20px"
    fontWeight: 500
    lineHeight: 1.15
  body:
    fontFamily: "'Hanken Grotesk', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.45
  title:
    fontFamily: "'Hanken Grotesk', system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 700
    lineHeight: 1.2
  label:
    fontFamily: "'Hanken Grotesk', system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.2
  chalk:
    fontFamily: "Caveat, 'Segoe Print', 'Bradley Hand', cursive"
    fontSize: "clamp(10.5px, 1.42vw, 20px)"
    fontWeight: 700
    lineHeight: 1.22
rounded:
  fire: "7px"
  earth: "12px"
  water: "18px"
  air: "22px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
components:
  button:
    backgroundColor: "rgba(0,0,0,.30)"
    textColor: "{colors.ash-white}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "40px"
  button-accent:
    backgroundColor: "{colors.ember-orange}"
    textColor: "{colors.ember-ink}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "40px"
  button-danger:
    textColor: "{colors.wound-red}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "40px"
  button-danger-hover:
    backgroundColor: "{colors.wound-red}"
    textColor: "#2a0606"
  button-sm:
    rounded: "{rounded.pill}"
    padding: "0 12px"
    height: "32px"
  button-lg:
    rounded: "{rounded.pill}"
    padding: "0 22px"
    height: "48px"
  icon-button:
    textColor: "{colors.ember-dust}"
    rounded: "{rounded.pill}"
    size: "32px"
  dice-button:
    backgroundColor: "{colors.ember-orange}"
    textColor: "{colors.ember-ink}"
    rounded: "{rounded.pill}"
    padding: "0 22px 0 15px"
    height: "52px"
  roll-number:
    backgroundColor: "rgba(0,0,0,.30)"
    textColor: "{colors.ash-white}"
    rounded: "6px"
    padding: "5px 8px"
  roll-number-hover:
    backgroundColor: "{colors.ember-orange}"
    textColor: "{colors.ember-ink}"
  chip:
    backgroundColor: "rgba(0,0,0,.30)"
    textColor: "{colors.ash-white}"
    rounded: "{rounded.pill}"
    padding: "5px 11px"
  card:
    backgroundColor: "rgba(38,18,13,.78)"
    textColor: "{colors.ash-white}"
    rounded: "{rounded.fire}"
    padding: "16px 18px"
  input:
    backgroundColor: "rgba(0,0,0,.30)"
    textColor: "{colors.ash-white}"
    rounded: "6px"
    padding: "8px 10px"
  tab:
    textColor: "{colors.ember-dust}"
    typography: "{typography.title}"
    padding: "11px 15px"
  nameplate:
    textColor: "{colors.nameplate-ink}"
    width: "clamp(84px, 10.4vw, 160px)"
  chalkboard-log:
    backgroundColor: "{colors.chalkboard}"
    textColor: "#e8ecee"
    typography: "{typography.chalk}"
---

# Design System: Dört Element

## Overview

**Creative North Star: "Tavernadaki Masa"**

Dört Element'te her şey bir masanın etrafında olur. Karakter kağıdı, zar, kara tahta ve isimlik, oyuncuların önünde duran gerçek eşyalardır; ekran, bir ayar sayfası değil, oturulan bir yerdir. Yeni bir parça tasarlanırken sorulan soru şudur: "Bu, tavernadaki masanın üstünde duran bir şey gibi mi görünüyor, yoksa bir yazılımın penceresi gibi mi?" İkincisiyse yeniden düşünülür.

Sistem iki dünyadan oluşur ve ikisi bilerek ayrıdır. **Defter** (karakter kağıdı, DM ekranı, çekmeceler) oyuncunun seçtiği **elementin** rengini taşır: Ateş, Su, Toprak, Hava. Her tema kendi renk paketi, kendi köşe yuvarlaklığı ve kendi arka plan parçacıklarıyla gelir. **Taverna** (masa görünümü) ise herkes için aynıdır: elle boyanmış, sıcak kahve tonlu, mürekkep çizgili bir mekân. Temadan tavernaya yalnızca vurgu rengi geçer; böylece her oyuncu, hangi elementi seçmiş olursa olsun, aynı odada olduğunu hisseder.

Yoğunluk orta-yüksektir: D&D kağıdı çok sayı taşır ve bu gizlenmez; ama her sayı yeni başlayana kendini sade Türkçeyle açıklar. His **sakin ve net**tir: parlama, büyüme ve titreme yalnızca önemli anlara (zar sonucu, doğal 20, "sen" işareti) saklanır.

**Açık karar (2026-10-18, sonraya bırakıldı):** Kullanıcı dört element temasına ısınamadı. Temalar ileride D&D hikâyelerinde sevilen **hikâye temalarıyla** (ör. Ortaçağ, Cyberpunk, Western) değiştirilecek; böylece o tarzda oynayan masa kendine özel bir görünüme kavuşur. Bu bir tasarım işi olarak yol haritasının sonuna bırakıldı. O zamana kadar dört element geçerlidir; ama yeni kod temayı **yalnızca değişkenlerden** (`--accent`, `--surface`, `--radius`…) okumalı ki temalar değişince hiçbir parça elle düzeltilmek zorunda kalmasın.

**Hedef yön (kararlaştırıldı, henüz uygulanmadı):** Karakter kağıdı zamanla tavernanın malzemesini alacak: parşömen yüzey, mürekkep çizgi, tebeşir ve ahşap ayrıntılar. Bugünkü koyu, yarı saydam kartlar geçerli kuraldır; yeni yapılan paneller ve butonlar bu hedefe doğru adım atar (daha belirgin çerçeve, kağıt hissi), ama eski kartları tek seferde değiştirmez.

**Key Characteristics:**
- İki dünya: element temalı defter + herkes için aynı taverna.
- Köşe yuvarlaklığı temanın karakteridir: Ateş keskin (7px), Hava yumuşak (22px).
- Başlık ve büyük sayılar Grenze (gotik kitap harfi), arayüz Hanken Grotesk, kara tahta Caveat (tebeşir el yazısı).
- Terimler çift dilli: İngilizce terim + Türkçe açıklama yan yana.
- Sonuç zardan önce hiçbir yerde görünmez; animasyon yalnızca gösterimdir.

## Colors

Her element tek bir güçlü vurgu rengi ile ona eşlik eden ikinci bir sıcak ton taşır; geri kalan her şey o elementin koyu zemini ve soluk yazı tonudur. Değerler `index.html`'deki CSS değişkenlerindedir (`--accent`, `--accent-2`, `--bg`, `--surface`, `--line`, `--text`, `--muted`); tabloda varsayılan tema Ateş gösterilir.

### Primary
- **Kor Turuncusu / Ember Orange** (ember-orange): Ateş temasının vurgusu ve sitenin varsayılan kimlik rengi. Zar atılan sayıların üstüne gelince, ana butonlarda ("Yeni karakter", "Masaya katıl"), seçili sekmede, portre çerçevesinde, odak halkasında. Yazı üstüne gelecekse koyu Kor Mürekkebi ile.
- **Element vurguları** (tema değişince `--accent` olur): **Gelgit Camgöbeği / Tide Cyan** (tide-cyan, Su), **Yosun Yeşili / Moss Green** (moss-green, Toprak), **Gök Çividi / Sky Indigo** (sky-indigo, Hava; tek açık tema, üstüne beyaz yazı).

### Secondary
- **Kor Altını / Ember Gold** (ember-gold): Ateş'in ikinci vurgusu (`--accent-2`). Yalnızca "ilham" (Heroic Inspiration) yıldızında ve masada DM'in işaretinde. Diğer temalarda karşılığı: Su #82f2d4, Toprak #e2b45c, Hava #9a6be6.

### Tertiary
- **Durum renkleri**, her temada aynı anlam: **Şans Yeşili / Luck Green** (luck-green): bağlı, can dolu, doğal 20. **Yara Kırmızısı / Wound Red** (wound-red): durumlar (conditions), can azaldı, doğal 1, silme ve masadan ayrılma. **Lamba Kehribarı / Lamp Amber** (lamp-amber): bekleniyor, bağlanıyor, can yarıda. Hava temasında üçü de koyulaşır (#1c8f59, #cf3636, #a86e00).

### Neutral
- **Ocak Karası / Hearth Black** (hearth-black): Ateş temasının zemini; arkasında kor parçacıkları.
- **Kül Beyazı / Ash White** (ash-white): ana yazı.
- **Kor Tozu / Ember Dust** (ember-dust): ikincil yazı, açıklamalar, Türkçe karşılıklar, etiketler.
- **Kart zemini** (`--surface`, Ateş'te rgba(38,18,13,.78)) ve **alan zemini** (`--field`, rgba(0,0,0,.30)): yarı saydam; arkadaki element katmanı hafifçe görünür.
- **Çizgi** (`--line`, Ateş'te rgba(255,150,95,.24)): kart, buton ve alan kenarları. **Bilinen sorun:** zemine karşı zıtlığı ~1,4:1; kartlar birbirinden ayrılmıyor (Aşama 2'de çözülecek).
- **Taverna paleti** (masa görünümünde temanın yerine geçer): **Taverna Zemini** (tavern-floor), **Mum Işığı** (tavern-candle) yazı, **Taverna Tozu** (tavern-dust) ikincil yazı, **Kara Tahta** (chalkboard) ve **Meşe Çerçeve** (board-oak), **İsimlik Mürekkebi** (nameplate-ink, parşömen üstünde), **Pirinç** (brass, isimlikteki portre halkası).

### Named Rules
**The One Hearth Rule.** Taverna temanın renklerini almaz; yalnızca `--accent` geçer (zar, "sen" halkası, POV çerçevesi). Masa görünümüne yeni bir parça eklerken tema değişkenleri değil taverna paleti kullanılır.

**The Variables Only Rule.** Defterde yeni kod sabit renk yazmaz; `--accent`, `--surface`, `--line`, `--text`, `--muted`, `--good`, `--bad`, `--warn` kullanır. Tema değişince her şey birlikte değişmelidir. (İstisna: taverna paleti ve element seçici düğmelerinin kendi renkleri.)

**The Meaning Is Fixed Rule.** Yeşil, kırmızı ve kehribar yalnızca durum anlatır (bağlı / tehlike / bekliyor). Süs için kullanılmaz; vurgu rengi de durum anlatmak için kullanılmaz.

## Typography

**Display Font:** Grenze (Palatino Linotype, Book Antiqua, Georgia yedekleriyle)
**Body Font:** Hanken Grotesk (system-ui yedeğiyle)
**Label/Mono Font:** Caveat, yalnızca kara tahtada (tebeşir)

**Character:** Grenze, eski bir kural kitabının başlıklarını andıran keskin, hafif gotik bir kitap harfidir; karakter adı, kart başlıkları ve büyük sayılar onunla yazılır. Hanken Grotesk sade ve okunaklıdır; bütün arayüz, etiket ve açıklamalar onunla. Caveat yalnızca tavernadaki kara tahtada, tebeşir el yazısı olarak. Üçü de Google Fonts'tan gelir.

### Hierarchy
- **Display** (Grenze 600, clamp(28px, 3.4vw, 44px), 1.1): karakter adı.
- **Numeral** (Grenze 600, 26–52px, 1): skor modifiyeleri (40px), can (52px), AC ve hız (38px), pasifler (26px). Sayı bu sitenin kahramanıdır.
- **Headline** (Grenze 500, 20px, 1.15): kart ve panel başlıkları. Başlığın yanında Türkçe karşılığı Hanken 500, 12,5px, soluk renkte (`Saving Throws  Kurtarma zarları`).
- **Title** (Hanken 700, 14px): sekmeler, satır adları, liste başlıkları.
- **Body** (Hanken 400, 15px, 1.45): genel metin. Açıklama paragrafları 72–74ch'yi geçmez.
- **Label** (Hanken 700, 12px): alan etiketleri; yanında Türkçe karşılık 500 ağırlıkta. Yetenek kısaltmaları (STR, DEX…) 800 ağırlık, harf aralığı .14em, vurgu renginde.
- **Chalk** (Caveat 700): kara tahtadaki son atışlar.

### Named Rules
**The Two Tongues Rule.** Her D&D terimi iki dilde durur: İngilizce terim önde ve kalın, Türkçe karşılığı yanında ya da altında, soluk ve ince. Sıra hiçbir yerde ters çevrilmez.

**The Hint Floor Rule.** Okunması gereken hiçbir yazı 12px'in altına inmez. (Bilinen sorun: yetenek etiketleri 10,5px; düzeltilecek.)

## Layout

Defter en çok 1320px genişliğinde ortalanmış tek bir sütundur (yanlarda 20px boşluk). Karakter başlığının altında altı yetenek kartı yan yana, sonra iki sütunlu yerleşim: solda 336px'lik sabit sütun (kurtarma zarları, beceriler, pasifler), sağda esnek ana alan (savaş değerleri, sekmeler). Kartlar arası boşluk 14–16px, kart içi 16px 18px.

Kırılma noktaları: 1180px ve 1100px'te yetenekler ve yan sütun daralır; 980px'te buton yazıları gizlenir (yalnızca ikon kalır); 820px'te tek sütuna geçilir; 560px telefon düzenidir.

Masa görünümü ayrı bir ölçü kullanır: **birim** (`--u`), ekrana sığan en büyük 16:9 kutunun genişliğinin %1'idir. Panel, kara tahta, oyuncu kutusu ve tablo bununla ölçülür; ekran genişleyince büyümezler, yalnızca tavernanın daha çok yeri görünür. Sol şerit (POV paneli) sahnenin yukarıdan aşağıya tamamıdır; kara tahta sağ üstte, oyuncu kutusu sağ altta, araç çubuğu POV panelinin hemen sağında, yakınlaştırma sol altta.

### Named Rules
**The Stage Owns The Screen Rule.** Masa görünümünde sahne ekranın tamamıdır; arayüz parçaları kenarlara yaslanır ve sahnenin ortasını (oyun masasını) asla kapatmaz.

## Elevation & Depth

Derinlik üç katmanla verilir: arkada temanın hareketli element katmanı, ortada yarı saydam ve bulanıklaştırılmış (backdrop blur 10–18px) kartlar, önde çekmece, tepsi ve bildirimler. Kartlar tek ve yumuşak bir gölge taşır (`--shadow`); tonla katmanlama, gölgeden daha çok iş yapar.

### Shadow Vocabulary
- **Kart gölgesi** (`box-shadow: 0 18px 44px -14px rgba(0,0,0,.65)`): bütün kartlar, tepsi, çekmece, bildirim. Hava temasında mavimsi ve daha hafif.
- **Odak halkası** (`box-shadow: 0 0 0 3px` vurgu %22): alana yazarken.
- **Vurgu parlaması** (`box-shadow: 0 0 28px -6px var(--glow)`): yalnızca masadaki zar sonucu, doğal 20 / 1 ve "sen" halkası. 2026-10-18'de logo, portre, zar düğmesi, yetkinlik noktaları, bağlantı noktası, AC kalkanı ve seçili element düğmesindeki süs parlamaları kaldırıldı.
- **İlham yıldızı** (`filter: drop-shadow(0 0 6px` altın %75`)`): ilham varken yalnızca yıldız altın sarısıyla (`--star`, her temada aynı) dolar ve parlar; kutu dolmaz, yalnızca kenarı altına döner.
- **Yüzen düğme gölgesi** (`box-shadow: 0 10px 24px -10px rgba(0,0,0,.75), 0 2px 6px rgba(0,0,0,.35)`): Zar düğmesi; zar atan sayının üstüne gelince `0 6px 14px -8px rgba(0,0,0,.7)`.
- **Taverna gölgeleri** (`drop-shadow`): figür, sandalye, isimlik ve zarlar masaya oturmuş görünsün diye.

### Named Rules
**The Earned Glow Rule.** Parlama bir ödüldür: zar sonucu, doğal 20 / doğal 1, masadaki "sen" halkası ve ilham. Durağan bir düğme ya da çerçeve parlamaz. Yeni parçalara parlama eklenmez; mevcut süs parlamaları zamanla kaldırılır.

## Shapes

Köşe dili temanın kişiliğidir: **Ateş 7px** (keskin), **Toprak 12px**, **Su 18px**, **Hava 22px** (yumuşak). Kartlar `--radius`, iç kutular `--radius × .8 + 2px`, alanlar `--radius × .55 + 2px` kullanır; böylece iç içe köşeler her temada uyumlu kalır. Butonlar, çipler, element seçici ve segmentler her temada **hap** biçimindedir (999px); dairesel öğeler (portre, ikon düğmesi, yetkinlik noktası, zar düğmesi) tam yuvarlaktır. Zırh sınıfı bir kalkan, can bir çubuk, yetkinlik içi dolan bir daire olarak çizilir: D&D'nin kendi simgeleri biçim olarak kullanılır.

Defterde kartlar arma çerçevelidir (bkz. Components → Cards): metal kenar, üstte arma, altta baklava.

Tavernada biçimler elle yapılmış eşyalardır: ahşap isimlik (görsel), meşe çerçeveli kara tahta, mürekkep çizgili sahne. Burada tema köşeleri kullanılmaz.

### Named Rules
**The One Frame Per Area Rule.** Birbirine ait parçalar tek arma çerçevede durur; çerçeve içine çerçeve konmaz, iç bölümleri ince çizgiler ayırır.

## Components

### Buttons
Tek sistem (2026-10-18). Hap biçimli, kalın yazılı, sakin; durum renkle ve zeminle anlatılır, parlamayla değil.
- **Shape:** hap (999px); yalnızca ikondan oluşanlar tam yuvarlak.
- **Üç boy:** küçük `.sm` 32px (kart içi, masa araçları, satır işleri), normal 40px (üst çubuk, çekmece, ana işler), büyük `.lg` 48px (ilk ekrandaki iki büyük seçenek). **Dokunmatik ekranda** (pointer: coarse) sırasıyla 40 / 44 / 52px'e büyür; parmak için en az 44px hedefi.
- **Yapı:** ikon + yazı; ikon normal boyda 18px, küçükte 16px, büyükte 20px. Dar ekranda (≤560px) üst çubukta yazı gizlenir, ikon kalır; o düğmelerde mutlaka `title` vardır.
- **Default:** alan zemini, ince çizgi kenar, Hanken 700 13,5px. Üstüne gelince kenar vurgu rengine döner ve zemin %10 vurguya boyanır; yazı rengi değişmez. Basınca 1px aşağı iner.
- **Accent:** vurgu zemini, koyu yazı; bir ekranda tek ana iş ("Yeni karakter", "Masaya katıl", "Zarı at"). Üstüne gelince biraz aydınlanır.
- **Danger (`.bad`) / Good (`.good`):** yalnızca kenar ve yazı renkli; üstüne gelince dolar ve yazı **koyu** olur (`--on-bad`, `--on-good`; Hava temasında kırmızı üstünde beyaz).
- **Aç/kapa (aria-pressed):** açıkken kenar vurgu rengi, zemin %16 vurgu, ikon vurgu renginde. Kapalıyken normal düğme gibi görünür; **asla soluklaşmaz** (soluk düğme "çalışmıyor" gibi okunur).
- **Disabled:** %45 görünürlük, üstüne gelince değişmez.
- **Icon button** (`.btn.icon` ya da küçük yuvarlak `.icon-btn`): kapat, sil, eksi/artı, yakınlaştır. İkon çizimdir (SVG); ×, −, + gibi klavye işaretleri ikon yerine kullanılmaz. Silme düğmeleri (`.del`) üstüne gelince kırmızı.
- **Masada:** taverna üstündeki düğmeler taverna kart zeminini (`--surface`) alır; açık olan %24 vurguya boyanır.

### Zar Düğmesi (imza parçası)
Sağ altta sabit, **yazılı hap**: d20 ikonu + "Zar at". Yuvarlak, yazısız bir balon olmaz (sitelerin "yardım / sohbet" düğmesiyle karışıyordu). 52px yüksek, vurgu zemini, koyu yazı; nötr, aşağı düşen gölge (parlama değil). Üstüne gelince 2px yükselir. Zar tepsisini açar.

### Roll Numbers (imza parçası)
Kağıdın kendisi zar tepsisidir: zar atan her sayı bir düğmedir. Alan zemini, ince kenar, kalın tabular rakamlar. Üstüne gelince vurgu rengiyle dolar ve 1px yükselir; tıklayınca zar atılır. Büyük hâli (inisiyatif, saldırı) Grenze 38px. Bu davranış başka hiçbir öğeye verilmez: vurguyla dolup yükselen şey zar atar.

### Chips
Hap biçimli, alan zemini, kalın İngilizce ad + soluk Türkçe karşılık. Durum çiplerinde seçili hâl Yara Kırmızısı ile dolar. Masa durum çubuğundaki "Masada:" listesi aynı biçimi kullanır (bağlı noktası ile).

### Cards / Containers (Arma Çerçeve)
Oyunların yükleme ekranı kartları gibi (kullanıcının referansı: League of Legends yükleme ekranı çerçevesi, 2026-10-18). **Bir alan, tek çerçeve:** birbirine ait parçalar (altı yetenek; AC + inisiyatif + hız + can; can zarı + ölüm zarları + durumlar) tek çerçevede toplanır, aralarını ince çizgiler ayırır. Çerçeve içinde çerçeve olmaz.
- **Metal çerçeve:** 3px, yukarıdan aşağı yansımalı renk geçişi (`--metal`: vurgu renginin açık ve koyu tonları). Ateş'te bakır, Su'da gümüş-camgöbeği, Toprak'ta bronz-yeşil, Hava'da gümüş-çivit. Kartın yarı saydam zemini bozulmasın diye halka `::before` + maske ile çizilir.
- **İç kenarlar:** metalin hemen içinde 1px koyu kenar (gömme hissi), 7px içeride ince açık çizgi (`--metal-line`, vurgu %30).
- **Arma:** üst ortada 48×17px kanatlı arma (ortada baklava taş, iki yanda incelen kanatlar), alt ortada 13px baklava; ikisi de aynı metal geçişle, hafif gölgeli. `::after` + maske.
- **İç bölümler:** çerçevenin içindeki kartlar zeminsiz ve çerçevesizdir (`.card :where(.card)`); aralarında 1px `--line` çizgi. Dar ekranda yetenekler 3'lü sıraya geçince ikinci sıranın üstüne, can zarı/durumlar alt alta geçince aralarına yatay çizgi.
- **Başlık:** Grenze başlık + Türkçe karşılık, altında 1px `--line` çizgi, sağda isteğe bağlı küçük buton.
- **Internal Padding:** tek kart 20px 22px; grup çerçevesinde iç bölümler 16px 18px.
- **Aralık:** alt alta çerçeveler arasında en az 26px (üsttekinin alt baklavası ile alttakinin arması değmesin).
- **İleride:** hikâye temaları gelince metal, arma biçimi ve iç çizgi temayla birlikte değişebilir (ör. Cyberpunk'ta neon çizgi, Western'de deri ve perçin); kod renkleri yalnızca değişkenlerden okur.

### Portre
Daire, vurgu renginde 2px kenar ve 6px soluk halka. Boşken ortada kalem ikonu (yazı yok); üstüne gelince kalem vurgu rengine döner. Resim yüklüyken sağ altta vurgu renginde küçük kalem rozeti ("değiştir"), sağ üstte kaldırma (×) düğmesi.

### Inputs / Fields
- **Style:** `--field` zemin, 1px `--line` kenar, alan köşesi, 8px 10px.
- **Focus:** kenar vurgu rengine döner + 3px yumuşak vurgu halkası.
- **Hover:** kenar vurguya doğru yarı karışım.
- **Özel:** karakter adı alanı çerçevesizdir; yalnızca kesikli alt çizgi ve Grenze display.
- **Disabled:** DM bir oyuncunun kağıdını izlerken bütün alanlar salt okunurdur.

### Navigation
- **Üst çubuk:** yapışkan, temanın `--bar` rengi, bulanık. Solda logo (elementin ikonu, vurgu dairesinde), ortada element seçici (hap içinde dört hap; seçili olan kendi elementinin rengiyle dolar), sağda kayıt durumu, Açıklamalar, Karakterler ve Masa (masadayken masa kodu ve bağlantı noktası).
- **Sekmeler:** alt çizgili; seçili sekme vurgu renginde yazı ve 2px alt çizgi. Dar ekranda yatay kayar.
- **Masa durum çubuğu:** bağlantı noktası + durum cümlesi + eylem düğmesi; bağlantı koparken kehribar, hatada kırmızı kenar; altında "Masada:" çipleri.

### Taverna İsimliği (imza parçası)
Ahşap levha görseli: ad parşömen şeridinde Grenze 700, karakter adı alt çıtada küçük açık renk yazı, solda pirinç halkalı yuvarlak portre ve köşesinde bağlantı noktası. DM'in portresi yerine her zaman zar simgesi. Kendi koltuğun vurgu renginde hafif parlar. Bağlantısı kopanın isimliği %66 soluk, portresi gri.

### Kara Tahta (imza parçası)
Sağ üstte, meşe çerçeveli koyu tahta; son atışlar Caveat ile tebeşir yazısı. Doğal 20 açık yeşil, doğal 1 açık kırmızı tebeşir. Üstüne gelince sola doğru büyür ve ayrıntılar okunur.

## Do's and Don'ts

### Do:
- **Do** yeni bir parçayı önce "masanın üstünde duran bir eşya mı?" sorusuyla tasarla (Tavernadaki Masa).
- **Do** defterde yalnızca tema değişkenlerini kullan (`--accent`, `--surface`, `--line`, `--text`, `--muted`); masa görünümünde taverna paletini.
- **Do** her D&D terimini İngilizce + Türkçe ver; açıklamayı sade, yeni başlayanı küçümsemeyen bir dille yaz.
- **Do** iç içe köşeleri `--radius`'tan türet (kart, iç kutu ×.8 + 2px, alan ×.55 + 2px).
- **Do** dokunma hedeflerini en az 44px, metin zıtlığını en az 4,5:1 yap (PRODUCT.md hedefi).
- **Do** ikon tek başına kaldığında ona açıklama (title ve aria-label) ver.
- **Do** butonları yalnızca üç boydan (32 / 40 / 48px) ve dört türden (normal, accent, bad, good) seç; yeni bir buton biçimi icat etme.
- **Do** "Hareket azaltma" açıkken animasyonu atla, sonucu doğrudan göster.

### Don't:
- **Don't** durağan düğme, çerçeve ya da logoya vurgu parlaması ekleme (The Earned Glow Rule).
- **Don't** zar sonucunu zar yere inmeden hiçbir yerde gösterme (bildirim, tahta, sayı, geçmiş).
- **Don't** tavernaya temanın zemin, kart ya da çizgi renklerini taşıma; yalnızca vurgu geçer.
- **Don't** Yara Kırmızısı (#ff6464) üstüne beyaz yazı koyma (zıtlık 2,9:1); `--on-bad` (koyu) kullan.
- **Don't** ×, −, + gibi klavye işaretlerini ya da emojiyi ikon yerine kullanma; ikonlar aynı çizgi kalınlığında SVG'dir.
- **Don't** kapalı bir aç/kapa düğmesini soluklaştırma.
- **Don't** 12px'in altında okunması gereken yazı kullanma.
- **Don't** yeşil / kırmızı / kehribarı süs için kullanma; bunlar yalnızca durum anlatır.
- **Don't** sayfanın altındaki İngilizce Fan Content ve SRD atıf metnine dokunma.
