#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/12/10 16:40
@File    : test_loadTopicWordModel.py
@Desc    : 
"""


import scipy.sparse as sparse
import numpy as np

def test_loadTopicWordModel(topic_word_path, topic_summary_path):
    """
    加载主题_词模型
    :param topic_word_path: lightlda 生成的 server_0_table_0.model(主题_词模型)
    :param topic_summary_path: lightlda 生成的 server_0_table_1.model(主题数目统计)
    :return:
    """
    row = []
    col = []
    data = []
    with open(topic_word_path, 'r', encoding='utf-8') as f:
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
    topic_vocab_mat = sparse.csr_matrix((data, (row, col)), shape=(vn, tn))
    # 每个主题出现的次数
    with open(topic_summary_path, 'r', encoding='utf-8') as f:
        line_str = f.readline().strip('\n')
        if line_str:
            topic_cnts = [float(topic_info.split(':')[1]) for topic_info in line_str.split(' ')[1:]]
        pass
    # 计算概率
    factor = vn * b  # 归一化因子
    topic_cnts_factor = np.array(topic_cnts) + factor
    topic_vocab_prob_mat = (topic_vocab_mat.toarray() + b) / topic_cnts_factor
    return topic_vocab_prob_mat


topic_word_path = "server_0_table_0.model"
topic_summary = "server_0_table_1.model"
b = 0.01
tn = 1000
vn = 2022810
mat = test_loadTopicWordModel(topic_word_path, topic_summary)
print(mat[0])