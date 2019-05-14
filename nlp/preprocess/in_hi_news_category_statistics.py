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
from urllib.parse import urlparse
# 谷歌翻译api
from googletrans import Translator





class CleanResult(object):
    """从解析结果中提取出结果为空的、非空的结果，并写入文件"""
    def __init__(self, data_base_dir, fname1, fname2):
        self._dir = data_base_dir
        self.fn1 = fname1
        self.fn2 = fname2
        self.get_result()

    def get_result(self):
        for i in range(17, 23):
            data_file = os.path.join(self._dir, 'parsered_hi_news_201904{}'.format(i))
            print(">>>>> 正在处理文件:{}".format(data_file))
            nonempty_result_file = os.path.join(self._dir, self.fn1)
            empty_result_file = os.path.join(self._dir, self.fn2)
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


class GetCT(object):
    """从非空结果中统计出分类、tag文件及相关信息"""
    def __init__(self, nonempty_parsered_file, category_file, tag_file):
        self.ncf = nonempty_parsered_file
        self.cf = category_file
        self.tf = tag_file
        self.get_category_and_tag()

    def get_category_and_tag(self):
        result_f = open(self.ncf, 'r')
        category_f = open(self.cf, 'w')
        tag_f = open(self.tf, 'w')
        category_result_f = open("{}_stat".format(self.cf), 'w', encoding='utf-8')
        tag_result_f = open("{}_stat".format(self.tf), 'w', encoding='utf-8')
        print(">>>>> 正在获取category、tag文件")
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
                # print(line)
                continue
            if 'tag' in line['result'].keys():
                if line['result']['tag'] != []:
                    tag_f.write(_line)
                    for t in line['result']['tag']:
                        if t in tag_dict.keys():
                            tag_dict[t] += 1
                        else:
                            tag_dict[t] = 1
            else:
                # print(line)
                continue
        print(">>>>>> 正在获取category、tag统计信息")
        c_sort_dict = dict_sort(category_dict)
        t_sort_dict = dict_sort(tag_dict)
        category_result_f.writelines(json.dumps(c_sort_dict, indent=4))
        tag_result_f.writelines(json.dumps(t_sort_dict, indent=4))
        category_f.close()
        tag_f.close()
        category_result_f.close()
        tag_result_f.close()
        print("<<<<< category文件已生成：{}".format(self.cf))
        print("<<<<< category统计文件已生成：{}_stat".format(self.cf))
        print("<<<<< tag文件已生成：{}".format(self.tf))
        print("<<<<< tag统计文件已生成：{}_stat".format(self.tf))


class Hi2EnMap(object):
    """获取分类的印地语到英语的映射"""
    def __init__(self, category_stat_file, hi_category_list_file, en_category_list_file, hi2en_map_file):
        self.csf = category_stat_file
        self.hclf = hi_category_list_file
        self.eclf = en_category_list_file
        self.mf = hi2en_map_file
        self.get_hi_category_list(limnum=2300)
        self.get_hi2en_map_file()

    def read_json_file(self, file):
        hi_f = open(file, 'r')
        lines_ = hi_f.read()
        lines = json.loads(lines_)
        hi_f.close()
        return lines

    def read_file(self, file):
        f = open(file, 'r')
        lines = [line.strip() for line in f.readlines()]
        f.close()
        return lines

    def get_hi_category_list(self, limnum=2300):
        lines = self.read_json_file(self.csf)
        print(">>>>>> 正在处理印地语category列表文件")
        hi_category_f = open(self.hclf, 'w')
        for i, k in enumerate(lines.keys()):
            # print(k)
            if i < limnum:
                k_clean = k.replace(">", "").replace("<", "").strip()
                # print(k_clean)
                hi_category_f.write(k_clean + "\n")
        hi_category_f.close()
        print("<<<<< 印地语category列表文件已生成：{}".format(self.hclf))

    def get_hi2en_map_file(self):
        hi = self.read_file(self.hclf)
        if os.path.exists(self.eclf):
            en = self.read_file(self.eclf)
            hi_en = dict(zip(hi, en))
            print(">>>>> 正在生成印地语-英语映射文件")
            hi_en_f = open(self.mf, 'w')
            hi_en_f.writelines(json.dumps(hi_en, indent=4))
            hi_en_f.close()
            print("<<<<< 映射文件已生成：{}".format(self.mf))
        else:
            raise Exception("请对印地语分类做翻译")

    def translate_hi_to_en(te):
        # header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20130405 Firefox/22.0"}
        # url = "https://translate.google.cn/#view=home&op=translate&sl=auto&tl=en&text={}".format(text)
        # r = requests.get(url, headers=header)
        # print(r.text)
        proxy = {'http': '119.101.112.106:9999'}
        translator = Translator(service_urls=['translate.google.com'], proxies=proxy)
        # lang = translator.detect(text).lang
        result = translator.translate(te, dest='en').text
        return result


class GetTopcategory(object):
    """从解析的分类中提取出一级分类"""
    def __init__(self, nonempty_category_file, hi2en_map_file, out_file):
        self.ncf = nonempty_category_file
        self.mf = hi2en_map_file
        self._of = out_file
        self.get_stadnard_category()

    def get_stadnard_category(self):
        with open(self.mf, 'r') as sf:
            # lines = sf.readline()
            dict_line = json.load(sf)
        print(dict_line.keys())
        out_file = open(self._of, 'w')
        with open(self.ncf, 'r') as cf:
            _lines = cf.readlines()
        _count = 0
        _top_count = 0
        for _li in _lines:
            li = json.loads(_li.strip())
            if 'category' in li['result'].keys():
                cates = li['result']['category']
                true_cate = list()
                # print(cates[:3])
                for _c in cates[:4]:
                    c = _c.replace(">", "").replace("<", "").strip()
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
                        _top_count += 1
                        out_file.write(json.dumps(li) + "\n")
                    else:
                        _count += 1
                        # print(",".join(s))
                        continue
        out_file.close()
        print(">>>>> {}篇新闻有明确的一级分类".format(_top_count))
        print(">>>>> {}篇新闻存在映射出多个一级分类".format(_count))
        print("<<<<< 已生成印地语新闻的一级分类文件：{} ".format(self._of))

