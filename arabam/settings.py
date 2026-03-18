import os
os.makedirs("logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

BOT_NAME = "arabam"

SPIDER_MODULES = ["arabam.spiders"]
NEWSPIDER_MODULE = "arabam.spiders"

# Hız ayarları — 4000 request'te 0 hata (429/503 yok) olduğu için güvenle artırıldı
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 6
CONCURRENT_REQUESTS_PER_DOMAIN = 6
ROBOTSTXT_OBEY = True

# AutoThrottle — sunucu yanıt süresine göre otomatik hız ayarı
# Site yavaşlarsa otomatik olarak geri çekilir, güvenlik ağı görevi görür
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.5
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 3.0
AUTOTHROTTLE_DEBUG = False

# Retry
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Timeout
DOWNLOAD_TIMEOUT = 30

# HTTP Cache KAPALI — 6GB disk israfı ve bozuk sayfa riski
HTTPCACHE_ENABLED = False

# Middlewares
DOWNLOADER_MIDDLEWARES = {
    "arabam.middlewares.UserAgentRotationMiddleware": 400,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
}

# Pipelines
ITEM_PIPELINES = {
    "arabam.pipelines.DataCleaningPipeline": 100,
    "arabam.pipelines.DuplicateFilterPipeline": 200,
}

# JSON çıktı
FEEDS = {
    "output/arabam_%(time)s.json": {
        "format": "json",
        "encoding": "utf-8",
        "indent": None,  # Compact JSON — disk tasarrufu (~%40 daha küçük dosya)
    },
}

# Headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/arabam.log"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
