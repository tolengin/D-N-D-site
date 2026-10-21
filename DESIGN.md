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
    padding: "0 20px"
    height: "40px"
  button-accent:
    backgroundColor: "{colors.ember-orange}"
    textColor: "{colors.ember-ink}"
    rounded: "{rounded.pill}"
    padding: "0 20px"
    height: "40px"
  button-danger:
    textColor: "{colors.wound-red}"
    rounded: "{rounded.pill}"
    padding: "0 20px"
    height: "40px"
  button-danger-hover:
    backgroundColor: "{colors.wound-red}"
    textColor: "#2a0606"
  button-sm:
    rounded: "{rounded.pill}"
    padding: "0 14px"
    height: "32px"
  button-lg:
    rounded: "{rounded.pill}"
    padding: "0 26px"
    height: "48px"
  icon-button:
    textColor: "{colors.ember-dust}"
    rounded: "{rounded.pill}"
    size: "32px"
  dice-button:
    backgroundColor: "{colors.ember-orange}"
    textColor: "{colors.ember-ink}"
    rounded: "{rounded.pill}"
    padding: "0 26px 0 24px"
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
    padding: "11px 22px"
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

**The Hint Floor Rule.** Okunması gereken hiçbir yazı 12px'in altına inmez. (2026-10-20: yetenek etiketleri 10,5px'ten, çip / liste başlığı / yuva etiketleri 11,5px'ten 12px'e çıktı.)

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
- **İç boşluk (kullanıcının kuralı, 2026-10-20):** yandaki boşluk üstteki boşluğun **2 katı**. Üstteki boşluk = (boy − 2px kenar − ikon) / 2 olduğundan yandaki boşluk boydan hesaplanır: `padding-inline: calc(var(--h) - 2px - var(--ic))`. Sonuç: küçük 14px, normal 20px, büyük 26px; dokunmatikte 22 / 24 / 30px. Boy değişince oran kendiliğinden korunur; düğmeye elle `padding` yazılmaz. İstisna: yalnız ikonlu yuvarlak düğmeler (boşluk yok) ve zar atan sayılar (`.roll`, ortalanmış rakam). Sekmeler 11px 22px, Zar Düğmesi 0 26px 0 24px.
- **Yapı:** ikon + yazı; ikon normal boyda 18px, küçükte 16px, büyükte 20px (`--ic`). Dar ekranda (≤560px) üst çubukta yazı gizlenir, ikon kalır; o düğmelerde mutlaka `title` vardır.
- **Default:** alan zemini, ince çizgi kenar, Hanken 700 13,5px. Üstüne gelince kenar vurgu rengine döner ve zemin %10 vurguya boyanır; yazı rengi değişmez. Basınca 1px aşağı iner.
- **Accent:** vurgu zemini, koyu yazı; bir ekranda tek ana iş ("Yeni karakter", "Masaya katıl", "Zarı at"). Üstüne gelince biraz aydınlanır.
- **Danger (`.bad`) / Good (`.good`):** yalnızca kenar ve yazı renkli; üstüne gelince dolar ve yazı **koyu** olur (`--on-bad`, `--on-good`; Hava temasında kırmızı üstünde beyaz).
- **Aç/kapa (aria-pressed):** açıkken kenar vurgu rengi, zemin %16 vurgu, ikon vurgu renginde. Kapalıyken normal düğme gibi görünür; **asla soluklaşmaz** (soluk düğme "çalışmıyor" gibi okunur).
- **Disabled:** %45 görünürlük, üstüne gelince değişmez.
- **Icon button** (`.btn.icon` ya da küçük yuvarlak `.icon-btn`): kapat, sil, eksi/artı, yakınlaştır. İkon çizimdir (SVG); ×, −, + gibi klavye işaretleri ikon yerine kullanılmaz. Silme düğmeleri (`.del`) üstüne gelince kırmızı.
- **Masada:** taverna üstündeki düğmeler taverna kart zeminini (`--surface`) alır; açık olan %24 vurguya boyanır.

