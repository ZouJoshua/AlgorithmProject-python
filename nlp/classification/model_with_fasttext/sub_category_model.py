#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/1/3 15:55
@File    : sub_category_model.py
@Desc    : 二级分类模型 - fasttext
"""

import json
import random
import fasttext
from pyquery import PyQuery
import logging
import re
import os
from nlp.classification.preprocess.util import clean_string
from nlp.classification.model_evaluate.calculate_p_r_f import evaluate_model
from sklearn import cross_validation
from sklearn.model_selection import KFold,StratifiedKFold

# 制作label映射map
label_idx_map = {"crime": "401", "education": "402", "law": "403", "politics": "404"}
idx_label_map = {"401": "crime", "402": "education", "403": "law", "404": "politics"}

class_cnt_map = {}
trainingDir = "/data/zoushuai/news_content/sub_classification_model/national"
train_data_path = "/data/zoushuai/news_content/sub_classification_model/national/sub_training_data_content+title"
test_data_path = "/data/zoushuai/news_content/sub_classification_model/national/sub_test_data_content+title"
test_data_json_path = "/data/zoushuai/news_content/sub_classification_model/national/sub_test_data_content+title_json"
test_data_json_path1 = "/data/zoushuai/news_content/sub_classification_model/national/sub_test_data_content+title_json2"
model_path = "/data/zoushuai/news_content/sub_classification_model/national/ft_model_sub_content+title"

class SubCategoryModel(object):

    def __init__(self, dataDir, category='national', k=5, model_level='two_level'):
        if os.path.exists(dataDir) and os.path.isdir(dataDir):
            self._datadir = dataDir
        else:
            raise Exception('数据路径不存在，请检查路径')
        self._level = model_level
        self.cg = category
        self.k = k

    def _preprocess_data(self):
        fnames = os.listdir(self._datadir)
        datafiles = [os.path.join(self._datadir, fname) for fname in fnames]
        class_cnt = dict()
        train_format_data = list()
        for datafile in datafiles:
            dataf = open(datafile, 'r', encoding='utf-8')
            data_all = dataf.readlines()
            # random.shuffle(data_all)
            # data_count = len(data_all)
            for li in data_all:
                line = li.strip('\n')
                dataX, dataY = self._preline(line)
                _data = dataX + "\t__label__" + dataY
                train_format_data.append(_data)
                if dataY in class_cnt and dataX != "":
                    class_cnt[dataY] += 1
                elif dataX != "":
                    class_cnt[dataY] = 1
            dataf.close()
        self.generate_kfold_data(train_format_data)


    def generate_kfold_data(self, train_format_data):
        """
        分层k折交叉验证
        :param train_format_data:
        :return:
        """
        datax = [i.split('\t__label__')[0] for i in train_format_data]
        datay = [i.split('\t__label__')[1] for i in train_format_data]
        skf = StratifiedKFold(n_splits=self.k)
        i = 0
        for train_index, test_index in skf.split(datax, datay):
            i += 1
            train_label_count = self._label_count([datay[i] for i in train_index])
            test_label_count = self._label_count([datay[j] for j in test_index])
            train_data = [train_format_data[i] for i in train_index]
            test_data = [train_format_data[j] for j in test_index]
            model_data_path = self._mkdir_path(i)
            train_file = os.path.join(model_data_path, 'train.txt')
            test_file = os.path.join(model_data_path, 'test.txt')
            self.write_file(train_file, train_data)
            self.write_file(test_file, test_data)
            print('文件:{}\n训练数据类别统计：{}'.format(train_file, train_label_count))
            print('文件:{}\n测试数据类别统计：{}'.format(test_file, test_label_count))

    def _label_count(self, label_list):
        label_count = dict()
        for i in label_list:
            if i in label_count:
                label_count[i] += 1
            else:
                label_count[i] = 1
        return label_count

    def write_file(self, file, data):
        with open(file, 'w', encoding='utf-8') as f:
            for line in data:
                f.write(line)
                f.write('\n')
        return

    def _mkdir_path(self, i):
        model_path = os.path.join(self._datadir, "{}_model_{}".format(self.cg, i))
        if not os.path.exists(model_path):
            # os.mkdir(model_path)
            model_data_path = os.path.join(model_path, "data")
            os.makedirs(model_data_path)
            return model_data_path
        else:
            raise Exception('已存在该路径')


    def _get_label(self):
        pass

    def _parse_html(self, html):
        # TODO:解析html内容
        pass

    def _preline(self, line):
        line_json = json.loads(line)
        title = line_json["title"]
        content = ""
        dataY = str(label_idx_map[line_json[self._level].strip().lower()])
        if "content" in line_json:
            content = line_json["content"]
        elif "html" in line_json:
            content = self._parse_html(line_json["html"])
        dataX = clean_string((title + content).lower())  # 清洗数据
        return dataX, dataY

    def train_model(self):
        train_precision = dict()
        test_precision = dict()
        for i in range(self.k):
            data_dir = "{}_model_{}".format(self.cg, i+1)
            model_path = os.path.join(self._datadir, data_dir)
            train_data_path = os.path.join(model_path, 'data', 'train.txt')
            test_data_path = os.path.join(model_path, 'data', 'test.txt')
            classifier = fasttext.supervised(train_data_path, model_path, label_prefix="__label__")
            train_pred = classifier.test(train_data_path)
            test_pred = classifier.test(test_data_path)
            train_precision["model_{}".format(i+1)] = train_pred.precision
            test_precision["model_{}".format(i+1)] = test_pred.precision
            print("在训练集{}上的准确率：\n{}".format(data_dir, train_pred.precision))
            print("在测试集{}上的准确率：\n{}".format(data_dir, test_pred.precision))

    def evaluate_model(self, datapath):
        return evaluate_model(datapath)



with open(test_data_json_path, 'r') as test_json_f, open(test_data_json_path1, "a") as test_json_f1:
    lines = test_json_f.readlines()
    for line in lines:
        line = json.loads(line)
        title = line["title"]
        content_list = []
        content = ""
        label = str(label_idx_map[line['two_level'].lower().strip()])
        if "html" in line:
            content = line["html"]
        elif "content" in line:
            content = line["content"]
        desc = clean_string((title + content).lower())  # 清洗数据
        content_list.append(desc)
        labels = classifier.predict_proba(content_list)
        line['predict_sub_category'] = idx_label_map[labels[0][0][0].replace("'", "").replace("__label__", "")]
        # print(line['predict_top_category'])
        line['predict_sub_category_proba'] = labels[0][0][1]
        test_json_f1.write(json.dumps(line) + "\n")