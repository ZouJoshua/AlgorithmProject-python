#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/1/10 15:17
@File    : sub_category_model_v1.py
@Desc    : 尝试以两个模型训练
"""



import os
from os.path import dirname
import sys
root_path = dirname(dirname(dirname(dirname(os.path.realpath(__file__)))))
class_path = dirname(dirname(os.path.realpath(__file__)))
sys.path.append(root_path)
sys.path.append(dirname(class_path))


import json
import fasttext
from pyquery import PyQuery
from nlp.classification.preprocess.util import clean_string
from nlp.classification.model_evaluate.calculate_p_r_f import evaluate_model
from sklearn.model_selection import KFold, StratifiedKFold
import time



class SubCategoryModel(object):

    def __init__(self, dataDir, category='national', k=5, model_level='two_level'):
        self._level = model_level
        self.cg = category
        self.k = k
        if os.path.exists(dataDir) and os.path.isdir(dataDir):
            self._datadir = dataDir
        else:
            raise Exception('数据路径不存在，请检查路径')
        self.label_idx_map, self.idx_label_map = self._get_label(os.path.join(class_path, 'model_label_map', 'label_idx_map.json'))

    def preprocess_data(self):
        fnames = os.listdir(self._datadir)
        datafiles = [os.path.join(self._datadir, fname) for fname in fnames]
        data_all = list()
        class_cnt = dict()
        s = time.time()
        for datafile in datafiles:
            dataf = open(datafile, 'r', encoding='utf-8')
            data = dataf.readlines()
            # random.shuffle(data)
            # data_count = len(data)
            for li in data:
                line = li.strip('\n')
                title, content, dataY = self._preline(line).split("\t__label__")
                label = self.idx_label_map[dataY]
                if label in class_cnt and title != "" and content != "":
                    class_cnt[label] += 1
                elif title != "" and content != "":
                    class_cnt[label] = 1
                data_all.append(line)
            dataf.close()
        e = time.time()
        print('数据分类耗时：\n{}'.format(e - s))
        print('所有数据分类情况:\n{}'.format(class_cnt))
        self._generate_kfold_data(data_all)
        return

    def _preline(self, line):
        line_json = json.loads(line)
        title = line_json["title"]
        content = ""
        dataY = str(self.label_idx_map[line_json[self._level].strip().lower()])
        if "content" in line_json:
            content = line_json["content"]
        elif "html" in line_json:
            content = self._parse_html(line_json["html"])
        title_dataX = clean_string((title).lower())
        content_dataX = clean_string((content).lower())  # 清洗数据
        _data = title_dataX + "\t__label__" + content_dataX + "\t__label__" + dataY
        return _data

    def _preline_type(self, line, model_type="title"):
        line_json = json.loads(line)
        dataY = str(self.label_idx_map[line_json[self._level].strip().lower()])
        content = ""
        if "content" in line_json:
            content = line_json["content"]
        elif "html" in line_json:
            content = self._parse_html(line_json["html"])
        title = line_json['title']
        title_dataX = clean_string((title).lower())
        _title = title_dataX + "\t__label__" + dataY
        content_dataX = clean_string((content).lower())  # 清洗数据
        _content = content_dataX + "\t__label__" + dataY
        if model_type == 'title':
            return _title
        elif model_type == 'content':
            return _content
        else:
            dataX = clean_string((title + '.' + content).lower())  # 清洗数据
            _data = dataX + "\t__label__" + dataY
            return _data


    def _generate_kfold_data(self, data_all):
        """
        分层k折交叉验证
        :param train_format_data:
        :return:
        """
        s = time.time()
        titleX = [self._preline(i).split('\t__label__')[0] for i in data_all]
        Y = [self._preline(i).split('\t__label__')[2] for i in data_all]
        e1 = time.time()
        print('数据分X\Y耗时{}'.format(e1 - s))
        skf = StratifiedKFold(n_splits=self.k)
        i = 0
        for train_index, test_index in skf.split(titleX, Y):
            i += 1
            e2 = time.time()
            train_label_count = self._label_count([self.idx_label_map[Y[i]] for i in train_index])
            test_label_count = self._label_count([self.idx_label_map[Y[j]] for j in test_index])
            title_train_data = [self._preline_type(data_all[i], model_type='title') for i in train_index]
            title_test_data = [self._preline_type(data_all[j], model_type='title') for j in test_index]
            content_train_data = [self._preline_type(data_all[i], model_type='content') for i in train_index]
            content_test_data = [self._preline_type(data_all[j], model_type='content') for j in test_index]
            train_check = [data_all[i] for i in train_index]
            test_check = [data_all[i] for i in test_index]
            e3 = time.time()
            print('数据分训练集、测试集耗时{}'.format(e3 - e2))
            model_data_path = self._mkdir_path(i)
            title_train_file = os.path.join(model_data_path, 'title_train.txt')
            title_test_file = os.path.join(model_data_path, 'title_test.txt')
            content_train_file = os.path.join(model_data_path, 'content_train.txt')
            content_test_file = os.path.join(model_data_path, 'content_test.txt')
            train_check_file = os.path.join(model_data_path, 'train_check.json')
            test_check_file = os.path.join(model_data_path, 'test_check.json')
            self.write_file(title_train_file, title_train_data, 'txt')
            self.write_file(title_test_file, title_test_data, 'txt')
            self.write_file(content_train_file, content_train_data, 'txt')
            self.write_file(content_test_file, content_test_data, 'txt')
            self.write_file(train_check_file, train_check, 'json')
            self.write_file(test_check_file, test_check, 'json')
            print('文件:{}\n训练数据类别统计：{}'.format(title_train_file, train_label_count))
            print('文件:{}\n测试数据类别统计：{}'.format(title_test_file, test_label_count))

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
        s = time.time()
        with open(file, 'w', encoding='utf-8') as f:
            if file_format == 'txt':
                for line in data:
                    f.write(line)
                    f.write('\n')
            elif file_format == 'json':
                for line in data:
                    # line_json = json.dumps(line)
                    f.write(line)
                    f.write('\n')
        e = time.time()
        print('写文件耗时{}'.format(e -s))
        return

    def train_model(self):
        # self.preprocess_data()
        train_precision = dict()
        test_precision = dict()
        for i in range(self.k):
            s = time.time()
            _model = "{}_model_{}".format(self.cg, i+1)
            data_path = os.path.join(self._datadir, _model)
            model_path = os.path.join(data_path, '{}_sub_classification_model'.format(self.cg))
            title_train_data_path = os.path.join(data_path, 'data', 'title_train.txt')
            title_test_data_path = os.path.join(data_path, 'data', 'title_test.txt')
            content_train_data_path = os.path.join(data_path, 'data', 'content_train.txt')
            content_test_data_path = os.path.join(data_path, 'data', 'content_test.txt')
            train_check_path = os.path.join(data_path, 'data', 'train_check.json')
            test_check_path = os.path.join(data_path, 'data', 'test_check.json')
            title_train_check_pred_path = os.path.join(data_path, 'data', 'title_train_check_pred.json')
            title_test_check_pred_path = os.path.join(data_path, 'data', 'title_test_check_pred.json')
            content_train_check_pred_path = os.path.join(data_path, 'data', 'content_train_check_pred.json')
            content_test_check_pred_path = os.path.join(data_path, 'data', 'content_test_check_pred.json')
            title_classifier = fasttext.supervised(title_train_data_path, model_path, label_prefix="__label__", lr=0.1, epoch=20, dim=200)
            title_train_pred = title_classifier.test(title_train_data_path)
            title_test_pred = title_classifier.test(title_test_data_path)
            content_classifier = fasttext.supervised(content_train_data_path, model_path, label_prefix="__label__", lr=0.1, epoch=20, dim=200)
            content_train_pred = content_classifier.test(content_train_data_path)
            content_test_pred = content_classifier.test(content_test_data_path)
            train_precision["model_{}".format(i+1)] = title_train_pred.precision
            test_precision["model_{}".format(i+1)] = title_test_pred.precision
            print("在训练集{}上title模型的准确率：\n{}".format(_model, title_train_pred.precision))
            print("在测试集{}上title模型的准确率：\n{}".format(_model, title_test_pred.precision))
            print("在训练集{}上content模型的准确率：\n{}".format(_model, content_train_pred.precision))
            print("在测试集{}上content模型的准确率：\n{}".format(_model, content_test_pred.precision))
            e = time.time()
            print('训练模型耗时{}'.format(e - s))
            self._predict(title_classifier, train_check_path, title_train_check_pred_path, model='title')
            self._predict(title_classifier, test_check_path, title_test_check_pred_path, model='title')
            print('正在评估title模型>>>>>>>>>>')
            self.evaluate_model(title_test_check_pred_path, self._level, _model)
            self._predict(title_classifier, train_check_path, content_train_check_pred_path, model='content')
            self._predict(title_classifier, test_check_path, content_test_check_pred_path, model='content')
            print('正在评估model模型>>>>>>>>>>')
            self.evaluate_model(content_test_check_pred_path, self._level, _model)
        return train_precision, test_precision


    def _predict(self, classifier, json_file, json_out_file, model='title'):
        with open(json_file, 'r', encoding='utf-8') as jfile, \
                open(json_out_file, 'w', encoding='utf-8') as joutfile:
            s = time.time()
            lines = jfile.readlines()
            for line in lines:
                _line = json.loads(line)
                _data = self._preline_type(line, model_type=model)
                labels = classifier.predict_proba([_data])
                _line['predict_{}'.format(self._level)] = self.idx_label_map[labels[0][0][0].replace("'", "").replace("__label__", "")]
                # print(line['predict_top_category'])
                _line['predict_{}_proba'.format(self._level)] = labels[0][0][1]
                joutfile.write(json.dumps(_line) + "\n")
                del line
                del _line
            e = time.time()
            print('预测及写入文件耗时{}'.format(e - s))

    def evaluate_model(self, datapath, model_level, model_num):
        return evaluate_model(datapath, model_level, model_num)

    def _get_label(self, jsonfile):
        with open(jsonfile, 'r', encoding='utf-8') as jfile:
            line = json.load(jfile)
        if line[self._level][self.cg]:
            label_idx_map = line[self._level][self.cg]
        else:
            raise Exception('请检查 label 文件')
        idx_label_map = dict()
        for key, value in label_idx_map.items():
            if value in idx_label_map:
                idx_label_map[value] = '{}+{}'.format(idx_label_map[value], key)
            else:
                idx_label_map[value] = key
        return label_idx_map, idx_label_map

    def _parse_html(self, html):
        # TODO:解析html内容
        pass

if __name__ == '__main__':
    s = time.time()
    dataDir = "/data/zoushuai/news_content/sub_classification_model/national"
    sub_model = SubCategoryModel(dataDir, category='national', k=5, model_level='two_level')
    # sub_model.preprocess_data()
    train_precision, test_precision = sub_model.train_model()
    e = time.time()
    print('训练二级分类模型耗时{}'.format(e - s))