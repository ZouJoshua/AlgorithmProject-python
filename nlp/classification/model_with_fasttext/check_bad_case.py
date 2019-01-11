#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/1/8 22:24
@File    : check_bad_case.py
@Desc    : 
"""

import os
from os.path import dirname
import sys
root_path = dirname(dirname(dirname(dirname(os.path.realpath(__file__)))))
class_path = dirname(dirname(os.path.realpath(__file__)))
sys.path.append(root_path)
sys.path.append(dirname(class_path))
from IPython.display import clear_output
import json

class Check(object):

    def __init__(self, checkfile, check_outfile, level='two_level', subcategory='law', check_type='all', filter_proba=1):
        self.cf = checkfile
        self.cof = check_outfile
        self.check_type = check_type
        self.level = level
        self.subcategory = subcategory
        self.pp = filter_proba

    def get_check_data(self):
        f = open(self.cf, 'r', encoding='utf-8')
        lines = f.readlines()
        bucket = list()
        for line in lines:
            line_json = json.loads(line.strip("\n"))
            if self.check_type == 'all':
                if line_json[self.level] == self.subcategory:
                    bucket.append(line_json)
                continue
            elif self.check_type == 'right':
                if line_json[self.level] == self.subcategory and line_json["predict_two_level"] == self.subcategory:
                    bucket.append(line_json)
                continue
            else:
                if line_json[self.level] == self.subcategory and line_json["predict_two_level"] != self.subcategory:
                    bucket.append(line_json)
                continue
        f.close()
        return bucket

    def check(self, bucket):
        print('当前检查总计：\n{}'.format(len(bucket)))
        check_out = list()
        while True:
            line_dict = bucket.pop()
            p = line_dict['predict_two_level_proba']
            if p < self.pp:
                out = '正在检查：\n' \
                      'ID：{}\n' \
                      'Title：{}\n' \
                      'Content：\n{}\n' \
                      '人工标注分类：{}\n' \
                      '机器预测分类：{}\n' \
                      '机器预测分类概率：{}\n'.format(line_dict["article_id"], line_dict["title"],
                                             line_dict['content'], line_dict[self.level],
                                             line_dict['predict_two_level'], p)
                yield out
                is_right = input("请检查，输入 'y' or 'n'\n")
                if is_right.lower() in ['y', 'n']:
                    out['is_right'] = is_right
                    check_out.append(out)
            continue


checkfile="/data/zoushuai/news_content/sub_classification_model/national_v0/national_model_1/data/train_check_pred.json"
checkoutfile = "/data/zoushuai/news_content/sub_classification_model/national_v0/national_model_1/check.json"
c = Check(checkfile, checkoutfile, level='two_level', subcategory='law', check_type='right', filter_proba=1)
bucket = c.get_check_data()
c_test = c.check(bucket)


check_out = list()
File = open(checkoutfile, 'a+')
while True:
    try:
        clear_output()
        sys.stdout.flush()
        out = bucket[-1]
        print(next(c.check(bucket)))
#         print(len(check_out))
        is_right = input("请检查，输入 'y' or 'n'\n")
        if is_right.lower() in ['y', 'n']:
            out['is_right'] = is_right
            if is_right == 'y':
                out["two_level_checked"] = ''
            else:
                out['two_level_checked'] = input("请输入正确类别：{1:crime, 2:law, 3:education, 4:politics, 5:others}\n")
            File.write(json.dumps(out) + '\n')
            File.flush()
        continue
    except StopIteration:
        File.close()
        sys.exit()