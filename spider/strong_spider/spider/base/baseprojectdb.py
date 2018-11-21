#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/8/28 16:32
@File    : baseprojectdb.py
@Desc    : 项目数据库基类
"""

import re

class BaseProjectDB(object):
    status_str = [
        'TODO',
        'STOP',
        'CHECKING',
        'DEBUG',
        'RUNNING',
    ]

    def insert(self, name, obj={}):
        raise NotImplementedError

    def update(self, name, obj={}, **kwargs):
        raise NotImplementedError

    def get_all(self, fields=None):
        raise NotImplementedError

    def get(self, name, fields):
        raise NotImplementedError

    def drop(self, name):
        raise NotImplementedError

    def check_update(self, timestamp, fields=None):
        raise NotImplementedError

    def split_group(self, group, lower=True):
        if lower:
            return re.split("\W+", (group or '').lower())
        else:
            return re.split("\W+", group or '')

    def verify_project_name(self, name):
        if len(name) > 64:
            return False
        if re.search(r"[^\w]", name):
            return False
        return True

    def copy(self):
        '''
        database should be able to copy itself to create new connection
        it's implemented automatically by pyspider.database.connect_database
        if you are not create database connection via connect_database method,
        you should implement this
        '''
        raise NotImplementedError