# -*- coding: utf-8 -*-
"""使用fasttext训练词向量"""
import fasttext
import os
import json
import logging

train_dataDir = "/data"
train_dataPath = "/traindata"




def train_word2vec_embed_by_fasttext(save_path=None, model_file="word2vec.model", word2vec_file="word2vec.bin"):
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
    model = fasttext.skipgram(train_dataPath, model_file, dim=300)
    model.save(model_path)
    model.wv.save_word2vec_format(vector_path, binary=True)
    print("<<<<< 词向量模型已保存【{}】".format(model_path))
    print("<<<<< 词向量embedding已保存【{}】".format(vector_path))