### Sade / Tam Görünüm (2026-10-20, yol haritası 32)
Kağıdın iki görünümü; seçici kağıdın şeridinde, "Masaya dön"ün solunda (hap içinde iki hap; seçili olan vurgu kenarı + %18 vurgu zemini, dolgu değil). Seçim karakterle saklanır; yeni karakterler Sade, eski kayıtlar Tam açılır; DM'in izlediği kağıt hep Tam. Kullanılabilirlik araştırmalarına göre iki seviyeden fazlası kullanıcıyı zorlar; üçüncü seviye yok.
- **Sade (yeni başlayan):** portre, ad, tür, sınıf, geçmiş, seviye, ilham; altı yetenek; kurtarma zarları; yalnızca yetkin olunan beceriler ("Bütün beceriler (18)" ile açılır); AC, inisiyatif, hız, can; can zarı; yalnızca seçili durumlar ("Durum ekle" ile açılır, bitkinlik de); ölüm zarları yalnızca can 0'dayken ya da işaret varken; sekmeler Saldırılar, Envanter, Özellikler, Notlar (Büyüler büyü kullananlarda). Saldırıda "Yetkin" ve "Ek bonus", büyüde süre / menzil / C·R·M sütunları, yuvası olmayan büyü seviyeleri, CP / SP / EP / PP, uyum, yetkinlikler, hünerler, pasif algılar, XP ve yetkinlik bonusu gizli.
- **The Never Hide Data Rule:** Sade dolu bir alanı asla saklamaz; içi dolu parça görünür kalır. Yazarken bir alan yalnızca görünür hâle geçebilir; gizlenmesi görünüm ya da karakter değişince olur (silerken alan elin altından kaybolmasın).

### Karakter Oluşturma (2026-10-20, yol haritası 31)
Kağıdın yerine geçen tek arma çerçeveli kart (en çok 1040px): üstte Grenze başlık ve sağda adım hapları (numara dairesi + ad; geçilen adıma basınca geri dönülür, telefonda yalnızca numara), ortada bir soru (Grenze 24px), tek satır açıklama ve seçenekler, altta Vazgeç | Geri · Devam (ana iş; seçim yapılmadan soluk).
- **Seçenek döşemesi:** düz alan zemini, ince çizgi, köşe `--radius × .8 + 2px`; İngilizce ad Grenze 22px + Türkçe karşılık, tek satır açıklama, altta soluk kısa bilgi ("Yakın dövüş · ağır zırh · Can zarı d10"). Seçili: vurgu kenarı + %14 vurgu zemini (dolgu değil). Gölge yok.
- **Bir ekranda en çok dört karar:** önce yeni başlayana önerilen dört seçenek, gerisi "Bütün seçenekler (N)"; "Önerilen" rozeti yalnızca hepsi açıkken görünür.
- **0. adım:** Hazır Büyücü, Hazır Paladin ("Hazır" rozeti), "Kendim oluşturayım"; altta küçük "Boş kağıtla başla (oyunu biliyorum)".
- **Yetenekler:** altı kutu; büyük Grenze modifiye, altında standart dizi seçimi (aynı sayı seçilirse yer değiştirir), geçmiş artışı vurgu renginde "+2".

