#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/5 15:02
@File    : proxy_htmldownloader.py
@Desc    : download proxy html
"""

import random
import setting
from proxy_sqlitedb import ProxySqliteDB
from spider.base.headers import get_http_header

import requests
import chardet


class HtmlDownloader(object):

    @staticmethod
    def download(url):
        try:
            r = requests.get(url=url, headers=get_http_header(), timeout=setting.TIMEOUT)
            r.encoding = chardet.detect(r.content)['encoding']
            if (not r.ok) or len(r.content) < 500:
                raise requests.ConnectionError
            else:
                return r.text

        except Exception:
            count = 0  # 重试次数
            proxylist = ProxySqliteDB.get_all(limit=20)
            if not proxylist:
                return None

            while count < setting.RETRY_TIME:
                try:
                    proxy = random.choice(proxylist)
                    ip = proxy[0]
                    port = proxy[1]
                    proxies = {"http": "http://%s:%s" % (ip, port), "https": "http://%s:%s" % (ip, port)}

                    r = requests.get(url=url, headers=get_http_header(), timeout=setting.TIMEOUT, proxies=proxies)
                    r.encoding = chardet.detect(r.content)['encoding']
                    if (not r.ok) or len(r.content) < 500:
                        raise requests.ConnectionError
                    else:
                        return r.text
                except Exception:
                    count += 1

        return None