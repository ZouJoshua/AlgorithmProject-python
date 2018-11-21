#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/11/9 10:04
@File    : news_lda_bak.py
@Desc    : 
"""

import os
import sys
import numpy as np
import matplotlib
import scipy
import matplotlib.pyplot as plt
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer

import json

def get_content(filepath):
    _content = []
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[:2000]:
            d = json.loads(line)
            text = d['html']
            _content.append(text.strip())
    return _content

if __name__ == "__main__":


    # 存储读取语料 一行语料为一个文档
    filepath = r'C:\Users\zoushuai\Desktop\new1_json\part-00000'
    corpus = get_content(filepath)
    print(corpus[:10])

    # 将文本中的词语转换为词频矩阵 矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()
    print(vectorizer)

    X = vectorizer.fit_transform(corpus)
    analyze = vectorizer.build_analyzer()
    weight = X.toarray()

    print(len(weight))
    print(weight[:5, :5])

    # LDA算法
    print('LDA:')
    import numpy as np
    import lda
    import lda.datasets

    model = lda.LDA(n_topics=2, n_iter=500, random_state=1)
    model.fit(np.asarray(weight))  # model.fit_transform(X) is also available
    topic_word = model.topic_word_  # model.components_ also works

    # 文档-主题（Document-Topic）分布
    doc_topic = model.doc_topic_
    print("type(doc_topic): {}".format(type(doc_topic)))
    print("shape: {}".format(doc_topic.shape))

    # 输出前10篇文章最可能的Topic
    label = []
    for n in range(10):
        topic_most_pr = doc_topic[n].argmax()
        label.append(topic_most_pr)
        print("doc: {} topic: {}".format(n, topic_most_pr))

    # 计算文档主题分布图
    import matplotlib.pyplot as plt

    f, ax = plt.subplots(6, 1, figsize=(8, 8), sharex=True)
    for i, k in enumerate([0, 1, 2, 3, 8, 9]):
        ax[i].stem(doc_topic[k, :], linefmt='r-',
                   markerfmt='ro', basefmt='w-')
        ax[i].set_xlim(-1, 2)  # x坐标下标
        ax[i].set_ylim(0, 1.2)  # y坐标下标
        ax[i].set_ylabel("Prob")
        ax[i].set_title("Document {}".format(k))
    ax[5].set_xlabel("Topic")
    plt.tight_layout()
    plt.show()

    # import matplotlib.pyplot as plt
    # f, ax = plt.subplots(2, 1, figsize=(6, 6), sharex=True)
    # for i, k in enumerate([0, 1]):  # 两个主题
    #     ax[i].stem(topic_word[k, :], linefmt='b-',
    #                markerfmt='bo', basefmt='w-')
    #     ax[i].set_xlim(-2, 20)
    #     ax[i].set_ylim(0, 1)
    #     ax[i].set_ylabel("Prob")
    #     ax[i].set_title("topic {}".format(k))
    #
    # ax[1].set_xlabel("word")
    #
    # plt.tight_layout()
    # plt.show()

    # 计算TFIDF
    corpus = []

    # 读取预料 一行预料为一个文档
    for line in open('test.txt', 'r').readlines():
        # print line
        corpus.append(line.strip())
    # print corpus

    # 将文本中的词语转换为词频矩阵 矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()

    # 该类会统计每个词语的tf-idf权值
    transformer = TfidfTransformer()

    # 第一个fit_transform是计算tf-idf 第二个fit_transform是将文本转为词频矩阵
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))

    # 获取词袋模型中的所有词语
    word = vectorizer.get_feature_names()

    # 将tf-idf矩阵抽取出来，元素w[i][j]表示j词在i类文本中的tf-idf权重
    weight = tfidf.toarray()

    # 打印特征向量文本内容
    print('Features length: ' + str(len(word)))
    for j in range(len(word)):
        print(word[j])

    # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个遍历某一类文本下的词语权重
    for i in range(len(weight)):
        for j in range(len(word)):
            print(weight[i][j])
        print('\n')

    # 存储读取语料 一行预料为一个文档
    corpus = []
    for line in open('test.txt', 'r').readlines():
        # print line
        corpus.append(line.strip())
    # print corpus

    # 将文本中的词语转换为词频矩阵 矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()

    # fit_transform是将文本转为词频矩阵
    X = vectorizer.fit_transform(corpus)

    # 获取词袋模型中的所有词语
    word = vectorizer.get_feature_names()
    analyze = vectorizer.build_analyzer()
    weight = X.toarray()

    # 打印特征向量文本内容
    print('Features length: ' + str(len(word)))
    for j in range(len(word)):
        print(word[j])

    # 打印每类文本词频矩阵
    print('TF Weight: ')
    for i in range(len(weight)):
        for j in range(len(word)):
            print(weight[i][j])
        print('\n')

    print(len(weight))
    print(weight[:5, :5])

    # LDA算法
    print('LDA:')
    import numpy as np
    import lda
    import lda.datasets

    model = lda.LDA(n_topics=2, n_iter=500, random_state=1)
    model.fit(np.asarray(weight))  # model.fit_transform(X) is also available
    topic_word = model.topic_word_  # model.components_ also works

    # 输出主题中的TopN关键词
    word = vectorizer.get_feature_names()
    for w in word:
        print(w)
    print(topic_word[:, :3])
    n = 5
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(word)[np.argsort(topic_dist)][:-(n + 1):-1]
        print(u'*Topic {}\n- {}'.format(i, ' '.join(topic_words)))

        # 文档-主题（Document-Topic）分布
    doc_topic = model.doc_topic_
    print("type(doc_topic): {}".format(type(doc_topic)))
    print("shape: {}".format(doc_topic.shape))