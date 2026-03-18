# arabam.com Scraper - Kullanım Kılavuzu

Bu kılavuz, arabam.com scraper projesini **hiç bilmeyen** birinin sıfırdan kurup çalıştırabilmesi için hazırlanmıştır.

---

## İçindekiler

- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Çalıştırma](#calistirma)
- [Çıktı Dosyalarını Anlama](#cikti-dosyalarini-anlama)
- [Ayarları Değiştirme](#ayarlari-degistirme)
- [Scraping'i Durdurma ve Devam Ettirme](#scrapingi-durdurma-ve-devam-ettirme)
- [Sıkça Karşılaşılan Sorunlar](#sikca-karsilasilan-sorunlar)

---

## Gereksinimler

Başlamadan önce aşağıdakilerin bilgisayarınızda kurulu olduğundan emin olun:

| Gereksinim | Minimum Sürüm | Kontrol Komutu |
|-----------|---------------|----------------|
| **Python** | 3.10+ | `python --version` |
| **pip** | (Python ile gelir) | `pip --version` |

> **Python kurulu mu kontrol edin:**
> Terminal (Komut İstemi) açın ve `python --version` yazın.
> Eğer "Python 3.x.x" gibi bir çıktı görüyorsanız kurulu demektir.
> Göremiyorsanız [python.org](https://www.python.org/downloads/) adresinden indirip kurun.

---

## Kurulum

### Adım 1: Projeyi bilgisayarınıza indirin

Projeyi ZIP olarak indirdiyseniz, bir klasöre çıkartın.
Git kullanıyorsanız:

```bash
git clone <repo-url>
```

### Adım 2: Proje klasörüne gidin

```bash
cd arabam.com-scraping
```

### Adım 3: Sanal ortam oluşturun (Önerilen)

Sanal ortam, bu projenin bağımlılığının diğer projelerinizi etkilememesini sağlar.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> **Başarılı olduğunu nasıl anlarsınız?**
> Terminalinizin başında [(venv)](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/spiders/otomobil.py#65-72) yazısı görünür:
> ```
> (venv) C:\Users\Kullanici\arabam.com-scraping>
> ```

### Adım 4: Bağımlılıkları kurun

```bash
pip install -r requirements.txt
```

Bu komut `scrapy` kütüphanesini ve alt bağımlılıklarını kuracaktır. Kurulum birkaç dakika sürebilir.

### Adım 5: Kurulumu doğrulayın

```bash
scrapy version
```

`Scrapy 2.x.x` gibi bir çıktı görmeniz gerekir. Görüyorsanız kurulum başarılı demektir.

---

## Çalıştırma

### Temel Kullanım

Proje klasöründe aşağıdaki komutu çalıştırın:

```bash
scrapy crawl otomobil
```

Bu komut:
1. arabam.com'daki **tüm ikinci el otomobil ilanlarını** sayfa sayfa gezmeye başlar
2. Her ilanın detay sayfasına girer ve bilgileri toplar
3. Sonuçları `output/` klasörüne JSON dosyası olarak kaydeder

### Sonuçları Farklı Bir Dosyaya Kaydetme

Varsayılan olarak sonuçlar `output/arabam_<tarih>.json` dosyasına kaydedilir.
İsterseniz kendiniz bir dosya adı belirleyebilirsiniz:

```bash
scrapy crawl otomobil -o sonuclar.json
```

veya CSV olarak kaydetmek için:

```bash
scrapy crawl otomobil -o sonuclar.csv
```

### Kısıtlı Test Çalışması (Önerilen İlk Adım)

Tüm siteyi kazımak **saatler sürebilir** (binlerce ilan vardır). İlk defa çalıştırıyorsanız, sadece küçük bir deneme yapmanızı öneririz:

```bash
scrapy crawl otomobil -s CLOSESPIDER_ITEMCOUNT=10 -o test.json
```

Bu komut **sadece 10 ilan** topladıktan sonra durur. Böylece her şeyin doğru çalıştığını hızlıca kontrol edebilirsiniz.

Diğer kısıtlama seçenekleri:

| Parametre | Açıklama | Örnek |
|-----------|----------|-------|
| `CLOSESPIDER_ITEMCOUNT=N` | N ilan topladıktan sonra dur | `-s CLOSESPIDER_ITEMCOUNT=50` |
| `CLOSESPIDER_PAGECOUNT=N` | N sayfa gezdikten sonra dur | `-s CLOSESPIDER_PAGECOUNT=5` |
| `CLOSESPIDER_TIMEOUT=N` | N saniye sonra dur | `-s CLOSESPIDER_TIMEOUT=60` |

---

## Çıktı Dosyalarını Anlama

Scraper çalıştıktan sonra `output/` klasöründe bir JSON dosyası oluşur. Bu dosya ilan bilgilerini içerir.

### Örnek Veri

Her ilan için şu bilgiler toplanır:

```json
{
  "listing_id": "38274257",
  "url": "https://www.arabam.com/ilan/.../38274257",
  "scraped_at": "2026-03-14T15:55:40.654381+00:00",
  "ilan_basligi": "Galeriden Peugeot 301 1.5 BlueHDI Active 2019 Model...",
  "fiyat": 667750,
  "sehir": "İstanbul",
  "ilce": "Bahçelievler",
  "marka": "Peugeot",
  "seri": "301",
  "model": "1.5 BlueHDI Active",
  "yil": 2019,
  "km": 152200,
  "vites_tipi": "Düz",
  "yakit_tipi": "Dizel",
  "kasa_tipi": "Sedan",
  "renk": "Beyaz",
  "motor_hacmi": "1499 cc",
  "motor_gucu": "102 hp",
  "motor_kaputu": "Boyanmış",
  "sol_on_camurluk": "Boyanmış",
  "sag_on_kapi": "Orijinal"
}
```

### Alan Tablosu

| Alan | Tür | Açıklama |
|------|-----|----------|
| [listing_id](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/utils.py#29-35) | string | İlanın benzersiz numarası |
| `url` | string | İlanın web adresi |
| `scraped_at` | string | Verinin çekildiği tarih/saat (UTC) |
| `fiyat` | integer | Araç fiyatı (TL, sayı olarak) |
| `marka` | string | Araç markası (Peugeot, Renault, vb.) |
| `seri` | string | Araç serisi (301, Clio, Corolla, vb.) |
| `model` | string | Araç modeli (1.5 BlueHDI Active, vb.) |
| `yil` | integer | Model yılı |
| [km](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/utils.py#12-18) | integer | Kilometre (sayı olarak) |
| `vites_tipi` | string | Düz / Otomatik / Yarı Otomatik |
| `yakit_tipi` | string | Dizel / Benzin / Hibrit / LPG vb. |
| `kasa_tipi` | string | Sedan / Hatchback / Station wagon vb. |
| `renk` | string | Araç rengi |
| `motor_hacmi` | string | Motor hacmi (cc cinsinden) |
| `motor_gucu` | string | Motor gücü (hp cinsinden) |
| `sehir` | string | İlanın bulunduğu şehir |
| `ilce` | string | İlanın bulunduğu ilçe |
| `ilan_aciklamasi` | string | Serbest format ilan metni |
| `motor_kaputu` | string | Orijinal / Boyanmış / Değişmiş |
| `sol_on_camurluk` | string | Orijinal / Boyanmış / Değişmiş |
| ... | ... | (13 parça için aynı format) |

---

## Ayarları Değiştirme

Scraping davranışını değiştirmek için [arabam/settings.py](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/settings.py) dosyasını düzenleyebilirsiniz.

### Hız Ayarları

```python
# İstekler arası bekleme süresi (saniye)
# Daha düşük = daha hızlı ama site sizi engelleyebilir
# Daha yüksek = daha yavaş ama daha güvenli
DOWNLOAD_DELAY = 2

# Aynı anda yapılacak istek sayısı
CONCURRENT_REQUESTS = 4
```

> **Uyarı:** `DOWNLOAD_DELAY` değerini 1'in altına düşürmeyin.
> arabam.com sizi geçici olarak engelleyebilir (HTTP 429 hatası).

### Cache Ayarları

```python
# True = Aynı sayfayı 24 saat içerisinde tekrar ziyaret etmez (geliştirme için)
# False = Her seferinde siteye istek gönderir (üretim için)
HTTPCACHE_ENABLED = True
```

Gerçek veri toplamak için cache'i kapatmak isterseniz:

```bash
scrapy crawl otomobil -s HTTPCACHE_ENABLED=False
```

### Log Ayarları

```python
# Log seviyesi: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Log dosyası
LOG_FILE = "logs/arabam.log"
```

Terminalde daha fazla detay görmek için:

```bash
scrapy crawl otomobil -s LOG_LEVEL=DEBUG
```

---

## Scraping'i Durdurma ve Devam Ettirme

### Durdurma

Scraper çalışırken durdurmak için terminalde `Ctrl + C` tuşlarına basın.

- **1 kez** basarsanız: Scraper mevcut istekleri tamamlayıp düzgün bir şekilde kapanır.
- **2 kez** basarsanız: Hemen zorla kapatır (önermiyoruz).

### Devam Ettirme (Resume)

Bu proje **resume desteğine** sahiptir. Scraper durdurulup tekrar başlatıldığında, **kaldığı yerden devam eder**.

Bu özellik `crawls/` klasöründeki durum dosyaları sayesinde çalışır.

```bash
# İlk çalıştırma
scrapy crawl otomobil
# (Ctrl+C ile durdurun)

# Kaldığı yerden devam etme - aynı komutu tekrar çalıştırın
scrapy crawl otomobil
```

> **Sıfırdan başlatmak istiyorsanız**, `crawls/` klasörünü silin:
> ```bash
> # Windows
> rmdir /s /q crawls
>
> # macOS / Linux
> rm -rf crawls
> ```

---

## Sıkça Karşılaşılan Sorunlar

### 1. `scrapy: command not found` veya `scrapy tanınmıyor`

**Sebep:** Scrapy kurulu değil veya sanal ortam aktif değil.

**Çözüm:**
```bash
# Sanal ortamı aktif edin
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Scrapy'i tekrar kurun
pip install -r requirements.txt
```

### 2. HTTP 403 veya 429 Hatası

**Sebep:** arabam.com çok fazla istek aldığınızı algıladı ve engelledi.

**Çözüm:**
- `DOWNLOAD_DELAY` değerini artırın (örneğin `5`)
- `CONCURRENT_REQUESTS` değerini azaltın (örneğin `2`)

```bash
scrapy crawl otomobil -s DOWNLOAD_DELAY=5 -s CONCURRENT_REQUESTS=2
```

### 3. Çıktı Dosyası Boş

**Sebep:** robots.txt izin vermiyor olabilir veya site yapısı değişmiş olabilir.

**Çözüm:**
Öncelikle test komutu ile deneyin:
```bash
scrapy crawl otomobil -s CLOSESPIDER_ITEMCOUNT=5 -o test.json -s LOG_LEVEL=DEBUG
```
Terminaldeki log çıktısını inceleyerek hatanın kaynağını bulabilirsiniz.

### 4. Deprecation Uyarıları (Spider argument)

Log dosyasında şu uyarıyı görebilirsiniz:
```
ScrapyDeprecationWarning: process_request() requires a spider argument
ScrapyDeprecationWarning: process_item() requires a spider argument
```

**Sebep:** Scrapy'nin yeni sürümleri `spider` parametresi bekliyor.

**Çözüm:** Bu uyarılar scraper'ın çalışmasını **engellemez**, ancak gelecek sürümler için düzeltme yapılması gereken yerler:

| Dosya | Mevcut | Olması Gereken |
|-------|--------|----------------|
| [middlewares.py](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/middlewares.py) | [process_request(self, request)](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/middlewares.py#20-22) | [process_request(self, request, spider)](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/middlewares.py#20-22) |
| [pipelines.py](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/pipelines.py) | [process_item(self, item)](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/pipelines.py#7-39) | [process_item(self, item, spider)](file:///c:/Users/YOGA/Desktop/A2M2_CheckList/arabam.com-scraping/arabam/pipelines.py#7-39) |

### 5. `UnicodeDecodeError` veya Türkçe Karakter Sorunu

**Çözüm:** Bu sorun genellikle olmaz çünkü proje `UTF-8` encoding kullanır. Ancak sorunla karşılaşırsanız:
```bash
# Windows Komut İstemi için:
chcp 65001
scrapy crawl otomobil
```

---

## Hızlı Başlangıç Özeti

Sadece 5 adımda başlayın:

```bash
# 1. Proje klasörüne gidin
cd arabam.com-scraping

# 2. Sanal ortam oluşturun ve aktif edin
python -m venv venv
venv\Scripts\activate

# 3. Bağımlılıkları kurun
pip install -r requirements.txt

# 4. Test çalışması yapın (10 ilan)
scrapy crawl otomobil -s CLOSESPIDER_ITEMCOUNT=10 -o test.json

# 5. Sonuçları görüntüleyin
type test.json
```

Her şey çalışıyor mu? O zaman tam çalıştırma için:

```bash
scrapy crawl otomobil
```

Sonuçlar `output/` klasöründe JSON dosyası olarak kaydedilir.

