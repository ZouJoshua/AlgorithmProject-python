#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 18-11-25 下午10:19
@File    : lightlda_get_topic.py
@Desc    : 

"""

"""
从lightlda获取topic结果
"""

class LDAResult:

    def __init__(self, alpha=0.01, beta=0.1, topic_num=100, vocab_num=1000000, doc_num=100000):
        self.a = alpha  # 主题分布Dirichlet分布参数
        self.b = beta  # 词分布Dirichlet分布参数
        self.k = topic_num  # 主题数目
        self.n = vocab_num  # 词数目
        self.d = doc_num  # 文档数目
        # self.dt = doc_topic_mat  # 二维数组, 文档_主题概率矩阵[topic_num][doc_num]
        # self.tv = topic_vocab_mat  # 二维数组, 主题_词概率矩阵[vocab_num][topic_num]
        # self.dw = doc_word_info  # 二维数组, 每个文档的topN个词的信息矩阵[doc_num][n]
        # self.tw = topic_word_info  # 二维数组, 每个主题的topN个词的信息矩阵[topic_num][n]

    def result(self):
        pass

    # 得到所有词
    @staticmethod
    def loadVocabs(ori_path):
        out = []
        with open(ori_path,"r") as f:
            lines = f.readlines()
            for line in lines:
                out.append(line.strip())
        return out

    # 得到主题-词概率分布
    def loadTopicWordModel(self,topic_word_path, topic_summary):
        pass

    # 得到文档-主题概率分布
    def loadDocTopicModel(self, doc_topic_path):
        pass

    # 每个主题的前10个关键词写入到output_topic_topn_words中
    def dump_topic_topn_words(self,output_topic_topn_words,topn=20):
        pass


if __name__ == "__main__":


    doc_topic_path = "doc_topic.0"
    topic_word_path = "server_0_table_0.model"
    topic_summary = "server_0_table_1.model"
    ori_word_path = "vocab.news.txt"
    output_doc_topn_words = "doc.topn"
    output_topic_topn_words = "topic.topn"

    # lda = LDAResult(alpha=0.1 , beta=0.01 , topic_num=500 , vocab_num=1479643 , doc_num=26893850)
    # lda.loadVocabs(ori_word_path)
    # print("加载完毕!")
    # lda.loadTopicWordModel(topic_word_path, topic_summary)
    # lda.loadDocTopicModel(doc_topic_path)
    # lda.dump_topic_topn_words(output_topic_topn_words, 10)

    def loadVocabs(ori_path):
        out = []
        with open(ori_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                out.append(line.strip("\n"))
        return out
    out = loadVocabs(ori_word_path)
    print(len(out))
    print(out[:10])