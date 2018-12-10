#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/12/10 14:20
@File    : test_loadDocTopicModel.py
@Desc    : 
"""

import scipy.sparse as sparse

def test_loadDocTopicModel(doc_topic_path,index_with_0=True):
    """
    得到每篇文章的所属主题（top3）
    :param doc_topic_path: lightlda 模型生成的doc_topic.0文件
    :return: 稀疏矩阵
    """
    """
            得到文档-主题概率分布,得到每篇文章的所属主题（top3）
            :param doc_topic_path: lightlda 模型生成的doc_topic.0文件
            :param index_with_0: docID索引是否以0开始
            :return: doc_topic_prob_mat[topic_id][doc_id] = topic_cnt
            """

    if index_with_0:
        offset = 0
    else:
        offset = 1
    with open(doc_topic_path, 'r', encoding='utf-8') as f:
        row = []
        col = []
        data = []
        while True:
            line_str = f.readline().strip('\n')
            if line_str:
                line = line_str.split('  ')  # 两个空格分割
                if line[0] == '':
                    print(line_str)
                docID = int(line[0]) - offset
                topic_list = line[1:][0].split(' ')  # 一个空格分割
                for topic in topic_list:
                    if topic:
                        topic_info = topic.split(':')
                        assert topic_info.__len__() == 2
                        topic_id = topic_info[0]
                        topic_cnt = float(topic_info[1])
                        row.append(topic_id)
                        col.append(docID)
                        data.append(topic_cnt)
                    continue
            else:
                break
    assert row.__len__() == data.__len__()
    assert col.__len__() == data.__len__()
    doc_topic_mat = sparse.csr_matrix((data, (row, col)), shape=(tn, dn))
    # 计数（每个文档对应的主题数量和，即包含词的数目）
    doc_cnts = doc_topic_mat.sum(axis=0)
    # 计算概率
    factor = tn * a
    doc_cnts_factor = doc_cnts + factor
    assert doc_topic_mat.shape[1] == doc_cnts_factor.shape[1]
    doc_topic_prob_mat = (doc_topic_mat.toarray() + a) / doc_cnts_factor
    return doc_topic_prob_mat


doc_topic_path = "doc_topic.0"
a = 0.05
tn = 1000
dn = 2019265
out = test_loadDocTopicModel(doc_topic_path)
print(out.shape)
