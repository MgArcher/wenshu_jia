# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import re
import json
import logging
import requests
from scrapy import signals
from scrapy.conf import settings
import random, requests, logging, base64
from wenshu_jia.TheUserAgent import UserAgent


ua = UserAgent()


class RandomUserAgentMiddleware(object):
    '''
    变换的user-agent
    '''

    def process_request(self, request, spider):
        request.headers['User-Agent'] = ua.random_userAgent()

    def process_response(self, request, response, spider):
        '''处理返回的response'''
        html = response.body.decode()
        if (response.status != 200 and response.status != 202) or 'remind key' in html or 'remind' in html or '请开启JavaScript' in html or '服务不可用' in html:
            print('正在重新请求************')

            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        else:
            return response


# 法一:连接阿布云动态代理隧道(付费:IP质量好)
class ABYProxyMiddleware(object):

    """ 阿布云代理中间件 """

    def __init__(self):
        self.proxy_server = "http://http-dyn.abuyun.com:9020"
        proxy_user = "HF58077XJO2431ZD"
        proxy_pass = "B440C79F680AD3A9"
        self.proxy_auth = "Basic " + base64.urlsafe_b64encode(bytes((proxy_user + ":" + proxy_pass), "ascii")).decode("utf8")

    def process_request(self, request, spider):
        request.meta["proxy"] = self.proxy_server
        request.headers["Proxy-Authorization"] = self.proxy_auth


class ProxyMiddleware(object):
    """
    代理
    """
    def __init__(self, proxy_url):
        self.logger = logging.getLogger(__name__)
        self.proxy_url = proxy_url
        self.proxy_url_http = settings.get('PROXY_URL_HTTP')

    def get_random_proxy(self):
        try:
            response = requests.get(self.proxy_url, timeout=5)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return False

    def get_random_proxy_http(self):
        try:
            response = requests.get(self.proxy_url_http, timeout=5)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        the_http = request.url.split('://')[0]
        if 'https' in the_http:
            proxy = self.get_random_proxy()
            if proxy:
                uri = 'https://{proxy}'.format(proxy=proxy)
                proxy = str(proxy)
                self.logger.debug('使用代理 ' + proxy)
                request.meta['proxy'] = uri
        else:
            proxy = self.get_random_proxy_http()
            if proxy:
                uri = 'http://{proxy}'.format(proxy=proxy)
                proxy = str(proxy)
                self.logger.debug('使用代理 ' + proxy)
                request.meta['proxy'] = uri
        # if request.meta.get('retry_times'):
        #     proxy = self.get_random_proxy()
        #     if proxy:
        #         uri = 'https://{proxy}'.format(proxy=proxy)
        #         self.logger.debug('使用代理 ' + proxy)
        #         request.meta['proxy'] = uri


    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            proxy_url=settings.get('PROXY_URL')
        )



