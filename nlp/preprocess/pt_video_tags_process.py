#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-7-22 上午10:47
@File    : ko_video_tags_process.py
@Desc    : 巴西视频tag处理
"""

import json
from collections import OrderedDict
import os
import re
import langdetect
import emoji
import string
from nltk.corpus import stopwords


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


def pt_tags_process(raw_file, tag_file, tag_tokens_file, tag_type_file, tag_standard_file):
    print(">>>>> 正在读取巴西原始tag")
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
    print("\n>>>>> 正在获取tag tokens字典")
    tag_tokens_dict = dict()
    for tag in tags_dict.keys():
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

    schedule = 0
    result = dict()
    for tag in tags_dict.keys():
        schedule += 1
        if schedule % 10000 == 0:
            print("已处理{}行".format(schedule))
        tag_str = tag.replace(" ", "")
        # tag_tokens = tag.split(" ")
        # tag_tok_len = len(tag_tokens)
        sim_dict = dict()
        for _tag in tags_dict.keys():
            tag_str_ = _tag.replace(" ", "")
            tag_tokens_ = _tag.split(" ")
            if tag_str == tag_str_:
                sim_dict[_tag] = len(tag_tokens_)

        if len(sim_dict.keys()) > 1:
            sim_dict_sort = sorted(sim_dict.items(), key=lambda x: x[1], reverse=True)
            # print(sim_dict_sort)
            tf_dict = {k: tags_dict[k] for k in sim_dict.keys()}
            tf_dict_sort = sorted(tf_dict.items(), key=lambda x: x[1], reverse=True)
            tf_standard_tag = tf_dict_sort[0][0]
            len_standard_tag = sim_dict_sort[0][0]
            if tf_standard_tag == len_standard_tag:
                standard_tag = len_standard_tag
            else:
                standard_tag = tf_standard_tag

            # print(standard_tag)
            if standard_tag not in result:
                count = 0
                for k, v in sim_dict_sort:
                    count += tags_dict[k]
                result[standard_tag] = count
            else:
                continue
        else:
            result[tag] = tags_dict[tag]



    tag_set = set(result.keys())
    print(">>>>> 原始tag总共{}个".format(len(tag_set)))
    print(">>>>> 正在写入tag字典")
    with open(tag_file, "w") as f:
        f.writelines(json.dumps(dict_sort(result), ensure_ascii=False, indent=4))
    print("<<<<< 原始tag list 已写入文件【{}】".format(tag_file))




def find_lcsubstr(s1, s2):
    s1_len = s1.split(" ")
    s2_len = s2.split(" ")
    m = [[0 for i in range(len(s2_len)+1)] for j in range(len(s1_len)+1)]  # 生成0矩阵，为方便后续计算，比字符串长度多了一列
    mmax = 0   # 最长匹配的长度
    p = 0  # 最长匹配对应在s1中的最后一位
    for i in range(len(s1_len)):
        for j in range(len(s2_len)):
            if s1_len[i] == s2_len[j]:
                m[i+1][j+1] = m[i][j]+1
                if m[i+1][j+1] > mmax:
                    mmax = m[i+1][j+1]
                    p = i+1
    substr = " ".join(s1_len[p-mmax:p]).strip()

    return substr, mmax


def get_standard_tag(tag_file, tag_file_new):
    with open(tag_file, 'r') as f:
        tag_dict = json.load(f)

    clean_tag_dict = dict()

    for tag in tag_dict.keys():
        k = pre_clean(tag).strip()
        if k.isdigit(): continue
        if k:
            if k in clean_tag_dict:
                clean_tag_dict[k] += tag_dict[tag]
            else:
                clean_tag_dict[k] = tag_dict[tag]

    new_tag_dict = dict()
    for k in clean_tag_dict:
        if not k.endswith("s") and k + "s" in clean_tag_dict.keys():
            if clean_tag_dict[k] >= clean_tag_dict[k+"s"]:
                new_tag_dict[k] = clean_tag_dict[k] + clean_tag_dict[k+"s"]
            else:
                new_tag_dict[k+"s"] = clean_tag_dict[k] + clean_tag_dict[k+"s"]
        elif k.endswith("s") and k[:-1] in clean_tag_dict.keys():
            if clean_tag_dict[k[:-1]] >= clean_tag_dict[k]:
                if k[:-1] in new_tag_dict:
                    continue
                else:
                    new_tag_dict[k[:-1]] = clean_tag_dict[k[:-1]] + clean_tag_dict[k]
            else:
                if k in new_tag_dict:
                    continue
                else:
                    new_tag_dict[k] = clean_tag_dict[k[:-1]] + clean_tag_dict[k]

        else:
            new_tag_dict[k] = clean_tag_dict[k]

    print(">>>>> 正在写入tag字典")
    with open(tag_file_new, "w") as f:
        f.writelines(json.dumps(dict_sort(new_tag_dict), ensure_ascii=False, indent=4))
    print("<<<<< 原始tag list 已写入文件【{}】".format(tag_file_new))


def get_new_tag(tag_file, substr_file):
    with open(tag_file, 'r') as f:
        tag_dict = json.load(f)

    with open(substr_file, 'r') as f:
        substr_tag_dict = json.load(f)

    new_tag_dict = dict()

    for tg in substr_tag_dict.keys():
        if tg in tag_dict.keys():
            tag_dict[tg] = substr_tag_dict[tg]
        else:
            tag_dict[tg] = substr_tag_dict[tg]

    soccer_patten = re.compile("\d-\d|\d:\d|\d \d")

    for ta in tag_dict.keys():
        no_num_tag = soccer_patten.sub("", ta).strip()

        if no_num_tag:
            if no_num_tag.find(" vs ") >= 0:
                new_tag_ = no_num_tag.split(" vs ")
            elif no_num_tag.find(" - ") >= 0:
                new_tag_ = no_num_tag.split(" - ")
            else:
                new_tag_ = no_num_tag.split("\n")
            for tg in new_tag_:
                if tg in new_tag_dict.keys():
                    if tg in tag_dict.keys():
                        new_tag_dict[tg] += tag_dict[tg]
                    else:
                        new_tag_dict[tg] = tag_dict[ta]
                else:
                    if tg in tag_dict.keys():
                        new_tag_dict[tg] = tag_dict[tg]
                    else:
                        new_tag_dict[tg] = tag_dict[ta]
        else:
            continue



    print(">>>>> 正在写入新的tag字典")
    with open(tag_file + "_new", "w") as f:
        f.writelines(json.dumps(dict_sort(new_tag_dict), ensure_ascii=False, indent=4))
    print("<<<<< 原始tag list 已写入文件【{}】".format(tag_file + "_new"))


def get_type_tag(tag_list_file, tag_standard_file, tag_type_file):

    with open(tag_list_file, 'r') as f:
        tags_dict = json.load(f)

    print(">>>>> 正在获取tag type")

    print("\n>>>>> 正在获取常用tag列表")

    new_proofed_tag_tokens_dict = dict()
    one_gram_tag_dict = dict()
    for k, v in tags_dict.items():
        if v > 10 and k not in stopwords.words('english'):
            one_gram_tag_dict[k] = v

    for k, v in tags_dict.items():
        if v > 10:
            new_proofed_tag_tokens_dict[k] = dict()
            for _k in tags_dict.keys():
                if tags_dict[_k] > 5:
                    if _k.find(k+" ") >= 0 or _k.find(" "+k) >= 0 or _k == k:
                        if _k in new_proofed_tag_tokens_dict[k]:
                            new_proofed_tag_tokens_dict[k][_k] += tags_dict[_k]
                        else:
                            new_proofed_tag_tokens_dict[k][_k] = tags_dict[_k]


    print(">>>>> 标准化一元tag写入文件")
    with open(tag_standard_file, "w") as f:
        f.writelines(json.dumps(dict_sort(one_gram_tag_dict, limit_num=5), ensure_ascii=False, indent=4))
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
    1.剔除数字 1. 2. 3.
    2.替换带括号的字符 标点符号！ vs.
    :param text:
    :return:
    """
    l_tag = text.lower()
    no_emoji = clean_emoji(l_tag)
    no_url = clean_url(no_emoji)
    no_num = rm_num(no_url)
    no_sym = remove_symbol(no_num)

    return no_sym

