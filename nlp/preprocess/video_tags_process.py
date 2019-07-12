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
import emoji
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree



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
        if limit_num:
            if i[1] > limit_num:
                result_sort[i[0]] = i[1]
                domain_count += 1
                count_limit += i[1]
        else:
            result_sort[i[0]] = i[1]
    return result_sort


def es_tags_process(raw_file, tag_file, tag_tokens_file, standard_tag_file):
    print(">>>>> 正在读取西班牙原始tag")
    tag_list = list()
    for line in read_json_format_file(raw_file):
        vtag_str = line["vtaglist"]
        if vtag_str:
            tags = vtag_str.split(",")
            tag_list += tags

    print("\n>>>>> 正在获取tag字典")
    tags_dict = dict()
    for tag in tag_list:
        tag = tag.lower()
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

    print("\n>>>>> 正在获取常用一元tag列表")
    proof_tag_dict = dict()
    for k, v in tags_dict.items():
        _k = k.split(" ")
        if len(_k) == 1:
            if not k.endswith("s") and k + "s" in tag_tokens_dict.keys():
                if len(k) > 2:
                    proof_tag_dict[k] = tag_tokens_dict[k] + tag_tokens_dict[k + "s"]
                else:
                    continue

    print(">>>>> 标准化tag写入文件")
    # with open(standard_tag_file, "w") as f:
    #     f.writelines(json.dumps(dict_sort(proof_tag_dict, limit_num=60), ensure_ascii=False, indent=4))
    print("<<<<< 标准化tag已写入文件【{}】".format(standard_tag_file))



def standard_tag(tag, standard_tag_list):
    # print(">>>>> 正在标准化tag")
    l_tag = tag.lower()
    tag = clean_url(l_tag)
    if tag.find("=") < 0 and tag.find("�") < 0:
        _tag = tag.replace("#0", "")
        year_tag = clean_period(_tag)
        if year_tag:
            no_punc_tag = _tag
        else:
            no_punc_tag = clean_punc(_tag)
        new_tag = proof_tag(no_punc_tag, standard_tag_list)
    else:
        new_tag = ""

    return new_tag.strip()

def get_clean_tag_dict(tag_list_file, standard_tag_file, type_tag_file):
    print(">>>>> 正在读取原始tag 列表")
    with open(tag_list_file, "r") as f:
        tags_dict = json.load(f)
    print("\n>>>>> 正在读取标准tag 列表")
    with open(standard_tag_file, "r") as f:
        standard_tag_dict = json.load(f)
    standard_tag_list = list(standard_tag_dict.keys())

    print("\n>>>>> 正在标准化tag 列表")
    clean_tags_dict = dict()
    for ta in tags_dict.keys():
        new_tag = standard_tag(ta, standard_tag_list)
        if new_tag:
            if new_tag in clean_tags_dict:
                clean_tags_dict[new_tag] += tags_dict[ta]
            else:
                clean_tags_dict[new_tag] = tags_dict[ta]
        else:
            continue
    print("\n>>>>> 正在处理统计一元类型tag")
    one_gram_dict = dict()
    for k, v in clean_tags_dict.items():
        _k = k.split(" ")
        if len(_k) == 1:
            if not k.isdigit():
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
        if v:
            _v = dict()
            for i in v.keys():
                if len(i.split(" ")) < 5 and v[i] > 5:
                    _v[i] = v[i]
                else:
                    continue
            if _v:
                one_gram_dict_tmp[k] = _v
        else:
            continue

    print("\n>>>>> 正在写入分类tag到文件")
    with open(type_tag_file, "w") as f:
        f.writelines(json.dumps(one_gram_dict_tmp, ensure_ascii=False, indent=4))
    print("<<<<< 分类tag已写入【{}】文件".format(type_tag_file))



def proof_tag(tag, standard_tag_list):
    """
    将tag标准化，如video变成videos
    :param tag:
    :param standard_tag_list:
    :return:
    """
    tag_len = tag.split(" ")
    if len(tag_len) == 1:
        if tag in standard_tag_list:
            return tag + "s"
        else:
            return tag
    else:
        new_tag = ""
        new_tmp_tag = ""
        replace_count = 0
        for tg in tag_len:
            if tg in standard_tag_list:
                replace_count += 1
                new_tmp_tag += "{}s ".format(tg)
            else:
                new_tmp_tag += "{} ".format(tg)
        if replace_count < 2:
            new_tag = new_tmp_tag
        else:
            new_tag = tag
        return new_tag.strip()


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

