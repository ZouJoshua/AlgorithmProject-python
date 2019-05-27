#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-5-23 下午12:28
@File    : en_news_emotion_pretrain_process.py
@Desc    : 印度英语情感分析embedding预处理
"""

import os
import json

def read_json_format_file(file):
    print(">>>>> 正在读原始取数据文件：{}".format(file))
    with open(file, 'r') as f:
        while True:
            _line = f.readline()
            if not _line:
                break
            else:
                line = json.loads(_line.strip())
                yield line


data_dir = "/data/emotion_analysis"
file1 = os.path.join(data_dir, "emotion_region_taste_timeliness_text")
file2 = os.path.join(data_dir, "sub_category_text")
embed_text = os.path.join(data_dir, "en_news_embed_text")
out_f = open(embed_text, 'w')
lines1 = read_json_format_file(file1)
for line in lines1:
    new_line = dict()
    new_line["id"] = line["id"]
    new_line["title"] = line["title"]
    new_line["content"] = line["text"]
    out_f.write(json.dumps(new_line) + "\n")
lines2 = read_json_format_file(file2)
for line in lines2:
    new_line = dict()
    new_line["id"] = line["article_id"]
    new_line["title"] = line["title"]
    new_line["content"] = line["content"]
    out_f.write(json.dumps(new_line) + "\n")

out_f.close()


