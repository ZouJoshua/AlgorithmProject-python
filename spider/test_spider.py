#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/11/20 11:36
@File    : test_spider.py
@Desc    : 
"""

import requests

url = "https://www.cricbuzz.com/cricket-news/105227/windies-cricket-appoint-nic-pothas-interim-head-coach-south-africa"
html = requests.get(url)
with open("test.txt", "w") as f:
    f.write(html.text.encode("gbk", "ignore").decode("utf-8"))
