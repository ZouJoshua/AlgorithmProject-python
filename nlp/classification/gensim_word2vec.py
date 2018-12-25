# -*- coding: utf-8 -*-

import fasttext
import re
import os
import json
import logging
from gensim.models import word2vec
import numpy as np
from pyquery import PyQuery

dataDir = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/recent_news"
doc_vectorPath = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/recent_news/doc_vector"
dataPath = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/gensim_word2vec"
modelPath = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/gensim_word2vec_model"


def clean_string(text):
    text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ").replace("&#13;", " ").replace("\"", " ")
    url_list = re.findall(r'http://[a-zA-Z0-9.?/&=:]*', text)
    for url in url_list:
        text = text.replace(url, " ")
    email_list = re.findall(r"[\w\d\.-_]+(?=\@)", text)
    for email in email_list:
        text = text.replace(email, " ")
    # 去除诡异的标点符号
    cleaned_text = ""
    for c in text:
        if (ord(c) >= 32 and ord(c) <= 126):
            if c.isalpha():
                cleaned_text += c
            else:
                cleaned_text += " "
    return cleaned_text


def generate_sentences(dirname):
    fnames = os.listdir(dirname)
    fnames.remove('.DS_Store')
    sentences = []
    for fname in fnames:
        print(os.path.join(dirname, fname))
        with open(os.path.join(dirname, fname), "r") as f:
            for line in f.readlines():
                line = json.loads(line)
                title = line["title"].replace("\t", "").replace("\n", "").replace("\r", "")
                content = ""
                if "html" in line and line["html"].strip() != "":
                    content = line["html"].strip()
                if "content" in line and line["content"].strip() != "":
                    content = line["content"].strip()
                desc = title + content

                word_list = []
                for word in desc.split(" "):
                    if word.isalpha():
                        word_list.append(word.lower())
                # word_list = [word if word.isalpha() else pass for word in title.split(" ")]
                sentences.append(word_list)
    return sentences

sentences = generate_sentences(dataDir)
model = word2vec.Word2Vec(sentences, size=300)  # 默认训练词向量的时候把频次小于5的单词从词汇表中剔除掉
model.save("/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/gensim_word2vec_title+content_model")
model.wv.save_word2vec_format("title+content_word_vector.bin", binary=True)

# modelPath = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/gensim_word2vec_title+content_model"
model = word2vec.Word2Vec.load(modelPath)
# print(model.most_similar("model"))


# 对每篇文章生成vector
def generate_doc_word_list(text_json):
    title = text_json["title"].strip().replace("\t", "").replace("\n", "").replace("\r", "")
    html = PyQuery(text_json["html"]).text().strip()
    desc = title + ". " + html
    word_list = []
    for word in desc.split(" "):
        if word.isalpha():
            word_list.append(word.lower())
    return word_list

fnames = os.listdir(dataDir)
# fnames.remove(".DS_Store")
for fname in fnames:
    with open(os.path.join(dataDir, fname), "r") as input_f, open(doc_vectorPath, "a") as doc2vec_f:
        for line in input_f.readlines():
            line = json.loads(line)
            word_list = generate_doc_word_list(line)
            doc_length = len(word_list)

            doc_vec_matrix = np.zeros(300)
            for word in word_list:
                if word in model:
                    word_vec = model[word]
                else:
                    continue
                doc_vec_matrix = np.row_stack((doc_vec_matrix, word_vec))
            doc_vec = doc_vec_matrix.sum(axis=0)/[doc_length]
            line["doc_vec"] = doc_vec.tolist()
            doc2vec_f.write(json.dumps(line) + "\n")
