---
name: Kervansaray
description: D&D 2024 için Türkçe açıklamalı karakter defteri ve elle boyanmış bir tavernada oynanan çevrim içi masa; arayüzü koyu bir kurşun ızgarasına oturtulmuş vitray camlardır.
colors:
  lead: "#0a080d"
  night: "#100d14"
  lead-bar: "#17141c"
  smoke-pane: "#1c1823"
  smoke-pane-raised: "#251f2e"
  well: "#0f0c13"
  hairline: "#352e40"
  opal: "#f4ede0"
  lilac-mist: "#b4abbf"
  lit-ink: "#0b0910"
  on-cobalt: "#08101f"
  on-amber: "#1f1402"
  glass-cobalt: "#4b7bec"
  glass-amber: "#f2b33d"
  glass-violet: "#9a6ae3"
  glass-teal: "#25b4c6"
  glass-rose: "#e46aa4"
  glass-copper: "#e07d43"
  glass-citrine: "#e2d35a"
  glass-ice: "#9cc3ea"
  glass-nacre: "#ddd5ea"
  glass-garnet: "#c8465f"
  state-good: "#3fc38a"
  state-bad: "#f06070"
  on-good: "#03170d"
  on-bad: "#26050a"
typography:
  display:
    fontFamily: "Eczar, Georgia, 'Times New Roman', serif"
    fontSize: "clamp(28px, 3.4vw, 44px)"
    fontWeight: 600
    lineHeight: 1.1
  numeral:
    fontFamily: "Eczar, Georgia, 'Times New Roman', serif"
    fontSize: "46px"
    fontWeight: 700
    lineHeight: 1
    fontFeature: "lnum"
  headline:
    fontFamily: "Eczar, Georgia, 'Times New Roman', serif"
    fontSize: "21px"
    fontWeight: 600
    lineHeight: 1.15
  title:
    fontFamily: "Figtree, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "14px"
    fontWeight: 700
    lineHeight: 1.2
  body:
    fontFamily: "Figtree, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Figtree, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.2
  abbr:
    fontFamily: "Figtree, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
    fontSize: "13px"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "0.14em"
rounded:
  square: "0px"
spacing:
  lead: "3px"
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  pane-y: "20px"
  pane-x: "22px"
components:
  button:
    backgroundColor: "{colors.smoke-pane-raised}"
    textColor: "{colors.opal}"
    rounded: "{rounded.square}"
    padding: "0 20px"
    height: "40px"
  button-sm:
    rounded: "{rounded.square}"
    padding: "0 14px"
    height: "32px"
  button-lg:
    rounded: "{rounded.square}"
    padding: "0 26px"
    height: "48px"
  button-accent:
    backgroundColor: "{colors.glass-cobalt}"
    textColor: "{colors.on-cobalt}"
    rounded: "{rounded.square}"
    padding: "0 20px"
    height: "40px"
  button-bad:
    textColor: "{colors.state-bad}"
    rounded: "{rounded.square}"
    height: "40px"
  button-bad-hover:
    backgroundColor: "{colors.state-bad}"
    textColor: "{colors.on-bad}"
  button-good:
    textColor: "{colors.state-good}"
    rounded: "{rounded.square}"
    height: "40px"
  button-good-hover:
    backgroundColor: "{colors.state-good}"
    textColor: "{colors.on-good}"
  icon-button:
    backgroundColor: "{colors.smoke-pane-raised}"
    textColor: "{colors.lilac-mist}"
    rounded: "{rounded.square}"
    size: "32px"
  roll-number:
    backgroundColor: "{colors.well}"
    textColor: "{colors.opal}"
    rounded: "{rounded.square}"
    padding: "5px 8px"
  roll-number-hover:
    backgroundColor: "{colors.glass-cobalt}"
    textColor: "{colors.on-cobalt}"
  dice-button:
    backgroundColor: "{colors.glass-amber}"
    textColor: "{colors.on-amber}"
    rounded: "{rounded.square}"
    padding: "0 26px 0 24px"
    height: "52px"
  pane:
    backgroundColor: "{colors.smoke-pane}"
    textColor: "{colors.opal}"
    rounded: "{rounded.square}"
    padding: "20px 22px"
  input:
    backgroundColor: "{colors.well}"
    textColor: "{colors.opal}"
    rounded: "{rounded.square}"
    padding: "8px 10px"
  chip:
    backgroundColor: "{colors.well}"
    textColor: "{colors.opal}"
    rounded: "{rounded.square}"
    padding: "5px 11px"
  chip-active:
    backgroundColor: "{colors.state-bad}"
    textColor: "{colors.on-bad}"
  tab:
    textColor: "{colors.lilac-mist}"
    typography: "{typography.title}"
    padding: "11px 22px"
  turn-lancet:
    backgroundColor: "{colors.smoke-pane}"
    textColor: "{colors.opal}"
    width: "66px"
    height: "102px"
  turn-lancet-lit:
    backgroundColor: "{colors.glass-cobalt}"
    textColor: "{colors.lit-ink}"
    height: "114px"
  guide-line:
    backgroundColor: "{colors.lead-bar}"
    textColor: "{colors.opal}"
    padding: "10px 18px"
  my-pane-ability:
    backgroundColor: "{colors.smoke-pane}"
    textColor: "{colors.opal}"
    width: "72px"
    padding: "8px 2px"
---

# Design System: Kervansaray

## Overview

**Creative North Star: "Arkadan Işık Alan Cam"**

