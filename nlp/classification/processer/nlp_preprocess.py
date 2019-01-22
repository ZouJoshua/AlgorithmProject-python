# 大数据需要提供一个version文件用于存放最新模型文件的文件夹路径，一旦有模型更新，则更新version文件
# 线上会定时轮训version文件，如果version文件有变动，加载新的模型
# 另外提供一个文件用于ID和存储文本的映射关系，Json格式如：{"11":"sports","22":"basketball"}

import fasttext
from pyquery import PyQuery
import json
import re
import os


class ClassificationProccesser:

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
        topcategory_list = ["international", "national", "sports", "technology", "business", "science", "auto", "lifestyle", "entertainment"]
        classifier_dict = dict()
        # 加载一级模型
        topcategory_model_path = os.path.join(path, 'top_content_model.bin')
        topcategory_classifier = fasttext.load_model(topcategory_model_path)
        classifier_dict['topcategory_model'] = topcategory_classifier
        topcategory_auto_science_model_path = os.path.join(path, 'top_auto_science_model.bin')
        auto_science_classifier = fasttext.load_model(topcategory_auto_science_model_path)
        classifier_dict['auto_science'] = auto_science_classifier
        # 加载二级模型
        for topcategory in topcategory_list:
            model_path = os.path.join(path, "{}_sub_classification_model.bin".format(topcategory))
            if os.path.exists(model_path):
                classifier = fasttext.load_model(model_path)
                classifier_dict[topcategory] = classifier
            continue
        idx2labelmap_path = os.path.join(path, "idx2label_map.json")
        with open(idx2labelmap_path, "r") as load_f:
            idx2label_map = json.load(load_f)

        return classifier_dict, idx2label_map

    # 用于线上预测，输入：文章正文 输出json如：
    # {
    #   "top_category":  "sports",
    #   "top_category_id": 6,
    #   "top_category_proba": 0.6,
    #   "sub_category": "basketball",
    #   "sub_category_id": 613,
    #   "sub_category_proba": 0.83
    #  }

    # 一级分类模型2个模型，auto_science独立一个模型
    # 二级分类模型目前已有6个模型，world、lifestyle的样本还在标注，没有的模型二级分类会返回一级预测结果
    # 先进行一级预测，预测结果后对二级分类进行预测
    def predict(self, content, title, classifier_dict, idx2label):
        content_list = []
        content_list.append(self.clean_string(title + '.' + content))
        predict_top_res = self._predict_topcategory(content_list, classifier_dict, idx2label)
        predict_top_category = predict_top_res['top_category']
        if predict_top_category in classifier_dict:
            classifier = classifier_dict[predict_top_category]
            # assert isinstance(classifier, SupervisedModel):
            predict_sub_res = self._predict_subcategory(content_list, classifier, idx2label, predict_top_res)
        else:
            predict_sub_res = predict_top_res
        return predict_sub_res

    def _predict_topcategory(self, content_list, classifier_dict, idx2label):
        try:
            predict_res = dict()
            classifier = classifier_dict['topcategory_model']
            label = classifier.predict_proba(content_list)
            predict_res['top_category_id'] = int(label[0][0][0].replace("__label__", ""))
            category = idx2label['topcategory'][label[0][0][0].replace("__label__", "")]
            predict_res['top_category'] = category
            predict_res['top_category_proba'] = label[0][0][1]
            if category == 'auto or science':
                auto_science_classifier = classifier_dict['auto_science']
                label = auto_science_classifier.predict_proba(content_list)
                predict_res['top_category_id'] = int(label[0][0][0].replace("__label__", ""))
                predict_res['top_category'] = idx2label['topcategory'][label[0][0][0].replace("__label__", "")]
                predict_res['top_category_proba'] = label[0][0][1]
            return predict_res
        except Exception as e:
            print(e)

    def _predict_subcategory(self, content_list, classifier, idx2label, predict_res):
        try:
            label = classifier.predict_proba(content_list)
            if predict_res:
                predict_sub_res = predict_res
            else:
                predict_sub_res = dict()
            predict_sub_res['sub_category_id'] = int(label[0][0][0].replace("__label__", ""))
            category = idx2label['subcategory'][label[0][0][0].replace("__label__", "")]
            predict_sub_res['sub_category'] = category
            predict_sub_res['sub_category_proba'] = label[0][0][1]
            return predict_sub_res
        except Exception as e:
            print(e)



