#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-5-10 下午5:00
@File    : in_hi_news_tags_statistics.py
@Desc    : 印地语新闻tag处理
"""

import json
from collections import OrderedDict

class TagProcess(object):

    def __init__(self, tag_file):
        self._tf = tag_file
        self.tag_dict = self.read_json_file(self._tf)
        # self.rewrite_tags(self.tag_dict, new_tag_file)

    def read_json_file(self, file):
        hi_f = open(file, 'r')
        lines_ = hi_f.read()
        lines = json.loads(lines_)
        hi_f.close()
        return lines

    def rewrite_tags(self, tag_dict, tag_file):
        """处理抓取的tag为多个tag join为一个字符串的情况"""
        new_tags = dict()
        for k, v in tag_dict.items():
            _k_list = [i.strip().replace("#", "") for i in k.split(",") if i != ""]
            if len(_k_list) == 1:
                new_tags[_k_list[0]] = v
            else:
                for k in _k_list:
                    if k in new_tags.keys():
                        new_tags[k] +=1
                    else:
                        new_tags[k] = 1
        with open(tag_file, "w") as f:
            f.writelines(json.dumps(dict_sort(new_tags), indent=4))


def dict_sort(result, limit_num=None):
    _result_sort = sorted(result.items(), key=lambda x: x[1], reverse=True)
    result_sort = OrderedDict()

    count_limit = 0
    domain_count = 0
    for i in _result_sort:
        result_sort[i[0]] = i[1]
        if limit_num:
            if i[1] > limit_num:
                domain_count += 1
                count_limit += i[1]
    return result_sort


tf = "/data/in_hi_news_parser_result/result_tag_all_stat"
ntf = "/data/in_hi_news_parser_result/result_tag_all_stat_final"

tag_dict = TagProcess(ntf).tag_dict
print(len(tag_dict.keys()))
s = 0
for k, v in tag_dict.items():
    if v > 1:
        s += 1
print(s)
