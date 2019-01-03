# -*- coding: utf8 -*-

import os
import pickle
import codecs
import json
import re
from gensim.models import Word2Vec


def create_vocabulary(word2vec_model_path, name_scope=''):
    """
    创建词汇索引表
    :param word2vec_model_path: 训练好的word2vec模型存放路径
    :return: {单词：索引}表和{索引：单词}表
    """
    # TODO：这里需要加参数
    cache_path = "/data/caifuli/news_classification/textcnn/cache_vocabulary_pik/" + name_scope + "_word_vocabulary.pik"
    print("cache_path:", cache_path, "file_exists:", os.path.exists(cache_path))

    if os.path.exists(cache_path):  # 如果缓存文件存在，则直接读取
        with open(cache_path, 'rb') as data_f:
            vocabulary_word2idx, vocabulary_idx2word = pickle.load(data_f)
            return vocabulary_word2idx, vocabulary_idx2word
    else:
        vocabulary_word2idx = {}
        vocabulary_idx2word = {}

        print("building vocabulary（words with frequency above 5 are included). word2vec_path:", word2vec_model_path)
        vocabulary_word2idx['PAD_ID'] = 0
        vocabulary_idx2word[0] = 'PAD_ID'
        special_index = 0

        model = Word2Vec.load(word2vec_model_path)
        # model = word2vec.load(word2vec_model_path, kind='bin')

        for i, vocab in enumerate(model.wv.vocab):
            if vocab.isalpha():
                vocabulary_word2idx[vocab] = i+1+special_index  # 只设了一个special ID
                vocabulary_idx2word[i+1+special_index] = vocab

        # 如果不存在写到缓存文件中
        if not os.path.exists(cache_path):
            with open(cache_path, 'ab') as data_f:
                pickle.dump((vocabulary_word2idx, vocabulary_idx2word), data_f)
    return vocabulary_word2idx, vocabulary_idx2word


def create_label_vocabulary(training_data_dir_path='/data/caifuli/news_classification/data', name_scope=''):
    """
    创建标签映射  label is sorted. 1 is high frequency, 2 is low frequency.
    :param training_data_path: 带label的训练语料
    :return: label2idx和idx2label
    """
    print("building vocabulary_label_sorted. training_data_dir__path:", training_data_dir_path)
    cache_path = '/data/caifuli/news_classification/textcnn/cache_vocabulary_label_pik/' + name_scope + "_label_vocabulary.pik"
    print("cache_path:", cache_path, "file_exists:", os.path.exists(cache_path))

    if os.path.exists(cache_path):  # 如果缓存文件存在，则直接读取
        with open(cache_path, 'rb') as data_f:
            vocabulary_word2index_label, vocabulary_index2word_label = pickle.load(data_f)
            return vocabulary_word2index_label, vocabulary_index2word_label
    else:
        label2idx = {}
        idx2label = {}
        label_count_dict = {}  # {label:count} 统计各类别的样本数
        fnames = os.listdir(training_data_dir_path)
        fnames.remove('.DS_Store')
        for fname in fnames:
            with open(os.path.join(training_data_dir_path, fname), "r") as f:
                for line in f.readlines():
                    line = json.loads(line)
                    label = line['category']
                    if label_count_dict.get(label, None) is not None:
                        label_count_dict[label] = label_count_dict[label] + 1
                    else:
                        label_count_dict[label] = 1

        list_label = sort_by_value(label_count_dict)  # 按样本数降序排之后的key列表

        print("length of list_label:", len(list_label))

        for i, label in enumerate(list_label):
            label2idx[label] = i
            idx2label[i] = label

        # 如果不存在写到缓存文件中
        if not os.path.exists(cache_path):
            with open(cache_path, 'ab') as data_f:
                pickle.dump((label2idx, idx2label), data_f)
    print("building vocabulary_label(sorted) ended.len of vocabulary_label: ", len(idx2label))
    return label2idx, idx2label


def sort_by_value(d):   # 根据value排序，返回降序后的key的列表
    items = d.items()
    backitems = [[v[1], v[0]] for v in items]  # 把item的key和value交换位置放在list中
    backitems.sort(reverse=True)  # 按list中每个元素的第一个值降序排序
    return [backitems[i][1] for i in range(0, len(backitems))]


