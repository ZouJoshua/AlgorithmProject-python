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
from collections import OrderedDict
import requests

# 谷歌翻译api
from googletrans import Translator



data_base_dir = r'/data/in_hi_news_parser_result'

class CleanResult(object):

    def __init__(self, data_base_dir):
        self._dir = data_base_dir
        self.get_result()

    def get_result(self):
        for i in range(17, 23):
            data_file = os.path.join(self._dir, 'parsered_hi_news_201904{}'.format(i))
            print(">>>>> 正在处理文件:{}".format(data_file))
            nonempty_result_file = os.path.join(self._dir, 'nonempty_category_all')
            empty_result_file = os.path.join(self._dir, 'empty_category_all')
            if os.path.exists(data_file):
                self.write_file(data_file, nonempty_result_file, empty_result_file)

    def write_file(self, file, res_file, nores_file):
        f = open(file, 'r')
        res_f = open(res_file, 'a')
        nores_f = open(nores_file, 'a')
        none_result = {"category": [], "title": [], "tag": [], "hyperlink_text": [], "hyperlink_url": []}
        none_result_str = {"category": [], "title": "", "tag": [], "hyperlink_text": [], "hyperlink_url": []}
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
                    out = self.str2dict(line['result'])
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


    def str2dict(self, s):
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



def get_category_and_tag(file, category_file, tag_file):
    result_f = open(file, 'r')
    category_f = open(category_file, 'w')
    tag_f = open(tag_file, 'w')
    category_result_f = open("{}_stat".format(category_file), 'w', encoding='utf-8')
    tag_result_f = open("{}_stat".format(tag_file), 'w', encoding='utf-8')
    category_dict = dict()
    tag_dict = dict()
    for _line in result_f:
        line = json.loads(_line.strip())
        if 'category' in line['result'].keys():
            if line['result']['category'] != []:
                category_f.write(_line)
                for c in line['result']['category']:
                    if c in category_dict.keys():
                        category_dict[c] += 1
                    else:
                        category_dict[c] = 1
        else:
            print(line)
        if 'tag' in line['result'].keys():
            if line['result']['tag'] != []:
                tag_f.write(_line)
                for t in line['result']['category']:
                    if t in tag_dict.keys():
                        tag_dict[t] += 1
                    else:
                        tag_dict[t] = 1
        else:
            print(line)

    c_sort_dict = dict_sort(category_dict)
    t_sort_dict = dict_sort(tag_dict)
    category_result_f.writelines(json.dumps(c_sort_dict, indent=4))
    tag_result_f.writelines(json.dumps(t_sort_dict, indent=4))
    category_f.close()
    tag_f.close()
    category_result_f.close()
    tag_result_f.close()


def translate_hi_to_en(te):
    # header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20130405 Firefox/22.0"}
    # url = "https://translate.google.cn/#view=home&op=translate&sl=auto&tl=en&text={}".format(text)
    # r = requests.get(url, headers=header)
    # print(r.text)
    proxy = {'http': '119.101.112.106:9999'}
    translator = Translator(service_urls=['translate.google.com'],proxies=proxy)
    # lang = translator.detect(text).lang
    result = translator.translate(te, dest='en').text
    return result


def get_translation_of_category(file, outfile):
    hi_f = open(file, 'r')
    hi_en_f = open(outfile, 'w')
    lines_ = hi_f.read()
    hi_f.close()
    lines = json.loads(lines_)
    en_dict = dict()
    with open("/home/zoushuai/algoproject/algo-python/nlp/preprocess/in_hi_data/category.txt", 'w') as f:
        for i, k in enumerate(lines.keys()):
            print(k)
            if i < 2300:
                # line_en = dict()
                k_clean = k.replace(">", "").replace("<", "").strip()
                print(k_clean)
                f.write(k_clean + "\n")
            # _k = translate_hi_to_en(k_clean).title()
            # en_dict[k] = _k
            # out = "{} -> {}".format(k, _k)
            # print(out)
            # hi_en_f.write(out + "\n")
    hi_en_f.close()

def rewrite_translation(file, hi_en_file):
    hi_f = open(file, 'r')
    hi_en_f = open(hi_en_file, 'w')
    lines_ = hi_f.read()
    lines = json.loads(lines_)
    hi = list()
    for i, k in enumerate(lines.keys()):
        if i < 2300:
            hi.append(k.strip())
    with open("/home/zoushuai/algoproject/algo-python/nlp/preprocess/in_hi_data/category_en.txt", 'r') as f:
        c_lines = f.readlines()
    en = list()
    for i, line in enumerate(c_lines):
        en.append(line.strip())
    hi_en = dict(zip(hi, en))
    hi_en_f.writelines(json.dumps(hi_en, indent=4))


def get_stadnard_category(category_file, stand_file, out_file):
    with open(stand_file, 'r') as sf:
        # lines = sf.readline()
        dict_line = json.load(sf)
    print(dict_line.keys())
    out_file = open(out_file, 'w')
    with open(category_file, 'r') as cf:
        _lines = cf.readlines()
    for _li in _lines:
        li = json.loads(_li.strip())
        if 'category' in li['result'].keys():
            cates = li['result']['category']
            true_cate = list()
            # print(cates[:3])
            for c in cates[:4]:
                if c in dict_line.keys():
                    c_out = dict_line[c]['top']
                else:
                    c_out = ""
                true_cate.append(c_out)
            s = set(true_cate)
            if "" in s:
                s.remove("")
            if len(s):
                if len(s) == 1:
                    _s = s.pop()
                    li['top_category'] = _s
                    out_file.write(json.dumps(li) + "\n")
                else:
                    print(",".join(s))
                    # li['top_category'] = "||".join(s)



def main():
    file = os.path.join(data_base_dir, 'in_hi_news_nonempty_all')
    c_file = os.path.join(data_base_dir, 'in_hi_news_category_all')
    c_s_file = os.path.join(data_base_dir, 'in_hi_news_category_all_stat')
    c_en_file = os.path.join(data_base_dir, 'in_hi_news_category_en_all')
    t_file = os.path.join(data_base_dir, 'in_hi_news_tag_all')
    # c_stand_file = os.path.join(data_base_dir, 'category_standard.txt')
    c_stand_file = "/home/zoushuai/algoproject/algo-python/nlp/preprocess/in_hi_data/category_standard.txt"
    # c_out_file = os.path.join(data_base_dir, 'in_hi_news_standard_category')
    c_out_file = "/home/zoushuai/algoproject/algo-python/nlp/preprocess/in_hi_data/in_hi_news_standard_category"
    # get_category_result(file, c_file, t_file)
    # get_translation_of_category(c_s_file, c_en_file)
    # rewrite_translation(c_s_file, c_en_file)

    get_stadnard_category(c_file, c_stand_file, c_out_file)



if __name__ == '__main__':
    main()