### Karakter Kartı (2026-10-20, yol haritası 16)
Masada, sağ altta oyuncunun kendi kartı (kullanıcının örnek kartından uyarlandı). Masada durduğu için **taverna malzemesi**: parşömen yüzey (#efe2c0 → #e3cfa2), mürekkep yazı (#2a1c10), 3px meşe çerçeve (#6b4a2a) ve 1px pirinç iç çizgi (#c9a45c), hafif içe gölge. Temadan yalnızca vurgu geçer (zar atan sayının üstüne gelince). Parşömen üstünde hasar / iyileşme için koyulaştırılmış kırmızı (#9a2c1c) ve yeşil (#2b6437).
- **Kapalı:** başlık (yuvarlak arma: portre ya da baş harf, pirinç halkalı; ad Grenze; altında büyük harfle "HUMAN · PALADIN"; sağda "SEVİYE" ve sayı; ok düğmesi) ve can şeridi (can / en çok, çubuk, AC). Bütün başlık kartı açar.
- **Açık:** portre (16:10, varsa), altı yetenek (kısa ad, büyük modifiye, dairede skor; zar atar), solda kurtarma zarları (yetkinse dolu nokta), sağda can kutusu ve kalkan biçiminde AC, can işlemleri, dört küçük kutu (yetkinlik, hız, inisiyatif (zar), pasif algı), en çok dört saldırı, altta "Kağıdın tamamı" ve figür. Açıkken daha geniş (23,5 birim) ve sağ sütunun üstüne biner.
- İngilizce büyük harfli etiketlerde `lang="en"` (Türkçe büyük harf kuralı "Hit Points"i "HİT POİNTS" yapıyordu).

### Bildirim ve Geri Al (2026-10-20)
Sol altta, tepsi zemininde, vurgu kenarlı kart: kalın başlık + soluk alt satır. Geri alınabilir bir iş (satır silme) sorulmadan yapılır ama bildirimde küçük **"Geri al"** düğmesi (geri ok ikonu) 7 sn durur; basınca silinen satır yerine döner. Onay kutusu yalnızca geri alınamayan işlerde (uzun dinlenme, karakter silme).

### Zar Düğmesi (imza parçası)
Sağ altta sabit, **yazılı hap**: d20 ikonu + "Zar at". Avantaj ya da dezavantaj açıkken düğmede de yazar ("Zar at · Avantaj"): mod açık kalır, unutulmasın. Yuvarlak, yazısız bir balon olmaz (sitelerin "yardım / sohbet" düğmesiyle karışıyordu). 52px yüksek, vurgu zemini, koyu yazı; nötr, aşağı düşen gölge (parlama değil). Üstüne gelince 2px yükselir. Zar tepsisini açar.

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
- **Sürgü (range, 2026-10-19, ilk kullanım ses paneli):** gömük, koyu bir yiv (8px, hap, `--field` + içe gölge, ince `--line` kenar); dolu kısmı vurgu renginde, koyudan açığa geçişli. Düğme 18px yuvarlak, kart çerçevesiyle aynı metal (`--metal`), hafif aşağı gölge; üstüne gelince %15 büyür. Değer sağda Grenze rakamla yazılır. Tarayıcının hazır sürgüsü kullanılmaz.

### Ses Paneli
Üst çubuğun sağ ucundaki hoparlör ikonundan açılan, arma çerçeveli küçük kart (`.ses-pop.card`). Başlık "Sound · Ses", yanında ses aç/kapa düğmesi (aria-pressed). Üç satır (Müzik, Ortam, Efektler): solda kanalın ikonu (nota, alev, d20; basınca o kanal susar ve ikon üstü çizili hoparlöre döner), ad + soluk Türkçe açıklama, sağda değer, altta sürgü. Ses kapalıyken satırlar %55 görünür. Zemin opaktır (üst çubuğun bulanıklığı iç içe çalışmaz).

### Navigation
- **Üst çubuk:** yapışkan, temanın `--bar` rengi, bulanık. Solda logo (elementin ikonu, vurgu dairesinde), ortada element seçici (hap içinde dört hap; seçili olan kendi elementinin rengiyle dolar), sağda kayıt durumu, Açıklamalar, Karakterler ve Masa (masadayken masa kodu ve bağlantı noktası).
- **Sekmeler:** alt çizgili; seçili sekme vurgu renginde yazı ve 2px alt çizgi. Dar ekranda yatay kayar.
- **Masa durum çubuğu:** bağlantı noktası + durum cümlesi + eylem düğmesi; bağlantı koparken kehribar, hatada kırmızı kenar; altında "Masada:" çipleri.

### Taverna İsimliği (imza parçası)
Ahşap levha görseli: ad parşömen şeridinde Grenze 700, karakter adı alt çıtada küçük açık renk yazı, solda pirinç halkalı yuvarlak portre ve köşesinde bağlantı noktası. DM'in portresi yerine her zaman zar simgesi. Kendi koltuğun vurgu renginde hafif parlar. Bağlantısı kopanın isimliği %66 soluk, portresi gri.

### Kara Tahta (imza parçası)
Sağ üstte, meşe çerçeveli koyu tahta; son atışlar Caveat ile tebeşir yazısı. Doğal 20 açık yeşil, doğal 1 açık kırmızı tebeşir. Üstüne gelince sola doğru büyür ve ayrıntılar okunur.

### Kağıt Masada (2026-10-19, madde 7)
Masadan kağıda geçince kağıt ayrı bir sayfa olmaz: kamera koltuğa yaklaşır, kağıt tavernanın üstünde kendi içinde kayan bir katman olarak aşağıdan kalkar (0,42 sn, hafif büyüyerek), arkada taverna kararır ve bulanıklaşır (blur 7px, parlaklık %45). Üstte **kağıdın şeridi** (2026-10-20): kağıtla aynı genişlikte, yapışkan, dolu zeminli (`--bar`), alt köşeleri yuvarlak, altında yumuşak gölge; solda karakterin adı (Grenze) ve soluk "3. seviye Human Ranger", sağda "Masaya dön" (Esc de kapatır). Satırlar şeridin altına girer; yüzen düğme olmaz (eskiden satırların × düğmesini örtüyordu). DM ekranında aynı şerit "DM ekranı" yazar. Kapatınca kağıt iner, kamera eski yerine döner. Yasal yazı kağıdın içinde, en altta; karanlık taverna üstünde her temada açık renk. Telefonda ve hareket azaltmada kamera kımıldamaz.

**Kamera inişi (7a):** kağıt ya da DM ekranı açılırken figürler ve POV paneli çekilir, kamera koltuğun arkasından ve yukarısından (tavanın altında) masaya bakarak göz hizasına iner (0,9 sn, yumuşak başlayıp yumuşak durur); kağıt bu sırada kalkar. Kapanınca kamera yükselir (0,7 sn), eğik görünüm ve figürler geri gelir.

### Kayan Üst Çubuklar ve Büyütme Tutamağı (2026-10-19, madde 9 ve 11)
- **Masa ekranında üst çubuk ve durum çubuğu yukarı kayar**, sahne bütün ekranı kaplar. Üst ortada asılı küçük bir "Menü" tutamağı (çubuk zemini, alt köşeleri yuvarlak); fareyle en üst kenara gelince ya da tutamağa basınca çubuklar sahnenin üstüne iner, fare çekilince yarım saniye sonra yine kayar. Telefonda ve tam ekranda yok.
- **Büyütme tutamağı:** köşede 22 px'lik yarı saydam kare, iki çapraz açık çizgi; üstüne gelince belirginleşir. POV panelinin sağ altında (panel %45–100), sağ sütunun sol altında (sütun %70–180). Büyüklük tarayıcıda hatırlanır. Telefonda yok.
- **Yandaki tutamak (2026-10-19):** kenarın ortasında 12×56 px'lik dik çubuk, iki dik açık çizgi; yalnızca yatayda genişletir. POV panelinin sağ kenarında (genişlik ×0,6–3, en çok sahnenin %64'ü), sağ sütunun sol kenarında (×0,8–2,6). Panel genişleyince el kareleri büyümez, altta ortada kalır.
- **Menüyü sabitle (raptiye):** üst çubukta ses düğmesinin solunda ikon düğme (aç/kapa). Basılıyken masa ekranında çubuklar kaymaz. Yalnızca çubukların kaydığı yerde (masa, geniş ekran) görünür.
- **Yalnız POV:** araç çubuğunda "POV"un yanında aç/kapa düğme. Açıkken POV paneli bütün sahneyi kaplar; eğik görünüm ve isimlikler çizilmez; araç çubuğu ve savaş sırası panelin sol üstünde, karakter adı sol altta. Kara tahta, düşmanlar ve oyuncu kutusu yerinde kalır. Telefonda yok.

