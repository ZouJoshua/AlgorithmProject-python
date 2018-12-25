# -*- coding: utf-8 -*-
"""训练词向量"""
import fasttext
import re
import os
import json
import logging

trainingDir = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/datasets_not_null"
train_data_path = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/ft_word2vec"


def clean_string(text):
    # 清洗html标签
    # doc = PyQuery(text)
    # text = doc.text()
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
label_idx_map = {"entertainment": "15", "sports": "6", "sport": "6", "national": "4", "international": "3", "world": "3", "business": "8",
                 "lifestyle": "12", "technology": "10", "tech": "10", "auto": "7", "science": "7"}
idx_label_map = {"3": "international", "4": "national", "6": "sports", "8": "business", "10": "technology",
                 "7": "auto or science", "12": "lifestyle", "15": "entertainment"}
class_cnt_map = {}
fnames = os.listdir(trainingDir)
fnames.remove('.DS_Store')
for fname in fnames:
    with open(os.path.join(trainingDir, fname),  "r") as input_f, open(train_data_path, "a") as train_f:
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
                        content = line["html"]
                    elif "content" in line:
                        content = line["content"]
                    desc = clean_string((title + content).lower())  # 清洗数据
                    new_line = desc + "\t" + "__label__" + label
                    train_f.write(new_line + "\n")

            except:
                print(line)
                pass

print(class_cnt_map)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

model = fasttext.skipgram(train_data_path, "w2vmodel", dim=300)


