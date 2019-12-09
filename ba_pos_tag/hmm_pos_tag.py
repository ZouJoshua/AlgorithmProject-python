#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 12/9/19 1:30 PM
@File    : hmm_pos_tag.py
@Desc    : 隐马尔科夫词性标注

"""



import nltk
import sys
from nltk.corpus import brown



# 预处理词库
def pre_process(brown):
    brown_tags_words = []
    for sent in brown.tagged_sents():
        brown_tags_words.append(("START", "START"))
        brown_tags_words.extend([(tag[:2], word) for (word, tag) in sent])
        brown_tags_words.append(("END", "END"))
    return brown_tags_words

# print(brown_tags_words[:20])

# 词统计
def get_tagwords_cpd(brown_tags_words):
    # 条件频率分布
    cfd_tagwords = nltk.ConditionalFreqDist(brown_tags_words)
    # 条件概率分布
    cpd_tagwords = nltk.ConditionalProbDist(cfd_tagwords, nltk.MLEProbDist)
    return cpd_tagwords

def get_tags_cpd(brown_tags_words):
    brown_tags = [tag for (tag, word) in brown_tags_words]
    cfd_tags = nltk.ConditionalFreqDist(nltk.bigrams(brown_tags))
    cpd_tags = nltk.ConditionalProbDist(cfd_tags, nltk.MLEProbDist)
    return brown_tags, cpd_tags


def evaluation(cpd_tagwords, cpd_tags):
    """
    I want go race  -> PP VB TO VB
    :return:
    """
    prob = cpd_tags["START"].prob("PP") * \
           cpd_tagwords["PP"].prob("I") * cpd_tags["PP"].prob("VB") * \
           cpd_tagwords["VB"].prob("want") * cpd_tags["VB"].prob("TO") * \
           cpd_tagwords["TO"].prob("to") * cpd_tags["TO"].prob("VB") * \
           cpd_tagwords["VB"].prob("race") * cpd_tags["VB"].prob("END")

    return prob


def decoding(sen_list, brown_tags_words):
    """
    viterbi算法
    :param sen_list:
    :param brown_tags_words:
    :return:
    """
    cpd_tagwords = get_tagwords_cpd(brown_tags_words)
    brown_tags, cpd_tags = get_tags_cpd(brown_tags_words)
    distinct_tags = set(brown_tags)
    sen_len = len(sen_list)

    viterbi = []
    backpointer = []

    first_viterbi = {}
    first_backpointer = {}

    for tag in distinct_tags:
        if tag == "START": continue
        first_viterbi[tag] = cpd_tags["START"].prob(tag) * cpd_tagwords[tag].prob(sen_list[0])
        first_backpointer[tag] = "START"

    viterbi.append(first_viterbi)
    backpointer.append(first_backpointer)

    currbest = max(first_viterbi.keys(), key=lambda tag:first_viterbi[tag])
    print("word", "'" + sen_list[0] + "'", "current best two-tag sequence:", first_backpointer[currbest], currbest)

    for wordindex in range(1, sen_len):
        this_viterbi = {}
        this_backpointer = {}
        prev_viterbi = viterbi[-1]

        for tag in distinct_tags:
            if tag == "START": continue

            # 如果现在这个tag是x, 单词是w, 想找前一个tag y, 并且让最好的tag sequence 以y x 结尾
            # 也就是说y要最大化 prev_viterbi[y] * p(x|y) * p(w|x)
            best_previous = max(prev_viterbi.keys(), key=lambda prevtag:
                                prev_viterbi[prevtag] * cpd_tags[prevtag].prob(tag) * cpd_tagwords[tag].prob(sen_list[wordindex]))
            this_viterbi[tag] = prev_viterbi[best_previous] * cpd_tags[best_previous].prob(tag) * cpd_tagwords[tag].prob(sen_list[wordindex])
            this_backpointer[tag] = best_previous

        currbest = max(this_viterbi.keys(), key=lambda tag: this_viterbi[tag])
        viterbi.append(this_viterbi)
        backpointer.append(this_backpointer)

    # 找所有以END结尾的tag sequence
    prev_viterbi = viterbi[-1]
    best_previous = max(prev_viterbi.keys(), key=lambda prevtag: prev_viterbi[prevtag] * cpd_tags[prevtag].prob("END"))
    prob_tagsequence = prev_viterbi[best_previous] * cpd_tags[best_previous].prob("END")
    # 倒着存储的
    best_tagsequence = ["END", best_previous]
    # 同理
    backpointer.reverse()


    current_best_tag = best_previous
    for bp in backpointer:
        best_tagsequence.append(bp[current_best_tag])
        current_best_tag = bp[current_best_tag]
    best_tagsequence.reverse()

    print("The sentence was:", end=" ")
    for w in sen_list: print(w, end=" ")
    print("\n")
    print("The best tag sequence:", end=" ")
    for t in best_tagsequence: print(t, end=" ")
    print("\n")
    print("The probability of the best tag sequence is:", prob_tagsequence)

sentence = ["My", "name", "is", "Mike"]
brown_tags_words = pre_process(brown)
decoding(sentence, brown_tags_words)