### Bekleyen Hasar (2026-10-19)
DM'in kendi (ya da bir düşman adına attığı) hasar zarı kendiliğinden vurulmaz. Zar yere inince sağ altta, hedef etiketinin üstünde bir kart çıkar: isimlik kutusuyla aynı zemin, solda 3px kırmızı şerit (tehlike), hançer ikonu. Başlık "Goblin → Kara" (Grenze), altında zarın adı ve hesabı; ortada −/+ düğmeleri arasında Grenze 24px sayı alanı ve "Yarısı"; değiştirilmişse sağda soluk "zar 9". Altta "Vazgeç" ve tek ana iş "Hasarı vur" (accent). En çok dört kart üst üste. Oyuncuların zarları eskisi gibi kendiliğinden uygulanır.

### Hedef Etiketi ve İsimlik Kutusu (2026-10-19, Aşama 4)
- **Hedef etiketi:** seçili hedef "Zar at"ın hemen üstünde, vurgu kenarlı hap: hedef ikonu, "→ Goblin (5/7 can, AC 12)", × ile kaldırma. DM bir düşman adına atıyorsa başta düşmanın adı.
- **Seçili hedefin isimliği:** çevresinde kesikli vurgu halkası (parlama değil; The Earned Glow Rule).
- **İsimlik kutusu:** yalnızca DM'de; bir oyuncunun isimliğine basınca açılan küçük kart (taverna zemini, ince çizgi, kart gölgesi): ad (Grenze) ve "Hedef yap". (Güvenilir / hain oyları ve oy çipleri 2026-10-20'de kaldırıldı.)
- **Düşman kartı (DM ekranı):** her düşman ince çizgili bir iç kutu: ad alanı, Can / En çok / AC sayı alanları, "Masada" ve "Can görünsün" aç/kapa düğmeleri, silme. Canı biten düşman %60 soluk.