def remove_symbol(text):
    """
    清除符号
    :param text:
    :return:
    """
    sym_patten = re.compile(r"#|!|;|\(|\)|\[|\]", flags=0)
    if text.find("=") < 0:
        text = sym_patten.sub("", text)
        # text = text.replace(" vs. ", " vs ")
    else:
        text = ''
    return text.strip()



def rm_num(text):
    """
    清除纯数字序号
    :param text:
    :return:
    """
    num_patten = re.compile(r"^\d\.| \d\. ")
    text = num_patten.sub("", text)
    return text.strip()


def clean_period(input_str):
    pattern_period = r'[1-2]\d{3}[s]{0,1}$|^\d{1,2}/\d{1,2}/^\d{2,4}$|\d{2,4}[-/]\d{2,4}$'
    res_period = re.compile(pattern_period, flags=0)
    mat = res_period.search(input_str)
    if mat:
        year_tag = mat.group(0)
    else:
        year_tag = ""
    return year_tag


def clean_emoji(text):
    """
    清洗表情符号
    :param text:
    :return:
    """
    token_list = text.replace("¡", "").replace("¿", "").split(" ")
    em_str = r":.*?:"
    em_p = re.compile(em_str, flags=0)
    clean_token = list()
    for token in token_list:
        em = emoji.demojize(token)
        emj = em_p.search(em)
        if emj:
            _e = emj.group(0)
            # print(_e)
        else:
            clean_token.append(token)
    cleaned_text = " ".join(clean_token)
    return cleaned_text.strip()


