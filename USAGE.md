# Kullanım Kılavuzu

## Gereksinimler

| Gereksinim | Minimum Sürüm | Kontrol Komutu |
|-----------|---------------|----------------|
| Python | 3.10+ | `python --version` |
| pip | (Python ile gelir) | `pip --version` |

Python kurulu değilse [python.org](https://www.python.org/downloads/) adresinden indirip kurun.

## Kurulum

```bash
# 1. Proje klasörüne gidin
cd arabam.com-scraping

# 2. Sanal ortam oluşturun ve aktif edin
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 3. Bağımlılıkları kurun
pip install -r requirements.txt

# 4. Kurulumu doğrulayın
scrapy version
```

Sanal ortam aktif olduğunda terminalin başında `(venv)` yazısı görünür.

## Çalıştırma

### Test Çalışması (Önerilen İlk Adım)

Tüm siteyi taramak saatler sürebilir. İlk defa çalıştırıyorsanız önce test yapın:

```bash
scrapy crawl otomobil -s CLOSESPIDER_ITEMCOUNT=10 -o test.json
```

Bu komut sadece 10 ilan topladıktan sonra durur.

Diğer kısıtlama seçenekleri:

| Parametre | Açıklama | Örnek |
|-----------|----------|-------|
| `CLOSESPIDER_ITEMCOUNT=N` | N ilan topladıktan sonra dur | `-s CLOSESPIDER_ITEMCOUNT=50` |
| `CLOSESPIDER_PAGECOUNT=N` | N sayfa gezdikten sonra dur | `-s CLOSESPIDER_PAGECOUNT=5` |
| `CLOSESPIDER_TIMEOUT=N` | N saniye sonra dur | `-s CLOSESPIDER_TIMEOUT=60` |

### Tam Çalışma

```bash
scrapy crawl otomobil
```

Bu komut tüm ikinci el otomobil ilanlarını tarar ve sonuçları `output/arabam_<tarih>.json` dosyasına kaydeder. Loglar `logs/arabam.log` dosyasına yazılır. Her iki klasör de otomatik oluşturulur.

### Sonuçları Farklı Formatta Kaydetme

```bash
# Belirli bir JSON dosyasına
scrapy crawl otomobil -o sonuclar.json

# CSV olarak
scrapy crawl otomobil -o sonuclar.csv
```

## Çıktı Dosyalarını Anlama

Her ilan için şu bilgiler toplanır:

```json
{
  "listing_id": "38274257",
  "url": "https://www.arabam.com/ilan/.../38274257",
  "scraped_at": "2026-03-14T15:55:40",
  "ilan_basligi": "Galeriden Peugeot 301 1.5 BlueHDI Active",
  "fiyat": 667750,
  "sehir": "Istanbul",
  "ilce": "Bahcelievler",
  "marka": "Peugeot",
  "seri": "301",
  "model": "1.5 BlueHDI Active",
  "yil": 2019,
  "km": 152200,
  "vites_tipi": "Duz",
  "yakit_tipi": "Dizel",
  "kasa_tipi": "Sedan",
  "renk": "Beyaz",
  "motor_hacmi": "1499 cc",
  "motor_gucu": "102 hp",
  "motor_kaputu": "Boyanmis",
  "sol_on_camurluk": "Boyanmis",
  "sag_on_kapi": "Orijinal"
}
```

Fiyat ve km değerleri otomatik olarak integer'a çevrilir (`"1.250.000 TL"` → `1250000`). Tüm veri alanlarının listesi için [README.md](README.md) dosyasına bakın.

## Durdurma ve Devam Ettirme

### Durdurma

Scraper çalışırken `Ctrl + C` basın.

- **1 kez** basarsanız: Mevcut istekleri tamamlayıp düzgün kapanır.
- **2 kez** basarsanız: Hemen zorla kapatır (önerilmez).

### Devam Ettirme

Scraper JOBDIR desteği sayesinde kaldığı yerden devam eder. Durdurduktan sonra aynı komutu tekrar çalıştırın:

```bash
scrapy crawl otomobil
```

### Sıfırdan Başlatma

Devam etmek yerine sıfırdan başlatmak istiyorsanız durum dosyalarını silin:

```bash
# Windows
rmdir /s /q crawls

# macOS / Linux
rm -rf crawls
```

Sonra tekrar çalıştırın: `scrapy crawl otomobil`

## Ayarları Değiştirme

`arabam/settings.py` dosyasındaki önemli ayarlar:

### Hız Ayarları

```python
DOWNLOAD_DELAY = 1.5          # İstekler arası bekleme süresi (saniye)
CONCURRENT_REQUESTS = 6       # Aynı anda yapılacak istek sayısı
```

Komut satırından geçici olarak değiştirmek için:

```bash
scrapy crawl otomobil -s DOWNLOAD_DELAY=3 -s CONCURRENT_REQUESTS=2
```

> **Uyarı:** DOWNLOAD_DELAY değerini 1'in altına düşürmeyin. arabam.com sizi geçici olarak engelleyebilir (HTTP 429 hatası).

### Log Ayarları

```python
LOG_LEVEL = "INFO"             # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "logs/arabam.log"
```

Terminalde daha fazla detay görmek için:

```bash
scrapy crawl otomobil -s LOG_LEVEL=DEBUG
```

## Sıkça Karşılaşılan Sorunlar

### `scrapy: command not found`

Sanal ortam aktif değil veya Scrapy kurulu değil.

```bash
venv\Scripts\activate              # Windows
source venv/bin/activate           # macOS / Linux
pip install -r requirements.txt
```

### HTTP 403 veya 429 Hatası

arabam.com çok fazla istek aldığınızı algıladı. Hızı düşürerek deneyin:

```bash
scrapy crawl otomobil -s DOWNLOAD_DELAY=5 -s CONCURRENT_REQUESTS=2
```

### Çıktı Dosyası Boş

Test komutu ile debug yapın:

```bash
scrapy crawl otomobil -s CLOSESPIDER_ITEMCOUNT=5 -o test.json -s LOG_LEVEL=DEBUG
```

Log çıktısını inceleyerek hatanın kaynağını bulabilirsiniz.

### Türkçe Karakter Sorunu (Windows)

```bash
chcp 65001
scrapy crawl otomobil
```