Kervansaray'ın ekranı koyu bir kurşun ızgarasıdır; arayüzün her parçası bu ızgaraya oturtulmuş bir camdır. Cam, figürsüz ve geometriktir (revzen pencereleri gibi), süslü çerçevesi yoktur. Bir cam yalnızca başına bir şey gelince arkadan ışık alır: sıran gelince senin penceren, zar inince o zarı atanın satırı, üstüne gelince zar atan sayı. Işık bir hale değildir; camın kendi renginin açılmasıdır. Yeni bir parça tasarlanırken sorulan soru şudur: "Bu, kurşuna oturmuş bir cam mı ve ne zaman ışık alıyor?"

Tavernanın kendisi (3D, elle boyanmış, mürekkep çizgili) olduğu gibi kalır; vitray onun önünde duran arayüzdür. Masa ana yerdir: sahne ekranın tamamını kaplar, camlar kenarlara yaslanır. Oyuncunun oyun sırasında gereken her şey alttaki **kendi camında** durur (Oyna yüzü); kağıt kurulum ve ayrıntı içindir (Kur yüzü) ve masanın üstüne gelir.

Her oyuncunun masada kendi **koltuk camı** vardır (kobalt, kehribar, mor, turkuaz, gül, bakır, limon, buz; DM sedef, düşmanlar lal). Bir kişi her yerde aynı renktedir: isimliği, son atışlardaki satırı, sıra penceresi, zarları. Senin camının rengi bütün sitenin vurgusu olur. Yoğunluk orta-yüksektir; D&D kağıdı çok sayı taşır ve bu gizlenmez, ama her camda tek bir dev sayı öne çıkar ve her terim yeni başlayana kendini sade Türkçeyle açıklar.

Dört element teması (Ateş, Su, Toprak, Hava), metal arma çerçeveler, hap düğmeler, parşömen karakter kartı ve kara tahta 2026-10-21'de kalktı. **Açık karar:** ileride hikâye temaları (Ortaçağ, Cyberpunk…) gelince yalnızca cam renkleri değişir, kurşun ızgara kalır; bu yüzden kod renkleri yalnızca değişkenlerden okur.

**Key Characteristics:**
- Tek kalınlıkta kurşun çizgi (3px) her camı ayırır; çerçeve, arma, metal yok.
- Camlar köşesizdir; kemer yalnızca sıra şeridindeki pencerelerdedir (kemer = sıra).
- Her oyuncu tek bir cam rengine sahiptir ve o renk her yerde onu gösterir.
- Işık dolgudur, hale değil: olay olunca cam kendi renginin açık tonuyla dolar.
- Başlık ve büyük sayılar Eczar, arayüz Figtree; terimler İngilizce önde, Türkçe yanında.
- Sonuç zar yere inmeden hiçbir yerde görünmez.

## Colors

Üç değerli bir cam paleti: neredeyse siyah, mora çalan kurşun; koyu duman rengi cam; sıcak sedef yazı. Renk yalnızca koltuk camlarından ve üç durum renginden gelir. Değerler `index.html`'deki `:root` değişkenlerindedir (`--lead`, `--surface`, `--text`, `--g-…`).

### Primary
- **Senin Camın** (`--accent`): sabit bir renk değildir; masadaki koltuğunun camıdır (masaya bağlı değilken Kobalt). Seçili sekme, odak çizgisi, açık aç/kapa düğmesi, zar atan sayının dolgusu, kendi isimliğin ve alttaki "ben" camı bu rengi alır. Üstüne yazı gelecekse koyu Cam Mürekkebi ile.
- **Kobalt Cam / Cobalt Glass** (glass-cobalt): varsayılan vurgu ve ilk oyuncunun koltuğu.

### Secondary
- **Koltuk camları**, koltuk sırasıyla dağıtılır (DM önce, sonra oyuncular; herkesin ekranında aynı sıra): **Kehribar** (glass-amber), **Mor** (glass-violet), **Turkuaz** (glass-teal), **Gül** (glass-rose), **Bakır** (glass-copper), **Limon** (glass-citrine), **Buz** (glass-ice). **Sedef / Nacre** (glass-nacre) her zaman DM'in, **Lal / Garnet** (glass-garnet) her zaman düşmanların.
- **Kehribar** ayrıca "Zar at" düğmesinin (`--accent-2`) ve ilhamın (`--star`) rengidir.

### Tertiary
- **Durum renkleri**, anlamı her yerde aynı: **Şifa Yeşili** (state-good): bağlı, can dolu, doğal 20, iyileşme. **Yara Kırmızısı** (state-bad): durumlar (conditions), can azaldı, doğal 1, silme, ayrılma, bekleyen hasar. **Bekleme kehribarı** (`--warn`, glass-amber ile aynı değer): bağlanıyor, can yarıda. Dolu zemin üstünde yazı koyu olur (on-good, on-bad).

### Neutral
- **Kurşun / Lead** (lead): camların arasındaki çizgi ve ızgaraların zemini. Taverna yüklenemezse sayfa zemininde sekiz köşeli yıldızlı soluk bir kurşun deseni.
- **Gece** (night): sayfanın zemini.
- **Kurşun Çubuk** (lead-bar): üst çubuk, kağıdın şeridi, panel başlıkları, rehber satırı, tepsi.
- **Duman Camı** (smoke-pane) ve **Açık Duman Camı** (smoke-pane-raised): camların ve iç kutuların, düğmelerin zemini.
- **Kuyu** (well): yazı alanları ve zar atan sayıların koyu oyuğu.
- **İnce Çizgi** (hairline): alan, düğme ve başlık altı çizgileri (1px). Kurşun değildir; bir camın içindeki ayrımı gösterir.
- **Sedef Yazı / Opal** (opal): ana yazı. **Leylak Sisi / Lilac Mist** (lilac-mist): ikincil yazı, Türkçe karşılıklar, etiketler.
- **Cam Mürekkebi** (lit-ink): ışık almış (koltuk rengiyle dolmuş) camın üstündeki koyu yazı.

