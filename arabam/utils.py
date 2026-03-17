import re


def clean_price(text):
    """'1.250.000 TL' -> 1250000"""
    if not text:
        return None
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else None


def clean_km(text):
    """'45.000 km' -> 45000"""
    if not text:
        return None
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else None


def clean_text(text):
    """Boşlukları temizle, boş string'i None yap."""
    if not text:
        return None
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text if text else None


def extract_listing_id(url):
    """URL'den ilan ID'sini çıkar. Örn: /ilan/.../38705623 -> 38705623"""
    if not url:
        return None
    match = re.search(r"/(\d+)(?:\?|$)", url)
    return match.group(1) if match else None
