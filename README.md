# arabam.com Scraper

arabam.com üzerindeki ikinci el otomobil ilanlarını toplayan Scrapy tabanlı web scraper.

## Özellikler

- **Akıllı kategori bölme:** arabam.com sayfa başına maksimum 50 sayfa (1000 ilan) gösterir. Bu sınırı aşan kategoriler marka → seri → model hiyerarşisinde otomatik olarak alt kategorilere bölünerek tüm ilanlar toplanır.
- **41 veri alanı:** Fiyat, km, marka, model, yıl, konum, motor bilgileri, boya/değişen detayları ve daha fazlası.
- **Duraklatma ve devam:** JOBDIR desteği sayesinde yarıda kalan tarama kaldığı yerden devam eder.
- **Veri temizleme:** Fiyat ve km değerleri sayıya çevrilir, metinler normalize edilir, tekrarlanan ilanlar filtrelenir.
- **Bot koruması:** 12 farklı User-Agent rotasyonu, AutoThrottle ve robots.txt uyumu.

## Kurulum

```bash
git clone https://github.com/KULLANICI_ADI/arabam.com-scraping.git
cd arabam.com-scraping
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

## Kullanım

```bash
# Test çalışması (10 ilan)
scrapy crawl otomobil -s CLOSESPIDER_ITEMCOUNT=10

# Tam çalışma
scrapy crawl otomobil

# Durdurma: Ctrl+C (tek basış)
# Devam ettirme: aynı komutu tekrar çalıştır (JOBDIR sayesinde kaldığı yerden devam eder)

# Sıfırdan başlatma:
rmdir /s /q crawls
scrapy crawl otomobil
```

Çıktılar `output/arabam_<tarih>.json`, loglar `logs/arabam.log` dosyasına yazılır. Bu klasörler otomatik oluşturulur.

Detaylı kullanım bilgileri için [USAGE.md](USAGE.md) dosyasına bakın.

## Proje Yapısı

```
arabam.com-scraping/
├── scrapy.cfg              # Scrapy proje konfigürasyonu
├── requirements.txt        # Python bağımlılıkları (Scrapy==2.14.2)
├── README.md
├── USAGE.md                # Detaylı kullanım kılavuzu
└── arabam/
    ├── __init__.py
    ├── items.py            # Veri modeli (CarItem - 41 alan)
    ├── middlewares.py       # User-Agent rotasyonu
    ├── pipelines.py        # Veri temizleme + tekrar filtresi
    ├── settings.py         # Scrapy ayarları
    ├── utils.py            # Yardımcı fonksiyonlar
    └── spiders/
        ├── __init__.py
        └── otomobil.py     # Ana spider (4 aşamalı tarama)
```

## Çalışma Akışı

Spider 4 aşamalı bir süreçle çalışır:

1. **Kategori Keşfi** — Ana sayfadan tüm marka bağlantıları toplanır.
2. **Kategori Değerlendirme** — Her kategori kontrol edilir. 1000'den fazla ilan varsa alt kategorilere bölünür (seri → model), yoksa doğrudan taramaya geçilir.
3. **Listeleme Sayfaları** — Kategori sayfalarından ilan detay bağlantıları çıkarılır. Sayfalama ile tüm sayfalar (1-50) gezilir.
4. **Detay Çıkarma** — Her ilan sayfasından HTML ve gömülü JSON verisi ayrıştırılarak 41 alan toplanır.

## Veri Akışı

```
arabam.com ana sayfa
        │
        ▼
  Marka linkleri (Audi, BMW, Fiat, ...)
        │
        ▼
  Kategori kontrolü (ilan sayısı ≤ 1000 mi?)
        │
   ┌────┴────┐
   │ Evet    │ Hayır → Alt kategorilere böl (seri/model) → Tekrar kontrol et
   ▼         │
  Listeleme sayfaları (sayfa 1..50)
        │
        ▼
  İlan detay sayfaları (/ilan/12345678)
        │
        ▼
  DataCleaningPipeline → fiyat/km temizleme, metin normalize
        │
        ▼
  DuplicateFilterPipeline → tekrar filtreleme
        │
        ▼
  output/arabam_<zaman>.json
```

## Bileşen Görevleri

| Bileşen | Görev |
|---------|-------|
| **OtomobilSpider** | 4 aşamalı taramayı yönetir, sayfalama sınırını akıllı bölme ile aşar |
| **CarItem** | 41 alanlı veri modeli (meta + araç bilgileri + boya/değişen) |
| **UserAgentRotationMiddleware** | Her istekte 12 farklı tarayıcı imzasından birini atar |
| **DataCleaningPipeline** | Fiyat/km sayıya çevirir, yılı integer yapar, metinleri normalize eder |
| **DuplicateFilterPipeline** | Aynı listing_id'ye sahip tekrar ilanları filtreler |
| **utils.py** | Regex tabanlı veri çıkarma ve temizleme fonksiyonları |
| **settings.py** | Hız limiti, yeniden deneme, timeout, pipeline ve middleware bağlantıları |

## Toplanan Veri Alanları

**Meta (3):** listing_id, url, scraped_at

**İlan Detayları (25):** fiyat, ilan_basligi, sehir, ilce, ilan_aciklamasi, ilan_tarihi, marka, seri, model, yil, km, vites_tipi, yakit_tipi, kasa_tipi, renk, motor_hacmi, motor_gucu, cekis, arac_durumu, ort_yakit_tuketimi, yakit_deposu, agir_hasarli, boya_degisen, takasa_uygun, kimden

**Boya/Değişen (13):** on_tampon, arka_tampon, motor_kaputu, tavan, sol_on_camurluk, sol_on_kapi, sol_arka_kapi, sol_arka_camurluk, sag_on_camurluk, sag_on_kapi, sag_arka_kapi, sag_arka_camurluk, arka_kaput

## Ayarlar

| Ayar | Değer | Açıklama |
|------|-------|----------|
| ROBOTSTXT_OBEY | True | robots.txt'e saygılı scraping |
| DOWNLOAD_DELAY | 1.5 sn | İstekler arası bekleme süresi |
| CONCURRENT_REQUESTS | 6 | Aynı anda max istek sayısı |
| AUTOTHROTTLE_ENABLED | True | Sunucu yüküne göre otomatik hız ayarı |
| RETRY_TIMES | 3 | Başarısız istekleri 3 kez tekrar dene |
| HTTPCACHE_ENABLED | False | Cache kapalı |

Detaylı kullanım kılavuzu için: [USAGE.md](USAGE.md)
