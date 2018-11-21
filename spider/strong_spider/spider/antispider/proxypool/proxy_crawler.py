#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/5 15:51
@File    : proxy_crawler.py
@Desc    : 代理下载调度
"""

from gevent import monkey
monkey.patch_all()

import sys
import time
import gevent

from gevent.pool import Pool
from multiprocessing import Queue, Process, Value

import setting
from spider.tools.utils import md5

from proxy_htmldownloader import HtmlDownloader
from proxy_htmlparser import HtmlParser
from proxy_validator import Validator
from proxy_sqlitedb import ProxySqliteDB
from proxy_pipeline import SqlitePipeline


def start_proxycrawl(proxy_queue, db_proxy_num, myip):
    crawl = ProxyCrawl(proxy_queue, db_proxy_num, myip)
    crawl.run()


class ProxyCrawl(object):
    proxies = set()

    def __init__(self, proxy_queue, db_proxy_num, myip):
        self.crawl_pool = Pool(setting.THREADNUM)
        self.queue = proxy_queue
        self.db_proxy_num = db_proxy_num
        self.myip = myip

    def run(self):
        while True:
            self.proxies.clear()
            str_ = 'Starting crawl proxy!'
            sys.stdout.write(str_ + "\r\n")
            sys.stdout.flush()
            proxylist = ProxySqliteDB.get_all()

            spawns = []
            for proxy in proxylist:
                spawns.append(gevent.spawn(Validator.detect_from_db, self.myip, proxy, self.proxies))
                if len(spawns) >= setting.MAX_CHECK_CONCURRENT_PER_PROCESS:
                    gevent.joinall(spawns)
                    spawns= []
            gevent.joinall(spawns)
            self.db_proxy_num.value = len(self.proxies)
            str_ = 'IPProxyPool----->>>>>>>>db exists ip:%d' % len(self.proxies)

            if len(self.proxies) < setting.MINNUM:
                str_ += '\r\nIPProxyPool----->>>>>>>>now ip num < MINNUM, start crawling...'
                sys.stdout.write(str_ + "\r\n")
                sys.stdout.flush()
                spawns = []
                for p in setting.parserList:
                    spawns.append(gevent.spawn(self.crawl, p))
                    if len(spawns) >= setting.MAX_DOWNLOAD_CONCURRENT:
                        gevent.joinall(spawns)
                        spawns= []
                gevent.joinall(spawns)
            else:
                str_ += '\r\nIPProxyPool----->>>>>>>>now ip num meet the requirement,wait UPDATE_TIME...'
                sys.stdout.write(str_ + "\r\n")
                sys.stdout.flush()

            time.sleep(setting.UPDATE_TIME)

    def crawl(self, parser):
        html_parser = HtmlParser()
        for url in parser['urls']:
            response = HtmlDownloader.download(url)
            if response is not None:
                proxylist = html_parser.parse(response, parser)
                if proxylist is not None:
                    for proxy in proxylist:
                        proxy_str = '%s:%s' % (proxy['ip'], proxy['port'])
                        proxy['proxy_id'] = md5(proxy_str)
                        if proxy_str not in self.proxies:
                            self.proxies.add(proxy_str)
                            while True:
                                if self.queue.full():
                                    time.sleep(0.1)
                                else:
                                    self.queue.put(proxy)
                                    break

if __name__ == "__main__":
    DB_PROXY_NUM = Value('i', 0)
    q1 = Queue()
    q2 = Queue()
    p0 = Process(target=start_api_server)
    p1 = Process(target=start_proxycrawl, args=(q1, DB_PROXY_NUM))
    p2 = Process(target=Validator.validator, args=(q1, q2))
    p3 = Process(target=SqlitePipeline.save_data, args=(q2, DB_PROXY_NUM))

    p0.start()
    p1.start()
    p2.start()
    p3.start()