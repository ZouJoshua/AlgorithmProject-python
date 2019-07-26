#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-7-22 上午10:47
@File    : ko_video_tags_process.py
@Desc    : 韩国视频tag处理
"""

import json
from collections import OrderedDict
import os
import re
import langdetect


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



def dict_sort(result, limit_num=None):
    _result_sort = sorted(result.items(), key=lambda x: x[1], reverse=True)
    result_sort = OrderedDict()

    count_limit = 0
    domain_count = 0
    for i in _result_sort:
        if limit_num:
            if i[1] > limit_num:
                result_sort[i[0]] = i[1]
                domain_count += 1
                count_limit += i[1]
        else:
            result_sort[i[0]] = i[1]
    return result_sort


def ko_tags_process(raw_file, tag_file, tag_tokens_file, tag_type_file, tag_standard_file):
    print(">>>>> 正在读取韩国原始tag")
    tag_list = list()
    for line in read_json_format_file(raw_file):
        vtag_str = line["vtaglist"]
        if vtag_str:
            tags = vtag_str.split(",")
            tag_list += tags

    print("\n>>>>> 正在获取tag字典")
    tags_dict = dict()
    for tag in tag_list:
        # tag = tag.lower()
        tag = pre_clean(tag)
        # print(tag)
        if tag:
            if tag in tags_dict.keys():
                tags_dict[tag] += 1
            else:
                tags_dict[tag] = 1
    tag_set = set(tags_dict.keys())
    print(">>>>> 原始tag总共{}个".format(len(tag_set)))
    print(">>>>> 正在写入tag字典")
    with open(tag_file, "w") as f:
        f.writelines(json.dumps(dict_sort(tags_dict), ensure_ascii=False, indent=4))
    print("<<<<< 原始tag list 已写入文件【{}】".format(tag_file))

    print("\n>>>>> 正在获取tag tokens字典")
    tag_tokens_dict = dict()
    for tag in tag_list:
        tag = tag.lower()
        _tag = tag.split(" ")
        for ta in _tag:
            if ta in tag_tokens_dict.keys():
                tag_tokens_dict[ta] += 1
            else:
                tag_tokens_dict[ta] = 1

    print("<<<<< 正在写入tag tokens字典")
    with open(tag_tokens_file, "w") as f:
        f.writelines(json.dumps(dict_sort(tag_tokens_dict), ensure_ascii=False, indent=4))
    print("<<<<< 原始tag tokens 已写入文件【{}】".format(tag_tokens_file))

    print(">>>>> 正在获取tag type")
    tmp_proofed_tag_tokens_dict = dict()
    for r_tag in tags_dict.keys():
        tag = standard_tag(r_tag)
        if tag == r_tag:
            if tag not in tmp_proofed_tag_tokens_dict:
                tmp_proofed_tag_tokens_dict[tag] = tags_dict[r_tag]
            else:
                tmp_proofed_tag_tokens_dict[tag] += tags_dict[r_tag]
        else:
            if tag in tags_dict:
                if tag not in tmp_proofed_tag_tokens_dict:
                    tmp_proofed_tag_tokens_dict[tag] = tags_dict[tag] + tags_dict[r_tag]
                else:
                    tmp_proofed_tag_tokens_dict[tag] += tags_dict[r_tag]
            else:
                if tag not in tmp_proofed_tag_tokens_dict:
                    tmp_proofed_tag_tokens_dict[tag] = tags_dict[r_tag]
                else:
                    tmp_proofed_tag_tokens_dict[tag] += tags_dict[r_tag]

    proofed_tag_tokens_dict = dict()

    for p_tag, v in tmp_proofed_tag_tokens_dict.items():
        tag_tok = p_tag.split(" ")
        if len(tag_tok) == 1:
            if p_tag not in proofed_tag_tokens_dict.keys():
                proofed_tag_tokens_dict[p_tag] = dict()
                proofed_tag_tokens_dict[p_tag][p_tag] = v
            else:
                continue
        else:
            for k in tag_tok:
                if k in proofed_tag_tokens_dict.keys():
                    proofed_tag_tokens_dict[k][p_tag] = v
                else:
                    continue

    print("\n>>>>> 正在获取常用一元tag列表")

    new_proofed_tag_tokens_dict = dict()
    one_gram_tag_dict = dict()
    for k, v in proofed_tag_tokens_dict.items():
        k_count = 0
        for _k, _v in v.items():
            k_count += _v
        if k_count > 10:
            new_proofed_tag_tokens_dict[k] = v
        if k_count > 50:
            one_gram_tag_dict[k] = k_count



    print(">>>>> 标准化一元tag写入文件")
    with open(tag_standard_file, "w") as f:
        f.writelines(json.dumps(dict_sort(one_gram_tag_dict, limit_num=100), ensure_ascii=False, indent=4))
    print("<<<<< 标准化tag已写入文件【{}】".format(tag_standard_file))



    print("\n>>>>> 正在写入分类tag到文件")
    with open(tag_type_file, "w") as f:
        f.writelines(json.dumps(new_proofed_tag_tokens_dict, ensure_ascii=False, indent=4))
    print("<<<<< 分类tag已写入【{}】文件".format(tag_type_file))





def get_stardard_list(tag_tokens_file):
    with open(tag_tokens_file, 'r') as f:
        tag_list_tokens = json.load(f)
    tag_tokens_list = tag_list_tokens.keys()
    stardard_tag_dict = dict()
    for tag in tag_list_tokens.keys():
        if tag.find("-") >= 0:
            n_tag = tag.replace("-", '')
            if not n_tag.isdigit():
                if n_tag in tag_tokens_list:
                    stardard_tag_dict[tag] = tag_list_tokens[tag] + tag_list_tokens[n_tag]
        else:
            continue
    print(json.dumps(dict_sort(stardard_tag_dict), indent=4, ensure_ascii=False))


def get_stardard_list_v1(tag_list_file):
    with open(tag_list_file, 'r') as f:
        tags_dict = json.load(f)
    one_gram_list = list()
    one_gram_dict = dict()
    # tag_list = [k for k in tags_dict.keys()]
    for tag in tags_dict.keys():
        tag_tok = tag.split(" ")
        if len(tag_tok) == 1:
            if not tag.endswith("s") and tag + 's' in tags_dict.keys():
                one_gram_dict[tag] = tags_dict[tag] + tags_dict[tag+'s']
                one_gram_list.append(tag)

    print(json.dumps(dict_sort(one_gram_dict), indent=4, ensure_ascii=False))





def standard_tag(raw_tag):
    standard_tag_list1 = ["new", "game", "sport", "highlight", "idol", "kb", "goal", "vlog",
    "play", "interview", "transfer", "song", "recipe", "champion", "tutorial", "skill", "giant",
    "dog", "battleground", "legend", "kid", "animal", "final", "fichaje", "cat", "movie",
    "toy", "tip", "spur", "creator", "star", "fruit", "girl", "playoff", "gooner", "prank", "deporte",
    "video", "assist", "noticia", "youtuber", "cosmetic", "dribble", "blue", "replay", "puma",
    "mark", "dunk", "exercise", "hairstyle", "voice", "review", "celebration", "cartoon", "american"]

    standard_tag_list2 = ["k-pop", "v-log", "k-food", "g-20", "make-up", "e-sports", "k-drama", "a-pink",
    "min-a", "k-beauty", "hip-hop", "a-jax", "k-culture", "k-popcover", "k-star",
    "uh-oh", "play-offs", "hyun-jin", "la-liga", "t-series", "wan-bissaka", "u-20",
    "jin-young", "hyun-moo", "so-mi", "hyeong-don", "k-style", "ji-won", "jong-shin",
    "gyu-ri", "k-뷰티", "j-hope", "ji-eun", "min-ho", "young-jae", "u-know", "u-kiss",
    "gu-ra", "ji-hye", "seul-gi", "ju-ne", "jung-kook", "c-clown", "j-reyez", "ga-in",
    "sung-min", "block-b", "new-tro", "eun-i", "g-dragon", "hyun-a", "g-idle",
    "chung-ha", "wo-man", "4-4-2oons", "monsta-x", "jae-seok", "seung-yoon", "dong-yup",
    "ac-milan", "hat-trick", "real-madrid", "c-jes", "b-boy", "슈퍼주니어-d&e", "ha-neul",
    "twi-light", "a-teen", "ph-1", "k-ville", "ji-hyo", "line-up", "chae-young", "i-dle",
    "yeon-jung", "manchester-united", "xo-iq", "tteok-bokki", "hye-won", "woo-sung",
    "do-yeon", "k-9", "u-15", "semi-finals", "sung-jae", "seung-hoon", "na-young",
    "transfer-news", "heung-min", "j-pop", "premier-league", "u-20월드컵", "jin-hwan",
    "so-yi", "sae-rom", "jin-woo"]

    for tag in standard_tag_list1:
        if raw_tag.find(tag+' ') >= 0 or raw_tag.find(" "+tag) >= 0 or raw_tag == tag:
            if raw_tag.find(tag+'s ') >= 0 or raw_tag.find(" "+tag+"s") >= 0 or raw_tag == tag+"s":
                raw_tag = raw_tag
            else:
                raw_tag = raw_tag.replace(tag, tag + "s")
        else:
            continue
    for tag in standard_tag_list2:
        if raw_tag.find(tag.replace("-", "")+" ") >= 0 or raw_tag.find(" "+tag.replace("-","")) >= 0 or raw_tag == tag.replace("-",""):
            raw_tag = raw_tag.replace(tag.replace("-", ""), tag)
        elif raw_tag.find(tag.replace("-", " ")+" ") >= 0 or raw_tag.find(" "+tag.replace("-"," ")) >= 0 or raw_tag == tag.replace("-"," "):
            raw_tag = raw_tag.replace(tag.replace("-", " "), tag)
        else:
            continue
    tag_tok = raw_tag.split(" ")
    if len(tag_tok) == 1:
        standardtag_list = [k+"s" for k in standard_tag_list1] + standard_tag_list2
        for tag in standardtag_list:
            if raw_tag.find(tag):
                raw_tag = raw_tag.replace(tag, tag+" ")
            else:
                continue

    return raw_tag





def pre_clean(text):
    """
    预处理文本
    1.剔除全数字（match日期）
    2.剔除带‘=’的字符
    3.语言检测（剔除非韩语、非英语外的语言）
    4.替换带括号的字符,替换‘#’字符
    :param text:
    :return:
    """
    details = list()
    result_tag = dict()
    tag = ""
    l_tag = text.lower()
    symbol_text, symbol_detail = remove_symbol(l_tag)
    details.append("【{}】0==>【{}】".format(l_tag, symbol_text))
    result_tag['symbol'] = symbol_text
    if symbol_text:
        num_text, num_detail = rm_num(symbol_text)
        details.append("【{}】1==>【{}】".format(symbol_text, num_text))
        result_tag['num'] = num_text
        if num_text:
            # print(num_text)
            tag = num_text
            # lang_text, lang_detail = detect_lang(num_text)
            # details.append("【{}】2==>【{}】".format(num_text, lang_text))
            # result_tag['lang'] = lang_text
            # if lang_text:
            #     tag = lang_text
        else:
            tag = num_text
    else:
        tag = symbol_text

    return tag

def remove_symbol(text):
    """
    清除符号
    :param text:
    :return:
    """
    sym_patten = re.compile(r"\(.*?\)|#", flags=0)
    if text.find("=") < 0:
        non_sym = sym_patten.sub("", text)
        detail = "non_symbol_tag"
        new_tag = non_sym.strip()
    else:
        detail = "non_symbol_tag"
        new_tag = ""
    return new_tag, detail




def detect_lang(text):
    """
    检测非韩语、非英语外的tag
    :param text:
    :return:
    """
    detail = ''
    try:
        lang = langdetect.detect(text)
    except:
        lang = 'none'
    finally:
        if lang not in ['ko', 'en']:
            detail = 'non_ko_en_tag'
            return "", detail
        else:
            detail = 'ko_or_en_tag'
            return text, detail



def rm_num(text):
    """
    清除纯数字，年份、日期标记
    :param text:
    :return:
    """
    detail = ''

    try:
        float(text)
        detail = 'num_tag'
        return "", detail
    except:
        if text.isdigit():
            time_str = clean_period(text)
            if time_str:
                detail = 'time_tag'
                return time_str, detail
            else:
                detail = 'num_tag'
                return time_str, detail
        else:
            return text, detail


def clean_period(input_str):
    pattern_period = r'[1-2]\d{3}[s]{0,1}$|^\d{1,2}/\d{1,2}/^\d{2,4}$|\d{2,4}[-/]\d{2,4}$'
    res_period = re.compile(pattern_period, flags=0)
    mat = res_period.search(input_str)
    if mat:
        year_tag = mat.group(0)
    else:
        year_tag = ""
    return year_tag




if __name__ == '__main__':
    tag_dir = r"/home/zoushuai/algoproject/algo-python/nlp/preprocess/tags"
    raw_file = os.path.join(tag_dir, 'KR_video_tags')
    tag_file = os.path.join(tag_dir, 'KR_tag_list')
    tag_tokens_file = os.path.join(tag_dir, 'KR_tag_list_tokens')
    tag_type_file = os.path.join(tag_dir, "KR_tag_type")
    tag_standard_file = os.path.join(tag_dir, "kr_base_tags")
    ko_tags_process(raw_file, tag_file, tag_tokens_file, tag_type_file, tag_standard_file)
    # get_stardard_list_v1(tag_file)
    # get_stardard_list(tag_tokens_file)