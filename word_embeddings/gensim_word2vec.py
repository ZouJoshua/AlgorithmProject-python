#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-6-13 下午5:36
@File    : gensim_word2vec.py
@Desc    : 
"""

import os
from gensim.models import word2vec


import sys
cwd = os.path.realpath(__file__)
print(cwd)
root_dir = os.path.dirname(os.path.dirname(cwd))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "preprocess"))





def train_word2vec_embed_by_gensim(doc_word_list, save_path=None, model_file="word2vec.model", word2vec_file="word2vec.bin"):
    """
    gensim训练词向量
    :param doc_word_list:
    :param save_path:
    :param model_file:
    :param word2vec_file:
    :return:
    """
    # 引入日志配置
    import logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    #skip gram（预测更准确些）
    if save_path:
        model_path = os.path.join(save_path, model_file)
        vector_path = os.path.join(save_path, word2vec_file)
    else:
        model_path = model_file
        vector_path = word2vec_file
    print(">>>>> 正在使用skip gram模型训练词向量")
    model = word2vec.Word2Vec(doc_word_list, size=300, workers=4, sg=1, iter=50)  # 默认训练词向量的时候把频次小于5的单词从词汇表中剔除掉
    model.save(model_path)
    model.wv.save_word2vec_format(vector_path, binary=True)
    print("<<<<< 词向量模型已保存【{}】".format(model_path))
    print("<<<<< 词向量embedding已保存【{}】".format(vector_path))
