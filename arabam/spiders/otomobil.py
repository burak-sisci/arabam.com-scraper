import json
import re
from datetime import datetime, timezone

import scrapy

from arabam.items import CarItem
from arabam.utils import extract_listing_id


class OtomobilSpider(scrapy.Spider):
    name = "otomobil"
    allowed_domains = ["arabam.com"]

    BASE_URL = "https://www.arabam.com/ikinci-el/otomobil"

    custom_settings = {
        "JOBDIR": "crawls/otomobil-listing",
    }

    # arabam.com sayfalama limiti: 50 sayfa × 20 ilan = 1000 ilan
    MAX_PAGE = 50
    MAX_ITEMS_PER_SEGMENT = MAX_PAGE * 20  # 1000

    # Özellikler tablosundaki Türkçe etiketler -> item alan adları
    PROPERTY_MAP = {
        "İlan Tarihi": "ilan_tarihi",
        "Marka": "marka",
        "Seri": "seri",
        "Model": "model",
        "Yıl": "yil",
        "Kilometre": "km",
        "Vites Tipi": "vites_tipi",
        "Yakıt Tipi": "yakit_tipi",
        "Renk": "renk",
        "Kasa Tipi": "kasa_tipi",
        "Motor Hacmi": "motor_hacmi",
        "Motor Gücü": "motor_gucu",
        "Çekiş": "cekis",
        "Araç Durumu": "arac_durumu",
        "Ort. Yakıt Tüketimi": "ort_yakit_tuketimi",
        "Yakıt Deposu": "yakit_deposu",
        "Ağır Hasarlı": "agir_hasarli",
        "Boya-değişen": "boya_degisen",
        "Takasa Uygun": "takasa_uygun",
        "Kimden": "kimden",
    }

    # Boya-değişen parça adları -> item alan adları
    DAMAGE_PART_MAP = {
        "Sağ Arka Çamurluk": "sag_arka_camurluk",
        "Arka Kaput": "arka_kaput",
        "Sol Arka Çamurluk": "sol_arka_camurluk",
        "Sağ Arka Kapı": "sag_arka_kapi",
        "Sağ Ön Kapı": "sag_on_kapi",
        "Tavan": "tavan",
        "Sol Arka Kapı": "sol_arka_kapi",
        "Sol Ön Kapı": "sol_on_kapi",
        "Sağ Ön Çamurluk": "sag_on_camurluk",
        "Motor Kaputu": "motor_kaputu",
        "Sol Ön Çamurluk": "sol_on_camurluk",
        "Ön Tampon": "on_tampon",
        "Arka Tampon": "arka_tampon",
    }

    # Atlanacak alt-kategori kelimeleri (sayfa filtreleri, ilan türü filtreler)
    SKIP_SUFFIXES = (
        "sahibinden", "galeriden", "yetkili-bayiden",
        "yetkili-bayi", "duz", "otomatik", "yari-otomatik",
        "benzin", "dizel", "lpg", "hibrit", "elektrik",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.segment_count = 0
        self.expected_items = 0

    # ─────────────────────────────────────────────────────────
    # AŞAMA 1: Kategori keşfi (ana sayfa → markalar)
    # ─────────────────────────────────────────────────────────

    async def start(self):
        """Ana listeleme sayfasından marka linklerini keşfet."""
        yield scrapy.Request(
            f"{self.BASE_URL}?page=1",
            callback=self.parse_discover_brands,
            priority=2,
        )

    def parse_discover_brands(self, response):
        """Ana sayfadan marka linklerini çıkar ve kontrol et."""
        brand_links = response.css(
            'a[href*="/ikinci-el/otomobil/"]::attr(href)'
        ).getall()

        seen = set()
        for href in brand_links:
            # Sadece /ikinci-el/otomobil/BRAND formatı (tek seviye)
            path = href.rstrip("/")
            if path in seen:
                continue

            # Ana URL'i atla
            if path == "/ikinci-el/otomobil":
                continue

            # Path parçaları: /ikinci-el/otomobil/BRAND
            parts = path.split("/")
            if len(parts) != 4:  # ['', 'ikinci-el', 'otomobil', 'brand']
                continue

            brand_slug = parts[3]

            # Filtre alt-kategorilerini atla
            if brand_slug.endswith(tuple(f"-{s}" for s in self.SKIP_SUFFIXES)):
                continue
            if brand_slug in self.SKIP_SUFFIXES:
                continue

            seen.add(path)
            full_url = response.urljoin(f"{path}?page=1")
            yield scrapy.Request(
                full_url,
                callback=self.parse_check_category,
                meta={"category_path": path, "depth_level": 0},
                priority=2,
                dont_filter=True,
            )

        self.logger.info(
            "Ana sayfadan %d marka kesfedildi.", len(seen)
        )

    # ─────────────────────────────────────────────────────────
    # AŞAMA 2: Kategori kontrol — küçükse tara, büyükse böl
    # ─────────────────────────────────────────────────────────

    def parse_check_category(self, response):
        """Kategoriyi kontrol et: ≤1000 ilan → tara, >1000 → alt kategoriye böl."""
        category_path = response.meta["category_path"]
        depth_level = response.meta["depth_level"]
        total = self._extract_total(response)

        if total is None or total == 0:
            self.logger.debug(
                "Bos kategori: %s", category_path,
            )
            return

        max_page = min((total + 19) // 20, self.MAX_PAGE)

        if total <= self.MAX_ITEMS_PER_SEGMENT:
            # ✅ Bu kategori 50 sayfaya sığıyor — taramaya başla
            self.segment_count += 1
            self.expected_items += total
            self.logger.info(
                "SEGMENT #%d: %s → %d ilan, %d sayfa "
                "(toplam beklenen: %d)",
                self.segment_count, category_path, total, max_page,
                self.expected_items,
            )
            # Sayfa 1 zaten indirildi — ilan linklerini çıkar
            yield from self._extract_listings(response)

            # Kalan sayfaları kuyruğa al
            for page in range(2, max_page + 1):
                url = response.urljoin(f"{category_path}?page={page}")
                yield scrapy.Request(
                    url,
                    callback=self._parse_listing_page,
                    meta={"category_path": category_path, "page": page},
                    priority=3,
                )
        else:
            # ❌ Kategori çok büyük — alt kategorilere böl
            self.logger.info(
                "Boluyor (seviye %d): %s → %d ilan, alt kategoriler araniyor...",
                depth_level, category_path, total,
            )
            yield from self._discover_subcategories(
                response, category_path, depth_level, total
            )

    def _discover_subcategories(self, response, parent_path, depth_level, parent_total):
        """Sayfadaki alt-kategori linklerini bul ve kuyruğa al."""
        # Alt-kategori linklerini bul (parent path'ten uzun olanlar)
        all_links = response.css(
            'a[href*="/ikinci-el/otomobil/"]::attr(href)'
        ).getall()

        seen = set()
        parent_clean = parent_path.rstrip("/")

        for href in all_links:
            path = href.rstrip("/")
            if path in seen or path == parent_clean:
                continue

            # Alt-kategori olmalı (parent path ile başlamalı ve daha uzun)
            if not path.startswith(parent_clean + "-"):
                continue

            # Filtre suffixlerini atla
            slug = path[len(parent_clean) + 1:]  # parent-slug sonrası
            if any(slug.endswith(s) or slug == s for s in self.SKIP_SUFFIXES):
                continue
            # Şehir/bölge filtrelerini de atla (sahibinden, galeriden)
            if any(f"-{s}" in slug for s in self.SKIP_SUFFIXES):
                continue

            seen.add(path)

        if not seen:
            # Alt-kategori bulunamadı — ilk 1000 ilanı al (kayıp olacak)
            capped = min(parent_total, self.MAX_ITEMS_PER_SEGMENT)
            self.segment_count += 1
            self.expected_items += capped
            self.logger.warning(
                "ALT-KATEGORİ YOK: %s → %d ilan, sadece ilk %d alinacak! "
                "(segment #%d, toplam beklenen: %d)",
                parent_path, parent_total, capped,
                self.segment_count, self.expected_items,
            )
            yield from self._extract_listings(response)
            for page in range(2, self.MAX_PAGE + 1):
                url = response.urljoin(f"{parent_path}?page={page}")
                yield scrapy.Request(
                    url,
                    callback=self._parse_listing_page,
                    meta={"category_path": parent_path, "page": page},
                    priority=3,
                )
            return

        self.logger.info(
            "Kategori %s icin %d alt-kategori bulundu.",
            parent_path, len(seen),
        )

        for sub_path in sorted(seen):
            url = response.urljoin(f"{sub_path}?page=1")
            yield scrapy.Request(
                url,
                callback=self.parse_check_category,
                meta={
                    "category_path": sub_path,
                    "depth_level": depth_level + 1,
                },
                priority=2,
                dont_filter=True,
            )

    # ─────────────────────────────────────────────────────────
    # AŞAMA 3: Listeleme sayfalarını tara
    # ─────────────────────────────────────────────────────────

    def _parse_listing_page(self, response):
        """Listeleme sayfasından ilan linklerini çıkar."""
        yield from self._extract_listings(response)

    def _extract_listings(self, response):
        """Sayfadaki tüm ilan detay linklerini çıkar."""
        detail_links = response.css('a[href*="/ilan/"]::attr(href)').getall()
        seen = set()
        for href in detail_links:
            if href in seen:
                continue
            seen.add(href)
            yield response.follow(
                href,
                callback=self.parse_detail,
                priority=10,
            )

        if not seen:
            page = response.meta.get("page", 1)
            category = response.meta.get("category_path", "?")
            self.logger.warning(
                "UYARI: Hic ilan linki bulunamadi! kategori=%s sayfa=%d "
                "url=%s yanit=%d byte",
                category, page, response.url, len(response.text),
            )

    # ─────────────────────────────────────────────────────────
    # AŞAMA 4: İlan detay sayfasını parse et
    # ─────────────────────────────────────────────────────────

    def parse_detail(self, response):
        """İlan detay sayfasını parse et."""
        item = CarItem()

        product_detail = self._parse_product_detail(response)

        # Meta bilgiler
        item["listing_id"] = extract_listing_id(response.url)
        item["url"] = response.url
        item["scraped_at"] = datetime.now(timezone.utc).isoformat()

        # İlan başlığı
        item["ilan_basligi"] = response.css(
            ".sticky-information-title::text"
        ).get("").strip() or response.css("h1::text").get("").strip()

        # Fiyat: önce productDetail, sonra CSS
        if product_detail.get("Price"):
            item["fiyat"] = str(product_detail["Price"])
        else:
            price_text = (
                response.css(".desktop-information-price::text").get("")
                or response.css(".product-price ::text").get("")
            )
            item["fiyat"] = price_text.strip()

        # Konum: önce dataLayer, sonra CSS
        collect_data = self._parse_collect_data(response)
        if collect_data.get("city") or collect_data.get("district"):
            item["sehir"] = collect_data.get("city")
            item["ilce"] = collect_data.get("district")
        else:
            location_parts = response.css(".product-location ::text").getall()
            location_text = " ".join(
                p.strip() for p in location_parts if p.strip()
            )
            self._parse_location(item, location_text)

        # İlan açıklaması
        desc_parts = response.css("#tab-description *::text").getall()
        desc_text = " ".join(
            part.strip() for part in desc_parts if part.strip()
        )
        if desc_text.startswith("Açıklama"):
            desc_text = desc_text[len("Açıklama") :].strip()
        item["ilan_aciklamasi"] = desc_text or None

        # Özellikler tablosu
        for prop in response.css(".property-item"):
            key = prop.css(".property-key::text").get("").strip()
            value = prop.css(".property-value::text").get("").strip()
            field_name = self.PROPERTY_MAP.get(key)
            if field_name and value:
                item[field_name] = value

        # Boya-değişen detayları
        self._parse_damage_data(response, item)

        yield item

    # ─────────────────────────────────────────────────────────
    # Yardımcı metodlar
    # ─────────────────────────────────────────────────────────

    def _extract_total(self, response):
        """Sayfadaki toplam ilan sayısını bul."""
        m = re.search(r'"Total"\s*:\s*(\d+)', response.text)
        if m:
            return int(m.group(1))
        return None

    def _parse_product_detail(self, response):
        """window.productDetail JSON objesini parse et."""
        m = re.search(
            r"window\.productDetail\s*=\s*(\{.*?\});\s*\n",
            response.text,
            re.DOTALL,
        )
        if not m:
            return {}
        try:
            return json.loads(m.group(1))
        except (json.JSONDecodeError, ValueError):
            return {}

    def _parse_collect_data(self, response):
        """dataLayer'dan şehir/ilçe bilgisini çıkar."""
        result = {}
        m = re.search(r"'CD_il'\s*:\s*'([^']*)'", response.text)
        if m:
            result["city"] = m.group(1).strip() or None
        m = re.search(r"'CD_ilce'\s*:\s*'([^']*)'", response.text)
        if m:
            result["district"] = m.group(1).strip() or None
        return result

    def _parse_location(self, item, location_text):
        """'Seyran Mh. Akşehir, Konya' -> sehir='Konya', ilce='Akşehir'"""
        if not location_text:
            item["sehir"] = None
            item["ilce"] = None
            return

        parts = [p.strip() for p in location_text.split(",")]
        if len(parts) >= 2:
            item["sehir"] = parts[-1].strip()
            ilce_part = parts[-2].strip()
            if ilce_part:
                ilce_clean = re.sub(r"^.*?\.\s*", "", ilce_part)
                item["ilce"] = ilce_clean if ilce_clean else ilce_part
            else:
                item["ilce"] = None
        elif len(parts) == 1:
            item["sehir"] = parts[0]
            item["ilce"] = None

    def _parse_damage_data(self, response, item):
        """window.damage JSON verisinden boya-değişen bilgilerini çıkar."""
        damage_match = re.search(
            r"window\.damage\s*=\s*(\[.*?\]);",
            response.text,
            re.DOTALL,
        )
        if not damage_match:
            return

        try:
            damage_data = json.loads(damage_match.group(1))
        except (json.JSONDecodeError, ValueError):
            self.logger.warning(
                "Boya-degisen verisi parse edilemedi: %s", response.url
            )
            return

        for part in damage_data:
            part_name = part.get("Name", "")
            value_desc = part.get("ValueDescription", "")
            field_name = self.DAMAGE_PART_MAP.get(part_name)
            if field_name and value_desc:
                item[field_name] = value_desc
