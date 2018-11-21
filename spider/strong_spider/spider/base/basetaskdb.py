#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/8/28 16:34
@File    : basetaskdb.py
@Desc    : 任务数据库基类
"""

class BaseTaskDB(object):
    ACTIVE = 1
    SUCCESS = 2
    FAILED = 3
    BAD = 4

    projects = set()  # projects in taskdb

    def load_tasks(self, status, project=None, fields=None):
        raise NotImplementedError

    def get_task(self, project, taskid, fields=None):
        raise NotImplementedError

    def status_count(self, project):
        '''
        return a dict
        '''
        raise NotImplementedError

    def insert(self, project, taskid, obj={}):
        raise NotImplementedError

    def update(self, project, taskid, obj={}, **kwargs):
        raise NotImplementedError

    def drop(self, project):
        raise NotImplementedError

    @staticmethod
    def status_to_string(status):
        return {
            1: 'ACTIVE',
            2: 'SUCCESS',
            3: 'FAILED',
            4: 'BAD',
        }.get(status, 'UNKNOWN')

    @staticmethod
    def status_to_int(status):
        return {
            'ACTIVE': 1,
            'SUCCESS': 2,
            'FAILED': 3,
            'BAD': 4,
        }.get(status, 4)

    def copy(self):
        raise NotImplementedError