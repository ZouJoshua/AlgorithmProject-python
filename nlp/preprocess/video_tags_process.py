#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-7-3 下午5:44
@File    : video_tags_process.py
@Desc    : 视频tag处理
"""


import json
import os
from collections import OrderedDict
import string
import re


def read_json_format_file(file):
    print(">>>>> 正在读原始取数据文件：【{}】".format(file))
    with open(file, 'r') as f:
        while True:
            _line = f.readline()
            if not _line:
                break
            else:
                line = json.loads(_line.strip())
                yield line



def split_data_by_country(data_dir):
    """
    按国家分割tag数据
    :param data_dir: 文件目录
    :return:
    """
    tag_country = dict()
    ori_file = os.path.join(data_dir, 'video_tags')
    for line in read_json_format_file(ori_file):
        country = line["country"]
        if country in tag_country.keys():
            tag_country[country].append(line)
        else:
            tag_country[country] = list()
            tag_country[country].append(line)

    for c, value in tag_country.items():
        country_tag_file = os.path.join(data_dir, "{}_video_tags".format(c))
        with open(country_tag_file, 'w') as f:
            for li in value:
                f.write(json.dumps(li) + "\n")
        print("<<<<< 国家{}的tag已写入文件【{}】".format(c, country_tag_file))


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


def es_tags_process(file, tag_file):
    print(">>>>> 正在处理西班牙tag")
    tag_list = list()
    for line in read_json_format_file(file):
        vtag_str = line["vtaglist"]
        if vtag_str:
            tags = vtag_str.split(",")
            tag_list += tags
    # tag_dict = dict()
    # for tag in tag_list:
    #     tag = tag.lower()
    #     if tag in tag_dict.keys():
    #         tag_dict[tag] += 1
    #     else:
    #         tag_dict[tag] = 1
    tag_dict = standard_tag(tag_list)
    # print(">>>>> tag信息\n{}".format(json.dumps(tag_dict, indent=4)))
    tag_tmp = list()
    for k in tag_dict.keys():
        tag_tmp.append(k)
    tag_set = set(tag_tmp)
    print(">>>>> tag总共{}".format(len(tag_set)))

    with open(tag_file, "w") as f:
        f.writelines(json.dumps(dict_sort(tag_dict), ensure_ascii=False, indent=4))
    print("<<<<< tag list 已写入文件【{}】".format(tag_file))

    tag_split_all = dict()
    for k in tag_dict.keys():
        _k = k.split(" ")
        for _kk in _k:
            if _kk != "":
                if _kk in tag_split_all.keys():
                    tag_split_all[_kk] += 1
                else:
                    tag_split_all[_kk] = 1

    with open(tag_file+"_tokens", "w") as f:
        f.writelines(json.dumps(dict_sort(tag_split_all), ensure_ascii=False, indent=4))
    print("<<<<< tag list 已写入文件【{}】".format(tag_file+"_tokens"))


def standard_tag(tag_list):
    print(">>>>> 正在标准化tag")
    tag_dict = dict()
    for tag in tag_list:
        tag = tag.lower()
        tag = clean_url(tag)
        if tag.find("=") < 0:
            _tag = tag.replace("#0", "")
            del_symbol = string.punctuation  # ASCII 标点符号
            remove_punctuation_map = dict((ord(char), " ") for char in del_symbol)
            _tag = _tag.translate(remove_punctuation_map)  # 去掉ASCII 标点符号
            _tag = re.sub(r"\s+", " ", _tag)
            _tag = _tag.strip()
        else:
            continue
        if _tag.strip():
            if _tag in tag_dict.keys():
                tag_dict[_tag] += 1
            else:
                tag_dict[_tag] = 1
    return tag_dict




def clean_url(text):
    # 去除网址
    pattern = re.compile(r'(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
    # pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-zA-Z][0-9a-zA-Z]))+')
    url_list = re.findall(pattern, text)
    for url in url_list:
        text = text.replace(url, " ")
    return text.replace("( )", " ")





def get_tag_dict(file, type_file):
    with open(file, "r") as f:
        tags_dict = json.load(f)
    one_gram_dict = dict()
    for k, v in tags_dict.items():
        _k = k.split(" ")
        if len(_k) == 1:
            if k not in one_gram_dict.keys():
                one_gram_dict[k] = dict()
                if v > 5:
                    one_gram_dict[k][k] = v
            else:
                continue
        else:
            for kk in _k:
                if kk in one_gram_dict.keys():
                    one_gram_dict[kk][k] = v
                else:
                    continue
    one_gram_dict_tmp = dict()
    for k, v in one_gram_dict.items():
        if one_gram_dict[k]:
            one_gram_dict_tmp[k] = v
        else:
            pass

    with open(type_file, "w") as f:
        f.writelines(json.dumps(one_gram_dict_tmp, ensure_ascii=False, indent=4))
    print(">>>>> 分类tag已写入【{}】文件".format(type_file))

def clean_period(input_str):
    pattern_period = r'[1-2]\d{3}[s]{0,1}$|^\d{1,2}/\d{1,2}/^\d{2,4}$|\d{2,4}[-/]\d{2,4}$'
    res_period = re.compile(pattern_period, flags=0)
    mat = res_period.search(input_str)
    if mat:
        year_tag = mat.group(0)
    else:
        year_tag = ""
    return year_tag


def trim_tag(tag):
    pattern_period = r"[1-2]\d{3}[s]{0,1}$"
    res_period = re.compile(pattern_period, flags=0)
    mat = res_period.search(tag)
    if mat:
        year_tag = mat.group(0)
        new_tag = res_period.sub(" {}".format(year_tag), tag)
    else:
        new_tag = tag
    return new_tag





"""
tag 处理逻辑
1.是否存在vtaglist
2.处理vtaglist
    step1 -> 大小写，清洗tag，去除包含标点符号的tag
    step2 -> 日期 08/08/18、08/08/2018、1980s、1946、2014-2015、10/15、10-15、3-6-19
    step3 -> 
    step4 -> 
    step5 -> 
    step6 -> 
    step7 -> 
    step8 -> 
    step9 -> 
    step10 -> 



3.抽取title和text中的tag
4.返回处理的tag list

"""




if __name__ == "__main__":
    data_dir = "/data/video_tags"
    # split_data_by_country(data_dir)
    es_tag_file = "/data/video_tags/ES_video_tags"
    es_tag_list = "/data/video_tags/ES_tag_list"
    es_tag_type_file = "/data/video_tags/ES_tag_type"
    # es_tags_process(es_tag_file, es_tag_list)
    get_tag_dict(es_tag_list, es_tag_type_file)