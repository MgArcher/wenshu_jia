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
    name = "wenshu"
    # allowed_domains = ['china.findlaw.cn']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open('encrypt.js', 'r', encoding="utf-8") as f:
            js1 = f.read()
        with open('ywtu.js', 'r', encoding="utf-8") as f:
            js2 = f.read()
        with open('vl5x.js', 'r', encoding="utf-8") as fp:
            js = fp.read()
        with open(r'docid.js', encoding='utf-8') as f:
            jsdata_2 = f.read()
        self.js_encrypt = execjs.compile(js1)
        self.js_ywtu = execjs.compile(js2)
        self.js_vl5x = execjs.compile(js)
        self.js_docid = execjs.compile(jsdata_2)
        self.search_criteria = ['案件类型:民事案件']
        '494'
        self.open_spider()

    def open_spider(self):
        self.client = pymongo.MongoClient(
            host='localhost',
            port=27017
        )
        self.db = self.client['caipananli']
        self.collection = self.db['minshi_anli']
        self.collection_b = self.db['minshi_liebiao']

    def start_requests(self):
        """
        设定列表页查询条件，第一次请求首页
        :return:
        """
        for criteria in self.search_criteria:
            for i in range(1, 21):
                headers = {
                    "Host": "wenshu.court.gov.cn",
                    "Origin": "http://wenshu.court.gov.cn",
                }
                url = "http://wenshu.court.gov.cn/List/List?sorttype=1"
                yield Request(
                    url=url,
                    headers=headers,
                    callback=self.second_requests,
                    dont_filter=True,
                    meta={
                        'criteria': criteria,
                        'index': str(i),
                        'start_requests': True
                    })

    def again_requests(self, criteria, index):
        """
        重新请求
        :param criteria:
        :param index:
        :return:
        """
        headers = {
            "Host": "wenshu.court.gov.cn",
            "Origin": "http://wenshu.court.gov.cn",
        }
        url = "http://wenshu.court.gov.cn/List/List?sorttype=1"
        yield Request(
            url=url,
            headers=headers,
            callback=self.second_requests,
            dont_filter=True,
            meta={
                'criteria': criteria,
                'index': index,
                'start_requests': True
            })

    def second_requests(self, response):
        """
        解析第一次请求的返回值，第二次带cookies请求首页
        :param response:
        :return:
        """
        try:
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
            yield Request(
                url=url, headers=headers,
                callback=self.third_requests,
                dont_filter=True,
                meta={
                    'criteria': response.meta['criteria'],
                    'f80s': f80s,
                    'f80t_n': f80t_n,
                    'index': response.meta['index']
                })
        except Exception as e:
            print('异常，重新开始', e)
            criteria = response.meta['criteria']
            index = response.meta['index']
            self.again_requests(criteria, index)


    def third_requests(self, response):
        """
        获得第一次请求得到的参数和第二次请求的参数，构造guid，获取number
        :param response:
        :return:
        """
        try:
            cookies = [str(i) for i in response.headers.getlist('Set-Cookie')]
            cookies = ''.join(cookies)
            vjkl5 = re.findall('vjkl5=(.*?);', cookies)[0]
            vl5x = self.js_vl5x.call('getKey', vjkl5)
            header = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'http://wenshu.court.gov.cn'
            }
            url_num = 'http://wenshu.court.gov.cn/ValiCode/GetCode'
            guid = str(uuid.uuid1())
            guid = guid.split('-')
            guid = "%s-%s-%s%s-%s" % tuple(guid)
            data = {
                'guid': guid
            }
            yield scrapy.FormRequest(
                url=url_num,
                headers=header,
                formdata=data,
                callback=self.fourth_requests,
                dont_filter=True,
                meta={
                 'vjkl5': vjkl5,
                 'vl5x': vl5x,
                 'guid': guid,
                 'f80s': response.meta['f80s'],
                 'f80t_n': response.meta['f80t_n'],
                 'criteria': response.meta['criteria'],
                 'index': response.meta['index']
                }, )
        except Exception as e:
            print('异常，重新开始', e)
            criteria = response.meta['criteria']
            index = response.meta['index']
            self.again_requests(criteria, index)

    def fourth_requests(self, response):
        """
        请求列表页
        :param response:
        :return:
        """
        try:
            number = response.text
            number = number[:4]
            guid = response.meta['guid']
            f80s = response.meta['f80s']
            f80t_n = response.meta['f80t_n']
            vjkl5 = response.meta['vjkl5']
            vl5x = response.meta['vl5x']
            param = response.meta['criteria']
            headers = {
                "Cookie": "FSSBBIl1UgzbN7N80S={}; FSSBBIl1UgzbN7N80T={}; vjkl5={};".format(
                    f80s, f80t_n, vjkl5),
                "Origin": "http://wenshu.court.gov.cn",
            }
            url = "http://wenshu.court.gov.cn/List/ListContent"
            data = {
                "Param": param,
                "Index": response.meta['index'],
                "Page": "10",
                "Order": "法院层级",
                "Direction": "asc",
                "vl5x": vl5x,
                "number": number,
                "guid": guid
            }
            yield scrapy.FormRequest(
                url=url,
                formdata=data,
                headers=headers,
                dont_filter=True,
                callback=self.get_list,
                meta={
                 'vjkl5': vjkl5,
                 'f80s': f80s,
                 'f80t_n': f80t_n,
                 'criteria': response.meta['criteria'],
                 'index': response.meta['index']
                   },)
        except Exception as e:
            print('异常，重新开始', e)
            criteria = response.meta['criteria']
            index = response.meta['index']
            self.again_requests(criteria, index)

    def get_list(self, response):
        """
        列表页出现remind
        文书id解密出错

        解析列表页，解密docid
        :param response:
        :return:
        """
        try:
            res_json = eval(json.loads(response.text))
            RunEval = res_json[0]['RunEval']
            # 判断count数来判断获取的全不全
            count = res_json[0]['Count']
            for item in res_json[1:]:
                try:
                    docid = self.js_docid.call('get_docid', RunEval, item['文书ID'])
                    item['文书ID'] = docid
                    self.collection_b.insert(item)
                except:
                    print('文书id解密出错')
                    print(item)
        except Exception as e:
            print('异常，重新开始', e)
            criteria = response.meta['criteria']
            index = response.meta['index']
            self.again_requests(criteria, index)


if __name__ == '__main__':
    from scrapy.cmdline import execute
    # excute 执行scrapy命令
    import os  # 用来设置路径
    import sys  # 调用系统环境，就如同cmd中执行命令一样

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute("scrapy crawl wenshu".split())
