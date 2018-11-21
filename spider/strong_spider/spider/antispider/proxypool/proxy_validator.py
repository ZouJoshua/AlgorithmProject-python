#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/5 16:25
@File    : proxy_validator.py
@Desc    : 代理可用性验证
"""

import sys

import chardet
from gevent import monkey
monkey.patch_all()

import json
import os
import gevent
import requests
import time
import psutil
from multiprocessing import Process, Queue

import setting
from spider.base.headers import get_http_header
from proxy_sqlitedb import ProxySqliteDB

class ValidatorScheduler(Validator):

    def __init__(self):
        Validator.__init__(self)

    def validator(self, proxy_queue, verified_queue, myip):
        tasklist = []
        proc_pool = {}  # 所有进程列表
        process_queue = Queue()  # 控制信息队列
        while True:
            if not process_queue.empty():
                # 处理已结束的进程
                try:
                    pid = process_queue.get()
                    proc = proc_pool.pop(pid)
                    proc_ps = psutil.Process(pid)
                    proc_ps.kill()
                    proc_ps.wait()
                except Exception as e:
                    pass
            try:
                if len(proc_pool) >= setting.MAX_CHECK_PROCESS:
                    time.sleep(setting.CHECK_WATI_TIME)
                    continue
                proxy = proxy_queue.get()
                tasklist.append(proxy)
                if len(tasklist) >= setting.MAX_CHECK_CONCURRENT_PER_PROCESS:
                    p = Process(target=self.start_validator, args=(tasklist, myip, verified_queue, process_queue))
                    p.start()
                    proc_pool[p.pid] = p
                    tasklist = []
            except Exception as e:
                if len(tasklist) > 0:
                    p = Process(target=self.start_validator, args=(tasklist, myip, verified_queue, process_queue))
                    p.start()
                    proc_pool[p.pid] = p
                    tasklist = []

    def start_validator(self, tasks, myip, verified_queue, process_queue):
        spawns = []
        for task in tasks:
            spawns.append(gevent.spawn(self.detect_proxy, myip, task, verified_queue))
        gevent.joinall(spawns)
        process_queue.put(os.getpid())  # 子进程退出是加入控制队列


class Validator(object):

    def __init__(self):
        pass

    def detect_from_db(self, selfip, proxy, proxies_set):
        proxy_dict = {'ip': proxy.get('ip'), 'port': proxy.get('port')}
        proxy_id = proxy.get('proxy_id')
        proxy_str = '%s:%s' % (proxy.get('ip'), proxy.get('port'))
        result = self.detect_proxy(selfip, proxy_dict)
        if result:
            _proxy_str = proxy_str
            proxies_set.add(_proxy_str)
        else:
            if proxy.get('scorce') < 1:
                ProxySqliteDB.drop(proxy_id)
            else:
                score = proxy.get('scorce') - 1
                ProxySqliteDB.update(proxy_id, {'score': score})
                _proxy_str = proxy_str
                proxies_set.add(_proxy_str)

    def detect_proxy(self, selfip, proxy, verified_queue=None):
        """
        :param selfip: myip
        :param proxy:
        :param verified_queue: Verified proxy queue
        :return:
        """
        ip = proxy['ip']
        port = proxy['port']
        proxies = {"http": "http://%s:%s" % (ip, port), "https": "http://%s:%s" % (ip, port)}
        protocol, types, speed = getattr(sys.modules[__name__], setting.CHECK_PROXY['function'])(selfip, proxies)
        # protocol, types, speed = self.checkProxy(selfip, proxies)
        if protocol >= 0:
            proxy['protocol'] = protocol
            proxy['types'] = types
            proxy['speed'] = speed
        else:
            proxy = None
        if verified_queue:
            verified_queue.put(proxy)
        return proxy

    def check_proxy(self, selfip, proxies):
        """
        :param selfip:
        :param proxies:
        :return:
        """
        protocol = -1
        types = -1
        speed = -1
        http, http_types, http_speed = self._checkHttpProxy(selfip, proxies)
        https, https_types, https_speed = self._checkHttpProxy(selfip, proxies, False)
        if http and https:
            protocol = 2
            types = http_types
            speed = http_speed
        elif http:
            types = http_types
            protocol = 0
            speed = http_speed
        elif https:
            types = https_types
            protocol = 1
            speed = https_speed
        else:
            types = -1
            protocol = -1
            speed = -1
        return protocol, types, speed

    def _checkHttpProxy(self, selfip, proxies, isHttp=True):
        types = -1
        speed = -1
        if isHttp:
            test_url = setting.TEST_HTTP_HEADER
        else:
            test_url = setting.TEST_HTTPS_HEADER
        try:
            start = time.time()
            r = requests.get(url=test_url, headers=get_http_header(), timeout=setting.TIMEOUT, proxies=proxies)
            if r.ok:
                speed = round(time.time() - start, 2)
                content = json.loads(r.text)
                headers = content['headers']
                ip = content['origin']
                proxy_connection = headers.get('Proxy-Connection', None)
                if ',' in ip:
                    types = 2
                elif proxy_connection:
                    types = 1
                else:
                    types = 0

                return True, types, speed
            else:
                return False, types, speed
        except Exception as e:
            return False, types, speed

    def baidu_check(self, selfip, proxies):
        """
        :param selfip:
        :param proxies:
        :return:
        """
        protocol = -1
        types = -1
        speed = -1
        try:
            start = time.time()
            r = requests.get(url='https://www.baidu.com', headers=get_http_header(), timeout=setting.TIMEOUT, proxies=proxies)
            r.encoding = chardet.detect(r.content)['encoding']
            if r.ok:
                speed = round(time.time() - start, 2)
                protocol = 0
                types = 0
            else:
                speed = -1
                protocol = -1
                types = -1
        except Exception as e:
            speed = -1
            protocol = -1
            types = -1
        return protocol, types, speed

    def chinaz_check(self, selfip, proxies):
        protocol = -1
        types = -1
        speed = -1
        try:
            # http://ip.chinaz.com/getip.aspx挺稳定，可以用来检测ip
            r = requests.get(url=setting.TEST_URL, headers=get_http_header(), timeout=setting.TIMEOUT,
                             proxies=proxies)
            r.encoding = chardet.detect(r.content)['encoding']
            if r.ok:
                if r.text.find(selfip) > 0:
                    return protocol, types, speed
            else:
                return protocol, types, speed
        except Exception as e:
            return protocol, types, speed

    @staticmethod
    def get_myip():
        try:
            r = requests.get(url=setting.TEST_IP, headers=get_http_header(), timeout=setting.TIMEOUT)
            ip = json.loads(r.text)
            return ip['origin']
        except Exception as e:
            raise Test_URL_Fail

class Test_URL_Fail(Exception):

    def __str__(self):
        str = "访问%s失败，请检查网络连接" % setting.TEST_IP
        return str

if __name__ == '__main__':
    ip = '222.186.161.132'
    port = 3128
    proxies = {"http": "http://%s:%s" % (ip, port), "https": "http://%s:%s" % (ip, port)}
    Validator._checkHttpProxy(None,proxies)