### Named Rules
**The Three Values Rule.** Bir camda üç değer vardır: kurşun, cam, sedef yazı. Dördüncü değer yalnızca ışıktır (camın kendi renginin açılması). Gradyan, doku ya da süs tonu eklenmez.

**The Seat Glass Rule.** Bir kişi her yerde tek renktir: isimlik, son atış satırı, sıra penceresi, zar ve savaş kartı aynı koltuk camını taşır. Koltuk camları arasında kırmızı ve yeşil yoktur, çünkü onlar durum anlatır.

**The Meaning Is Fixed Rule.** Yeşil, kırmızı ve kehribar yalnızca durum anlatır (iyi / tehlike / bekliyor). Süs için kullanılmaz; koltuk camı da durum anlatmak için kullanılmaz.

**The Variables Only Rule.** Yeni kod sabit renk yazmaz; `--lead`, `--surface`, `--line`, `--text`, `--muted`, `--accent`, `--g-…`, `--good`, `--bad`, `--warn` kullanır. Hikâye temaları geldiğinde yalnızca bu değerler değişecek.

## Typography

**Display Font:** Eczar (Georgia, Times New Roman yedekleriyle)
**Body Font:** Figtree (system-ui yedeğiyle)

**Character:** Eczar sıcak, keskin uçlu bir kitap harfidir; karakter adı, cam başlıkları ve büyük sayılar onunla yazılır. Figtree sade ve yuvarlak hatlı bir grotesk; bütün arayüz, etiket ve açıklamalar onunla. Hiyerarşiyi çerçeve değil yazı taşır. İkisi de Google Fonts'tan gelir.

### Hierarchy
- **Display** (Eczar 600, clamp(28px, 3.4vw, 44px), 1.1): kağıttaki karakter adı (çerçevesiz alan, kesikli alt çizgi).
- **Numeral** (Eczar 700, 1): her camın dev sayısı. Yetenek modifiyesi 46px (telefonda 34px), can 52px, AC ve inisiyatif 40px, kendi camında yetenek ve can 36px, sıra penceresinde inisiyatif 20px. Rakamlar dik (lining), tablolarda eşit genişlikte.
- **Headline** (Eczar 600, 21px, 1.15): cam başlıkları ("Saving Throws"); yanında Türkçe karşılığı Figtree 500, 13px, Leylak Sisi.
- **Title** (Figtree 700, 14px, 1.2): düğmeler, sekmeler, satır adları.
- **Body** (Figtree 400, 15px, 1.45): genel metin. Açıklama paragrafları 72–74ch'yi geçmez.
- **Label** (Figtree 700, 12px): alan etiketleri; yanında Türkçe karşılık 500 ağırlıkta.
- **Abbr** (Figtree 800, 13px, harf aralığı .14em): yetenek kısaltmaları (STR, DEX…); kağıtta senin camının açık tonunda, kendi camında soluk.