### Masada Sağ Sütun ve Savaş Sırası (2026-10-19)
- **Sağ sütun:** üstte kara tahta (son atışlar), altında **Düşmanlar panosu**: aynı meşe çerçeve, ama yüzeyi parşömen (#e9d8b2) ve yazı mürekkep (Grenze). Her düşman bir satır: yuvarlak görsel (yoksa baş harf), ad, "6/10 can · AC 15" (oyuncuda yalnızca DM izin verdiyse), can çubuğu. Satıra basınca hedef seçilir (kesikli vurgu çerçevesi); sırası gelen düşmanın satırı altın tonla dolar; canı biten soluk ve üstü çizili. İkisi de başlıktaki −/+ düğmesiyle kapanır (yalnızca başlık kalır). Telefonda sahnenin altında alt alta.
- **Savaş sırası şeridi:** savaş açıkken araç çubuğunun altında, masa kartı zemininde yatay şerit: solda "Savaş · Tur N" ve kimin sırası olduğu, ortada inisiyatife göre dizili yuvarlak portreler (altında inisiyatif sayısı ve ad; düşmanların halkası kesikli), sağda DM için "Sıradaki / Sırayı başlat" (ana iş) ve "Bitir", oyuncu için zar atmadıysa "İnisiyatif at". Sırası gelenin halkası vurgu renginde ve %12 büyük (parlama değil). Telefonda sahnenin altında.
- **Düşman görselleri:** hazır beş düşman (goblin, ork, iskelet, haydut, kurt) aynı tarzda: elle boyanmış, mürekkep çizgili, mum ışıklı, düz koyu kahve zeminli büst portresi; sitede yuvarlak kesilir.

### Savaş Sahnesi: Orman Açıklığı (2026-10-19)
Savaş başlayınca taverna yerine 2D bir orman açıklığı gelir (0,8 sn, parlaktan ve bulanıktan açılarak); ortada bir an "ORMAN YOLU / Savaş!" yazısı (Grenze, parşömen renginde, koyu gölgeli). Savaş bitince solarak taverna döner.
- **Arka plan:** gün batımında orman: sıcak ufuk, ağaçların arasından batan güneş, iki kat uzak çam sırtı (sisli), orta ağaçlar (güneşe bakan yanları açık), çok hafif ışık huzmeleri, ortada çiğnenmiş açık toprak, soldan gelen yol, önde koyu otlar ve taşlar, iki yanda çerçeveleyen kalın gövdeler, köşelerde çalı ve yaprak örtüsü, kenar kararması, hafif fırça dokusu. Mürekkep çizgileri tavernadaki gibi koyu kahve. Şimdilik kodla boyanır; `masa/savas/orman.webp` konunca o resim kullanılır.
- **Kart figür:** ayakta duran, üstü kemerli, 3:4 kart; oyuncularınki pirinç, düşmanlarınki kararmış demir metal kenarlı. İçinde portre (yoksa Grenze baş harf), altında kartın üstüne binen parşömen ad şeridi (Grenze, mürekkep), altında ince can çubuğu ve ayakta yumuşak gölge. Hafifçe nefes alır (3,4 sn). Ön sıra büyük, arka sıra %80.
- **Yerleşim:** oyuncular solda, düşmanlar sağda; aralarında boşluk: zarlar oraya, havaya iner. Az kişide tek sıra; çoksa ön sıra ve aralarına düşen arka sıra. Sağ sütun ve oyuncu kutusu kartları kapatmaz.
- **Durumlar:** sırası gelen kart yükselir, 3px vurgu kenarı ve üstünde küçük vurgu oku (parlama yok); hedef kesikli vurgu halkası; canı biten yana yatar ve renksizleşir ("yere düştü" / "baygın"); vurulan kart sarsılır, portresi bir an kızarır, üstünden kırmızı "−5" yükselir (iyileşmede yeşil "+3"). DM'in gizli düşmanları ve bağlantısı kopanlar %50.
- **Etkileşim:** hedeflenebilen karta basmak hedef seçer. Savaşta taverna gezinmesi, POV paneli ve "Bütün taverna / Canlı / POV / Yalnız POV" düğmeleri gizlidir.

### Karakter Figürü (2026-10-19)
Şimdilik masadaki herkes aynı 3D büyücü (Denys Almaral, CC-BY-4.0), sandalyede oturur pozda; DM'inki kızıl tonlu. Eğik görünümde de POV'da da aynı figür, toon gölgeli ve mürekkep çizgili. İleride başka sınıflar aynı iskeletle eklenecek.

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
