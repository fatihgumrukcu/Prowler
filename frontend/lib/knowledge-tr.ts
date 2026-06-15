/**
 * Turkish translations for check knowledge-base fields.
 * Overrides the English why_it_matters / how_to_fix coming from the backend.
 */

interface KBEntry {
  why: string
  fix: string
}

export const KNOWLEDGE_TR: Record<string, KBEntry> = {
  meta_title: {
    why: "Title etiketi, hem sıralama hem de SERP tıklama oranı için en güçlü sayfa içi sinyaldir.",
    fix: "50–60 karakter uzunluğunda, anahtar kelime açısından zengin benzersiz bir başlık yazın. Birincil anahtar kelimeyi başa yerleştirin.",
  },
  meta_description: {
    why: "Meta açıklamaları SERP snippet'leri olarak görünür ve tıklama oranını önemli ölçüde etkiler.",
    fix: "Hedef anahtar kelimeyi ve net bir eylem çağrısı içeren, 120–160 karakter uzunluğunda ilgi çekici bir özet yazın.",
  },
  heading_h1: {
    why: "H1, arama motorlarına sayfanın birincil konusu hakkında en net yapısal sinyali verir.",
    fix: "Her sayfaya hedef anahtar kelimeyi içeren ve içeriği doğru tanımlayan tam olarak bir H1 ekleyin.",
  },
  heading_h2: {
    why: "H2 başlıkları içeriği taranabilir bölümlere ayırır ve tarayıcılar için konusal alaka düzeyini güçlendirir.",
    fix: "Uzun içerikleri, açıklayıcı ve anahtar kelime ilişkili H2 bölümlerine ayırın.",
  },
  heading_hierarchy: {
    why: "Başlık seviyelerini atlamak (örn. H1 → H4), arama motorları ve ekran okuyucuların kullandığı belge yapısını bozar.",
    fix: "Başlıkların katı bir iç içe geçme sırasını takip ettiğinden emin olun — hiçbir zaman seviye atlamayın.",
  },
  heading_breakdown: {
    why: "Birden fazla H1 etiketi, birincil konu sinyalini zayıflatır ve arama motorlarını hangi konunun daha önemli olduğu konusunda karıştırır.",
    fix: "Sayfa başına tam olarak bir H1 kullanın; fazladan H1'leri H2 veya H3'e dönüştürün.",
  },
  content_word_count: {
    why: "Çok az içeriğe sahip sayfalar arama motorları tarafından 'zayıf içerik' olarak değerlendirilir.",
    fix: "En az 300 kelimelik benzersiz, anlamlı içerik hedefleyin; rekabetçi konular için 800+ kelime daha iyi sonuç verir.",
  },
  content_text_html_ratio: {
    why: "Çok düşük metin/HTML oranı, içeriğe kıyasla aşırı markup ile şişirilmiş bir sayfaya işaret eder.",
    fix: "Gereksiz satır içi stil ve markup'ı azaltın; görünür ve kullanışlı metin içeriğini artırın.",
  },
  content_js_render: {
    why: "Yalnızca JavaScript çalıştıktan sonra görünen içerik, JS'yi tam işlemeyen arama motorları tarafından indekslenemeyebilir.",
    fix: "Kritik içeriğin ilk HTML yanıtında mevcut olması için sunucu taraflı rendering (SSR) veya statik oluşturma (SSG) uygulayın.",
  },
  content_desc_title_dupe: {
    why: "Aynı başlık ve meta açıklama, arama snippet'lerinde ek bağlam iletme fırsatını boşa harcar.",
    fix: "Başlığı genişleten farklı bir meta açıklama yazın — başlık sayfayı adlandırır, açıklama tıklamayı satar.",
  },
  content_title_h1_match: {
    why: "Başlık etiketi ve H1 uyuşmadığında sayfanın birincil anahtar kelimesini pekiştirme fırsatı kaçırılır.",
    fix: "Başlık ve H1'i tematik olarak tutarlı yapın; aynı anahtar kelime amacını hedeflemelidir.",
  },
  url_length: {
    why: "Çok uzun URL'ler SERP'te kesilir, paylaşımı zorlaştırır ve anahtar kelime alaka düzeyini azaltabilir.",
    fix: "URL'leri 100 karakterin altında tutun; bağlaç sözcükleri ve gereksiz yol bölümlerini kaldırın.",
  },
  url_uppercase: {
    why: "Büyük harfler, bazı sunucular büyük/küçük harf yollarını farklı URL'ler olarak işlediğinden yinelenen içerik sorunlarına yol açabilir.",
    fix: "Tüm URL'lerde küçük harf kullanın ve büyük harf varyantlarından 301 yönlendirmesi ayarlayın.",
  },
  url_underscore: {
    why: "Google alt çizgileri kelime birleştirici olarak işler; 'benim_sayfam', 'benimsayfam' olarak okunur.",
    fix: "Tüm URL slug'larındaki alt çizgileri kısa çizgiyle değiştirin.",
  },
  url_spaces: {
    why: "URL'lerdeki boşluklar yüzde kodlama (%20) ile değiştirilir; okunaksız ve kırılgan hale gelir.",
    fix: "Boşlukları kısa çizgiyle değiştirin; URL'leri temiz ve okunabilir tutun.",
  },
  url_query_params: {
    why: "Aşırı sorgu parametreleri sonsuz tarama döngüleri ve kanonikleştirme sorunları yaratabilir.",
    fix: "URL parametrelerini tutumlu kullanın; parametre varyantlarını kanonik etiketlerle yönetin.",
  },
  url_tr_chars: {
    why: "ASCII dışı karakterler (ş, ğ, ı vb.) URL'lerde yüzde kodlamayla değiştirilir, okunaksız ve kırılgan hale gelir.",
    fix: "URL slug'larında özel karakterleri ASCII karşılıklarıyla değiştirin (ş→s, ğ→g, ı→i).",
  },
  indexability_canonical: {
    why: "Kanonik etiket olmadan arama motorları hangi URL'yi indeksleyeceğini tahmin etmek zorunda kalır; bağlantı değeri bölünebilir.",
    fix: "Her sayfaya tercih edilen URL'yi işaret eden <link rel='canonical' href='...'> ekleyin.",
  },
  indexability_noindex: {
    why: "Noindex yönergesi bu sayfayı arama motoru indekslerinden kaldırır, organik aramada görünmez hale getirir.",
    fix: "Bu sayfanın arama sonuçlarında görünmesi gerekiyorsa noindex yönergesini kaldırın.",
  },
  indexability_nofollow: {
    why: "Sayfa düzeyinde nofollow, arama motorlarının sayfadaki hiçbir bağlantıyı takip etmesini engeller.",
    fix: "Arama motorlarının bu sayfadaki bağlantıları keşfetmesini istiyorsanız sayfa düzeyinde nofollow'u kaldırın.",
  },
  indexability_lang: {
    why: "Lang özelliği, arama motorlarının içeriği doğru dildeki kullanıcılara sunmasına yardımcı olur.",
    fix: "<html> öğesine sayfanın birincil diliyle eşleşen bir lang özelliği ekleyin (örn. <html lang='tr'>).",
  },
  schema_json_ld: {
    why: "Yapısal veri, SERP'te zengin sonuçları (yıldız puanları, SSS, kırıntılar) etkinleştirir; tıklama oranını önemli ölçüde artırır.",
    fix: "<head> içine birincil içerik türünüz için JSON-LD yapısal verisi ekleyin (Article, Product, LocalBusiness, FAQ vb.).",
  },
  image_alt: {
    why: "Alt metni, arama motorlarının görsel içeriği anlamasındaki temel sinyaldir ve görsel arama sıralamaları için kritiktir.",
    fix: "Tüm anlamlı görsellere açıklayıcı alt özelliği ekleyin; tamamen dekoratif görseller için boş alt='' kullanın.",
  },
  image_dimensions: {
    why: "Açık genişlik/yükseklik değeri olmayan görseller düzen kaymalarına (CLS) neden olur; Temel Web Verileri'ni olumsuz etkiler.",
    fix: "Tüm <img> etiketlerine açık width ve height öznitelikleri ekleyin.",
  },
  image_modern_format: {
    why: "Modern görsel formatları (WebP, AVIF) JPEG/PNG'den %25–50 daha küçüktür; sayfa yükleme hızını doğrudan iyileştirir.",
    fix: "Görselleri WebP veya AVIF formatına dönüştürün; tarayıcı uyumluluğu için <picture> öğesi kullanın.",
  },
  image_filename_length: {
    why: "Aşırı uzun görsel dosya adları gereksiz URL ağırlığı ekler ve nadiren SEO faydası sağlar.",
    fix: "80 karakterin altında özlü, açıklayıcı dosya adları kullanın; kelimeleri kısa çizgiyle ayırın.",
  },
  image_lazy_above_fold: {
    why: "Ekranın üst kısmındaki görsellerde geç yükleme kullanmak, LCP (En Büyük İçerikli Boyama) metriğini doğrudan olumsuz etkiler.",
    fix: "İlk yüklemede görünen görsellerden loading='lazy' özelliğini kaldırın; yalnızca ekranın alt kısmındaki görseller için kullanın.",
  },
  links_internal: {
    why: "İç bağlantılar, PageRank'i site genelinde dağıtır ve kullanıcıların ilgili içeriği keşfetmesine yardımcı olur.",
    fix: "Açıklayıcı ve anahtar kelime ilişkili bağlantı metni kullanarak ilgili sayfalara bağlamsal iç bağlantılar ekleyin.",
  },
  links_external: {
    why: "Yetkili kaynaklara dış bağlantılar, konusal güvenilirlik sinyali verir ve kullanıcılara değer katar.",
    fix: "İlgili, kaliteli dış kaynaklara bağlantı ekleyin; güvenlik için rel='noopener noreferrer' kullanın.",
  },
  links_invalid: {
    why: "Bozuk bağlantılar kötü kullanıcı deneyimi yaratır ve tarama bütçesini ölü son URL'lere harcar.",
    fix: "Tüm bozuk bağlantıları düzeltin veya kaldırın; taşınan sayfalar için 301 yönlendirmesi ayarlayın.",
  },
  social_og: {
    why: "Open Graph etiketleri, sayfanızın sosyal ağlarda paylaşıldığında nasıl göründüğünü kontrol eder; tıklama oranını etkiler.",
    fix: "<head>'e og:title, og:description, og:image ve og:url <meta> etiketleri ekleyin.",
  },
  social_twitter: {
    why: "Twitter Card etiketleri, içerik Twitter/X'te paylaşıldığında zengin bağlantı önizlemeleri oluşturur.",
    fix: "twitter:card, twitter:title, twitter:description ve twitter:image <meta> etiketleri ekleyin.",
  },
  structural_viewport: {
    why: "Viewport meta etiketi olmadan mobil tarayıcılar sayfaları masaüstü genişliğinde işler; mobilde kullanılamaz hale gelir.",
    fix: "<head>'e <meta name='viewport' content='width=device-width, initial-scale=1'> ekleyin.",
  },
  structural_favicon: {
    why: "Favicon'lar tarayıcı sekmelerinde ve yer imlerinde görünür; yokluğu siteyi tamamlanmamış gösterir.",
    fix: "Bir favicon.ico veya SVG favicon ekleyin ve <head>'e <link rel='icon'> ile referans verin.",
  },
  structural_hreflang: {
    why: "Hreflang etiketleri olmadan arama motorları uluslararası kullanıcılara yanlış dil veya bölge varyantını gösterebilir.",
    fix: "Her dil/bölge varyantı için hreflang ek açıklamaları uygulayın; her sayfaya kendi kendine referans veren etiket ekleyin.",
  },
  structural_pagination: {
    why: "Sayfalandırma sinyallerinin eksikliği, arama motorlarını sayfalandırılmış içerik serileri hakkında kararsız bırakır.",
    fix: "Tüm sayfalandırılmış içerik için rel='prev' ve rel='next' bağlantı öğeleri ekleyin.",
  },
  structural_rss: {
    why: "RSS beslemesi, arama motorlarının ve toplayıcıların yeni içeriği daha hızlı keşfetmesini sağlar.",
    fix: "Bir RSS veya Atom beslemesi oluşturun ve <link rel='alternate' type='application/rss+xml'> ile referans verin.",
  },
  http_hsts: {
    why: "HSTS olmadan tarayıcılar yönlendirilmeden önce şifrelenmemiş HTTP isteği yapabilir; kullanıcıları açıkta bırakır.",
    fix: "Sunucunuzu Strict-Transport-Security: max-age=31536000; includeSubDomains başlığı gönderecek şekilde yapılandırın.",
  },
  http_compression: {
    why: "Sıkıştırılmamış yanıtlar 5–10 kat daha büyük olabilir; özellikle mobilde sayfa yüklemeyi önemli ölçüde yavaşlatır.",
    fix: "Tüm metin tabanlı yanıtlar için web sunucunuzda veya CDN'de gzip veya Brotli sıkıştırmayı etkinleştirin.",
  },
  http_caching: {
    why: "Uygun önbellek başlıkları olmadan tarayıcılar her ziyarette değişmemiş kaynakları yeniden indirir.",
    fix: "Statik kaynaklar (görseller, CSS, JS) için uygun max-age değerlerine sahip Cache-Control başlıkları ayarlayın.",
  },
  http_response_time: {
    why: "Yavaş sunucu yanıt süresi (TTFB) doğrudan bir sıralama sinyalidir ve sayfa yüklemenin her adımını geciktirir.",
    fix: "Sunucu performansını optimize edin, CDN kullanın, sunucu tarafı önbelleklemeyi etkinleştirin ve yavaş sorguları inceleyin.",
  },
  http_content_type: {
    why: "Eksik veya yanlış Content-Type başlığı, tarayıcıların sayfayı yanlış yorumlamasına neden olabilir.",
    fix: "Sunucunuzun tüm HTML yanıtları için Content-Type: text/html; charset=utf-8 döndürdüğünden emin olun.",
  },
  http_x_robots_tag: {
    why: "X-Robots-Tag HTTP başlığı sunucu düzeyinde indekslemeyi istemeden kısıtlıyor olabilir.",
    fix: "X-Robots-Tag yanıt başlığını denetleyin ve istenmeyen noindex veya nofollow yönergelerini kaldırın.",
  },
  http_x_robots_noindex: {
    why: "X-Robots-Tag: noindex bu sayfayı HTTP düzeyinde arama motorlarından gizler; meta etiketleri geçersiz kılar.",
    fix: "Bu sayfanın indekslenmesi gerekiyorsa X-Robots-Tag başlığındaki noindex yönergesini kaldırın.",
  },
  http_x_robots_nofollow: {
    why: "X-Robots-Tag: nofollow, HTTP düzeyinde arama motorlarının bu sayfadaki bağlantıları takip etmesini engeller.",
    fix: "Bu sayfadaki bağlantıların taranmasını istiyorsanız X-Robots-Tag başlığındaki nofollow yönergesini kaldırın.",
  },
  pagespeed_performance: {
    why: "Google'ın Temel Web Verileri performans skoru, özellikle mobilde arama sıralamalarını doğrudan etkiler.",
    fix: "Genel performans skorunu yükseltmek için işaretlenen CWV sorunlarını (LCP, CLS, FCP, TBT) giderin.",
  },
  pagespeed_lcp: {
    why: "En Büyük İçerikli Boyama (LCP), ana içeriğin ne kadar hızlı yüklendiğini ölçer — temel bir Google sıralama sinyali.",
    fix: "Kahraman görselini önceden yükleyin, hızlı barındırma kullanın ve render engelleme kaynaklarını azaltarak <2,5s hedefine ulaşın.",
  },
  pagespeed_cls: {
    why: "Kümülatif Düzen Kayması (CLS), görsel kararlılığı ölçer — beklenmedik kaymalar kullanıcı deneyimini bozar ve Google tarafından penalize edilir.",
    fix: "Görsellere ve yerleştirilmiş içeriklere açık boyutlar ekleyin; sayfa yüklendikten sonra mevcut içeriğin üstüne içerik eklemeyin.",
  },
  pagespeed_fcp: {
    why: "İlk İçerikli Boyama (FCP), kullanıcıların ilk içeriği ne zaman gördüğünü ölçer — yavaş FCP, sunucu veya ağ sorununa işaret eder.",
    fix: "Render engelleme kaynaklarını ortadan kaldırın, kritik CSS'yi satır içine alın ve sunucu yanıt sürelerini iyileştirin.",
  },
  pagespeed_tbt: {
    why: "Toplam Engelleme Süresi (TBT), yükleme sırasındaki ana iş parçacığı engellenme süresini ölçer — yüksek TBT sayfanın donuk hissettirmesine yol açar.",
    fix: "Uzun JavaScript görevlerini parçalara bölün, kritik olmayan JS'yi erteleyin ve yoğun hesaplamalar için web worker'ları kullanın.",
  },
  pagespeed_ttfb: {
    why: "İlk Bayta Kadar Geçen Süre (TTFB), sunucunun yanıt gecikmesidir ve sonraki her yükleme adımını doğrudan geciktirir.",
    fix: "CDN kullanın, sunucu önbelleğini etkinleştirin, veritabanı sorgularını optimize edin ve barındırma altyapınızı gözden geçirin.",
  },
  pagespeed_speed_index: {
    why: "Hız Endeksi, içeriğin görsel olarak ne kadar hızlı dolduğunu ölçer — yavaş bir skor kullanıcıları hayal kırıklığına uğratır.",
    fix: "Önce ekranın üst kısmındaki içeriği yüklemeye öncelik verin, ekran dışı kaynakları erteleyin ve kritik render yolunu optimize edin.",
  },
  pagespeed_seo: {
    why: "PageSpeed'in SEO denetimi, tarama engelleyicilerini, eksik viewport etiketlerini ve sıralamayı etkileyen optimize edilmemiş bağlantıları işaretler.",
    fix: "PageSpeed tarafından bu URL için raporlanan özel SEO sorunlarını inceleyin ve düzeltin.",
  },
  pagespeed_accessibility: {
    why: "Erişilebilirlik sorunları engelli kullanıcıları etkiler ve arama motorlarının içeriğinizi anlamasını sınırlar.",
    fix: "İşaretlenen sorunları düzeltin: eksik alt metni ekleyin, renk kontrastını artırın ve tüm etkileşimli öğelerin klavye ile erişilebilir olduğundan emin olun.",
  },
  pagespeed_error: {
    why: "PageSpeed API hatası, Temel Web Verileri verilerinin alınamadığı anlamına gelir; performans kör noktaları bırakır.",
    fix: "PageSpeed API anahtarının geçerli olduğunu ve sayfanın kamuya açık olduğunu doğrulayın, ardından analizi yeniden çalıştırın.",
  },
}
