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
import time
import gc
import os


class LDAResult:

    def __init__(self, alpha, beta, topic_num, vocab_num, doc_num, model_result_basedir):
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
        self.base_dir = model_result_basedir
        self.dwp = os.path.join(model_result_basedir, 'docword')
        self.vp = os.path.join(model_result_basedir, 'vocab')
        self.dtp = os.path.join(model_result_basedir, 'doc_topic.0')
        self.twp = os.path.join(model_result_basedir, 'server_0_table_0.model')
        self.tsp = os.path.join(model_result_basedir, 'server_0_table_1.model')
        self.docs = self.load_docs_from_docword(self.dwp)


    def load_vocabs(self):
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

    def load_doc_topic_mat(self, index_with_0=True):
        """
        得到文档-主题概率分布,得到每篇文章的所属主题
        :param index_with_0: docID索引是否以0开始
        :return: doc_topic_prob_mat[topic_id][doc_id] = topic_cnt
        """
        if index_with_0:
            offset = 0
        else:
            offset = 1
        s = time.time()
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
        e = time.time()
        print('>>>>>>>>>> 读取文件耗时{}'.format(e - s))
        assert row.__len__() == data.__len__()
        assert col.__len__() == data.__len__()
        doc_topic_mat = sparse.csr_matrix((data, (row, col)), shape=(self.tn, self.dn))
        # 计数（每个文档对应的主题数量和，即包含词的数目）
        doc_cnts = doc_topic_mat.sum(axis=0)
        # 计算概率
        s1 = time.time()
        factor = self.tn * self.a
        doc_cnts_factor = doc_cnts + factor
        assert doc_topic_mat.shape[1] == doc_cnts_factor.shape[1]
        doc_topic_prob_mat = (doc_topic_mat.toarray() + self.a) / doc_cnts_factor
        e1 = time.time()
        print(">>>>>>>>>> 计算概率矩阵耗时{}".format(e1 - s1))
        # 释放内存
        del doc_topic_mat
        gc.collect()
        print('------------------释放矩阵doc_topic_mat内存------------------')
        print('------------------文档-主题概率分布矩阵------------------')
        return doc_topic_prob_mat

    def load_topic_word_mat(self):
        """
        加载主题_词模型，生成主题-词概率矩阵
        :return: topic_vocab_prob_mat[wordID][topic_id] = topic_cnt
        """
        row = []
        col = []
        data = []
        s = time.time()
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
        e = time.time()
        print('>>>>>>>>>> 读取文件耗时{}'.format(e - s))
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
        s1 = time.time()
        factor = self.vn * self.b  # 归一化因子
        topic_cnts_factor = np.array(topic_cnts) + factor
        topic_vocab_prob_mat = (topic_vocab_mat.toarray() + self.b) / topic_cnts_factor
        e1 = time.time()
        print(">>>>>>>>>> 计算概率矩阵耗时{}".format(e1 - s1))
        # 释放内存
        del topic_vocab_mat
        gc.collect()
        print('------------------释放矩阵topic_vocab_mat内存------------------')
        print('------------------得到主题-词概率矩阵------------------')
        return topic_vocab_prob_mat


    def load_docs_from_docword(self, docword_file):
        print(">>>>>>>>>> 从文件 [{}] 加载docword".format(self.dwp))
        f = open(docword_file, 'r')
        doc_word_list = list()
        for i in range(self.dn):
            word_list = list()
            doc_word_list.append(word_list)
        did = 1
        while True:
            _line = f.readline()
            if _line:
                line = _line.strip()
                docID, wordID, wordCnt = line.split("|")
                for i in range(int(wordCnt)):
                    doc_word_list[int(docID)-1].append(int(wordID))
                # if docID == did:
                #     for i in range(wordCnt):
                #         doc_word_list.append(wordID)
                # else:
                #     docs.append(doc_word_list)
                #     did += 1
                #     doc_word_list = list()
            else:
                f.close()
                break
        print(">>>>>>>>>> 加载完成")
        return doc_word_list



    def dump_topic_topn_words(self, output_topic_topn_words, topn=None):
        """
        每个主题的前20个关键词写入到output_topic_topn_words中
        :param output_topic_topn_words: 主题的 topn 关键词输出文件
        :param topn: 前20个关键词
        :return: file
        """
        return self._get_topn_topic_words(output_topic_topn_words, topn)

    def dump_doc_topn_words(self, output_doc_topn_words, topn):
        """
        每篇文档的前n个关键词写入到output_doc_topn_words中
        :param output_doc_topn_words: 文档的 topn 关键词文件
        :param topn: 前20个关键词
        :return: file
        """
        return self._get_topn_doc_words(output_doc_topn_words, topn)

    def _get_topn_topic_words(self, output_topic_topn_words, topn):
        """
        生成所有主题-词dict
        :param topic_vocab_prob_mat: 主题—词概率矩阵
        :return: list[{"topic_id": id, "words":{"word": prob}},...]
        """
        vocabs = self.load_vocabs()
        mat_csc = sparse.csc_matrix(self.load_topic_word_mat())
        m, n = mat_csc.get_shape()
        f = open(output_topic_topn_words, 'w', encoding='utf-8')
        print('------------------处理排序------------------')
        for col_index in range(n):
            topn_topic_words_dict = dict()
            data = mat_csc.getcol(col_index).data
            row = mat_csc.getcol(col_index).indices
            row_len = row.shape[0]
            topn_topic_words_dict["topic_id"] = col_index
            topic_words_dict = dict()
            for index in range(row_len):
                prob = data[index]
                word = vocabs[int(row[index])]
                topic_words_dict[word] = prob
            s = time.time()
            topic_sort_list = sorted(topic_words_dict.items(), key=lambda words: words[1], reverse=True)
            e = time.time()
            print('>>>>>>>>>>Topic{} 排序耗时{}'.format(col_index, (e - s)))
            if topn:
                topn_list_tmp = topic_sort_list[:topn]
            else:
                topn_list_tmp = topic_sort_list
            topn_topic_words_dict["words"] = dict(topn_list_tmp)
            f.write(json.dumps(topn_topic_words_dict))
            f.write('\n')
            del data, row, topic_words_dict
            gc.collect()
        f.close()
        # 释放内存
        del mat_csc
        gc.collect()
        print('------------------已释放矩阵mat_csc内存------------------')
        print('------------------得到topn主题-词文件------------------')

    def _get_topn_doc_words(self, output_doc_topn_words, topn):
        pass

    def get_list_of_topic_topn(self, output_topic_topn_words, re_write_topic_topn_words):
        print('------------------将topn文件转化为可上传至hdfs的json文件------------------')
        if os.path.exists(output_topic_topn_words):
            f = open(output_topic_topn_words, 'r', encoding='utf-8')
            fout = open(re_write_topic_topn_words, 'w', encoding='utf-8')
            lines = f.readlines()
            for line in lines:
                re_write_json = dict()
                line_json = json.loads(line.strip('\n'))
                re_write_json['topic_id'] = line_json['topic_id']
                re_write_json['words'] = list()
                for word, prob in line_json['words'].items():
                    word_tuple = (word, prob)
                    re_write_json['words'].append(word_tuple)
                fout.write(json.dumps(re_write_json))
                fout.write('\n')
            f.close()
            fout.close()
        else:
            raise Exception('请检查文件路径')


    def perplexity(self, docs=None):
        print(">>>>>>>>>> 计算模型 {} 困惑度...".format(self.base_dir))
        if docs == None:
            docs = self.docs
            # print(len(docs))
        phi = np.array(self.load_topic_word_mat().T)
        # print(phi.shape)
        log_per = 0
        N = 0
        doc_topic_prob_mat = np.array(self.load_doc_topic_mat().T)
        # print(doc_topic_prob_mat.shape)
        Kalpha = self.tn * self.a
        for m, doc in enumerate(docs):
            theta = doc_topic_prob_mat[m] / (len(self.docs[m]) + Kalpha)
            if m % 10000 == 0:
                print("已计算{}篇文档".format(m))
            for w in doc:
                log_per -= np.log(np.inner(phi[:, w], theta))
            N += len(doc)
        print(N)
        return np.exp(log_per / N)

    def get_topic_topn_words_from_file(self, file):
        topic_words = []
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line_json = json.loads(line.strip())
                if line_json['words']:
                    topic_words.append(line_json['words'])
        return topic_words



