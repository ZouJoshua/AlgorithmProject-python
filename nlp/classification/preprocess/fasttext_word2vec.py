# -*- coding: utf-8 -*-
"""使用fasttext训练词向量"""
import fasttext
import os
import json
import logging
from util import clean_string

train_dataDir = "/data/caifuli/news_classification/data"
train_dataPath = "/data/caifuli/news_classification/fasttext_title+content_word2vec"

# 制作label映射map
label_idx_map = {"entertainment": "15", "sports": "6", "sport": "6", "national": "4", "international": "3", "world": "3",
                 "business": "8", "lifestyle": "12", "technology": "10", "tech": "10", "auto": "7", "science": "7"}


fnames = os.listdir(train_dataDir)
fnames.remove('.DS_Store')
for fname in fnames:
    with open(os.path.join(train_dataDir, fname),  "r") as input_f, open(train_dataPath, "a") as train_f:
        lines = input_f.readlines()
        # random.shuffle(lines)
        for line in lines:
            try:
                line = json.loads(line)
                title = line["title"]
                top_category = line["top_category"].strip().lower()
                content = ""
                if top_category in ['404', 'aoto']:
                    continue
                else:
                    label = str(label_idx_map[top_category])
                    if "html" in line:
                        content = line["html"].strip()
                    elif "content" in line:
                        content = line["content"].strip()
                    desc = clean_string((title + content).lower())  # 清洗数据
                    new_line = desc + "\t" + "__label__" + label
                    train_f.write(new_line + "\n")
            except:
                print(line)
                pass

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model = fasttext.skipgram(train_dataPath, "w2vmodel", dim=300)
