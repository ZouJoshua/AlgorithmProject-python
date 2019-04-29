#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-4-29 下午3:24
@File    : in_hi_news_category_statistics.py
@Desc    : 印地语新闻抓取结果统计分类、tag信息
"""

import os
import json
import re

data_base_dir = r'/data/in_hi_news_parser_result'


def write_file(file, res_file, nores_file):
    f = open(file, 'r')
    res_f = open(res_file, 'a')
    nores_f = open(nores_file, 'a')
    none_result = {"category": [], "title": [], "tag": [], "hyperlink_text": [], "hyperlink_url": []}
    none_result_str ={"category": [], "title": "", "tag": [], "hyperlink_text": [], "hyperlink_url": []}
    s = 0
    for _line in f:
        line = json.loads(_line.strip())
        if 'result' in line.keys():
            if type(line['result']) == dict:
                if line['result'] == none_result:
                    line['result'] = none_result_str
                    nores_f.write(json.dumps(line) + "\n")
                else:
                    # print(type(line['result']['title']))
                    if len(line['result']['title']):
                        line['result']['title'] = line['result']['title'][0]
                    else:
                        line['result']['title'] = ""
                    res_f.write(json.dumps(line) + "\n")
            elif type(line['result']) == str:
                out = str2dict(line['result'])
                line['result'] = out
                if out == none_result_str:
                    nores_f.write(json.dumps(line) + "\n")
                else:
                    res_f.write(json.dumps(line) + "\n")
        else:
            s += 1
    print("{}条没有result字段".format(s))
    f.close()
    res_f.close()
    nores_f.close()


def str2dict(s):
    result = re.findall(r"'category': (.*?), 'title': (.*?), 'tag': (.*?), 'hyperlink_text': (.*?), 'hyperlink_url': (.*?)}", s)
    out = dict()
    if result:
        if len(result[0]) == 5:
            if result[0][0] != '[]':
                cat_str = result[0][0].replace("['", "").replace("']", "")
                clean_cat = [i.strip() for i in cat_str.split("', '")]
            else:
                clean_cat = list()
            if result[0][1] != '[]':
                tit_str = result[0][1].replace("['", "").replace("']", "")
            else:
                tit_str = ''
            if result[0][2] != '[]':
                tag_str = result[0][2].replace("['", "").replace("']", "")
                clean_tag = [i.strip() for i in tag_str.split("', '")]
            else:
                clean_tag = list()
            if result[0][3] != '[]':
                hre_str = result[0][3].replace("['", "").replace("']", "")
                clean_hre = [i.strip() for i in hre_str.split("', '")]
            else:
                clean_hre = list()
            if result[0][4] != '[]':
                ref_str = result[0][4].replace("['", "").replace("']", "")
                clean_ref = [i.strip() for i in ref_str.split("', '")]
            else:
                clean_ref = list()

            out["category"] = clean_cat
            out["title"] = tit_str
            out["tag"] = clean_tag
            out["hyperlink_text"] = clean_hre
            out["hyperlink_url"] = clean_ref
        else:
            out = {"category": [], "title": "", "tag": [], "hyperlink_text": [], "hyperlink_url": []}
    else:
        print(s)
    return out




def main():
    for i in range(17, 23):
        data_file = os.path.join(data_base_dir, 'parsered_hi_news_201904{}'.format(i))
        result_file = os.path.join(data_base_dir, 'in_hi_news_category_all')
        noresult_file = os.path.join(data_base_dir, 'in_hi_news_no_category_all')
        if os.path.exists(data_file):
            write_file(data_file, result_file, noresult_file)


if __name__ == '__main__':
    main()