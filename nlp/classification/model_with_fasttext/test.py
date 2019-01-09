#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/1/7 17:18
@File    : test.py
@Desc    : 
"""

import os
from os.path import dirname
import sys


root_path = dirname(dirname(dirname(os.path.realpath(__file__))))
class_path = dirname(dirname(os.path.realpath(__file__)))

print(root_path)
print(class_path)
# sys.path.append(root_path)
# sys.path.append(class_path)

from nlp.classification.model_evaluate import calculate_p_r_f
import json


file = r"D:\Work2018\github\AlgorithmProject-python\nlp\classification\model_label_map\label_idx_map.json"
with open(file, 'r', encoding='utf-8') as f:
    line = json.load(f)
    print(line)
    label_idx_map = line["two_level"]["national"]
idx_label_map = dict()
for key, value in label_idx_map.items():
    if value in idx_label_map:
        idx_label_map[value] = '{}+{}'.format(idx_label_map[value], key)
    else:
        idx_label_map[value] = key
print(idx_label_map)


train = '/data/zoushuai/news_content/sub_classification_model/national/national_model_1/data/train.txt'
test = '/data/zoushuai/news_content/sub_classification_model/national/national_model_1/data/test.txt'
a = [i*2 for i in range(50)]
a.remove(0)
for i in a:
    classifier = fasttext.supervised(train, "model", label_prefix="__label__", lr=0.1, epoch=i, dim=100)
    train_pred = classifier.test(train)
    test_pred = classifier.test(test)
    print(">>>>>>>>>>第{}次迭代".format(i))
    print("在训练集上的准确率：\t{}".format(train_pred.precision))
    print("在测试集上的准确率：\t{}".format(test_pred.precision))

