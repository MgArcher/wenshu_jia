# -*- coding: utf-8 -*-

# Scrapy settings for wenshu_jia project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'wenshu_jia'

SPIDER_MODULES = ['wenshu_jia.spiders']
NEWSPIDER_MODULE = 'wenshu_jia.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'wenshu_jia (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1
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
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'wenshu_jia.middlewares.WenshuJiaSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'wenshu_jia.middlewares.WenshuJiaDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'wenshu_jia.pipelines.WenshuJiaPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
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
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate',
}

DOWNLOADER_MIDDLEWARES = {
   'wenshu_jia.middlewares.RandomUserAgentMiddleware': 543,
    # 'wenshu_jia.middlewares.ProxyMiddleware': 544,
    'wenshu_jia.middlewares.ABYProxyMiddleware': 545,
}

# ITEM_PIPELINES = {
#     'wenshu_jia.pipelines.manage_pipelines': 300,
#     'wenshu_jia.pipelines.MongoDBPipeline': 301,
#     'wenshu_jia.pipelines.MysqlPipeline': 302,
# }


######################
CONCURRENT_REQUESTS_PER_SPIDER = 5 # 线程数(因为阿布云设置的是每秒最多5个请求,有钱可以加到100的并发)
CONCURRENT_REQUESTS_PER_DOMAIN = 1000000 # 任何单个域执行的并发（即同时）请求的最大数量
# CONCURRENT_REQUESTS_PER_IP = 0 # 任何单个IP执行的并发（即同时）请求的最大数量 ; 默认值（0），这样就禁用了对每个IP的限制

# 启用DNS内存缓存
DNSCACHE_ENABLED = True
# 禁用cookies
COOKIES_ENABLED = False
# 禁止重定向
REDIRECT_ENABLED = False
# 添加 Redis 缓存url链接,防止爬取丢失
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# SCHEDULER_PERSIST = True
# REDIS_URL = 'redis://@39.108.219.137:6379'

# 输出日志  确定位置，级别
# LOG_FILE = './log_7down.log'
# LOG_LEVEL = 'WARNING'
# MongoDB
MONGODB_HOST = '39.108.219.137'
MONGODB_PORT = 27017
MONGODB_DB = 'jiajia'
MONGODB_TABLE = 'zfwwd'
# mysql
MYSQL_CONFIG = {
        'host': "39.108.219.137",
        'port': 3306,
        'username': "root",
        'password': "12345678",
        'database': "jiajia",
        'charset': "utf8"
    }
TABLE = 'zfwwd'
# # 设置多少次插入语句提交一次事务
# Submit_the_number = 50

# 获取代理
PROXY_URL = 'http://39.108.219.137:5432/random'
PROXY_URL_HTTP = 'http://39.108.219.137:5431/random'
# 设置下载文件存储路径
IMAGES_STORE = 'D:\\图片'
MEDIA_ALLOW_REDIRECTS = True

#设置重试
RETRY_ENABLED = True
RETRY_TIMES = 10
RETRY_HTTP_CODES = [401, 403, 408, 414, 500, 502, 503, 504, 302]