from scrapy.exceptions import DropItem

from arabam.utils import clean_km, clean_price, clean_text


class DataCleaningPipeline:
    def process_item(self, item):
        # Fiyat ve km temizleme
        if item.get("fiyat"):
            item["fiyat"] = clean_price(item["fiyat"])
        if item.get("km"):
            item["km"] = clean_km(item["km"])

        # Yıl'ı integer'a çevir
        if item.get("yil"):
            try:
                item["yil"] = int(item["yil"])
            except (ValueError, TypeError):
                pass

        # Tüm metin alanlarını temizle
        text_fields = [
            "ilan_basligi", "sehir", "ilce", "ilan_aciklamasi", "ilan_tarihi",
            "marka", "seri", "model", "vites_tipi", "yakit_tipi", "kasa_tipi",
            "renk", "motor_hacmi", "motor_gucu", "cekis", "arac_durumu",
            "ort_yakit_tuketimi", "yakit_deposu", "agir_hasarli", "boya_degisen",
            "takasa_uygun", "kimden",
            # Boya/değişen alanları
            "sag_arka_camurluk", "arka_kaput", "sol_arka_camurluk",
            "sag_arka_kapi", "sag_on_kapi", "tavan", "sol_arka_kapi",
            "sol_on_kapi", "sag_on_camurluk", "motor_kaputu",
            "sol_on_camurluk", "on_tampon", "arka_tampon",
        ]
        for field in text_fields:
            if item.get(field):
                item[field] = clean_text(item[field])

        return item


class DuplicateFilterPipeline:
    def __init__(self):
        self.seen_ids = set()

    def process_item(self, item):
        listing_id = item.get("listing_id")
        if listing_id in self.seen_ids:
            raise DropItem(f"Tekrarlanan ilan: {listing_id}")
        self.seen_ids.add(listing_id)
        return item
