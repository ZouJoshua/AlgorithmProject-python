#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/1/17 17:32
@File    : nlp_subcategory.py
@Desc    : 
"""

import fasttext
from fasttext.model import SupervisedModel
from pyquery import PyQuery
from sklearn.externals import joblib
import numpy as np
import json
import re
import os


class SubCategoryProccesser:

    # 全模型用于清洗正文数据
    def clean_string(self, text):
        # 清洗html标签
        doc = PyQuery(text)
        text = doc.text()
        # 去除网址和邮箱
        text = text.replace("\n", "").replace("\t", "").replace("\r", "").replace("&#13;", "").lower()
        url_list = re.findall(r'http://[a-zA-Z0-9.?/&=:]*', text)
        for url in url_list:
            text = text.replace(url, "")
        email_list = re.findall(r"[\w\d\.-_]+(?=\@)", text)
        for email in email_list:
            text = text.replace(email, "")
        # 去除诡异的标点符号
        cleaned_text = ""
        for c in text:
            if (ord(c) >= 65 and ord(c) <= 126) or (ord(c) >= 32 and ord(c) <= 63):
                cleaned_text += c
        return cleaned_text

    # 用于加载模型和ID的映射关系，path为本地模型所在文件夹路径,文件名是固定的直接拼接
    def load_models_and_idmap(self, path):
        topcategory_list = ["international", "national", "sports", "tech", "business", "science", "auto", "lifestyle", "entertainment"]
        classifier_dict = dict()
        for topcategory in topcategory_list:
            model_path = path + "{}_sub_classification_model.bin".format(topcategory)
            if os.path.exists(model_path):
                classifier = fasttext.load_model(model_path)
                classifier_dict[topcategory] = classifier
            continue
        idx2labelmap_path = path + "subcategory_idx2label_map.json"
        with open(idx2labelmap_path, "r") as f:
            idx2label_map = json.loads(f.readlines()[0])

        return classifier_dict, idx2label_map

    # 用于线上预测，输入：文章正文 输出json如：
    # {
    #   "top_category": {
    #     "sports": 0.35,
    #     "bussiness": 0.65
    #   }
    # }
    def _predict(self, content_list, classifier, idx2label):
        try:
            predict_res = {}
            label = classifier.predict_proba(content_list)
            predict_res['sub_category_id'] = int(label[0][0][0].replace("__label__", ""))
            category = idx2label[label[0][0][0].replace("__label__", "")]
            predict_res['sub_category'] = category
            predict_res['sub_category_proba'] = label[0][0][1]
            return predict_res
        except Exception as e:
            print(e)

    # 目前已有6个模型，world、lifestyle的样本还在标注，没有的模型二级分类会返回空dict
    def predict(self, content, title, classifier_dict, idx2label, predict_top_category):
        content_list = []
        content_list.append(self.clean_string(title + '.' + content))
        if predict_top_category in classifier_dict:
            classifier = classifier_dict[predict_top_category]
            # assert isinstance(classifier, SupervisedModel):
            predict_res = self._predict(content_list, classifier, idx2label)
        else:
            predict_res = dict()
        return predict_res

