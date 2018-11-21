#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/13 16:57
@File    : proxy_pipeline.py
@Desc    : data storage pipeline
"""

import sys

from spider.antispider.proxypool.proxy_sqlitedb import ProxySqliteDB

class SqlitePipeline(object):

    @staticmethod
    def save_data(verified_queue, db_proxy_num):
        '''
        读取队列中的数据，写入数据库中
        :param db_proxy_num:
        :return:
        '''
        successNum = 0
        failNum = 0
        while True:
            try:
                proxy = verified_queue.get(timeout=300)
                if proxy:
                    ProxySqliteDB.insert(proxy)
                    successNum += 1
                else:
                    failNum += 1
                str_ = 'IPProxyPool----->>>>>>>>Success ip num :%d,Fail ip num:%d' % (successNum, failNum)
                sys.stdout.write(str_ + "\r")
                sys.stdout.flush()
            except BaseException as e:
                if db_proxy_num.value != 0:
                    successNum += db_proxy_num.value
                    db_proxy_num.value = 0
                    str = 'IPProxyPool----->>>>>>>>Success ip num :%d,Fail ip num:%d' % (successNum, failNum)
                    sys.stdout.write(str + "\r")
                    sys.stdout.flush()
                    successNum = 0
                    failNum = 0