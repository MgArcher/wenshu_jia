import re
import uuid
import execjs
from lxml import etree
import time
import json
import scrapy
from scrapy.http import Request
import pymongo
from pyquery import PyQuery as pq
from wenshu_jia.items import WenshuJiaItem as ITEM


class QuotesSpider(scrapy.Spider):
    name = "wenshu_x"
    # allowed_domains = ['china.findlaw.cn']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open('encrypt.js', 'r', encoding="utf-8") as f:
            js1 = f.read()
        with open('ywtu.js', 'r', encoding="utf-8") as f:
            js2 = f.read()
        self.js_encrypt = execjs.compile(js1)
        self.js_ywtu = execjs.compile(js2)
        # 定义一个文书id
        self.wenshu_id = '539fa433-85b9-4256-b411-61e380ff9453'
        self.open_spider()

    def open_spider(self):
        self.client = pymongo.MongoClient(
            host='localhost',
            port=27017
        )
        self.db = self.client['caipananli']
        self.collection = self.db['minshi_anli']

    def start_requests(self):
        """
        设定列表页查询条件，第一次请求首页
        :return:
        """
        headers = {
            "Host": "wenshu.court.gov.cn",
            "Origin": "http://wenshu.court.gov.cn",
        }
        url = "http://wenshu.court.gov.cn/List/List?sorttype=1"
        yield Request(url=url, headers=headers, callback=self.second_requests,
                      dont_filter=True, meta={'start_requests': True})

    def second_requests(self, response):
        """
        解析第一次请求的返回值，第二次带cookies请求首页
        :param response:
        :return:
        """
        html = etree.HTML(response.text)
        meta = html.xpath('//*[@id="9DhefwqGPrzGxEp9hPaoag"]/@content')[0]
        ywtu = self.js_ywtu.call("getc", meta)
        cookies = [str(i) for i in response.headers.getlist('Set-Cookie')]
        cookies = ''.join(cookies)
        f80s = re.findall('FSSBBIl1UgzbN7N80S=(.*?);', cookies)[0]
        f80t = re.findall('FSSBBIl1UgzbN7N80T=(.*?);', cookies)[0]
        f80t_n = self.js_encrypt.call("getCookies", meta, f80t, ywtu)
        headers = {
            "Cookie": "FSSBBIl1UgzbN7N80S={}; FSSBBIl1UgzbN7N80T={};".format(
                f80s, f80t_n),
            "Host": "wenshu.court.gov.cn",
            "Origin": "http://wenshu.court.gov.cn",
        }
        url = "http://wenshu.court.gov.cn/List/List?sorttype=1"
        yield Request(url=url, headers=headers, callback=self.third_requests,
                      dont_filter=True, meta={'f80s': f80s,
                                              'f80t_n': f80t_n,
                                              })

    def third_requests(self, response):
        """
        获得第一次请求得到的f80s,f80t_n,获得第二次请求得到的vjkl5
        :param response:
        :return:
        """
        cookies = [str(i) for i in response.headers.getlist('Set-Cookie')]
        cookies = ''.join(cookies)
        vjkl5 = re.findall('vjkl5=(.*?);', cookies)[0]
        f80s = response.meta['f80s']
        f80t_n = response.meta['f80t_n']
        docid = self.wenshu_id

        headers = {
            "Cookie": "FSSBBIl1UgzbN7N80S={}; FSSBBIl1UgzbN7N80T={}; vjkl5={};".format(
                f80s, f80t_n, vjkl5),
            "Origin": "http://wenshu.court.gov.cn"
        }
        url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}".format(docid)
        yield Request(url=url, headers=headers, callback=self.get_wenshu)

    def get_wenshu(self, response):
        try:
            html = response.text
            html = str(html)
            html = html.split('var jsonHtmlData = "')
            x0 = html[0].split('JSON.stringify(')[1].split(');$')[0]
            x0 = json.loads(x0)

            x1 = html[1].split('var jsonData')[0]
            x1 = x1.replace('\\', '')
            x1 = re.sub('";', '', x1)
            x1 = json.loads(x1)

            x0['Title'] = x1['Title']
            x0['PubDate'] = x1['PubDate']
            html = x1['Html']
            html = pq(html)
            text_list = []
            for i in html('div').items():
                text_list.append(i.text())
            x0['text_list'] = text_list
            print(x0)
            self.collection.insert(x0)
        except:
            print(response.text)


if __name__ == '__main__':
    from scrapy.cmdline import execute
    # excute 执行scrapy命令
    import os  # 用来设置路径
    import sys  # 调用系统环境，就如同cmd中执行命令一样

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute("scrapy crawl wenshu_x".split())
