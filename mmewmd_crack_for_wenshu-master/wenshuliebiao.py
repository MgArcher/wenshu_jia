import uuid
import requests
import execjs
from lxml import etree
import time
import json
from TheUserAgent import UserAgent
ua = UserAgent()

with open('encrypt.js', 'r', encoding="utf-8") as f:
    js1 = f.read()
    ctx1 = execjs.compile(js1)
with open('ywtu.js', 'r', encoding="utf-8") as f:
    js2 = f.read()
    ctx2 = execjs.compile(js2)
with open('vl5x.js', 'r', encoding="utf-8") as fp:
    js = fp.read()
    ctx = execjs.compile(js)

headers = {
        "Host": "wenshu.court.gov.cn",
        "Origin": "http://wenshu.court.gov.cn",
        "User-Agent": ua.random_userAgent()
    }
url = "http://wenshu.court.gov.cn/List/List?sorttype=1"

rsp = requests.get(url, headers=headers)
print(rsp)
html = etree.HTML(rsp.text)
meta = html.xpath('//*[@id="9DhefwqGPrzGxEp9hPaoag"]/@content')[0]
print(rsp.text)
print('#####')
print(meta)
print('#####')
ywtu = ctx2.call("getc", meta)
f80s = rsp.cookies['FSSBBIl1UgzbN7N80S']
f80t = rsp.cookies['FSSBBIl1UgzbN7N80T']
f80t_n = ctx1.call("getCookies", meta, f80t, ywtu)
print(ywtu)
print(f80s)
print(f80t)
print(f80t_n)
print()

headers = {
    "Cookie": "FSSBBIl1UgzbN7N80S={}; FSSBBIl1UgzbN7N80T={};".format(
        f80s, f80t_n),
    "Host": "wenshu.court.gov.cn",
    "Origin": "http://wenshu.court.gov.cn",
    "User-Agent": ua.random_userAgent()
}
url = "http://wenshu.court.gov.cn/List/List?sorttype=1"

rsp = requests.get(url, headers=headers)
print(rsp)

vjkl5 = rsp.cookies['vjkl5']
vl5x = (ctx.call('getKey', vjkl5))
print(vjkl5)
print(vl5x)
print()


header = {
        "User-Agent": ua.random_userAgent(),
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
response = requests.post(url_num, data=data, headers=header)
number = response.text
number = number[:4]



data = {
    "Param": "案件类型:民事案件",
    "Index": "1",
    "Page": "10",
    "Order": "法院层级",
    "Direction": "asc",
    "vl5x": vl5x,
    "number": number,
    "guid": guid
}

headers = {
    "Cookie": "FSSBBIl1UgzbN7N80S={}; FSSBBIl1UgzbN7N80T={}; vjkl5={};".format(
        f80s, f80t_n, vjkl5),
    "Origin": "http://wenshu.court.gov.cn",
    "User-Agent": ua.random_userAgent()
}
url = "http://wenshu.court.gov.cn/List/ListContent"
rsp = requests.post(url, headers=headers, data=data)
print(data)
print(rsp.text)

# with open(r'docid.js', encoding='utf-8') as f:
#     jsdata_2 = f.read()
# js_2 = execjs.compile(jsdata_2)
# runeval = json_list[0]['RunEval']
# casewenshuid = json_list[-1].get('文书ID', '')
# print(runeval)
# print(casewenshuid)
# docid = js_2.call('get_docid', runeval, casewenshuid)
# print(docid)
#
# headers = {
#     "Cookie": "FSSBBIl1UgzbN7N80S={}; FSSBBIl1UgzbN7N80T={}; vjkl5={};".format(
#         f80s, f80t_n, vjkl5),
#     "Origin": "http://wenshu.court.gov.cn",
#     "User-Agent": ua.random_userAgent()
# }
# url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}".format(docid)
# rsp = requests.get(url, headers=headers)
# print(rsp.text)
