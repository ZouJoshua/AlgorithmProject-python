# 大数据需要提供一个version文件用于存放最新模型文件的文件夹路径，一旦有模型更新，则更新version文件
# 线上会定时轮训version文件，如果version文件有变动，加载新的模型
# 另外提供一个文件用于ID和存储文本的映射关系，Json格式如：{"11":"sports","22":"basketball"}

import fasttext
from pyquery import PyQuery
from sklearn.externals import joblib
import numpy as np
import json
import re
import base.logger as logging

class TopCategoryProccesser:

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
    def load(self, path):
        model_path = path + "top_content_model.bin"
        idx2labelmap_path = path + "idx2label_map.json"
        classifier = fasttext.load_model(model_path)
        idx2label_map = []
        with open(idx2labelmap_path, "r") as f:
            idx2label_map = json.loads(f.readlines()[0])
        if not idx2label_map:
            logging.logger.warning('id2label_map is null')
        return classifier, idx2label_map

    # 用于线上预测，输入：文章正文 输出json如：
    # {
    #   "top_category": {
    #     "sports": 0.35,
    #     "bussiness": 0.65
    #   }
    # }
    def predict(self, content, title, classifier, idx2label, path):  # path是存放auto_science那个模型的目录地址
        try:
            predict_res = {}
            content_list = []
            content_list.append(self.clean_string(title + content))
            label = classifier.predict_proba(content_list)
            predict_res['top_category_id'] = int(label[0][0][0].replace("'", "").replace("__label__", ""))
            predict_res['top_category'] = idx2label[label[0][0][0].replace("'", "").replace("__label__", "")]
            predict_res['top_category_proba'] = label[0][0][1]
            if predict_res['top_category'] == "auto or science":
                model_path = path + "/top_auto_science_model.bin"
                auto_science_classifier = fasttext.load_model(model_path)
                label = auto_science_classifier.predict_proba(content_list)
                auto_science_map = {"9": "science", "11": "auto"}
                predict_res['top_category'] = auto_science_map[label[0][0][0].replace("'", "").replace("__label__", "")]
                predict_res['top_category_id'] = int(label[0][0][0].replace("'", "").replace("__label__", ""))
                predict_res['top_category_proba'] = label[0][0][1]
            return predict_res
        except Exception as e:
            logging.logger.error('predict error msg:{}'.format(e))
