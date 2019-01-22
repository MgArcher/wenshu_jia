"""
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2019/1/16 15:42
@Author  : jiajia
@File    : ziji_demo.py
"""
"http://wenshu.court.gov.cn/list/list/?sorttype=1&number=QNYANHGM&guid=08890d44-0243-a2d3b0ad-e2a53037255e&conditions=searchWord+QWJS+++%E5%85%A8%E6%96%87%E6%A3%80%E7%B4%A2:%E5%A9%9A%E5%A7%BB"
import requests
import uuid
from urllib.parse import quote, urlencode
from TheUserAgent import UserAgent
ua = UserAgent()


def get_guid():
    guid = str(uuid.uuid1())
    guid = guid.split('-')
    guid = "%s-%s-%s%s-%s" % tuple(guid)
    return guid


def get_vjk15():
    url = 'http://wenshu.court.gov.cn'
    header = {
        'User-Agent': ua.random_userAgent(),
    }
    response = requests.get(url, headers=header)
    vjkl5 = response.headers['Set-Cookie']
    vjkl5 = vjkl5.split(';')[0].split('=')[1]
    return vjkl5


def get_number(guid):
    header = {
        'User-Agent': ua.random_userAgent(),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://wenshu.court.gov.cn'
    }
    url_num = 'http://wenshu.court.gov.cn/ValiCode/GetCode'
    data = {
        'guid': guid
    }
    response = requests.post(url_num, data=data, headers=header)
    number = response.text
    return number


def get_url(guid, number):
    url = r"http://wenshu.court.gov.cn/list/list/?"
    condit = "searchWord+QWJS+++" + quote('案由') + ':' + quote('遗赠扶养协议纠纷')
    parse = {
        'sorttype': '1',
        'number': number,
        'guid': guid,
    }
    url = url + urlencode(parse) + "&conditions=" + condit
    return url


if __name__ == '__main__':
    guid = get_guid()
    number = get_number(guid)
    url = get_url(guid, number)
    lua = """
function main(splash)
  splash:go("%s")
  splash:wait(50)
  return {
    html = splash:html(),
  }
end
"""
    lua = lua % url
    print(lua)