def clean_url(text):
    """
    清洗url网址
    :param text:
    :return:
    """
    pattern = re.compile(r'(?:(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])|(?:www\.[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])')
    # pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-zA-Z][0-9a-zA-Z]))+')
    url_list = re.findall(pattern, text)
    for url in url_list:
        text = text.replace(url, " ")
    return text.replace("( )", " ")



def clean_period(input_str):
    pattern_period = r'[1-2]\d{3}[s]{0,1}$|^\d{1,2}/\d{1,2}/^\d{2,4}$|\d{2,4}[-/]\d{2,4}$'
    res_period = re.compile(pattern_period, flags=0)
    mat = res_period.search(input_str)
    if mat:
        year_tag = mat.group(0)
    else:
        year_tag = ""
    return year_tag


def trim_video_tag(input_tag, tag_dict, standard_tag_list):
    # inputline = 'latest news	2019 news 2018'

    resultdict = {}
    details = []

    # 1. 预清洗
    new_tag = standard_tag(input_tag, standard_tag_list)
    # print(new_tag)
    tag_tokens = new_tag.split(" ")
    details.append("【{}】0==>【{}】".format(input_tag, new_tag))

    # 2. 预判断:is in tag_dict or not

    c_tag = []
    if len(tag_tokens) == 1:
        if new_tag in tag_dict.keys():
            c_tag = [new_tag]
    else:
        for tok in tag_tokens:
            if tok in tag_dict.keys():
                print(new_tag)
                print(tag_dict[tok].keys())
                if new_tag in tag_dict[tok].keys():
                    c_tag = [new_tag]
                    print(c_tag)
                else:
                    c_tag.append(tok)

    if len(c_tag) >= 1:
        resultdict["in_tag_dict"] = c_tag
        details.append("【{}】1==>【{}】".format(new_tag, c_tag))
        return c_tag, resultdict, details
    else:
        pass

    # 小于2元词不处理,直接返回
    if len(tag_tokens) < 2:
        resultdict["one_gram"] = [new_tag]
        details.append("【{}】2==>【{}】".format(new_tag, new_tag))
        return [new_tag], resultdict, details
    else:
        pass

    # 3.trim1 process: period trim 时间性单词 或修饰行状语

    pattern_period = r'^top\s{1}\d.\s{1}|^best|^best of|^hit|2015|2016|2017|2018|2019|latest|updates|today| new$|new released|^new '
    res_period = re.compile(pattern_period, flags=0)

    res1 = res_period.sub('', new_tag.strip())
    res1_tokens = []
    for w in res1.split(' '):
        w = w.strip()
        if w != '':
            res1_tokens.append(w)

    res1 = ' '.join(res1_tokens)

    res1findall = res_period.findall(new_tag.strip())
    resultdict['period'] = res1findall
    details.append("【{}】3==>【{}】".format(new_tag, res1))

    # 3. 预判断:is in tag_dict or not
    c_tag = []
    if len(res1_tokens) == 1:
        if res1 in tag_dict.keys():
            c_tag = [res1]
    else:
        for tok in res1_tokens:
            if tok in tag_dict.keys():
                if res1 in tag_dict[tok].keys():
                    c_tag = res1_tokens
                else:
                    c_tag.append(tok)

    if len(c_tag) >= 1:
        resultdict["period"] = c_tag
        details.append("【{}】4==>【{}】".format(res1, c_tag))
        return c_tag, resultdict, details
    else:
        pass

    # 小于2元词不处理,直接返回
    if len(res1_tokens) < 2:
        resultdict["period"] = [res1]
        details.append("【{}】5==>【{}】".format(new_tag, res1))
        return [res1], resultdict, details
    else:
        pass

    # 4.trim2 process: language trim

    pattern_lang = r'en español|español|españa|latino|latin|'

    res_lang = re.compile(pattern_lang, flags=0)
    res2 = res_lang.sub('', res1.strip())

    res2_tokens = []
    for w in res2.split(' '):
        w = w.strip()
        if w != '':
            res2_tokens.append(w)
    res2 = ' '.join(res2_tokens)

    res2findall = res_lang.findall(res1.strip())
    resultdict['lang'] = res2findall
    details.append("【{}】6==>【{}】".format(res1, res2))

    # 4. 预判断:is in tag_dict or not
    c_tag = []
    if len(res2_tokens) == 1:
        if res2 in tag_dict.keys():
            c_tag = [res2]
    else:
        for tok in res2_tokens:
            if tok in tag_dict.keys():
                if res2 in tag_dict[tok].keys():
                    c_tag = res2_tokens
                else:
                    c_tag.append(tok)

    if len(c_tag) >= 1:
        resultdict["lang"] = c_tag
        details.append("【{}】7==>【{}】".format(res1, c_tag))
        return c_tag, resultdict, details
    else:
        pass

    # 小于2元词不处理,直接返回
    if len(res1_tokens) < 2:
        resultdict["lang"] = [res2]
        details.append("【{}】\t8==>\t【{}】".format(new_tag, res2))
        return [res2], resultdict, details
    else:
        pass
    return [res2], resultdict, details


