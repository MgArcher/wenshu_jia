# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import re
import random

import pymysql
import pymongo

from scrapy import Request
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

from wenshu_jia.items import WenshuJiaItem
ITEM = WenshuJiaItem


class manage_pipelines(object):

    """
    数据处理类，对item的数据进行处理
    """

    def process_item(self, item, spider):
        for key in dict(item):
            if not item[key]:
                item[key] = '无'
        answer = item['answer']
        answer = '||'.join(answer) if answer else '无'
        answer = re.sub('\n|\r|\t|\s', '', answer)

        question = item['question']
        question = re.sub('\n|\r|\t|\s', '', question)

        item['question'] = question
        item['answer'] = answer
        item['dq'] = item['dq'] if item['dq'] else '无'
        the_time = item['time']
        the_time = re.findall(
            '[0-9]{4}-[0-9]{0,2}-[0-9]{0,2}'
            , the_time)
        item['time'] = the_time[0] if the_time else '无'

        return item


class MySQL:
    """
    mysql调用的类
    """
    __db = None

    # 在这里配置自己的SQL服务器
    __config = settings['MYSQL_CONFIG']

    def __init__(self):
        self.__connect()

    def __del__(self):
        if(self.__db is not None):
            self.__connect().commit()
            self.__db.close()

    def __connect(self):
        if (self.__db == None):
            # self.__db = POOL.connection()
            self.__db = pymysql.connect(
                    host   =self.__config['host'],
                    port   =self.__config['port'],
                    user   =self.__config['username'],
                    passwd =self.__config['password'],
                    db     =self.__config['database'],
                    charset=self.__config['charset']
                )
        return self.__db




    def query(self,_sql):
        cursor = self.__connect().cursor()
        try:
            cursor.execute(_sql)
            data = cursor.fetchall()
            # 提交到数据库执行
            self.__connect().commit()
        except:
            # 如果发生错误则回滚
            self.__connect().rollback()
            return False
        return data


    def query_dic(self,_sql_dic):
        if('select' in _sql_dic.keys()):
            sql = "SELECT "+_sql_dic['select']+" FROM "+_sql_dic['from']+self.where(_sql_dic['where'])

            return self.query(sql)
        elif ('update' in _sql_dic.keys()):
            sql = "update " + _sql_dic['update'] + ' set ' + _sql_dic['domain_array'] + '=' + _sql_dic['value_array'] + self.where(_sql_dic['where'])

            return self.query(sql)
        elif('insert' in _sql_dic.keys()):
            sql = "INSERT INTO "+_sql_dic['insert']+self.quote(_sql_dic['domain_array'],type_filter=False)+" VALUES "+self.quote(_sql_dic['value_array'])

            return self.query(sql)
        if ('delete' in _sql_dic.keys()):
            sql = "DELETE FROM " + _sql_dic['delete'] + self.where(_sql_dic['where'])

            return self.query(sql)

    def where(self, _sql):
        if not isinstance(_sql, dict):
            return " WHERE " + str(_sql)
        if isinstance(_sql, dict):
            _sql_dic = _sql
            s = " WHERE "
            index = 0
            for domain in _sql_dic:
                if index==0:
                    s += domain+"=" + str(_sql_dic[domain]) +" "
                    index += 1
                else:
                    s += "AND "+domain + "=" + str(_sql_dic[domain]) + " "
            return s

    # 为数组加上外括号，并拼接字符串
    def quote(self, _data_array, type_filter=True):
        s = "("
        index = 0
        if type_filter:
            for domain in _data_array:
                if index == 0:
                    if isinstance(domain, int):
                        s += str(domain)
                    elif isinstance(domain, str):
                        s += "'" + domain + "'"
                    index += 1
                else:
                    if isinstance(domain, int):
                        s += ", " + str(domain)
                    elif isinstance(domain, str):
                        s += ", " + "'" + domain + "'"
        else:
            for domain in _data_array:
                if index == 0:
                    s += str(domain)
                    index += 1
                else:
                    s += ", " + domain
        return s+")"

    # 建立游标指针
    def cursor(self):
        return self.__connect().cursor()

    # 提价事务
    def commit(self):
        return self.__connect().commit()

    # 想指针提交sql语句

    def execute(self, insertsql):
        self.cursor().execute(insertsql)


class MysqlPipeline(object):
    """
    数据存储到mysql
    """
    def __init__(self):
        self.count = 0
        self.mysql = MySQL()
        self.mysql.cursor()
        self.begin = False

    def create_table(self, table, keys):
        select_sql = "SELECT table_name FROM information_schema.TABLES WHERE table_name ='%s';" % table
        if self.mysql.query(select_sql):
            print('表已经存在')
        else:
            create_sql1 = "CREATE TABLE `%s` (`id` int(11) NOT NULL AUTO_INCREMENT," % table
            create_sql2 = ["`%s` longtext" % key for key in keys]
            create_sql2 = ','.join(create_sql2) + ','
            create_sql3 ="PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8"
            create_sql = create_sql1 + create_sql2 + create_sql3
            self.mysql.execute(create_sql)

    def process_item(self, item, spider):
        if isinstance(item, ITEM):
            item = dict(item)
            the_keys = tuple(item)
            the_values = [pymysql.escape_string(item[key]) for key in the_keys]
            Table = settings['TABLE']
            if self.begin == False:
                self.create_table(Table, the_keys)
                self.begin = True

            insertsql = "INSERT INTO " + Table + self.mysql.quote(the_keys, type_filter=False) + " VALUES " + self.mysql.quote(the_values) + ";"
            try:
                self.mysql.execute(insertsql)
            except :
                print('字符编码有问题')
            # 每500次执行一次事务
            self.count += 1
            if self.count % 500 == 0:
                self.mysql.commit()
            return item


class MongoDBPipeline(object):
    """
    数据存储到mongoDB
    """
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(
            host=settings['MONGODB_HOST'],
            port=settings['MONGODB_PORT']
        )
        self.db = self.client[settings['MONGODB_DB']]
        self.collection = self.db[settings['MONGODB_TABLE']]
        # 由于不能同时开启多个,使用isinstance进行判断

    def process_item(self, item, spider):
        if isinstance(item, ITEM):
            law_infos = dict(item)
            self.collection.insert(law_infos)
            return item


class Image_pipelines(ImagesPipeline):
    """
    图片下载类
    """
    IMAGES_STORE = get_project_settings().get("IMAGES_STORE")

    def get_media_requests(self, item, info):
        image_url = item['url']
        yield Request(url=image_url, meta={'name': item['title'], 'lb': item['lb']})

    def file_path(self, request, response=None, info=None):
        file_name = request.meta['name']
        file_name = file_name + str(random.randint(10000, 100000)) + '.jpg'
        path_name = request.meta['lb']
        file_name = path_name + '\\' + file_name
        return file_name

    def item_completed(self, results, item, info):
        image_path = [x['path'] for ok, x in results if ok]
        if not image_path:
            raise DropItem('下载失败')
        return item