def dict_sort(result, limit_num=None):
    print(">>>>> 正在排序...")
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


class WebsiteCategory(object):
    """从网址中提取一级分类"""
    def __init__(self, urls_file, urlpath_stat_file, mapping_file, raw_file, out_file):
        self.uf = urls_file
        self.usf = urlpath_stat_file
        self.mf = mapping_file
        self.rf = raw_file
        self.of = out_file

    def get_topcategory_from_website(self):
        with open(self.mf, 'r') as f:
            top_dict = json.load(f)
        _count = 0
        _top_count = 0
        of = open(self.of, 'w')
        for line in self.read_json_format_file(self.rf):
            if 'url' in line.keys():
                paths = self.split_website(line['url'])
                true_cate = list()
                for path in paths:
                    if path in top_dict.keys():
                        _out = top_dict[path]['top']
                    else:
                        _out = ''
                    true_cate.append(_out)
                s = set(true_cate)
                if "" in s:
                    s.remove("")
                if len(s):
                    if len(s) == 1:
                        _s = s.pop()
                        line['top_category'] = _s
                        of.write(json.dumps(line) + "\n")
                        _top_count += 1
                    else:
                        _count += 1
        of.close()
        print(">>>>> {}篇新闻有明确的一级分类".format(_top_count))
        print(">>>>> {}篇新闻存在映射出多个一级分类".format(_count))
        print("<<<<< 已生成印地语新闻的一级分类文件：{} ".format(self.of))


    def read_json_format_file(self, file):
        print(">>>>> 正在读原始取数据文件：{}".format(file))
        with open(file, 'r') as f:
            while True:
                _line = f.readline()
                if not _line:
                    break
                else:
                    line = json.loads(_line)
                    yield line


    def get_web2category(self):
        with open(self.mf, 'r') as f:
            web2category_dict = json.load(f)

        return web2category_dict
    def website_category_stat(self):
        print(">>>>> 正在从网址中获取分类统计信息")
        category_dict = dict()
        lines = self.get_url_from_file()
        line_count = 0
        for line in lines:
            line_count += 1
            if line_count % 100000 == 0:
                print("已处理{}行".format(line_count))
            if 'url' in line.keys():
                _url = line['url']
                _paths = self.split_website(_url)
                for p in _paths:
                    if p in category_dict.keys():
                        category_dict[p] += 1
                    else:
                        category_dict[p] = 1
        t_sort_dict = dict_sort(category_dict, limit_num=10)
        with open(self.usf, 'w') as f:
            f.writelines(json.dumps(t_sort_dict, indent=4))
        print("<<<<< 分类统计结果已生成：{}".format(self.usf))



    def split_website(self, url, lower=True):
        paths = list()
        if url:
            _url = url
            if lower:
                _url = url.lower()
            _path = urlparse(_url).path
            for p in _path.split("/"):
                if p:
                    paths.append(p)
        return paths

    def get_url_from_file(self):
        with open(self.uf, 'r') as f:
            while True:
                _line = f.readline()
                if not _line:
                    break
                line = json.loads(_line)
                yield line


def main():
    data_base_dir = r'/data/in_hi_news_parser_result'
    fname1 = 'result_nonempty_all'
    fname2 = 'result_empty_all'
    nonemp_file = os.path.join(data_base_dir, fname1)
    emp_file = os.path.join(data_base_dir, fname2)
    # 获取解析成功、失败的文件
    # CleanResult(data_base_dir, fname1, fname2)
    # 从解析成功的文件里提取分类、tag信息及相关统计
    c_file = os.path.join(data_base_dir, 'result_category_all')
    t_file = os.path.join(data_base_dir, 'result_tag_all')
    # GetCT(nonemp_file, c_file, t_file)
    # 获取印地语与英语转换的映射文件
    c_s_file = os.path.join(data_base_dir, 'result_category_all_stat')
    h_c_file = os.path.join(data_base_dir, 'result_hi_category.txt')
    e_c_file = os.path.join(data_base_dir, 'result_en_category.txt')
    h2e_c_file = os.path.join(data_base_dir, 'result_hi2en_category.json')
    # Hi2EnMap(c_s_file, h_c_file, e_c_file, h2e_c_file)
    # 从映射文件获取印地语新闻一级分类
    # todo:人工挑选出标准分类体系
    # standard_file = os.path.join(data_base_dir, "result_category_standard.json")
    # t_file = os.path.join(data_base_dir, 'result_topcategory_all')
    # GetTopcategory(nonemp_file, standard_file, t_file)
    # 印地语网址获取一级分类
    u_file = os.path.join(data_base_dir, "in_hi_html.json")
    us_file = os.path.join(data_base_dir, "in_hi_url_category_stat")
    # m_file = os.path.join(data_base_dir, "in_hi_url_category_mapping")
    m_file = "/home/zoushuai/algoproject/algo-python/nlp/data/n_hi_category_data/keywords_features.json"
    tw_file = os.path.join(data_base_dir, 'result_topcategory_website_all')
    wc = WebsiteCategory(u_file, us_file, m_file, u_file, tw_file)
    wc.get_topcategory_from_website()





if __name__ == '__main__':
    main()