#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-6-4 下午5:34
@File    : multi_country_news_preprocess.py
@Desc    : 多国家新闻预处理
"""


import json
import random
import requests
import langid

class DataPreprocess(object):


    def __init__(self, raw_data_path, predict_data_file):
        self.raw_path = raw_data_path
        self.predict_file = predict_data_file
        self.split_predict_data(self.raw_path, self.predict_file)

    def read_json_format_file(self, file):
        print(">>>>> 正在读原始取数据文件：{}".format(file))
        with open(file, 'r') as f:
            while True:
                _line = f.readline()
                if not _line:
                    break
                else:
                    line = json.loads(_line.strip())
                    yield line

    def write_json_format_file(self, source_data, file):
        """
        写每行为json格式的文件
        :param source_data:
        :param file:
        :return:
        """
        print(">>>>> 正在写入目标数据文件：{}".format(file))
        _count = 0
        f = open(file, "w")
        for _line in source_data:
            _count += 1
            if _count % 100000 == 0:
                print("<<<<< 已写入{}行".format(_count))
            if isinstance(_line, dict):
                line = json.dumps(_line, ensure_ascii=False)
                f.write(line + "\n")
            elif isinstance(_line, str):
                f.write(_line + "\n")
        f.close()


    def split_predict_data(self, path, outpath):
        _country = dict()
        source_data = list()
        lines = [i for i in self.read_json_format_file(path)]
        random.shuffle(lines)
        for line in lines:
            country = line["country"]
            if country in _country.keys():
                if _country[country] > 100:
                    continue
                else:
                    lang = langid.classify(line['title'])[0]
                    if lang == 'en':
                        _country[country] += 1
                        source_data.append(line)
                    else:
                        print(line['title'])
            else:
                _country[country] = 1
                source_data.append(line)
        # random.shuffle(source_data)
        self.write_json_format_file(source_data, outpath)


class Predict(object):

    def __init__(self, url, source_file, target_file):
        self.url = url
        self.sf = source_file
        self.tf = target_file

    def read_json_format_file(self, file):
        print(">>>>> 正在读原始取数据文件：{}".format(file))
        with open(file, 'r') as f:
            while True:
                _line = f.readline()
                if not _line:
                    break
                else:
                    line = json.loads(_line.strip())
                    yield line


    def predict(self):

        f = open(self.tf, 'w')

        for line in self.read_json_format_file(self.sf):
            title = line["title"]
            content = line["content"]
            parms = {"title": title, "content": content, "thresholds": 0.3}
            _res = requests.post(self.url, data=parms)  # 发送请求
            result = json.loads(_res.text)
            # print(result)
            top = result["result"]["top_category"][0]["category"]
            proba = result["result"]["top_category"][0]["proba"]
            line["predict_top_category"] = top
            line["predict_proba"] = proba
            f.write(json.dumps(line) + "\n")
        f.close()

class ResultCheck(object):

    def __init__(self,result_file):
        self.file = result_file
        self.get_result()

    def get_result(self):
        out_dict = dict()
        with open(self.file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            l_dict = json.loads(line.strip())
            is_right = l_dict["is_right"]
            category = l_dict["category"]
            country = l_dict["country"]
            if country in out_dict.keys():
                out_dict[country]["totle"] += 1
                if category in out_dict[country].keys():
                    if is_right == "y":
                        out_dict[country][category] += 1
                    else:
                        out_dict[country][category + "_wrong"] += 1
                else:
                    out_dict[country][category] = 0
                    out_dict[country][category + "_wrong"] = 0
                    if is_right == "y":
                        out_dict[country][category] = 1
                    else:
                        out_dict[country][category + "_wrong"] += 1
            else:
                out_dict[country] = dict()
                out_dict[country]["totle"] = 1
                out_dict[country][category] = 0
                out_dict[country][category+"_wrong"] = 0
                if is_right == 'y':
                    out_dict[country][category] = 1
                else:
                    out_dict[country][category + "_wrong"] = 1

        print(json.dumps(out_dict, indent=4))


if __name__ == '__main__':
    raw_data_path = "/data/multi_country_news/raw_train_data"
    predict_data_file = "/data/multi_country_news/raw_test_example"
    out_file = "/data/multi_country_news/raw_test_example_predict"
    result_file = "/data/multi_country_news/predict_check_result"
    # DataPreprocess(raw_data_path, predict_data_file)
    # url = 'http://127.0.0.1:19901/nlp_category/category'
    # p = Predict(url, predict_data_file, out_file)
    # p.predict()
    ResultCheck(result_file)