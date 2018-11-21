#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/11/08 16:30
@File    : news_mongo.py
@Desc    : news of mongodb
"""

import sys
import os
from os.path import dirname

_dirname = dirname(os.path.realpath(__file__))
sys.path.append(dirname(_dirname))
confpath = os.path.join(dirname(_dirname), 'conf') + os.sep + 'Default.conf'

try:
    import configparser
except:
    from six.moves import configparser


from mongoengine import register_connection
from mongoengine import Document
from mongoengine import StringField, IntField, ListField, DateTimeField, DictField

import time
from datetime import datetime

config = configparser.ConfigParser()
config.read(confpath, encoding='utf-8')
print(config.sections())

news_mongodb_config = {
    'name': config.get('MongoDB.news', 'name'),
    'username': config.get('MongoDB.news', 'username'),
    'password': config.get('MongoDB.news', 'password'),
    'host': config.get('MongoDB.news', 'host'),
    'port': config.getint('MongoDB.news', 'port'),
    'alias': config.get('MongoDB.news', 'alias')
}
article_mongodb_config_test = {
    'name': config.get('MongoDB.article', 'name'),
    'username': config.get('MongoDB.article', 'username'),
    'password': config.get('MongoDB.article', 'password'),
    'host': config.get('MongoDB.article', 'host'),
    'port': config.getint('MongoDB.article', 'port'),
    'alias': config.get('MongoDB.article', 'alias')
}
print(article_mongodb_config_test)

register_connection(**article_mongodb_config_test)

# _retry = 0
# _status = False
# while not _status and _retry <= 3:
#     try:
#         connect('simhash', host='mongodb://localhost:27017/simhash_invert_index')
#         _status = True
#     except:
#         print("连接失败，正在重试")
#         _status = False
#         _retry += 1
#         time.sleep(2)
#         if _retry == 4:
#             raise Exception("Mongodb连接失败，请检查")

class NewsArticleMark(Document):
    """
    article_info
    """
    article_id = StringField()
    country_lan = StringField()
    one_level = StringField()
    two_level = StringField()
    three_level = StringField()
    need_double_check = IntField()
    mark_level = IntField()
    article_url = StringField()
    title = StringField()
    article = StringField()
    entity_keywords = ListField(StringField())
    semantic_keywords = ListField(StringField())
    # create_time = DateTimeField(default=datetime.now())
    create_time = DateTimeField(default=int(time.time()))
    do_grab = IntField(default=0)

    meta = {
        'db_alias': 'article_repo',
        'strict': False,
        "collection": "article_info",
        "indexes": [
            "article_id",
            "country_lan",
            "one_level",
            "two_level",
            "three_level",
            "need_double_check",
            "mark_level",
            "article_url",
            "title",
            "article",
            "entity_keywords",
            "semantic_keywords",
            "-create_time",
            "do_grab"
        ]
    }

    def __str__(self):

        return 'article_id:{}'.format(self.article_id)

    # def save(self, *args, **kwargs):
    #
    #     return super(NewsArticleMark, self).save(*args, **kwargs)

    def get_all_simhash(self):

        return list(self.objects.all())

    def get_simhash_count(self):

        return len(self.get_all_simhash())


class NewsArticleTrain(Document):
    """
    operate_res
    """
    article_doc_id = StringField()
    article_id = StringField()
    choose_keywords = ListField(StringField())
    manual_keywords = ListField(StringField())
    is_right = IntField()
    one_level = StringField()
    two_level = StringField()
    three_level = StringField()
    op_id = StringField()
    op_name = StringField()
    # op_time = DateTimeField(default=datetime.now())
    op_time = IntField(default=int(time.time()))
    server_time = StringField(default=datetime.now())

    meta = {
        'db_alias': 'article_repo',
        'strict': False,
        "collection": "operate_res",
        "indexes": [
            "article_doc_id",
            "article_id",
            "choose_keywords",
            "manual_keywords",
            "is_right",
            "one_level",
            "two_level",
            "three_level",
            "op_id",
            "op_name",
            "op_time",
            "server_time",
        ]
    }

    def __str__(self):

        return 'article_id:{}'.format(self.article_id)

    def get_all_simhash(self):

        return list(self.objects.all())

    def get_simhash_count(self):

        return len(self.get_all_simhash())



if __name__ == '__main__':
    import random
    import string

    # 写数据到：operate_res
    # for i in range(200):
    #     news = NewsArticleTrain()
    #     news.article_doc_id = 'x{}x'.format(str(i))
    #     news.article_id = str(i)
    #     news.choose_keywords = ["apple", "banana"]
    #     news.manual_keywords = ["hello world", "test1", "test2"]
    #     news.is_right = 0
    #     news.one_level = 'auto'
    #     news.two_level = 'car'
    #     news.three_level = ''
    #     news.op_id = '000001'
    #     news.op_name = 'zhangsan'
    #     news.op_time = int(time.time())
    #     news.server_time = str(datetime.now())
    #     news.save()

    # 写数据到：article_info
    # for i in range(200):
    #     news = NewsArticleMark()
    #     news.article_id = str(i)
    #     news.country_lan = 'IN-EN'
    #     news.one_level = 'auto'
    #     news.two_level = 'car'
    #     news.three_level = ''
    #     news.need_double_check = 0
    #     news.mark_level = 1
    #     article_url = 'http://www.baidu.com'
    #     title = 'test{}'.format(str(i))
    #     news.article = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(100))
    #     news.entity_keywords = ['x{}'.format(str(i)), 'xx{}'.format(str(i))]
    #     news.semantict_keywords = ['apple', 'banana', 'car']
    #     news.create_time = datetime.now()
    #     news.do_grab = 0
    #     news.save()

    # 写数据到cms测试数据库：article_info
    news = NewsArticleMark()
    news.article_id = str(11111)
    news.country_lan = 'IN-EN'
    news.one_level = 'auto'
    news.two_level = 'car'
    news.three_level = ''
    news.need_double_check = 0
    news.mark_level = 1
    article_url = 'http://www.baidu.com'
    title = 'test{}'.format(str(111))
    news.article = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(100))
    news.entity_keywords = ['x{}'.format(str(111)), 'xx{}'.format(str(111))]
    news.semantic_keywords = ['apple', 'banana', 'car']
    news.create_time = datetime.now()
    news.do_grab = 0
    news.save()