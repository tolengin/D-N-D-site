# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Şimdi:** sahibi ve arkadaş grubu. Haftalık D&D 2024 oturumlarını bu siteyle, çevrim içi bir masada oynuyorlar.
- **Sonra (hedef):** Türkçe oynayan herkes, özellikle D&D'ye **hiç başlamamış** olanlar. Ardından dünyanın her yerinden oyuncular; site yalnızca Türkçe kalmayacak.
- **Ayrıca:** yayıncılar ve DM'ler. Oturumu yayında ya da ikinci ekranda yönetip seyirciye gösterenler.
- Roller:
  - **Oyuncu:** kendi karakter kağıdını doldurur, zar atar, masaya katılır.
  - **DM:** masa açar, oyuncuların kağıtlarını ve zarlarını canlı görür, ilham verir, oyuncu çıkarır.

## Product Purpose

D&D 2024 kuralları için **açıklamalı karakter defteri** ve arkadaşlarla oynanan **çevrim içi masa**.

Başarı ölçüleri (üçü de geçerli):
1. Sahibi ve arkadaşları masada düzenli olarak gerçekten bu siteyle oynuyor.
2. Hiç bilmeyen biri kağıdı doldururken oyunu öğreniyor.
3. Sahibinin portfolyosunda yurt dışı işverenlere art direction, 3D ve yapay zekâ ile üretim becerisini gösteren bir iş oluyor.

Yayılma planı: önce arkadaş grubu, sonra Reddit ve LinkedIn'de paylaşım.

## Positioning

- **Kağıdın kendisi zar tepsisidir:** sayıya basınca, bütün hesaplar (modifiye, yetkinlik, avantaj, bitkinlik) içinde, zar atılır.
- **Her sayı yeni başlayana kendini sade dille açıklar.**
- **Masa bir yer gibidir:** elle boyanmış görünümlü, canlı 3D bir taverna, birinci şahıs bakış ve masaya yuvarlanan zarlar. Sıradan bir ayar sayfası değil.
- **Hesap, kurulum, sunucu yok:** masa kodu paylaşılır, oyuncular katılır.

## Operating Context

- **Oturum sırasında:** oyuncular kendi tarayıcılarında (çoğu bilgisayar, bazısı telefon); DM de kendi tarayıcısında masayı açık tutar. DM'in sekmesi kapanınca masa kapanır, oyuncular DM dönünce kendiliğinden geri bağlanır.
- **Yayında:** DM'in ekranı seyirciye gösterilebilir; bu ekranda arayüzün az yer kaplaması ve zar sonuçlarının okunur olması önemli.
- **Oturum dışında:** oyuncu karakterini doldurur, birden çok karakter tutar, dosyaya dışa ve içe aktarır.

## Capabilities and Constraints

- **Çalışma biçimi:** tek sayfa, sunucusuz. Her şey tarayıcıda çalışır.
  - Karakterler tarayıcının hafızasında (localStorage) durur.
  - Masa bağlantısı PeerJS ile kurulur (ücretsiz aracı sunucu).
  - 3D sahne three.js ile gelir (CDN).
  - Yayın: GitHub Pages.
- **Masa:** en çok 8 oyuncu. Bir oyuncuya diğer oyuncular hakkında yalnızca ad, karakter adı, bağlantı durumu, küçük portre, sınıf ve figür seçimi gider. Can, AC, eşya ve notlar yalnızca DM'de kalır. DM koltuğunda her zaman zar simgesi görünür (NPC portresi sızmasın).
- **Zar:** sonucu atanın tarayıcısı hesaplar; animasyon yalnızca gösterimdir. Sonuç, zar yere inmeden hiçbir yerde görünmez.
- **Dil:** şu an Türkçe arayüz, terimlerde İngilizce karşılık. **Açık karar:** başka dillere (önce İngilizce) açılış planlanıyor; yöntemi (dil seçimi, çeviri dosyaları) henüz belirlenmedi.
- **Ücret:** şu an ücretsiz.
  - **Açık karar:** sahibinin amacı olabildiğince çok kişiye ücretsiz ulaşmak. Kullanıcı çoğalırsa uygulamaya dönüştürüp gelir elde etmek ya da projeyi satmak (oyunun sahibi dahil) da düşünülüyor; karar verilmedi.
  - **Lisans kısıtı:** şu anki dayanak Wizards of the Coast Fan Content Policy ve SRD 5.2.1 (CC-BY 4.0). Fan Content Policy ücretli erişime izin vermez. Gelir yolu seçilirse yalnızca SRD içeriğine dayanmak ve "D&D" markasını addan çıkarmak gibi değişiklikler gerekir. Bu karar verilmeden ücretli özellik tasarlanmaz.