### Named Rules
**The One Giant Number Rule.** Her camda tek bir dev sayı vardır ve göz önce ona gider (yetenekte modifiye, canda kalan can, AC'de zırh sınıfı). Skor, en çok can gibi ikinci sayılar küçük ve soluktur.

**The Two Tongues Rule.** Her D&D terimi iki dilde durur: İngilizce terim önde ve kalın, Türkçe karşılığı yanında ya da altında, soluk ve ince. Sıra hiçbir yerde ters çevrilmez. İngilizce büyük harfli etiketlerde `lang="en"` kullanılır (Türkçe büyük harf kuralı "HİT POİNTS" yazmasın).

**The Hint Floor Rule.** Okunması gereken hiçbir yazı 12px'in altına inmez.

## Layout

**Masa (Oyna yüzü):** sahne ekranın tamamıdır. Üst çubuk masa ekranında yukarı kayar (aşağıda: Kayan Üst Çubuklar); üst ortada sıra pencereleri asılı durur. Solda dik bir kurşun şerit içinde yalnız ikonlu kare camlar (görünüm araçları), sol altta yakınlaştırma. Sağ üstte yüzen bir sütun: Son atışlar, altında Düşmanlar. Alt ortada kendi camın, üstünde rehber satırı; sağ altta "Zar at". Masa içi ölçüler **birim** (`--u`) ile verilir: ekrana sığan en büyük 16:9 kutunun genişliğinin %1'i. Ekran genişleyince camlar büyümez, tavernanın daha çok yeri görünür.

**Kağıt (Kur yüzü):** en çok 1320px genişliğinde ortalanmış tek sütun (yanlarda 20px). Karakter başlığının altında altı yetenek camı, sonra iki sütun: solda 336px sabit sütun (kurtarma zarları, beceriler, pasifler), sağda esnek alan (savaş değerleri, sekmeler). Camlar arası 16px, cam içi 20px 22px.

Kırılma noktaları: 1180px'te başlığın yan kutuları alta iner; 980px'te tek sütun, yetenekler üçlü; 820px'te can kutusu tek sütun; 640px dik telefonda masa büyütülür ve camlar sahnenin altına sıralanır, kendi camın "Zar at"ın üstünde tam genişlikte sabitlenir; 560px telefon düzenidir (üst çubukta yazılar gizlenir, ikon kalır).

### Named Rules
**The Stage Owns The Screen Rule.** Masada sahne ekranın tamamıdır; camlar kenarlara yaslanır ve oyun masasının ortasını asla kapatmaz.

**The Two Faces Rule.** Oyuncu oyun sırasında kağıdı açmak zorunda kalmaz: can, AC, altı yetenek, saldırılar ve "Kağıdım" alttaki kendi camındadır (Oyna). Kağıt kurulum ve ayrıntı içindir (Kur) ve masanın üstüne gelir.

## Elevation & Depth

Derinlik üç katmanla verilir: arkada taverna (ya da kurşun deseni), ortada kurşun ızgaraya oturmuş camlar, önde tepsi, bildirim ve açılır kutular. Camlar tek, aşağı düşen yumuşak bir gölge taşır; asıl ayrımı gölge değil kurşun çizgi yapar. Bulanıklık (blur) yalnızca kağıt açılınca arkadaki tavernada kullanılır.

### Shadow Vocabulary
- **Cam gölgesi** (`box-shadow: 0 16px 34px -14px rgba(0,0,0,.75)`, `--shadow`): camlar, şeritler, ızgaralar, tepsi, bildirim.
- **Yüzen düğme gölgesi** (`box-shadow: 0 10px 24px -10px rgba(0,0,0,.75), 0 2px 6px rgba(0,0,0,.35)`): "Zar at" ve hedef etiketi.
- **Şerit gölgesi** (`box-shadow: 0 14px 28px -18px rgba(0,0,0,.85)`): kağıdın üst şeridi; altından kayan satırlar şeridin altına girer.
- **Taverna gölgeleri** (`drop-shadow`): figür, sandalye, isimlik ve zarlar masaya oturmuş görünsün diye.

### Named Rules
**The Backlight Rule.** Işık bir olaya cevaptır ve hale değil dolgudur: cam, kendi renginin açık tonuyla (`--lit`: vurgu %34 + cam) ya da tam koltuk rengiyle dolar. Sırası gelenin penceresi koltuk rengiyle dolar ve uzar; en yeni zar satırı atanın renginde ışık alıp 1,6 sn'de söner; zar atan sayı üstüne gelince senin renginle dolar. Hareket azaltma açıkken geçiş yoktur. Durağan bir düğme, çerçeve ya da logo ışık almaz.

**The Sheet Over Tavern Rule.** Kağıt ve DM ekranı ayrı bir sayfa olmaz; kararmış ve bulanık tavernanın üstünde açılır (`filter: blur(7px) brightness(.45) saturate(.8)`).

## Shapes

**Kare camlar.** Camlar, düğmeler, alanlar, çipler, sekmeler, şeritler köşesizdir (0px). Biçim dili tek kalınlıkta kurşun çizgiyle kurulur: bir ızgaranın zemini kurşundur, aradaki 3px boşluk kurşun çizgi olarak görünür, her parça kendi cam zeminini taşır.

**Kemer yalnızca sıra şeridinde.** (2026-10-21, kullanıcının kararı.) Yalnızca savaş sırasındaki pencereler (lanset) ve içlerindeki küçük portreler kemerlidir: kemerin yarıçapı genişliğin yarısıdır, alt köşeler düz. Portre (kağıtta 118×140px), isimlikteki pencere, kendi camındaki "ben" penceresi, karakter listesi, düşman portreleri, savaştaki kart figürler ve logo kare camdır.

**Durum işareti eşkenar dörtgendir** (45° döndürülmüş kare): yetkinlik, büyü yuvası, ölüm zarı, bağlantı noktası.

D&D'nin kendi simgeleri biçim olarak kalır: AC bir kalkan, can bir çubuk.

### Named Rules
**The One Lead Weight Rule.** Kurşun her yerde 3px'tir (`--lw`): camların arası, camın dış kenarı, şeritler. İkinci bir kalınlık, metal çerçeve, arma ya da iç süs çizgisi yoktur. Camın içindeki ayrımlar 1px ince çizgidir.

**The Arch Means Turn Rule.** Kemer yalnızca sıra şeridinde görülür. Portre, kart, düğme ya da panel kemerli olmaz; ekranda bir kemer görülürse o, savaşta kimin sırası olduğunu gösteren penceredir.

**The One Pane Per Area Rule.** Birbirine ait parçalar (altı yetenek; AC + inisiyatif + hız + can; can zarı + durumlar) tek bir kurşun ızgarada durur; çerçeve içine çerçeve konmaz.

## Components

### Buttons
Tek sistem. Köşesiz cam; durum dolguyla anlatılır, parlamayla değil.
- **Shape:** kare (0px); yalnız ikonlu olanlar kare kutu.
- **Üç boy:** küçük `.sm` 32px (cam içi, satır işleri), normal 40px (çubuklar, ana işler), büyük `.lg` 48px (ilk ekrandaki büyük seçenekler). **Dokunmatik ekranda** (pointer: coarse) sırasıyla 40 / 44 / 52px; masadaki şerit düğmeleri 44px.
- **İç boşluk (kullanıcının kuralı, 2026-10-20):** yandaki boşluk üstteki boşluğun **2 katı**. Üstteki boşluk = (boy − 2px kenar − ikon) / 2 olduğundan yandaki boşluk boydan hesaplanır: `padding-inline: calc(var(--h) - 2px - var(--ic))`. Sonuç: küçük 14px, normal 20px, büyük 26px; dokunmatikte 22 / 24 / 30px. Düğmeye elle `padding` yazılmaz. İstisna: yalnız ikonlu düğmeler (boşluk yok), zar atan sayılar, sekmeler (11px 22px), "Zar at" (0 26px 0 24px).
- **Yapı:** ikon + yazı; ikon normalde 18px, küçükte 16px, büyükte 20px (`--ic`). İkon tek başına kalırsa `title` ve `aria-label` zorunlu.
- **Dört tür:** **Normal** (açık duman camı, ince çizgi, Figtree 700 14px; üstüne gelince kenar senin rengine döner ve cam ışık alır; basınca 1px iner). **Accent** (senin camının rengiyle dolu, koyu yazı; ekranda tek ana iş; üstüne gelince %12 aydınlanır). **Bad** ve **Good** (yalnız yazı ve kenar renkli; üstüne gelince dolar ve yazı koyu olur).
- **Aç/kapa (aria-pressed):** açıkken kenar senin renginde, cam ışık almış (`--lit`). Kapalıyken normal düğmedir; **asla soluklaşmaz**.
- **Disabled:** %45 görünürlük.
- **Icon button:** 32px kare (kapat, sil, eksi/artı). İkon çizimdir (SVG). Silme düğmesi üstüne gelince kırmızı.

### Zar Atan Sayılar (imza parçası)
Kağıdın kendisi zar tepsisidir: zar atan her sayı bir düğmedir. Koyu kuyu zemini, ince çizgi, kalın eşit genişlikte rakam; sağ altta 6px'lik küçük üçgen "zar köşesi" (yazılır alanlardan ayrılsın). Üstüne gelince senin camının rengiyle dolar. Büyük hâli (yetenek modifiyesi, inisiyatif) Eczar 40–46px; üçgen yerine sol üstte 18px **d20 işareti** taşır (2026-10-27: yeni başlayanlar büyük sayıyı yazı alanı sanıyordu). Bu davranış başka öğeye verilmez: renkle dolan sayı zar atar.
- **The Die Or Field Rule.** Bir sayı ya zardır ya yazılır alandır, ikisine birden benzemez. Zar = kuyu + zar işareti; yanındaki yazılır ikinci sayı (yetenek skoru) kuyu taşımaz: karakter adı gibi kesikli alt çizgi, küçük ve soluk.

### Zar At Düğmesi (imza parçası)
Sağ altta sabit, yazılı, köşesiz **kehribar cam**: d20 ikonu + "Zar at", 52px, 3px kurşun kenar, Figtree 800 16px. Avantaj ya da dezavantaj açıkken düğmede de yazar ("Zar at · Avantaj"). Yuvarlak yazısız balon olmaz. Zar tepsisini açar. Zar ve sonuç plakası atanın koltuk camını alır.

### Durum İşaretleri (State Marks)
Tek dil, her yerde aynı: **boş eşkenar dörtgen** = yok; **dolu** = var (yetkin, yuva dolu, bağlı); **çift halkalı dolu** = uzmanlık; **kırmızı dolu** = başarısız / harcandı (ölüm zarı); **üstü çizili ve soluk** = yere düştü / öldü (düşman satırı, sıra penceresi); **kesikli çizgi** = seçili hedef; **koltuk rengiyle dolu** = şimdi (sıra).

### Panes / Cards (Cam)
- **Corner Style:** köşesiz (0px).
- **Background:** Duman Camı; iç kutular Açık Duman Camı.
- **Border:** 3px kurşun (`--lw`).
- **Shadow Strategy:** cam gölgesi (bkz. Elevation & Depth).
- **Internal Padding:** tek cam 20px 22px; ızgara içindeki parçalar 16px 18px.
- **Izgara:** bir alanın parçaları kurşun zeminli bir ızgarada ayrı camlardır (aradaki boşluk 3px). Başlık içerikten 1px ince çizgiyle ayrılır; Eczar başlık + Türkçe karşılık, sağda isteğe bağlı küçük düğme.

### Inputs / Fields
- **Style:** kuyu zemini, 1px ince çizgi, köşesiz, 8px 10px.
- **Hover:** kenar senin rengine doğru yarı karışım. **Focus:** kenar senin renginde, içte 1px aynı renk çizgi (hale yok).
- **Özel:** karakter adı alanı çerçevesizdir; yalnız kesikli alt çizgi ve Eczar display.
- **Disabled:** DM bir oyuncunun kağıdını izlerken bütün alanlar salt okunurdur.
- **Sürgü (ses paneli):** 8px koyu oyuk yiv, dolu kısmı senin renginde; düğme 18px kare sedef, 3px kurşun kenarlı.

### Chips
Köşesiz, kuyu zemini, kalın İngilizce ad + soluk Türkçe karşılık. Durum çiplerinde seçili hâl Yara Kırmızısı ile dolar. Karakter oluşturmadaki beceri çipleri seçilince senin rengine %18 boyanır.

### Navigation
- **Üst çubuk:** Kurşun Çubuk zemini, altında 3px kurşun. Solda logo (kare küçük revzen camı, senin camının renginde) + "Kervansaray" Eczar 24px ve alt başlık; sağda kayıt durumu, Açıklamalar, Karakterler, Masa, raptiye, ses.
- **Sekmeler:** alt çizgili; seçili sekme senin renginde yazı ve 2px alt çizgi. Dar ekranda yatay kayar.
- **Masa araç şeridi:** sol kenarda dik kurşun şerit, içinde 44px yalnız ikonlu kare camlar; adları `title` ve ekran okuyucu yazısıyla. Açık olan ışık alır.

### Sıra Pencereleri (Turn Lancets)
Savaş açıkken üst ortada kurşun bir şerit: solda "Savaş · Tur N" ve kimin sırası, ortada inisiyatife göre dizili kemerli pencereler (66×102px; içinde kemerli küçük portre, Eczar inisiyatif, ad), sağda DM için "Sıradaki / Sırayı başlat" ve "Bitir". Her pencere sahibinin camıyla %18 boyanır; düşmanlar lal. **Sırası gelenin penceresi koltuk rengiyle tamamen dolar ve 114px'e uzar**; yazı Cam Mürekkebi olur. Kendi pencerende ad kalın. Telefonda sahnenin altında.

### Son Atışlar (Log)
Sağ üstte yüzen kurşun sütun (17 birim genişlik): Kurşun Çubuk başlık "Son atışlar", altında her atış ayrı bir cam satırı, atanın camıyla %16 boyanmış; solda ad, sağda Eczar sonuç. En yeni satır atanın renginde %62 ışık alıp 1,6 sn'de söner. Doğal 20 sonucu yeşil, doğal 1 kırmızı. Normalde son altı atış ve yalnız sonuç; üstüne gelince sola doğru 40 birime genişler, ayrıntılar ve saatler okunur. Başlıktaki düğmeyle kapanır.

### Düşmanlar Panosu
Son atışlarla aynı kurşun sütun. Her düşman bir cam satırı: kare lal portre (yoksa baş harf), ad (Eczar), "6/10 can · AC 15" (oyuncuda yalnız DM izin verdiyse), ince can çubuğu. Satıra basınca hedef seçilir (kesikli çizgi); sırası gelenin satırı lal ile %45 dolar; canı biten soluk ve üstü çizili.

### Taverna İsimliği
Oyuncunun koltuk camıyla %26 boyanmış koyu cam levha, kurşun kenarlı; solda kare küçük pencere içinde portre (pencere çerçevesi koltuk renginde), köşesinde bağlantı işareti. Ad Eczar 700, altında karakter adı. Kendi isimliğin daha çok ışık alır (%52). DM'in portresi yerine her zaman zar simgesi, rengi sedef. Bağlantısı kopanın isimliği %62 soluk, portresi gri. Seçili hedefin isimliği kesikli çizgiyle çevrilir.

### Kendi Camın (Oyna yüzü)
Masada alt ortada, kurşun ızgaralı bir sıra cam (eski parşömen karakter kartının yerine). **Ana sıra:** "ben" camı (224px; senin renginle %30 dolu, kare portre penceresi, Eczar ad, "1. seviye Dwarf Paladin"; basınca kağıt açılır), can camı (Eczar 36px kalan / 17px en çok, can çubuğu), AC camı (kalkan içinde Eczar 28px), altı yetenek camı (72px; kısaltma, Eczar 36px modifiye, skor; her biri zar atar, üstüne gelince senin renginle dolar). **Üst sıra:** saldırılar (ad + vuruş ve hasar zarı), "Kağıdım", ayrıntı aç/kapa. **Ayrıntı camı:** kurtarma zarları (durum işaretiyle), can işlemleri, yetkinlik / hız / inisiyatif / pasif algı, ilham. Sahneyle birlikte ölçeklenir; dik telefonda "Zar at"ın üstünde tam genişlik.

### Rehber Satırı
Kendi camının üstünde, Kurşun Çubuk zeminli, 3px kurşun kenarlı tek satır (en çok 640px, Figtree 600 16px, ortalı): yeni başlayana o an ne yapacağını söyler. İçindeki eylem adları senin renginin açık tonunda. Üstteki "Açıklamalar" kapalıysa görünmez.

### Sade / Tam Görünüm (2026-10-20)
Kağıdın iki görünümü; seçici kağıdın şeridinde, "Masaya dön"ün solunda (kuyu zemininde iki kare düğme; seçili olan senin renginde kenar + %18 zemin, dolgu değil). Seçim karakterle saklanır; yeni karakterler Sade, eski kayıtlar Tam açılır; DM'in izlediği kağıt hep Tam. Üçüncü seviye yok.
- **Sade (yeni başlayan):** portre, ad, tür, sınıf, geçmiş, seviye, ilham; altı yetenek; kurtarma zarları; yalnız yetkin olunan beceriler ("Bütün beceriler (18)" ile açılır); AC, inisiyatif, hız, can; can zarı; yalnız seçili durumlar ("Durum ekle" ile açılır); ölüm zarları yalnız can 0'dayken ya da işaret varken; saldırıda "Yetkin" ve "Ek bonus", büyüde süre / menzil / C·R·M sütunları, yuvası olmayan büyü seviyeleri ve ileri düzey alanlar gizli.
- **Sade'de "Yetenek kulesi" (2026-10-27, oyunu bilmeyenler "her şey iç içe" dedi):** kurtarma zarı (Save · Kurtarma, durum işaretiyle) her yetenek camının altında durur, soldaki "Saving Throws" camı gizlenir. Camların altındaki açıklamalar yerine bölüm başına tek satır (yetenekler ızgarasının ve savaş değerlerinin altında); terimin ayrıntısı başlığın üstüne gelince (`title`). Savaş değerlerinde **can önde**, AC / inisiyatif / hız altında. Başlıktaki "1. seviye Dwarf Fighter" satırı alttaki alanları tekrarladığı için gizli. "-", "—", "yok" her iki görünümde boş sayılır.
- **Sade'nin okuma sırası (2026-10-27, UX baştan):** tek sütun, yukarıdan aşağı ve her bölüm üsttekinden türer: **kimlik** (portre, ad, "Dhampir · Fighter · Soldier" okuma satırı + "Değiştir" kalemi; alanlar yalnızca kalemle ya da tür ve sınıf boşken açılır; ad alanının kesikli çizgisi adın boyu kadar; yanda Seviye ve İlham) → **yetenekler** (içinde Save) → **beceriler** (yalnız yetkin olunanlar, yan yana) → **savaş** (can önde; AC, inisiyatif, hız; altında **saldırılar**) → **dinlenme ve durumlar** (Uzun dinlenme can zarının yanında) → **sekmeler** (Envanter, Özellikler, Notlar; Saldırılar sekmesi Sade'de yok). Kağıt kurulum ve öğrenme içindir; oyun sırasında hasar masadan gelir.
- **Okunur saldırı satırı (Sade):** ad (Eczar 18px), vuruş zarı, hasar yazısı, hançerli hasar zarı, soluk not, sağda kalem. Kalemle satır yazılabilir hâle geçer (yetenek seçimi ve sil görünür, sonda "bitti" işareti); yeni saldırı yazılabilir hâlde açılır. İki hâlde sütunlar aynıdır, sayılar alt alta durur.
- **Sade'de kağıdın geri kalanı (2026-10-27):** can camında "Miktar / Hasar al / İyileş" yok (hasar masadan gelir); kalan can kesikli alt çizgili yazılır sayı, yanında 1'er azaltan / artıran −/+ ikon düğmeleri; "Geçici can" yalnızca 0'dan büyükken. Can zarı camı **Rest · Dinlenme** olur: okunur satır "Can zarın: d10 · 1 / 1 kaldı" ve yan yana iki düğme, **Kısa dinlenme** (kamp ateşi ikonu; bir can zarı atar; can doluyken zar harcamaz, "Canın zaten dolu" der) ve **Uzun dinlenme** (ay). En yüksek can da kesikli çizgili yazılır sayıdır; geçici can alanı bir kez görününce ancak görünüm ya da karakter değişince gizlenir. Envanterde yalnız adet, eşya ve sil (ağırlık, kuşanma ve yük satırı Tam'da). Özellik kutuları boşken 5,5em, yazdıkça uzar. **Paralar iki görünümde de beşi birden** (CP, SP, EP, GP, PP; kullanıcının kararı).
- **The Never Hide Data Rule.** Sade dolu bir alanı asla saklamaz; içi dolu parça görünür kalır. Yazarken bir alan yalnız görünür hâle geçebilir; gizlenmesi görünüm ya da karakter değişince olur. **İstisnalar** (bilgi kaybolmaz, Tam'da durur): zırh türü ve kalkan kutusu (AC'yi değiştirmiyor, yalnızca not yazıyor; yeni başlayanı yanıltıyordu), can zarı türü menüsü (okunur satırda yazar), eşya ağırlıkları ve kuşanma düğmesi.

