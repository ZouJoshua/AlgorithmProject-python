#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author   : Joshua_Zou
@Contact  : joshua_zou@163.com
@Time     : 2018/8/7 23:06
@Software : PyCharm
@File     : WcSender.py
@Desc     : webpage 结果处理
"""

import os
import sys
dirname = os.path.split(os.path.realpath(__file__))[0] + '/'
import time
import json
import log

log = log.spiderLog()
reload(sys)
sys.setdefaultencoding("utf-8")

# send to local
class WcSender(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.save_path = '/home/zoushuai/wdj_spider/data/w1/'
        # self.save_path = r'D:\Work2018\pythonwork\Python2\spider_test\app_spider\data\webpage_classification\classification'
        # self.save_path = r'C:\Users\ZS\Desktop\webpage_classification'
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        self.last_hour_stamp = 0
        self.save_fobj = None

    def _send(self, task):
        try:
            #print task
            if task:
                content = {}
                content['url'] = task['url']
                content['category'] = task['doc_info'].get('category', '')
                content['tags'] = task['doc_info'].get('tags', '')
                content['version'] = task['doc_info'].get('version', '')
                content['developer'] = task['doc_info'].get('developer', '')
                content['status_code'] = task['status_code']
                content['proxy_code'] = task['proxy_code']

                msg = json.dumps(content, ensure_ascii=False)
                self.save_local_file(msg)
                log.info("Sucess write (%s)" % msg)
        except Exception as e:
            log.error('Failed to send up task, error(%s)' % str(e))
        finally:
            pass

    def save_local_file(self, msg):
        unit = 3600
        cur_time = int(time.time())
        hour_stamp = cur_time - (cur_time % unit)

        if hour_stamp > self.last_hour_stamp:
            if self.save_fobj is not None:
                self.save_fobj.close()

            timeArray = time.localtime(hour_stamp)
            otherStyleTime = time.strftime("%Y-%m-%d_%H", timeArray)
            save_file = self.save_path + str(os.getpid()) + '_' + otherStyleTime
            self.save_fobj = open(save_file, 'a+')

            self.last_hour_stamp = hour_stamp

        self.save_fobj.write(msg+'\n')

    def get_name(self):
        return self.__class__.__name__
