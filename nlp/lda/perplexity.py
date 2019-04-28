#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-4-24 下午2:37
@File    : perplexity.py
@Desc    : 困惑度计算
"""

"""
# 概率分布的perplexity
# 概率模型的perplexity
# 单词的perplexity
"""

# from imp import reload
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
import os
from gensim.corpora import Dictionary
from gensim import corpora, models
from gensim.test.utils import datapath
from datetime import datetime
import math


import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s : ', level=logging.INFO)





def perplexity(ldamodel, testset, dictionary, vocabs_num, topics_num):
    """calculate the perplexity of a lda-model"""
    # dictionary : {7822:'deferment', 1841:'circuitry',19202:'fabianism'...]
    print('the info of this ldamodel: \n')
    print('num of testset: %s; size_dictionary: %s; num of topics: %s' % (len(testset), vocabs_num, topics_num))
    prep = 0.0
    prob_doc_sum = 0.0
    # store the probablity of topic-word:[('business', 0.010020942661849608),('family', 0.0088027946271537413)...]
    topic_word_list = []
    for topic_id in range(topics_num):
        topic_word = ldamodel.show_topic(topic_id, vocabs_num)
        dic = {}
        for word, probability in topic_word:
            dic[word] = probability
        topic_word_list.append(dic)

    #store the doc-topic tuples:[(0, 0.0006211180124223594),(1, 0.0006211180124223594),...]
    doc_topics_ist = []
    for doc in testset:
        doc_topics_ist.append(ldamodel.get_document_topics(doc, minimum_probability=0))
    testset_word_num = 0
    for i in range(len(testset)):
        prob_doc = 0.0  # the probablity of the doc
        doc = testset[i]
        doc_word_num = 0  # the num of words in the doc
        for word_id, num in doc:
            prob_word = 0.0  # the probablity of the word
            doc_word_num += num
            word = dictionary[word_id]
            for topic_id in range(num_topics):
                # cal p(w) : p(w) = sumz(p(z)*p(w|z))
                prob_topic = doc_topics_ist[i][topic_id][1]
                prob_topic_word = topic_word_list[topic_id][word]
                prob_word += prob_topic*prob_topic_word
            prob_doc += math.log(prob_word)  # p(d) = sum(log(p(w)))
        prob_doc_sum += prob_doc
        testset_word_num += doc_word_num
    # perplexity = exp(-sum(p(d)/sum(Nd))
    prep = math.exp(-prob_doc_sum/testset_word_num)
    print("the perplexity of this ldamodel is : %s" % prep)
    return prep

if __name__ == '__main__':
    middatafolder = r'E:\work\lda' + os.sep
    dictionary_path = middatafolder + 'dictionary.dictionary'
    corpus_path = middatafolder + 'corpus.mm'
    ldamodel_path = middatafolder + 'lda.model'
    dictionary = corpora.Dictionary.load(dictionary_path)
    corpus = corpora.MmCorpus(corpus_path)
    lda_multi = models.ldamodel.LdaModel.load(ldamodel_path)
    num_topics = 50
    testset = []
    # sample 1/300
    for i in range(corpus.num_docs/300):
        testset.append(corpus[i*300])
    prep = perplexity(lda_multi, testset, dictionary, len(dictionary.keys()), num_topics)