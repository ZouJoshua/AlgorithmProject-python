#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/4 12:26
@File    : baseproxydb.py
@Desc    : proxy 抽象基类
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class BaseProxyDB(object):

    def init_db(self):
        raise NotImplemented

    def drop_db(self):
        raise NotImplemented

    def insert(self, tablename, value=None):
        raise NotImplemented

    def update(self, name, obj={}, **kwargs):
        raise NotImplemented

    def delete(self, fields=None):
        raise NotImplemented

    def select(self, count=None, fields=None):
        raise NotImplemented

    def exists(self, key, **kwargs):
        raise NotImplemented

    def get_all(self):
        raise NotImplemented