### Karakter Oluşturma (2026-10-20)
Kağıdın yerine geçen tek cam (en çok 1040px): üstte Eczar 30px başlık ve sağda adım düğmeleri (numara kutusu + ad; şu anki adım senin renginde, geçilenlere basınca geri dönülür; telefonda yalnız numara), ortada bir soru (Eczar 24px), tek satır açıklama ve seçenekler, altta Vazgeç | Geri · Devam (ana iş).
- **Seçenek döşemesi:** kuyu zemini, ince çizgi, gölgesiz; İngilizce ad Eczar 22px + Türkçe karşılık, tek satır açıklama, altta soluk kısa bilgi. Seçili: senin renginde kenar + %14 zemin + içte 1px çizgi (dolgu değil). Hazır karakterlerde üstte 4:3 portre.
- **The Four Choices Rule.** Bir ekranda en çok dört seçenek: önce yeni başlayana önerilen dört, gerisi "Bütün seçenekler (N)"; "Önerilen" etiketi yalnız hepsi açıkken görünür.
- **Yetenekler:** altı kutu; Eczar 34px modifiye, altında standart dizi seçimi, geçmiş artışı senin renginde "+2".

### Bildirim ve Geri Al
Sol altta (masada üst ortada) Kurşun Çubuk zeminli bildirim: solda senin renginle dolu kare içinde Eczar sonuç, kalın başlık + soluk alt satır; doğal 20'de yeşil, doğal 1'de kırmızı. Geri alınabilir bir iş (satır silme) sorulmadan yapılır, bildirimde küçük **"Geri al"** düğmesi (geri ok ikonu) 7 sn durur. Onay kutusu yalnız geri alınamayan işlerde (uzun dinlenme, karakter silme).