def tt_trim_tag(tag_type_file, standard_tag_file):
    # tag = "latest news	2019 news 2018"
    # tag = "atlético de madrid"
    tag = "gta 5 gameplay español"
    # tag = "chinas roleplays"
    with open(tag_type_file, 'r') as f:
        tag_dict = json.load(f)

    standard_tag_list = list()
    with open(standard_tag_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            standard_tag_list.append(line.strip())
    out, reson, detail = trim_video_tag(tag, tag_dict, standard_tag_list)
    print(out)
    print(reson)
    print(detail)

def tt_exract_tag(raw_file, tag_type_file, stopwords_file):
    print(">>>>> 正在读取西班牙原始tag")
    tag_list = list()
    with open(tag_type_file, 'r') as f:
        tag_dict = json.load(f)
    stopwords = list()
    with open(stopwords_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            stopwords.append(line.strip())
    count_ = 0
    for line in read_json_format_file(raw_file):

        title_str = line["article_title"]
        print(title_str)
        content_str = line["text"]

        if title_str and content_str:
            # print(title_str)
            tags = extract_tag(title_str, content_str, tag_dict, stopwords)
            print(">>>>> raw data:{}".format(title_str))
            print(">>>>> clean data:{}\n".format(tags))
        count_ += 1
        if count_ > 3:
            break

def clean_emoji(text):
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



def extract_tag(title, text, tag_dict, stopwords):
    # self.log.info("extracting tags from title and text...")
    mergetaglist = []
    mergetagdict = {}
    lasttaglist = []
    pattern1 = r"""(\||\-\s{1}|\s{1}\-|\(|\)|\?|!|–\s{1}|\s{1}–|│|\"|\'\s{1}|\s{1}\'|‘\s{1}|\s{1}‘|’\s{1}|\s{1}’|:|\s{1}\[|\]\s{1}|~|\/\s{1}|\s{1}\/|\*)"""
    res = re.compile(pattern1, flags=0)

    title_no_emoji = clean_emoji(title)
    title2 = res.sub("#", title_no_emoji)
    print(title2)
    if text.startswith(title):
        text = text[len(title):]
    text2 = text.replace('\n', " ").replace("\t", " ").replace("\r", " ")
    text2 = clean_emoji(text2)
    text2 = clean_url(text2)
    text2 = clean_mail(text2)
    text2_lower = text2.lower()

    text2_ner_list = get_continuous_chunks(text2_lower)
    print(text2_ner_list)


    title_ner_list = list()
    for title_trunk in title2.split('#'):
        title_trunk = title_trunk.strip()
        title_trunk_lower = title_trunk.lower()
        title_trunk_tokens = title_trunk_lower.split(" ")

        if title_trunk != '':
            if len(title_trunk_tokens) == 1:
                if title_trunk_lower not in mergetagdict:
                    mergetaglist.append([title_trunk_lower, 'title_trunk_vtag'])
                    mergetagdict[title_trunk_lower] = None
            elif len(title_trunk_tokens) < 6:

                for tok in title_trunk_tokens:
                    if tok in tag_dict:
                        if title_trunk_lower not in mergetagdict:
                            mergetaglist.append([title_trunk_lower, 'title_trunk_kw'])
                            mergetagdict[title_trunk_lower] = None
            else:
                continue

        title_trunk_list = get_continuous_chunks(title_trunk_lower)
        print(">>>>> title_trunk:{}".format(title_trunk))
        print(">>>>> title_trunk_list:{}".format(title_trunk_list))
        title_ner_list.extend(title_trunk_list)

    tfdict = dict()
    for trunk in title_ner_list:
        trunk_lower = trunk.lower()
        if trunk_lower == '': continue
        if trunk_lower in stopwords: continue
        if len(trunk_lower) < 3: continue
        n = len(trunk_lower.split(' '))
        x = 1.5
        if n >= 2:
            x = 2
        if trunk_lower not in tfdict:
            tfdict[trunk_lower] = x
        else:
            tfdict[trunk_lower] += x

    for trunk in text2_ner_list:
        trunk_lower = trunk.lower()
        if trunk_lower in stopwords: continue
        if trunk_lower == '': continue
        if len(trunk_lower) < 3: continue
        if trunk_lower not in tfdict:
            tfdict[trunk_lower] = 1
        else:
            tfdict[trunk_lower] += 1
    sorted_tfdict = sorted(tfdict.items(), key=lambda k: k[1], reverse=True)
    sorted_tfdict2 = [x for x in sorted_tfdict if x[1] >= 2]

    for c_tag, c_tf in sorted_tfdict2:

        if c_tag in tag_dict or len(c_tag.split(' ')) >= 2:
            if c_tag not in mergetagdict:
                mergetaglist.append([c_tag, 'tf_vtag'])
                mergetagdict[c_tag] = None

    for i, (tag, reason) in enumerate(mergetaglist):
        if i >= 5: break
        lasttaglist.append(tag)

    return lasttaglist

def get_continuous_chunks(text):

    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            continuous_chunk.append(" ".join(current_chunk))
            continuous_chunk.append(i[0])
            current_chunk = []
        else:
            continuous_chunk.append(i[0])
            continue
    if current_chunk:
        continuous_chunk.append(" ".join(current_chunk))
        current_chunk = []

    return continuous_chunk




def tt_clean_emoji():
    text = """ARK - ATACAMOS *NECROCITY* A CAÑONAZOSS!! 😂🤣 - #53 REINOS ENFRENTADOS 2 - Nexxuz"""

    emoji.demojize(text)
    # c_text = clean_emoji(text)
    print(">>>>> raw data:{}".format(text))
    print(">>>>> clean data:{}".format(emoji.demojize(text)))


"""
tag 处理逻辑
1.是否存在vtaglist
2.处理vtaglist
    step1 -> 大小写，清洗url
    step2 -> 是否包含特殊标记 “=”，“�”，“#0”, "¡","¿"等
    step3 -> 清洗时间标记tag，日期 08/08/18、08/08/2018、1980s、1946、2014-2015、10/15、10-15、3-6-19
    step4 -> 清洗标点符号
    step5 -> 标准化tag，video —> videos

3.抽取title和text中的tag
    step1 -> 清洗表情符号
    step2 -> 正则查找可能的tag块

4.返回处理的tag list

"""




if __name__ == "__main__":
    data_dir = "/data/video_tags"
    # split_data_by_country(data_dir)
    es_raw_file = "/home/zoushuai/algoproject/algo-python/nlp/preprocess/tags/ES_video_tags"
    es_tag_list_file = "/home/zoushuai/algoproject/algo-python/nlp/preprocess/tags/ES_tag_list"
    es_tag_tokens_file = "/home/zoushuai/algoproject/algo-python/nlp/preprocess/tags/ES_tag_list_tokens"
    es_standard_tag_file = "/home/zoushuai/algoproject/algo-python/nlp/preprocess/tags/ES_tag_list_standard"
    es_tag_type_file = "/home/zoushuai/algoproject/algo-python/nlp/preprocess/tags/ES_tag_type"
    stopwords_file = "/home/zoushuai/algoproject/nlp_server/src/data/video_tags/stopwords.txt"
    # es_tags_process(es_raw_file, es_tag_list_file, es_tag_tokens_file, es_standard_tag_file)
    # get_clean_tag_dict(es_tag_list_file, es_standard_tag_file, es_tag_type_file)
    # tt_trim_tag(es_tag_type_file, es_standard_tag_file)
    tt_exract_tag(es_raw_file, es_tag_type_file, stopwords_file)
    # tt_clean_emoji()