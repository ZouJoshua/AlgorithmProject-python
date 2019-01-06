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
from sklearn.model_selection import KFold, StratifiedKFold

# 制作label映射map
label_idx_map = {"crime": "401", "education": "402", "law": "403", "politics": "404"}
idx_label_map = {"401": "crime", "402": "education", "403": "law", "404": "politics"}

dataDir = "/data/zoushuai/news_content/sub_classification_model/national"

class SubCategoryModel(object):

    def __init__(self, dataDir, category='national', k=5, model_level='two_level'):
        self._level = model_level
        self.cg = category
        self.k = k
        if os.path.exists(dataDir) and os.path.isdir(dataDir):
            self._datadir = dataDir
        else:
            raise Exception('数据路径不存在，请检查路径')

    def preprocess_data(self):
        fnames = os.listdir(self._datadir)
        datafiles = [os.path.join(self._datadir, fname) for fname in fnames]
        data_all = list()
        class_cnt = dict()
        for datafile in datafiles:
            dataf = open(datafile, 'r', encoding='utf-8')
            data = dataf.readlines()
            # random.shuffle(data)
            # data_count = len(data)
            for li in data:
                line = li.strip('\n')
                dataX, dataY = self._preline(line).split('\t__label__')
                if dataY in class_cnt and dataX != "":
                    class_cnt[dataY] += 1
                elif dataX != "":
                    class_cnt[dataY] = 1
                data_all.append(line)
            dataf.close()
        print('所有数据分类情况:\n{}'.format(class_cnt))
        self._generate_kfold_data(data_all)
        return

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
        _data = dataX + "\t__label__" + dataY
        return _data

    def _generate_kfold_data(self, data_all):
        """
        分层k折交叉验证
        :param train_format_data:
        :return:
        """
        datax = [self._preline(i).split('\t__label__')[0] for i in data_all]
        datay = [self._preline(i).split('\t__label__')[1] for i in data_all]
        skf = StratifiedKFold(n_splits=self.k)
        i = 0
        for train_index, test_index in skf.split(datax, datay):
            i += 1
            train_label_count = self._label_count([datay[i] for i in train_index])
            test_label_count = self._label_count([datay[j] for j in test_index])
            train_data = [self._preline(data_all[i]) for i in train_index]
            test_data = [self._preline(data_all[j]) for j in test_index]
            test_check = [data_all[i] for i in test_index]
            model_data_path = self._mkdir_path(i)
            train_file = os.path.join(model_data_path, 'train.txt')
            test_file = os.path.join(model_data_path, 'test.txt')
            test_check_file = os.path.join(model_data_path, 'test_check.json')
            self.write_file(train_file, train_data, 'txt')
            self.write_file(test_file, test_data, 'txt')
            self.write_file(test_check_file, test_check, 'json')
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

    def _mkdir_path(self, i):
        data_path = os.path.join(self._datadir, "{}_model_{}".format(self.cg, i))
        if not os.path.exists(data_path):
            # os.mkdir(data_path)
            model_data_path = os.path.join(data_path, "data")
            os.makedirs(model_data_path)
            return model_data_path
        else:
            raise Exception('已存在该路径')

    def write_file(self, file, data, file_format='txt'):
        with open(file, 'w', encoding='utf-8') as f:
            if file_format == 'txt':
                for line in data:
                    f.write(line)
                    f.write('\n')
            elif file_format == 'json':
                for line in data:
                    line_json = json.loads(line)
                    f.write(line_json)
                    f.write('\n')
        return

    def train_model(self):
        train_precision = dict()
        test_precision = dict()
        for i in range(self.k):
            _model = "{}_model_{}".format(self.cg, i+1)
            data_path = os.path.join(self._datadir, _model)
            model_path = os.path.join(data_path, _model)
            train_data_path = os.path.join(data_path, 'data', 'train.txt')
            test_data_path = os.path.join(data_path, 'data', 'test.txt')
            test_check_path = os.path.join(data_path, 'data', 'test_check.json')
            test_check_pred_path = os.path.join(data_path, 'data', 'test_check_pred.json')
            classifier = fasttext.supervised(train_data_path, model_path, label_prefix="__label__")
            train_pred = classifier.test(train_data_path)
            test_pred = classifier.test(test_data_path)
            train_precision["model_{}".format(i+1)] = train_pred.precision
            test_precision["model_{}".format(i+1)] = test_pred.precision
            print("在训练集{}上的准确率：\n{}".format(_model, train_pred.precision))
            print("在测试集{}上的准确率：\n{}".format(_model, test_pred.precision))
            self._predict(classifier, test_check_path, test_check_pred_path)
            self.evaluate_model(test_check_pred_path, self._level, _model)
        return train_precision, test_precision

    def _predict(self, classifier, json_file, json_out_file):
        with open(json_file, 'r', encoding='utf-8') as jfile, \
                open(json_out_file, 'w', encoding='utf-8') as joutfile:
            lines = jfile.readlines()
            for line in lines:
                _data = self._preline(line)
                labels = classifier.predict_proba([_data])
                line['predict_{}'.format(self._level)] = idx_label_map[labels[0][0][0].replace("'", "").replace("__label__", "")]
                # print(line['predict_top_category'])
                line['predict_{}_proba'.format(self._level)] = labels[0][0][1]
                joutfile.write(json.dumps(line) + "\n")


    def evaluate_model(self, datapath, model_level, model_num):
        return evaluate_model(datapath, model_level, model_num)

    def _get_label(self):
        pass

    def _parse_html(self, html):
        # TODO:解析html内容
        pass

if __name__ == '__main__':
    dataDir = "/data/zoushuai/news_content/sub_classification_model/national"
    sub_model = SubCategoryModel(dataDir, category='national', k=5, model_level='two_level')
    train_precision, test_precision = sub_model.train_model()