### Bekleyen Hasar
DM'in kendi (ya da bir düşman adına attığı) hasar zarı kendiliğinden vurulmaz. Zar yere inince sağ altta, hedef etiketinin üstünde kırmızıya %14 boyanmış, 3px kurşun kenarlı bir cam çıkar: hançer ikonu, "Goblin → Kara" (Eczar 17px), altında zarın adı ve hesabı; −/+ arasında Eczar 24px sayı alanı ve "Yarısı"; değiştirilmişse sağda soluk "zar 9". Altta "Vazgeç" ve tek ana iş "Hasarı vur". En çok dört kart üst üste. Oyuncuların zarları kendiliğinden uygulanır.

### Hedef Etiketi
Seçili hedef "Zar at"ın hemen üstünde, senin renginde 1px kenarlı köşesiz etiket: hedef ikonu, "→ Goblin (5/7 can, AC 12)", kaldırma düğmesi. DM bir düşman adına atıyorsa başta düşmanın adı. İsimliğe basınca DM'de açılan küçük cam (ad + "Hedef yap") aynı dili kullanır.

### Kağıt Masada
Masadan kağıda geçince kağıt ayrı bir sayfa olmaz: kamera koltuğun arkasından ve yukarısından göz hizasına iner (0,9 sn, yumuşak başlayıp yumuşak durur; figürler ve POV paneli bu sırada çekilir), kağıt aşağıdan kalkar (0,42 sn, hafif büyüyerek), arkada taverna kararır ve bulanıklaşır. Üstte **kağıdın şeridi**: kağıtla aynı genişlikte, yapışkan, Kurşun Çubuk zeminli; solda karakterin adı (Eczar 20px) ve soluk "1. seviye Dwarf Paladin", sağda Sade/Tam ve "Masaya dön" (Esc de kapatır). DM ekranında aynı şerit. Kapatınca kağıt iner, kamera 0,7 sn'de yükselir. Yasal yazı kağıdın içinde en altta, kararmış taverna üstünde açık renk. Telefonda ve hareket azaltmada kamera kımıldamaz.

