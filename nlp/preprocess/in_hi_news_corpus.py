#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-5-14 下午12:20
@File    : in_hi_news_corpus.py
@Desc    : 印地语一级分类语料处理
"""

import os
import random
import json

class TopcategoryCorpus(object):

    def __init__(self, in_file1, in_file2, out_file):
        self.f1 = in_file1
        self.f2 = in_file2
        self.out = out_file
        self.get_topcategory_corpus()

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

    def shuff_data(self):
        data_all = list()
        for line in self.read_json_format_file(self.f1):
            if 'tags' in line.keys():
                del line['tags']
            if line['top_category'] not in ("technology", "auto", "science"):
                data_all.append(line)
        for line_ in self.read_json_format_file(self.f2):
            data_all.append(line_)
        # print(len(data_all))
        random.shuffle(data_all)
        return data_all

    def get_topcategory_corpus(self):
        print(">>>>> 正在处理训练语料")
        o_file = open(self.out, 'w')
        category_count = dict()
        for line in self.shuff_data():
            if line['top_category'] in category_count.keys():
                if category_count[line['top_category']] < 10000:
                    category_count[line['top_category']] += 1
                    o_file.write(json.dumps(line, ensure_ascii=False) + "\n")
                else:
                    continue
            else:
                category_count[line['top_category']] = 1
                o_file.write(json.dumps(line, ensure_ascii=False) + "\n")
        print(">>>>> 各一级类类别：\n{}".format(json.dumps(category_count, indent=4)))
        print("<<<<< 训练语料已处理完成：{}".format(self.out))


def main():
    data_base_dir = r'/data/in_hi_news/train_data'
    file1 = os.path.join(data_base_dir, 'topcategory_all')
    file2 = os.path.join(data_base_dir, 'auto_science_tech')
    out_file = os.path.join(data_base_dir, 'top_category_corpus')
    TopcategoryCorpus(file1, file2, out_file)


if __name__ == '__main__':
    main()