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

fnames = os.listdir(trainingDir)
for fname in fnames:
    with open(os.path.join(trainingDir, fname),  "r") as input_f, open(train_data_path, "a") as train_f, open(test_data_path, "a") as test_f, open(test_data_json_path, "a") as test_json_f:
        lines = input_f.readlines()
        # random.shuffle(lines)
        for line in lines:
            try:
                line = json.loads(line)
                title = line["title"]
                content = ""
                label = str(label_idx_map[line['two_level'].strip().lower()])
                if "html" in line:
                    content = line["html"]
                elif "content" in line:
                    content = line["content"]
                desc = clean_string((title + content).lower())  # 清洗数据

                # 统计各个类别的样本数，分出训练集和测试集
                if label in class_cnt_map and desc != "":
                    class_cnt_map[label] += 1
                elif desc != "":
                    class_cnt_map[label] = 1

                if class_cnt_map[label] <= 150000 and desc != "":
                    # pass
                    new_text = desc + "\t__label__" + label
                    train_f.write(new_text + "\n")
                elif desc != "":
                    new_text = desc + "\t__label__" + label
                    test_f.write(new_text + "\n")
                    test_json_f.write(json.dumps(line) + "\n")
            except:
                print("error")
                pass

# print(class_cnt_map)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# 训练模型
classifier = fasttext.supervised(train_data_path, model_path, label_prefix="__label__")
result1 = classifier.test(test_data_path)
result = classifier.test(train_data_path)
print("在测试集上的准确率：")
print(result1.precision)

print("在训练集上的准确率：")
print(result.precision)


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