### Kayan Üst Çubuklar, Raptiye ve Büyütme Tutamakları
- **Masa ekranında üst çubuk ve durum çubuğu yukarı kayar**, sahne bütün ekranı kaplar. Üst ortada asılı küçük "Menü" tutamağı (Kurşun Çubuk zemini, kurşun kenar); en üst kenara gelince ya da tutamağa basınca çubuklar iner. Telefonda ve tam ekranda yok.
- **Menüyü sabitle (raptiye):** üst çubukta aç/kapa ikon düğme; basılıyken çubuklar kaymaz. Yalnız çubukların kaydığı yerde görünür.
- **Büyütme tutamağı:** köşede 22px kurşun kare, iki çapraz soluk çizgi; üstüne gelince belirginleşir. POV panelinin sağ altında, sağ sütunun sol altında. **Yandaki tutamak:** kenarın ortasında 12×56px kurşun çubuk, iki dik çizgi; yalnız yatayda genişletir. Büyüklük tarayıcıda hatırlanır. Telefonda yok.
- **Yalnız POV:** araç şeridinde aç/kapa. Açıkken POV paneli bütün sahneyi kaplar, eğik görünüm ve isimlikler çizilmez; karakter adı sol altta. Son atışlar, düşmanlar ve kendi camın yerinde kalır. Telefonda yok.

