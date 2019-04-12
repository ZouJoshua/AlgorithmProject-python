#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-4-12 下午12:03
@File    : test_xpath_rule.py
@Desc    : 
"""

import requests
from lxml.html import etree
import json
import sys


header = {"User-Agent": "Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50"}

file = './data/hi_rules.json'
test_url_file = './data/in_hi_url.json'

with open(file, 'r') as f:
    xpath_rules = json.load(f)

with open(test_url_file, 'r') as f:
    test_url = json.load(f)


test_xpath_result_file = open("test_xpath_result.json", 'w')
out = dict()
for k, url_list in test_url.items():
    domain = 'www.jansatta.com'
    if k == domain:
        for _url in url_list:
            result = {"category": [], "title": [], "tag": [], "hyperlink_text": [], "hyperlink_url": []}
            xpath_keys = ["category", "title", "tag", "hyperlink_text", "hyperlink_url"]
            url = _url['url']
            result['url'] = url
            print("正在处理>>>{}".format(url))
            response = requests.get(url, headers=header)
            pt = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))
            for i in xpath_keys:
                xpath_str = xpath_rules[domain][i]
                if xpath_str != 'none':
                    _out = pt.xpath(xpath_str)
                    result[i] = [i.strip().strip("\n\t") for i in _out if i.strip().strip("\n\t")]
            out[_url['id']] = result
        test_xpath_result_file.write(json.dumps(out, indent=4))
        # sys.stdout.flush()
        # test_xpath_result_file.flush()

test_xpath_result_file.close()