def clean_punc(text):
    """
    清洗标点符号
    :param text:
    :return:
    """
    del_symbol = string.punctuation  # ASCII 标点符号
    remove_punctuation_map = dict((ord(char), " ") for char in del_symbol)
    new_text = text.translate(remove_punctuation_map)  # 去掉ASCII 标点符号
    new_text = re.sub(r"\s+", " ", new_text).strip()
    return new_text

def clean_mail(text):
    """
    清洗邮箱
    :param text:
    :return:
    """
    pattern = re.compile(r"\w+[-_.]*[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}")
    mail_list = re.findall(pattern, text)
    for mail in mail_list:
        text = text.replace(mail, " ")
    return text


def clean_url(text):
    """
    清洗url网址
    :param text:
    :return:
    """
    pattern = re.compile(
        r'(?:(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])|(?:www\.[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])')
    # pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-zA-Z][0-9a-zA-Z]))+')
    url_list = re.findall(pattern, text)
    for url in url_list:
        text = text.replace(url, " ")
    return text.replace("( )", " ")





if __name__ == '__main__':
    tag_dir = r"/home/zoushuai/algoproject/algo-python/nlp/preprocess/tags"
    raw_file = os.path.join(tag_dir, 'BR_video_tags')
    tag_file = os.path.join(tag_dir, 'BR_tag_list')
    tag_file_new = os.path.join(tag_dir, 'BR_tag_list_new')
    tag_tokens_file = os.path.join(tag_dir, 'BR_tag_list_tokens')
    tag_type_file = os.path.join(tag_dir, "BR_tag_type")
    tag_standard_file = os.path.join(tag_dir, "BR_base_tags")

    # get_standard_tag(tag_file, tag_file_new)
    # pt_tags_process(raw_file, tag_file, tag_tokens_file, tag_type_file, tag_standard_file)
    # get_new_tag(tag_file, "{}_substr".format(tag_file))
    get_type_tag(tag_file_new, tag_standard_file, tag_type_file)
    # get_stardard_list_v1(tag_file)
    # get_stardard_list(tag_tokens_file)