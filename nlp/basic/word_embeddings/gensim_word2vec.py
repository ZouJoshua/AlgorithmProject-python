# -*- coding: utf-8 -*-
"""使用gensim训练词向量"""
import os
import json
from util import clean_string
from gensim.models import word2vec
from pyquery import PyQuery
import numpy as np

dataDir = "/data/caifuli/news_classification/data/recent_news/data"
docVectorPath = "/data/caifuli/news_classification/recent_news/doc_vector"
wordVectorPath = "/data/caifuli/news_classification/recent_news/gensim_title+content_word2vec"
modelPath = "/data/caifuli/news_classification/recent_news/gensim_word2vec_model"


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


sentences = generate_sentences(dataDir)
model = word2vec.Word2Vec(sentences, size=300)  # 默认训练词向量的时候把频次小于5的单词从词汇表中剔除掉
model.save(modelPath)
model.wv.save_word2vec_format(wordVectorPath + ".bin", binary=True)
# print(model.most_similar("word"))


fnames = os.listdir(dataDir)
# fnames.remove(".DS_Store")
for fname in fnames:
    with open(os.path.join(dataDir, fname), "r") as input_f, open(docVectorPath, "a") as doc2vec_f:
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
