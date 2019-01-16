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

    def __init__(self, checkfile, check_outfile, check_type='all', level='two_level', subcategory='law', pred_subcategory='',filter_proba=1):
        self.cf = checkfile
        self.cof = check_outfile
        self.check_type = check_type
        self.level = level
        self.subcategory = subcategory
        self.pred_subcategory = pred_subcategory
        self.pp = filter_proba

    def get_check_data(self):
        f = open(self.cf, 'r', encoding='utf-8')
        lines = f.readlines()
        bucket = list()
        for line in lines:
            line_json = json.loads(line.strip("\n"))
            if self.check_type == 'all':
                if line_json[self.level] == self.subcategory and line_json['predict_two_level_proba'] <= self.pp:
                    bucket.append(line_json)
                continue
            elif self.check_type == 'right':
                if line_json[self.level] == self.subcategory and line_json["predict_two_level"] == self.subcategory and \
                        line_json['predict_two_level_proba'] <= self.pp:
                    bucket.append(line_json)
                continue
            else:
                if line_json[self.level] == self.subcategory and line_json["predict_two_level"] != self.subcategory and \
                        line_json['predict_two_level_proba'] <= self.pp:
                    if not self.pred_subcategory:
                        bucket.append(line_json)
                    elif self.pred_subcategory and line_json["predict_two_level"] == self.pred_subcategory:
                        bucket.append(line_json)
                continue
        f.close()
        return bucket

    def check(self, bucket):
        print('当前检查总计：\n{}'.format(len(bucket)))
        check_out = list()
        while True:
            line_dict = bucket.pop()
            out = '正在检查：\n' \
                  'ID：{}\n' \
                  'Title：{}\n' \
                  'Content：\n{}\n' \
                  '人工标注分类：{}\n' \
                  '机器预测分类：{}\n' \
                  '机器预测分类概率：{}\n'.format(line_dict["article_id"], line_dict["title"],
                                         line_dict['content'], line_dict[self.level],
                                         line_dict['predict_two_level'], line_dict['predict_two_level_proba'])
            yield out
            is_right = input("请检查，输入 'y' or 'n'\n")
            if is_right.lower() in ['y', 'n']:
                out['is_right'] = is_right
                check_out.append(out)
            continue


#  可修改想查看训练集、测试集的预测情况
# checkfile="/data/zoushuai/news_content/sub_classification_model/business/business_model_1/data/train_check_pred.json"
checkfile="/data/zoushuai/news_content/sub_classification_model/business/business_model_1/data/test_check_pred.json"
checkoutfile = "/data/zoushuai/news_content/sub_classification_model/business/business_model_1/check.json"
# 可修改标注的分类、预测的分类，即传入subcategory 为人工标注的分类、pred_subcategory 为机器预测的分类
# 如：想查看人工标注分类为 ‘market’，但是机器分类为‘finance’的情况 ，可设置subcategory='market', pred_subcategory='finance'
# ["industry economic","market", "finance", "investment" ,"others"]
c = Check(checkfile, checkoutfile, check_type='error', level='two_level', subcategory='market', pred_subcategory='others', filter_proba=1)
bucket = c.get_check_data()
c_test = c.check(bucket)
# print(next(c.check(bucket)))


check_out = list()
File = open(checkoutfile, 'a+')
if len(bucket):
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
else:
    raise Exception("bucket 无数据，请检查！")