### Savaş Sahnesi: Orman Açıklığı
Savaş başlayınca taverna yerine 2D bir orman açıklığı gelir (0,8 sn, parlaktan ve bulanıktan açılarak); ortada bir an "ORMAN YOLU / Savaş!" yazısı (Eczar). Savaş bitince solarak taverna döner. Arka plan elle boyanmış tarzdadır (gün batımı, çam sırtları, ortada açık toprak, mürekkep çizgiler; `masa/savas/orman.webp` konunca o resim).
- **Kart figür:** ayakta duran kare 3:4 kart: kurşun zemin, içte koltuk camının rengi; içinde portre (yoksa Eczar baş harf), altında karta binen Kurşun Çubuk ad şeridi (kendi kartında koltuk rengine boyalı), ince can çubuğu, ayakta yumuşak gölge. Hafifçe nefes alır (3,4 sn). Ön sıra büyük, arka sıra %80. Oyuncular solda, düşmanlar sağda; zarlar aradaki boşluğa iner.
- **Durumlar:** sırası gelen kart yükselir, ad şeridi koltuk rengiyle dolar, üstünde aynı renkte küçük ok; hedef kesikli çizgi; canı biten yana yatar ve renksizleşir; vurulan kart sarsılır, portresi bir an kızarır, üstünden "−5" yükselir (iyileşmede "+3"). Gizli düşmanlar ve bağlantısı kopanlar %50.

### Karakter Figürü
Şimdilik masadaki herkes aynı 3D büyücü (Denys Almaral, CC-BY-4.0), sandalyede oturur pozda; toon gölgeli ve mürekkep çizgili.

## Do's and Don'ts

### Do:
- **Do** yeni bir parçayı önce "kurşuna oturmuş bir cam mı, ne zaman ışık alıyor?" sorusuyla tasarla (Arkadan Işık Alan Cam).
- **Do** kurşunu her yerde 3px (`--lw`) kullan; bir alanın parçalarını kurşun zeminli bir ızgarada ayrı camlar olarak diz.
- **Do** bir kişiyi her yerde kendi koltuk camıyla göster (`--g`); senin camın `--accent`'tir.
- **Do** ışığı dolguyla ver (`--lit` ya da koltuk rengi); hareket azaltmada geçişsiz.
- **Do** her camda tek bir dev Eczar sayı öne çıkar; ikinci sayıları küçült ve soldur.
- **Do** her D&D terimini İngilizce önde, Türkçe yanında ver; açıklamayı sade, yeni başlayanı küçümsemeyen bir dille yaz.
- **Do** butonları yalnız üç boydan (32 / 40 / 48px) ve dört türden (normal, accent, bad, good) seç; iç boşluğu boydan hesapla.
- **Do** dokunma hedeflerini en az 44px, metin zıtlığını en az 4,5:1 yap.
- **Do** ikon tek başına kaldığında ona `title` ve `aria-label` ver.

### Don't:
- **Don't** metal çerçeve, arma, baklava, gradyan süs ya da hale ekleme; ışık camın kendi renginin açılmasıdır.
- **Don't** kemeri sıra şeridi dışında hiçbir yere verme (portre, kart, düğme, panel, logo kare kalır).
- **Don't** zar sonucunu zar yere inmeden hiçbir yerde gösterme (bildirim, son atışlar, sayı, geçmiş).
- **Don't** koltuk camları arasına kırmızı ya da yeşil koyma; yeşil / kırmızı / kehribarı süs için kullanma.
- **Don't** Yara Kırmızısı ya da Şifa Yeşili dolgusu üstüne beyaz yazı koyma; `--on-bad` / `--on-good` (koyu) kullan.
- **Don't** ×, −, + gibi klavye işaretlerini ya da emojiyi ikon yerine kullanma; ikonlar aynı çizgi kalınlığında SVG'dir.
- **Don't** kapalı bir aç/kapa düğmesini soluklaştırma.
- **Don't** 12px'in altında okunması gereken yazı kullanma.
- **Don't** sayfanın altındaki İngilizce Fan Content ve SRD atıf metnine dokunma.