- **Sunucu:** şimdilik yok. İleride (hesap, kalıcı masa, uygulama) eklenebilir; karar verilmedi.

## Brand Commitments

- **Ad:** "Dört Element". Alt başlık: "D&D karakter defteri".
- **Dört element teması** (Ateş, Su, Toprak, Hava): her biri ayrı renk paketi ve kendi arka plan parçacıkları (kor, kabarcık, yaprak, rüzgâr). Köşe yuvarlaklığı temanın karakterini taşır: Ateş keskin, Hava yumuşak. Hava tek açık temadır.
  - **Açık karar (2026-10-18):** sahibi dört element fikrine ısınamadı. Temalar ileride D&D hikâyelerinde popüler olan **hikâye temalarıyla** (ör. Ortaçağ, Cyberpunk, Western) değiştirilecek: o tarzda oynayan oyuncular kendini özel hissetsin. Uzun bir tasarım işi olduğu için yol haritasının sonuna bırakıldı; o zamana kadar dört element geçerli.
- **Taverna:** elle boyanmış, stilize fantastik tarz (toon gölgelendirme, mürekkep çizgisi, fırça dokusu), kesit görünüm. Bütün masa görselleri bu tarzda üretilir.
- **Ton:** samimi, sade Türkçe; yeni başlayanı küçümsemeyen, adım adım anlatan.
- **Yasal metin:** sayfanın altındaki İngilizce Fan Content ve SRD atıf metinleri değiştirilmez.

## Evidence on Hand

- Çalışan site: https://tolengin.github.io/D-N-D-site/ (değişiklikler commit + push sonrası oraya gider).
- Örnek karakter: hoş geldin kartındaki "Örnek karakteri yükle".
- Görseller: `masa/` (figürler, el kareleri), `masa/taverna-npr.glb` (3D taverna), boyalı dokular.
- Yok: kullanıcı yorumu, kullanım sayısı, basın. Bunlar uydurulmaz.

## Product Principles

1. **Önce işlev, sonra sanat:** bir özellik düzgün çalışmadan süslenmez.
2. **Yeni başlayan kaybolmaz:** her ekranda "şimdi ne yapacağım" belli olur; ileri düzey bilgi ihtiyaç olunca açılır.
3. **Masa ana yerdir:** oyuncu oturum boyunca masadan ayrılmak zorunda kalmamalı; kağıt masaya gelir.
4. **Gizlilik ve adalet:** oyuncu başkasının gizli bilgisini görmez; zar sonucu önceden sızmaz.
5. **Herkese açık kalmaya çalış:** ücretsiz, hesapsız, kurulumsuz giriş; zayıf bilgisayarda da (gerekirse daha sade görünümle) oynanabilir.

## Accessibility & Inclusion

- "Hareket azaltma" ayarı açıkken zar animasyonu atlanır, sonuç doğrudan gösterilir.
- Hedef: metin zıtlığı en az 4,5:1, dokunma hedefleri en az 44 px (2026-10-17 kritiğinde bunların altında kalan yerler bulundu).
- Kitle zamanla çok dilli olacak; metinler koda gömülü kalmamalı (açık karar, bkz. Dil).
