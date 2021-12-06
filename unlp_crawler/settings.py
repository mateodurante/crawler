# Scrapy settings for unlp_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'unlp_crawler'

SPIDER_MODULES = ['unlp_crawler.spiders']
NEWSPIDER_MODULE = 'unlp_crawler.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'unlp_crawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'unlp_crawler.middlewares.UnlpCrawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'unlp_crawler.middlewares.UnlpCrawlerDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'unlp_crawler.pipelines.UnlpCrawlerPipeline': 300,
#}
# Configure your pipelinesinsettings.py
# ITEM_PIPELINES = {
#     'unlp_crawler.pipelines.PreparePipeline': 100,
#     'unlp_crawler.pipelines.MongoDBPipeline': 300,
#     'unlp_crawler.pipelines.ElasticSearchPipeline': 400,
#     }

ITEM_PIPELINES = {
    'unlp_crawler.pipelines.PreparePipeline': 100,
    'unlp_crawler.pipelines.PersistencePipeline': 300,
    }

# Seleccionar el tipo de persistencia a utilizar
# types: 'elasticsearch', 'mongodb', 'sqlite', 'mysql', 'postgresql'
PERSISTENCE_TYPE = 'sqlite'

ELASTICSEARCH_SERVER = 'localhost'
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX_PREFIX = 'unlp2'

MONGO_SERVER = 'localhost'
MONGO_PORT = 27017
MONGO_DATABASE = 'unlp2'

SQLITE_DB = 'unlp2.db'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


import logging
from logging.handlers import RotatingFileHandler

from scrapy.utils.log import configure_logging

# LOG_ENABLED = False
# # Disable default Scrapy log settings.
configure_logging(install_root_handler=False)

# # Define your logging settings.
log_file = 'unlp.log'

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotating_file_log = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=1)
rotating_file_log.setLevel(logging.INFO)
rotating_file_log.setFormatter(formatter)
root_logger.addHandler(rotating_file_log)

# logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)


import logstash

host = 'localhost'

test_logger = logging.getLogger()
test_logger.setLevel(logging.INFO)
h = logstash.TCPLogstashHandler(host, 5000, version=1)
h.setLevel(logging.INFO)
test_logger.addHandler(h)

test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message.')
test_logger.warning('python-logstash: test logstash warning message.')

offsite_logger = logging.getLogger('scrapy.spidermiddlewares.offsite')
offsite_logger.setLevel(logging.DEBUG)
offsite_h = logstash.TCPLogstashHandler(host, 5000, version=1)
offsite_h.setLevel(logging.DEBUG)
offsite_logger.addHandler(offsite_h)



# LOG_LEVEL = 'ERROR'  # to only display errors
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'unlp.log'




##### BROAD CRAWLING #####

# Scrapy’s default scheduler priority queue is 'scrapy.pqueues.ScrapyPriorityQueue'. It works best during single-domain crawl. It does not work well with crawling many different domains in parallel
SCHEDULER_PRIORITY_QUEUE = 'scrapy.pqueues.DownloaderAwarePriorityQueue'

# The default global concurrency limit in Scrapy is not suitable for crawling many different domains in parallel, so you will want to increase it. How much to increase it will depend on how much CPU and memory you crawler will have available.
# But the best way to find out is by doing some trials and identifying at what concurrency your Scrapy process gets CPU bounded. For optimum performance, you should pick a concurrency where CPU usage is at 80-90%.
CONCURRENT_REQUESTS = 100

# Currently Scrapy does DNS resolution in a blocking way with usage of thread pool. With higher concurrency levels the crawling could be slow or even fail hitting DNS resolver timeouts. Possible solution to increase the number of threads handling DNS queries. The DNS queue will be processed faster speeding up establishing of connection and crawling overall.
REACTOR_THREADPOOL_MAXSIZE = 20

# When doing broad crawls you are often only interested in the crawl rates you get and any errors found. These stats are reported by Scrapy when using the INFO log level. In order to save CPU (and log storage requirements) you should not use DEBUG log level when preforming large broad crawls in production. Using DEBUG level when developing your (broad) crawler may be fine though.
LOG_LEVEL = 'INFO'

# Disable cookies unless you really need. Cookies are often not needed when doing broad crawls (search engine crawlers ignore them), and they improve performance by saving some CPU cycles and reducing the memory footprint of your Scrapy crawler.
COOKIES_ENABLED = False

# Retrying failed HTTP requests can slow down the crawls substantially, specially when sites causes are very slow (or fail) to respond, thus causing a timeout error which gets retried many times, unnecessarily, preventing crawler capacity to be reused for other domains.
RETRY_ENABLED = False

# Unless you are crawling from a very slow connection (which shouldn’t be the case for broad crawls) reduce the download timeout so that stuck requests are discarded quickly and free up capacity to process the next ones.
DOWNLOAD_TIMEOUT = 15

# Consider disabling redirects, unless you are interested in following them. When doing broad crawls it’s common to save redirects and resolve them when revisiting the site at a later crawl. This also help to keep the number of request constant per crawl batch, otherwise redirect loops may cause the crawler to dedicate too many resources on any specific domain.
# REDIRECT_ENABLED = False

# Some pages (up to 1%, based on empirical data from year 2013) declare themselves as ajax crawlable. This means they provide plain HTML version of content that is usually available only via AJAX. Pages can indicate it in two ways:
    # by using #! in URL - this is the default way;
    # by using a special meta tag - this way is used on “main”, “index” website pages.
AJAXCRAWL_ENABLED = True



##### breadth-first-search (BFS) CRAWLING #####

DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

