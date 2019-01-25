#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/1/24 18:41
@File    : pre_predict_subcategory.py
@Desc    : 
"""

import os
import json
from urllib.parse import urlparse


def pre_predict_subcategory(dataFile, classedFile, unclassedFile, words_list, topcategory):
    """
    预先给出文章的二级分类模型
    :param dataFile: 一级分类文件
    :param classedFile: 预测出二级分类的文件
    :param unclassedFile: 未预测出二级分类的文件
    :param words_list: 类别关键词
    :param topcategory: 一级分类名
    :return:
    """
    cnt_map = dict()
    f = open(dataFile, 'r', encoding='utf-8')
    outf1 = open(classedFile, 'a', encoding='utf-8')
    outf2 = open(unclassedFile, 'a', encoding='utf-8')
    try:
        while True:
            line = f.readline().strip('\n')
            line_json = json.loads(line)
            url = line_json["url"]
            title = line_json["title"].lower()
            top_category = line_json["predict_top_category"]
            # website = urlparse(url).netloc
            if top_category == topcategory:
                flag = 0
                line_json["top_category"] = topcategory
                tmp = list(words_list.values())[0]
                for w in title.split(" "):
                    if w.isalpha():
                        for k, v in tmp.items():
                            if w in v:
                                flag = 1
                                line_json["sub_category"] = k
                                if k in cnt_map:
                                    cnt_map[k] += 1
                                else:
                                    cnt_map[k] = 1
                                outf1.write(json.dumps(line_json) + "\n")
                                outf1.flush()
                            continue
                        continue
                if flag == 0:
                    line_json["sub_category"] = topcategory
                    outf2.write(json.dumps(line_json) + "\n")
                    outf2.flush()
                continue
    except Exception as e:
        print(e)
    finally:
        f.close()
        outf1.close()
        outf2.close()
    return cnt_map


