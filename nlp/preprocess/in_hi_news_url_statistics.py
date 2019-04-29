#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-4-11 下午3:48
@File    : url_statistics.py
@Desc    : url 域名统计
"""


from urllib.parse import urlparse
import json
from collections import OrderedDict


file = '/data/in_hi_html.json'


def count_url_domain():

    result = dict()
    all = 0
    with open(file, 'r') as f:
        try:
            while True:
                all += 1
                line = json.loads(f.readline())
                if line:
                    url = line['url']
                    domain = urlparse(url).netloc
                    if domain in result.keys():
                        result[domain] += 1
                    else:
                        result[domain] = 1
                else:
                    pass
        except Exception as e:
            print(e)
            print(">>>>>>>>>>所有数据{}个".format(all))

    _result_sort = sorted(result.items(), key=lambda x: x[1], reverse=True)
    result_sort = OrderedDict()

    count_limit = 0
    domain_count = 0
    for i in _result_sort:
        result_sort[i[0]] = i[1]
        if i[1] > 10000:
            domain_count += 1
            count_limit += i[1]

    print(">>>>>>>>>>大于10000的域名有{}个".format(domain_count))
    print(">>>>>>>>>>域名大于10000的网址总共{}个".format(count_limit))
    print(">>>>>>>>>>域名大于10000的网址占比{:0.2f}".format(count_limit/all))

    with open('count_result', 'w') as _of:
        _of.writelines(json.dumps(result_sort, indent=4))


def get_url_xpath_file(file):
    result = dict()
    xpath_rule = {"category": "none","title": "none","tag": "none","hyperlink_text": "none","hyperlink_url": "none"}
    with open(file, 'r') as f:
        line = json.load(f)
        for k,v in line.items():
            if v > 5476:
                result[k] = xpath_rule
            else:
                pass
    with open('hi_rules.json', 'w') as _of:
        _of.writelines(json.dumps(result, indent=4))


def get_url_demo(domain_file,html_file):
    _count = dict()
    result = dict()
    domain_list = list()
    with open(domain_file, 'r') as _if:
        for i in json.load(_if).keys():
            domain_list.append(i)


    with open(html_file, 'r') as f:
        try:
            while True:
                line = json.loads(f.readline())
                if line:
                    url = line['url']
                    _domain = urlparse(url).netloc
                    if _domain in domain_list:
                        if _domain in _count.keys():
                            if _count[_domain] > 50:
                                pass
                            else:
                                _count[_domain] += 1
                                result[_domain].append(line)
                        else:
                            _count[_domain] = 1
                            result[_domain] = list()
                else:
                    pass
        except Exception as e:
            print(e)

    with open("in_hi_url.json", 'w') as _of:
        _of.writelines(json.dumps(result, indent=4))


if __name__ == '__main__':
    file = '/home/zoushuai/algoproject/algo-python/nlp/preprocess/count_result'
    # get_url_xpath_file(file)
    domain_file = '/home/zoushuai/algoproject/algo-python/nlp/preprocess/hi_rules.json'
    url_file = '/data/in_hi_html.json'
    get_url_demo(domain_file, url_file)
