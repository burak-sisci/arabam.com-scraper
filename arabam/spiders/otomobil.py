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

    # Her listeleme sayfası işlendiğinde sonraki N sayfayı kuyruğa al
    LISTING_BATCH_SIZE = 5

    async def start(self):
        """İlk sayfa ile başla, toplam sayfa sayısını öğren."""
        yield scrapy.Request(
            f"{self.BASE_URL}?page=1",
            callback=self.parse_listing,
            meta={"page": 1, "batch_leader": True},
        )

    def parse_listing(self, response):
        """Listeleme sayfasından ilan linklerini çıkar, sonraki sayfaya geç."""
        page = response.meta["page"]
        is_batch_leader = response.meta.get("batch_leader", False)

        # İlan detay linklerini çıkar (yüksek priority -> önce işlenir)
        detail_links = response.css('a[href*="/ilan/"]::attr(href)').getall()
        seen = set()
        for href in detail_links:
            if href in seen:
                continue
            seen.add(href)
            yield response.follow(
                href, callback=self.parse_detail, priority=1
            )

        # İlk sayfada toplam sayfa sayısını öğren
        if page == 1:
            total = self._extract_total(response)
            if total:
                per_page = max(len(seen), 20)
                self.max_page = (total + per_page - 1) // per_page
                self.logger.info(
                    "Toplam %d ilan, %d sayfa bulundu.", total, self.max_page
                )
            else:
                self.max_page = None

        # Sadece batch leader sonraki batch'i kuyruğa alır (çoğalma önlenir)
        if not is_batch_leader:
            return

        max_page = getattr(self, "max_page", None)
        if max_page and page < max_page:
            batch_start = page + 1
            batch_end = min(page + self.LISTING_BATCH_SIZE, max_page)
            for p in range(batch_start, batch_end + 1):
                yield scrapy.Request(
                    f"{self.BASE_URL}?page={p}",
                    callback=self.parse_listing,
                    meta={
                        "page": p,
                        # Son sayfa sonraki batch'i tetikler
                        "batch_leader": p == batch_end,
                    },
                )
        elif not max_page and seen:
            yield scrapy.Request(
                f"{self.BASE_URL}?page={page + 1}",
                callback=self.parse_listing,
                meta={"page": page + 1, "batch_leader": True},
            )

    def _extract_total(self, response):
        """Sayfadaki toplam ilan sayısını bul."""
        m = re.search(r'"Total"\s*:\s*(\d+)', response.text)
        if m:
            return int(m.group(1))
        return None

    def parse_detail(self, response):
        """İlan detay sayfasını parse et."""
        item = CarItem()

        # window.productDetail JSON'unu parse et (fiyat, konum vb. için)
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
            location_text = " ".join(p.strip() for p in location_parts if p.strip())
            self._parse_location(item, location_text)

        # İlan açıklaması
        desc_parts = response.css("#tab-description *::text").getall()
        desc_text = " ".join(
            part.strip() for part in desc_parts if part.strip()
        )
        if desc_text.startswith("Açıklama"):
            desc_text = desc_text[len("Açıklama"):].strip()
        item["ilan_aciklamasi"] = desc_text or None

        # Özellikler tablosu
        for prop in response.css(".property-item"):
            key = prop.css(".property-key::text").get("").strip()
            value = prop.css(".property-value::text").get("").strip()
            field_name = self.PROPERTY_MAP.get(key)
            if field_name and value:
                item[field_name] = value

        # Boya-değişen detayları (window.damage JS değişkeninden)
        self._parse_damage_data(response, item)

        yield item

    # --- Yardımcı metodlar ---

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
                "Boya-değişen verisi parse edilemedi: %s", response.url
            )
            return

        for part in damage_data:
            part_name = part.get("Name", "")
            value_desc = part.get("ValueDescription", "")
            field_name = self.DAMAGE_PART_MAP.get(part_name)
            if field_name and value_desc:
                item[field_name] = value_desc
