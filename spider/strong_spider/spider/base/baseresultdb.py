#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/8/28 16:33
@File    : baseresultdb.py
@Desc    : 结果数据库基类
"""


class BaseResultDB(object):

    projects = set()  # projects in resultdb

    def save(self, project, taskid, url, result):
        raise NotImplementedError

    def select(self, project, fields=None, offset=0, limit=None):
        raise NotImplementedError

    def count(self, project):
        raise NotImplementedError

    def get(self, project, taskid, fields=None):
        raise NotImplementedError

    def drop(self, project):
        raise NotImplementedError

    def copy(self):
        '''
        database should be able to copy itself to create new connection
        it's implemented automatically by pyspider.database.connect_database
        if you are not create database connection via connect_database method,
        you should implement this
        '''
        raise NotImplementedError