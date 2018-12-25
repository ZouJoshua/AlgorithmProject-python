# -*- coding: utf8 -*-

import json
import random
import fasttext
from pyquery import PyQuery
import re
import os
import logging
import sys


def clean_string(text):
    # 清洗html标签
    doc = PyQuery(text)
    text = doc.text()
    # 去除网址和邮箱
    text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ").replace("&#13;", " ").lower()
    url_list = re.findall(r'http://[a-zA-Z0-9.?/&=:]*', text)
    for url in url_list:
        text = text.replace(url, " ")
    email_list = re.findall(r"[\w\d\.-_]+(?=\@)", text)
    for email in email_list:
        text = text.replace(email, " ")
    # 去除诡异的标点符号
    cleaned_text = ""
    for c in text:
        if (ord(c) >= 32 and ord(c) <= 236):
            if c.isalpha():
                cleaned_text += c
            else:
                cleaned_text += " "
    return cleaned_text

# 制作label映射map
label_idx_map = {"entertainment": "1", "sport": "2", "national": "3", "international": "4", "business": "6",
                 "lifestyle": "8", "tech": "10", "auto": "10", "science": "10"}
idx_label_map = {"1": "entertainment", "2": "sport", "3": "national", "4": "international", "6": "business", "8": "lifestyle",
                 "10": "tech or science or auto"}

'''labelPath = "/Volumes/Katherine_Cai/NLP/apus/real_data/app_classification/app_label.csv"
reader = csv.DictReader(open(labelPath, "r"))
idx = 1
for row in reader:
    label = row['category']
    if label not in label_idx_map:
        label_idx_map[label] = idx
        idx += 1
print(label_idx_map)'''


class_cnt_map = {}
trainingDir = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/clean_data"
train_data_path = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/top_training_data_content+title"
test_data_path = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/top_test_data_content+title"
test_data_json_path = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/top_test_data_content+title_json"
test_data_json_path1 = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/top_test_data_content+title_json2"
model_path = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/ft_model_top_content+title"
'''
trainingPath = "/Volumes/Katherine_Cai/NLP/apus/real_data/app_training_data"
train_data_path = "/Volumes/Katherine_Cai/NLP/apus/real_data/app_classification/main_training_data"
test_data_path = "/Volumes/Katherine_Cai/NLP/apus/real_data/app_classification/main_test_data"
model_path = "/Volumes/Katherine_Cai/NLP/apus/real_data/app_classification/ft_model_main"
'''

fnames = os.listdir(trainingDir)
fnames.remove('.DS_Store')
for fname in fnames:
    with open(os.path.join(trainingDir, fname),  "r") as input_f, open(train_data_path, "a") as train_f, open(test_data_path, "a") as test_f, open(test_data_json_path, "a") as test_json_f:
        lines = input_f.readlines()
        # random.shuffle(lines)
        for line in lines:
            try:
                line = json.loads(line)
                label = str(label_idx_map[line['top_category'].strip()])
                desc = clean_string(line["content"].lower())  # 清洗数据

            # 统计各个类别的样本数，分出训练集和测试集
                if label in class_cnt_map and desc != "":
                    class_cnt_map[label] += 1
                elif desc != "":
                    class_cnt_map[label] = 1

                if class_cnt_map[label] <= 100000 and desc != "":
                    new_text = desc + "\t__label__" + label
                    train_f.write(new_text + "\n")
                elif desc != "":
                    new_json = {}
                    new_json['url'] = line['url']
                    new_json['top_category'] = line['top_category']
                    new_text = desc + "\t__label__" + label
                    test_f.write(new_text + "\n")
                    test_json_f.write(json.dumps(new_json) + "\n")

                if label == '10' and class_cnt_map[label] <= 30000 and desc != "":
                    new_json = {}
                    new_json['url'] = line['url']
                    new_json['top_category'] = line['top_category']
                    new_text = desc + "\t__label__" + label
                    test_f.write(new_text + "\n")
                    test_json_f.write(json.dumps(new_json) + "\n")

            except:
                print(line)
                pass

# print(class_cnt_map)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# 训练模型
classifier = fasttext.supervised(train_data_path, model_path, label_prefix="__label__")
# 测试模型
classifier = fasttext.load_model('/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/ft_model_top_content+title.bin')
result1 = classifier.test(test_data_path)
result = classifier.test(train_data_path)
print("在测试集上的准确率：")
print(result1.precision)

print("在训练集上的准确率：")
print(result.precision)

content_list = []
with open(test_data_path, "r") as test:
    for line in test.readlines():
        content = line.split("\t__label__")[0]
        content_list.append(content)

labels = classifier.predict_proba(content_list)

with open(test_data_json_path, 'r') as test_json_f, open(test_data_json_path1, "a") as test_json_f1:
    lines = test_json_f.readlines()

    for line, label in zip(lines, labels):
        line = json.loads(line)
        line['predict_top_category'] = idx_label_map[label[0][0].replace("'", "").replace("__label__", "")]
        line['predict_top_category_proba'] = label[0][1]
        test_json_f1.write(json.dumps(line) + "\n")
