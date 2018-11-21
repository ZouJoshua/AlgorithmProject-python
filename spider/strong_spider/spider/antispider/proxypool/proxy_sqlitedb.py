#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/4 11:28
@File    : proxy_sqlitedb.py
@Desc    : 代理池 sqlite 数据库
"""

import time
from spider.base.basedb import BaseDB
from spider.database.sqlite.sqlitebase import SQLiteMixin
from spider.base.baseproxydb import BaseProxyDB


class ProxySqliteDB(SQLiteMixin, BaseProxyDB, BaseDB):
    __tablename__ = 'proxydb'
    placeholder = '?'

    def __init__(self, path):
        self.path = path
        self.last_pid = 0
        self.conn = None
        self._execute('''CREATE TABLE IF NOT EXISTS `%s` (
                            proxy_id PRIMARY KEY, 
                            ip, port, types, 
                            protocol, country, 
                            area, score, updatetime)''' % self.__tablename__)

    def insert(self, tablename, obj={}):
        obj = dict(obj)
        obj['updatetime'] = time.time()
        return self._insert(**obj)

    def update(self, proxy_id, obj={}, **kwargs):
        obj = dict(obj)
        obj.update(kwargs)
        obj['updatetime'] = time.time()
        ret = self._update(where="`proxy_id` = %s" % self.placeholder, where_values=(proxy_id,), **obj)
        return ret.rowcount

    def get_all(self, fields=None):
        return self._select2dic(what=fields)

    def get(self, proxy_id, fields=None):
        where = "`proxy_id` = %s" % self.placeholder
        for each in self._select2dic(what=fields, where=where, where_values=(proxy_id,)):
            return each
        return None

    def check_update(self, timestamp, fields=None):
        where = "`updatetime` >= %f" % timestamp
        return self._select2dic(what=fields, where=where)

    def drop(self, proxy_id):
        where = "`proxy_id` = %s" % self.placeholder
        return self._delete(where=where, where_values=(proxy_id,))

    def get_proxy_by_sort(self, num, fields=None):
        '''
        返回默认按存活时间排序的代理
        '''
        pass

    def close(self):
        return self.conn.close()