def load_data(vocabulary_word2idx, label2idx, valid_portion=0.2, training_data_dir_path='/data/caifuli/news_classification/data'):  # n_words=100000
    """
    划分训练集、测试集、验证集
    :param vocabulary_word2index: word2idx映射
    :param label2idx: label2idx映射
    :param valid_portion: 验证集所占比例
    :param training_data_path: 训练语料路径
    :return: 其中train_X是list of list，train_Y是label的list
    """
    # example:"w305 w6651 w3974 w1005 w54 w109 w110 w3974 w29 w25 w1513 w3645 w6 w111 __label__-400525901828896492"
    print("load data started...")
    # 从文件夹中读取新闻数据
    lines = []
    fnames = os.listdir(training_data_dir_path)
    fnames.remove('.DS_Store')
    for fname in fnames:
        with open(os.path.join(training_data_dir_path, fname), "r") as f:
            for line in f.readlines():
                lines.append(line)

    X = []
    Y = []
    for i, line in enumerate(lines):
        line = json.loads(line)
        x = line['title'].lower()
        y = line['category']  # .replace('\n', '')
        x = x.replace("\n", ' EOS ').strip()
        if i < 5:  # 打出来5条
            print("x0:", x)  # get raw x
        # x_=process_one_sentence_to_get_ui_bi_tri_gram(x)
        # if i<5:
        #    print("x1:",x_) #
        x = x.split(" ")
        x = [vocabulary_word2idx.get(e, 0) for e in x]  # 若找不到单词，用0填充
        if i < 5:
            print("x1:", x)  # word to index
        y = label2idx[y]  # np.abs(hash(y))
        X.append(x)
        Y.append(y)
    # 划分训练集、测试集和验证集   # TODO
    number_examples = len(X)
    print("number_examples:", number_examples)
    train = (X[0:int((1 - valid_portion) * number_examples)], Y[0:int((1 - valid_portion) * number_examples)])
    test = (X[int((1 - valid_portion) * number_examples) + 1:], Y[int((1 - valid_portion) * number_examples) + 1:])
    print("load_data ended...")
    return train, test, test


def load_final_test_data(file_path):
    """
    生成列表，列表中的项格式为(id,string)
    :param file_path: 文件路径
    :return: 
    """
    final_test_file_predict_object = codecs.open(file_path, 'r', 'utf8')
    lines = final_test_file_predict_object.readlines()
    data_lists_result = []
    for i, line in enumerate(lines):
        data_id, data_string = line.split("\t")
        data_string = data_string.strip().replace("\n", "").replace("\r", "")
        data_lists_result.append((data_id, data_string))
    print("length of total data lists:", len(data_lists_result))
    return data_lists_result


def load_data_predict(vocabulary_word2idx, questionid_question_lists, uni_to_tri_gram=False):  # n_words=100000,
    """
    
    :param vocabulary_word2idx: 
    :param questionid_question_lists: 
    :param uni_to_tri_gram: 
    :return: 
    """
    final_list = []
    for i, id_content_tuple in enumerate(questionid_question_lists):
        data_id, question_string_list = id_content_tuple
        if uni_to_tri_gram:
            x_ = process_one_sentence_to_get_ui_bi_tri_gram(question_string_list)
            x = x_.split(" ")
        else:
            x = question_string_list.split(" ")
        x = [vocabulary_word2idx.get(e, 0) for e in x]
        if i <= 2:
            print("data_id:", data_id)
            print("question_string_list:", question_string_list)
            print("x_indexed:", x)
        final_list.append((data_id, x))
    number_examples = len(final_list)
    print("number_examples:", number_examples)
    return final_list


# 将一句话转化为(uigram,bigram,trigram)后的字符串
def process_one_sentence_to_get_ui_bi_tri_gram(title, n_gram=3):
    """
    :param title: string. example:'w17314 w5521 w7729 w767 w10147 w111'
    :param n_gram:最大上文窗口
    :return:string. example:'w17314 w17314w5521 w17314w5521w7729 w5521 w5521w7729 w5521w7729w767 w7729 w7729w767 w7729w767w10147 w767 w767w10147 w767w10147w111 w10147 w10147w111 w111'
    """
    result = []
    word_list = title.split(" ")  # [sentence[i] for i in range(len(sentence))]
    unigram = ''
    bigram = ''
    length_sentence = len(word_list)
    for i, word in enumerate(word_list):
        unigram = word                           # ui-gram
        word_i = unigram
        if n_gram >= 2 and i+2 <= length_sentence:  # bi-gram
            bigram = " ".join(word_list[i:i+2])
            word_i = word_i + ' ' + bigram
        if n_gram >= 3 and i+3 <= length_sentence:  # tri-gram
            trigram = "".join(word_list[i:i+3])
            word_i = word_i + ' ' + trigram

        result.append(word_i)
    result = " ".join(result)
    return result


def clean_string(text):
    # 去除网址和邮箱
    text = text.replace("\n", " ").replace("\r", " ").replace("&#13;", " ").lower().strip()
    url_list = re.findall(r'http://[a-zA-Z0-9.?/&=:]*', text)
    for url in url_list:
        text = text.replace(url, " ")
    email_list = re.findall(r"[\w\d\.-_]+(?=\@)", text)
    for email in email_list:
        text = text.replace(email, " ")
    # 去除诡异的标点符号
    cleaned_text = ""
    for c in text:
        if (ord(c) >= 32 and ord(c) <= 126):
            cleaned_text += c
        else:
            cleaned_text += " "
    return cleaned_text
