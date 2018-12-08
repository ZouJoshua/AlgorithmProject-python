#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 18-11-25 下午10:19
@File    : lightlda_get_result.py
@Desc    : 

"""

"""
从lightlda获取topic结果
"""


import numpy as np
import scipy.sparse as sparse

class LDAResult:

    def __init__(self, alpha, beta, topic_num, vocab_num, doc_num):
        self.a = alpha
        self.b = beta
        self.tn = topic_num
        self.vn = vocab_num
        self.dn = doc_num


    @staticmethod
    def loadVocabs(ori_path):
        """
        得到所有原始词
        :param ori_path: 词汇量文件
        :return: list
        """
        out = []
        with open(ori_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                out.append(line.strip())
        return out


    def loadDocTopicModel(self, doc_topic_path):
        """
        得到文档-主题概率分布,得到每篇文章的所属主题（top3）
        :param doc_topic_path: lightlda 模型生成的doc_topic.0文件
        :return: doc_topic_mat[topic_id][doc_id] = topic_cnt
        """
        result = []
        with open(doc_topic_path, 'r', encoding='utf-8') as f:
            row = []
            col = []
            data = []
            while True:
                line = f.readline().strip('\n').split('  ')  # 两个空格分割
                if line:
                    docID = line[0]
                    topic_list = line[1:][0].split(' ')  # 一个空格分割
                    for topic in topic_list:
                        if topic:
                            topic_info = topic.split(':')
                            assert topic_info.__len__() == 2
                            topic_id = topic_info[0]
                            topic_cnt = topic_info[1]
                            row.append(topic_id)
                            col.append(docID)
                            data.append(topic_cnt)
                else:
                    break
        assert row.__len__() == data.__len__()
        assert col.__len__() == data.__len__()
        doc_topic_mat = sparse.csr_matrix((data, (row, col)), shape=(self.tn, self.dn))
        return doc_topic_mat

    @staticmethod
    def loadTopicWordModel(topic_word_path, topic_summary_path):
        """

        :param topic_word_path: lightlda 生成的 server_0_table_0.model
        :param topic_summary_path: lightlda 生成的 server_0_table_1.model
        :return:
        """

    # 每个主题的前10个关键词写入到output_topic_topn_words中
    def dump_topic_topn_words(self, output_topic_topn_words, topn=20):
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

    def loadDocTopicModel(doc_topic_path):
        """
        得到每篇文章的所属主题（top3）
        :param doc_topic_path: lightlda 模型生成的doc_topic.0文件
        :return: 稀疏矩阵
        """
        result = []
        with open(doc_topic_path, 'r', encoding='utf-8') as f:
            i = 0
            while True:
                line = f.readline().strip('\n').split('  ')  # 两个空格分割
                docID = line[0]
                topic_list = line[1:][0].split(' ')  # 一个空格分割
                topic_dic = {}
                for topic in topic_list:
                    if topic:
                        kv = topic.split(':')
                        topic_dic[kv[0]] = int(kv[1])
                line_json = {}
                x = sorted(topic_dic.items(), key=lambda item: item[1])
                print(x)
                line_json["docid"] = docID
                line_json["topic"] = topic_dic
                result.append(line_json)
                i += 1
                if i == 10:
                    break
        return result
    out = loadDocTopicModel(doc_topic_path)
    print(len(out))
    print(out)