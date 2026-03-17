import os
os.makedirs("logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

BOT_NAME = "arabam"

SPIDER_MODULES = ["arabam.spiders"]
NEWSPIDER_MODULE = "arabam.spiders"

# Polite scraping
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# Retry
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Timeout
DOWNLOAD_TIMEOUT = 30

# HTTP Cache (geliştirme için, production'da kapatılabilir)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = "httpcache"

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
        "indent": 2,
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
