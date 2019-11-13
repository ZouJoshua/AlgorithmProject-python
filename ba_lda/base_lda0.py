#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 11/9/19 12:37 PM
@File    : base_lda.py
@Desc    :  最简单的lda实现(列表实现)

"""


import random

alpha = 0.01
beta = 0.01
topic_number = 10
dic = []


def lda(z, nt, nd, nt_sum, nd_sum, dic, doc):
    doc_num = len(z)
    for time in range(50):
        for m in range(doc_num):
            doc_len = len(z[m])
            for i in range(doc_len):
                term = dic[doc[m][i]]  # 词语 -> 词汇
                gibbs_sampling(z, m, i, nt, nd, nt_sum, nd_sum, term)
    theta = calc_theta(nd, nd_sum)  # 计算每个文档的主题分布
    phi = calc_phi(nt, nt_sum)  # 计算每个主题的词分布
    return theta, phi

def gibbs_sampling(z, m, i, nt, nd, nt_sum, nd_sum, term):
    topic = z[m][i]  # 当前主题
    nt[term][topic] -= 1  # 去除当前词
    nd[m][topic] -= 1
    nt_sum[topic] -= 1
    nd_sum[m] -= 1

    topic_alpha = topic_number * alpha
    term_beta = len(dic) * beta
    p = [0 for x in range(topic_number)]  # p[k],属于主题k的概率
    for k in range(topic_number):
        p[k] = (nd[m][k] + alpha) / (nd_sum[m] + topic_alpha) * (nt[term][k] + beta) / (nt_sum[k] + term_beta)
        if k >= 1:
            p[k] += p[k - 1]
    gs = random.random() * p[topic_number - 1]  # 采样
    new_topic = 0
    while new_topic < topic_number:
        if p[new_topic] > gs:
            break
        new_topic += 1

    nt[term][new_topic] += 1
    nd[m][new_topic] += 1
    nt_sum[new_topic] += 1
    nd_sum[m] += 1
    z[m][i] = new_topic  # 新主题

def calc_theta(nd, nd_sum):
    """
    每个文档的主题分布
    :param nd:
    :param nd_sum:
    :return:
    """
    doc_num = len(nd)
    topic_alpha = topic_number * alpha
    theta = [[0 for t in range(topic_number)] for d in range(doc_num)]
    for m in range(doc_num):
        for k in range(topic_number):
            theta[m][k] = (nd[m][k] + alpha) / (nd_sum[m] + topic_alpha)

    return theta


def calc_phi(nt, nt_sum):
    """
    每个主题的词分布
    :param nt:
    :param nt_sum:
    :return:
    """
    term_num = len(nt)
    term_beta = term_num * beta
    phi = [[0 for w in range(term_num)] for t in range(topic_number)]
    for k in range(topic_number):
        for term in range(term_num):
            phi[k][term] = (nt[term][k] + beta) / (nt_sum[k] + term_beta)