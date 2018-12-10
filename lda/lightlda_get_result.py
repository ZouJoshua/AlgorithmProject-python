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
import json


class LDAResult:

    def __init__(self, alpha, beta, topic_num, vocab_num, doc_num, vocab_path, doc_topic_path, topic_word_path, topic_summary_path):
        """
        初始化参数
        :param alpha:
        :param beta:
        :param topic_num: 主题数目
        :param vocab_num: 词汇数目
        :param doc_num: 文档数目
        :param vocab_path: lightlda 模型的词汇文件
        :param doc_topic_path: lightlda 模型生成的doc_topic.0文件
        :param topic_word_path: lightlda 模型生成的 server_0_table_0.model(主题_词模型)
        :param topic_summary_path: lightlda 生成的 server_0_table_1.model(主题数目统计)
        """
        self.a = alpha
        self.b = beta
        self.tn = topic_num
        self.vn = vocab_num
        self.dn = doc_num
        self.vp = vocab_path
        self.dtp = doc_topic_path
        self.twp = topic_word_path
        self.tsp = topic_summary_path

    def loadVocabs(self):
        """
        得到所有原始词
        :return: list
        """
        out = []
        with open(self.vp, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                out.append(line.strip())

        return out

    def loadDocTopicModel(self, index_with_0=True):
        """
        得到文档-主题概率分布,得到每篇文章的所属主题
        :param index_with_0: docID索引是否以0开始
        :return: doc_topic_prob_mat[topic_id][doc_id] = topic_cnt
        """
        if index_with_0:
            offset = 0
        else:
            offset = 1
        with open(self.dtp, 'r', encoding='utf-8') as f:
            row = []
            col = []
            data = []
            while True:
                line_str = f.readline().strip('\n')
                if line_str:
                    line = line_str.split('  ')  # 两个空格分割
                    # if line[0] == '':
                    #     print(line_str)
                    docID = int(line[0]) - offset
                    topic_list = line[1:][0].split(' ')  # 一个空格分割
                    for topic in topic_list:
                        if topic:
                            topic_info = topic.split(':')
                            assert topic_info.__len__() == 2
                            topic_id = int(topic_info[0])
                            topic_cnt = float(topic_info[1])
                            row.append(topic_id)
                            col.append(docID)
                            data.append(topic_cnt)
                        continue
                else:
                    break
        assert row.__len__() == data.__len__()
        assert col.__len__() == data.__len__()
        doc_topic_mat = sparse.csr_matrix((data, (row, col)), shape=(self.tn, self.dn))
        # 计数（每个文档对应的主题数量和，即包含词的数目）
        doc_cnts = doc_topic_mat.sum(axis=0)
        # 计算概率
        factor = self.tn * self.a
        doc_cnts_factor = doc_cnts + factor
        assert doc_topic_mat.shape[1] == doc_cnts_factor.shape[1]
        doc_topic_prob_mat = (doc_topic_mat.toarray() + self.a) / doc_cnts_factor

        return doc_topic_prob_mat

    def loadTopicWordModel(self):
        """
        加载主题_词模型，生成主题-词概率矩阵
        :return: topic_vocab_prob_mat[wordID][topic_id] = topic_cnt
        """
        row = []
        col = []
        data = []
        with open(self.twp, 'r', encoding='utf-8') as f:
            while True:
                line_str = f.readline().strip('\n')
                if line_str:
                    line = line_str.split(' ')
                    wordID = int(line[0])  # 词id
                    for topic in line[1:]:
                        if topic:
                            topic_info = topic.split(":")
                            assert topic_info.__len__() == 2
                            topic_id = int(topic_info[0])
                            topic_cnt = float(topic_info[1])
                            row.append(wordID)
                            col.append(topic_id)
                            data.append(topic_cnt)
                        continue
                else:
                    break
        assert row.__len__() == data.__len__()
        assert col.__len__() == data.__len__()
        topic_vocab_mat = sparse.csr_matrix((data, (row, col)), shape=(self.vn, self.tn))
        # 每个主题出现的次数
        with open(self.tsp, 'r', encoding='utf-8') as f:
            line_str = f.readline().strip('\n')
            if line_str:
                topic_cnts = [float(topic_info.split(':')[1]) for topic_info in line_str.split(' ')[1:]]
            pass
        # 计算概率
        factor = self.vn * self.b  # 归一化因子
        topic_cnts_factor = np.array(topic_cnts) + factor
        topic_vocab_prob_mat = (topic_vocab_mat.toarray() + self.b) / topic_cnts_factor

        return topic_vocab_prob_mat

    def dump_topic_topn_words(self, output_topic_topn_words, topn=20):
        """
        每个主题的前20个关键词写入到output_topic_topn_words中
        :param output_topic_topn_words: 主题的 topn 关键词输出文件
        :param topn: 前20个关键词
        :return:
        """
        all_topic_words = self._get_all_topic_words()
        topn_list = list()
        with open(output_topic_topn_words, 'w', encoding='utf-8') as json_file:
            for topic in all_topic_words:
                topn_topic = dict()
                topn_topic["topic_id"] = topic["topic_id"]
                topic_sort_list = sorted(topic["words"].iteritems, key=lambda topic:topic[1], reverse=True)
                topn_list_tmp = topic_sort_list[:topn]
                topn_topic["words"] = dict(topn_list_tmp)
                topn_list.append(topn_topic)
                json_file.write(json.dumps(topn_topic))
                json_file.write('\n')


    def _get_all_topic_words(self):
        """
        生成所有主题-词dict
        :param topic_vocab_prob_mat: 主题—词概率矩阵
        :return: list[{"topic_id": id, "words":{"word": prob}},...]
        """
        vocabs = self.loadVocabs()
        mat_csc = sparse.csc_matrix(self.loadTopicWordModel())
        m, n = mat_csc.get_shape()
        all_topic_words = list()
        for col_index in range(n):
            topic_words_dict = dict()
            data = mat_csc.getcol(col_index).data
            row = mat_csc.getcol(col_index).indices
            row_len = row.shape[0]
            topic_words_dict["topic_id"] = col_index
            topic_words_dict["words"] = dict()
            for index in range(row_len):
                prob = data[index]
                word = vocabs[int(row[index])]
                topic_words_dict["words"][word] = prob
            all_topic_words.append(topic_words_dict)

        return all_topic_words

if __name__ == "__main__":

    doc_topic_path = "doc_topic.0"
    topic_word_path = "server_0_table_0.model"
    topic_summary = "server_0_table_1.model"
    vocab_path = "vocab.news.txt"
    output_doc_topn_words = "doc.topn"
    output_topic_topn_words = "topic.topn"

    # lda = LDAResult(alpha=0.1 , beta=0.01 , topic_num=500 , vocab_num=1479643 , doc_num=26893850)
    # lda.loadVocabs(ori_word_path)
    # print("加载完毕!")
    # lda.loadTopicWordModel(topic_word_path, topic_summary)
    # lda.loadDocTopicModel(doc_topic_path)
    # lda.dump_topic_topn_words(output_topic_topn_words, 10)

    lda = LDAResult(alpha=0.05, beta=0.01, topic_num=1000, vocab_num=2022810, doc_num=2019265,
                    vocab_path=vocab_path, doc_topic_path=doc_topic_path,
                    topic_word_path=topic_word_path, topic_summary_path=topic_summary)

    lda.dump_topic_topn_words(output_topic_topn_words)