if __name__ == "__main__":

    # 视频topic
    # topic_num = 256
    # base_dir = r'/data/zoushuai/lightlda/video_topic{}'.format(topic_num)
    # vocab_path = os.path.join(base_dir, "vocab")
    # output_doc_topn_words = os.path.join(base_dir, "doc.topn")
    # output_topic_topn_words = os.path.join(base_dir, "topic{}.top100".format(topic_num))
    # re_write_topic_topn_words = os.path.join(base_dir, "topic.top100")
    #
    # ldar = LDAResult(alpha=0.19, beta=0.1, topic_num=topic_num, vocab_num=1224992, doc_num=355284,
    #                 model_result_basedir=base_dir)
    #
    # ldar.dump_topic_topn_words(output_topic_topn_words, topn=100)
    # perp = ldar.perplexity()
    # print("模型[{}]困惑度：{}".format(base_dir, perp))
    # lda.get_list_of_topic_topn(output_topic_topn_words, re_write_topic_topn_words)

    # 新闻topic

    topic_num = 64
    base_dir = r'/data/zoushuai/lightlda/topic_v1/topic{}'.format(topic_num)
    vocab_path = os.path.join(base_dir, "vocab")
    output_doc_topn_words = os.path.join(base_dir, "doc.topn")
    output_topic_topn_words = os.path.join(base_dir, "topic{}.top100".format(topic_num))
    re_write_topic_topn_words = os.path.join(base_dir, "topic.top100")

    ldar = LDAResult(alpha=0.78, beta=0.1, topic_num=topic_num, vocab_num=1238320, doc_num=4995860,
                     model_result_basedir=base_dir)

    ldar.dump_topic_topn_words(output_topic_topn_words, topn=100)
    perp = ldar.perplexity()
    print("模型[{}]困惑度：{}".format(base_dir, perp))