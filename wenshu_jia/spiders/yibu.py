"""
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2019/1/9 11:35
@Author  : jiajia
@File    : yibu.py
"""
import re
import time
import json
import execjs
import pymongo
import asyncio
import aiohttp
from lxml import etree
from pyquery import PyQuery as pq
from multiprocessing import Pool

from wenshu_jia.TheUserAgent import UserAgent

ua = UserAgent()
start = time.time()



class WenshuXiangqing(object):
    def __init__(self):
        # 设置超时时间
        self.timeout = 15
        with open('encrypt.js', 'r', encoding="utf-8") as f:
            js1 = f.read()
        with open('ywtu.js', 'r', encoding="utf-8") as f:
            js2 = f.read()
        self.js_encrypt = execjs.compile(js1)
        self.js_ywtu = execjs.compile(js2)
        self.open_spider()

    def open_spider(self):
        self.client = pymongo.MongoClient(
            host='localhost',
            port=27017
        )
        self.db = self.client['caipananli']
        self.collection = self.db['minshi_anli']

    async def get(self, url, headers=None, proxy=None):
        if not headers:
            headers = {
                'User-Agent': ua.random_userAgent()
            }
        conn = aiohttp.TCPConnector(verify_ssl=False)
        if proxy:
            real_proxy = 'http://' + proxy
            print(proxy)
            async with aiohttp.ClientSession(connector=conn) as session:
                # allow_redirects 禁止重定向
                response = await session.get(url, headers=headers, proxy=real_proxy, timeout=self.timeout, allow_redirects=False)
                result = await response.text()
        else:
            async with aiohttp.ClientSession(connector=conn) as session:
                response = await session.get(url, headers=headers, timeout=self.timeout)
                result = await response.text()
        return response, result

    async def get_wenshu(self, result):
        html = result
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
        return x0

    async def liucheng(self, docid, proxy):
        # 第一次请求
        url = 'http://wenshu.court.gov.cn/List/List?sorttype=1'
        headers = {
            "Host": "wenshu.court.gov.cn",
            "Origin": "http://wenshu.court.gov.cn",
            'User-Agent': ua.random_userAgent()
        }
        response, result = await self.get(url, headers, proxy)

        cookies = response.cookies
        html = etree.HTML(result)
        meta = html.xpath('//*[@id="9DhefwqGPrzGxEp9hPaoag"]/@content')[0]
        ywtu = self.js_ywtu.call("getc", meta)
        f80s = re.findall('FSSBBIl1UgzbN7N80S=(.*?);', str(cookies.get('FSSBBIl1UgzbN7N80S')))[0]
        f80t = re.findall('FSSBBIl1UgzbN7N80T=(.*?);', str(cookies.get('FSSBBIl1UgzbN7N80T')))[0]
        f80t_n = self.js_encrypt.call("getCookies", meta, f80t, ywtu)
        # 第二次请求
        headers = {
            "Cookie": "FSSBBIl1UgzbN7N80S={}; FSSBBIl1UgzbN7N80T={};".format(
                f80s, f80t_n),
            "Host": "wenshu.court.gov.cn",
            "Origin": "http://wenshu.court.gov.cn",
        }
        url = "http://wenshu.court.gov.cn/List/List?sorttype=1"
        response, result = await self.get(url, headers, proxy)

        cookies = response.cookies
        vjkl5 = re.findall('vjkl5=(.*?);', str(cookies.get('vjkl5')))[0]
        # 第三次请求
        headers = {
            "Cookie": "FSSBBIl1UgzbN7N80S={}; FSSBBIl1UgzbN7N80T={}; vjkl5={};".format(
                f80s, f80t_n, vjkl5),
            "Origin": "http://wenshu.court.gov.cn"
        }
        url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}".format(docid)
        response, result = await self.get(url, headers, proxy)
        item = await self.get_wenshu(result)
        print(item)
        self.collection.insert(item)

    async def request(self, docid):
        try:
            proxy = '212.57.109.227:41884' # 对接获得代理程序
            # 不使用代理
            proxy = None
            await self.liucheng(docid, proxy)
        except Exception as e:
            print(e)
            print('报错')
            # 网络波动，ip被封，都会报错

    def run(self):
        docid_list = ['539fa433-85b9-4256-b411-61e380ff9453', '952a3bdf-6afe-43fe-ab86-30b14afe492b']
        tasks = [asyncio.ensure_future(self.request(docid)) for docid in docid_list]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

        end = time.time()
        print('Cost time:', end - start)


def main():
    # 开启异步协程
    ws = WenshuXiangqing()
    ws.run()


if __name__ == '__main__':
    # 开启多进程
    p = Pool(2)
    for i in range(2):
        p.apply_async(main, args=())
    p.close()
    p.join()
    # ws = WenshuXiangqing()
    # ws.run()

