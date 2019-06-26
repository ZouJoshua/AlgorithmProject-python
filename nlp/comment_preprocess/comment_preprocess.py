#coding:utf-8
"""
评论主题及正负面评价分布自动生成
"""
import codecs
import re
import time
from nltk.util import ngrams
import numpy as np
from sklearn.cluster import KMeans
import collections
from preprocess import preprocess
from preprocess import stop_word

# 加载情感词典
print "load sentiment_word_dict ..."
sentiment_word_dict = dict()
with codecs.open('../data/sentiment.dic', 'rb', 'utf-8', 'ignore') as infile:
    for line in infile:
        line = line.strip()
        if line:
            word, pos = line.split()
            word = word.lower()
            sentiment_word_dict[word] = int(pos)

# 加载单词向量词典
print "load word_vector_dict ..."
word_vector_dict = dict()
with codecs.open('../data/glove.6B.100d.txt', 'rb', 'utf-8', 'ignore') as infile:
    for line in infile:
        line = line.strip()
        if line:
            items_li = line.split(' ')
            if len(items_li) == 101:
                word = items_li[0]
                word_vector = np.array([float(w) for w in items_li[1::]])
                word_vector_dict[word] = word_vector

# 抽取ngrams2关键词序列
def extract_ngrams2(word_li):
    """
    输入要求是[(词语,词性)]
    """
    global stop_word
    # 抽取2grams关键词
    ngrams2_li_filter = []  # 过滤后剩余的2grams序列
    ngrams2_li = ngrams([w[0] for w in word_li], 2)
    if ngrams2_li:
        for ngrams2 in ngrams2_li:
            word1, word2 = ngrams2
            if (word1 not in stop_word) and (word2 not in stop_word) and (len(word1)>=3) and (len(word2)>=3) and (word1 != word2):
                ngrams2_str = u' '.join(ngrams2)
                ngrams2_li_filter.append(ngrams2_str)
    return ngrams2_li_filter

# ngrams2关键词序列过滤
def filter_ngrams2_li(ngrams2_li):
    """
    只保留能查到向量的key_phrase
    """
    valid_ngrams2_li = []
    for key_phrase in ngrams2_li:
        for key_word in key_phrase.split():
            if key_word in word_vector_dict:
                valid_ngrams2_li.append(key_phrase)
                break
    return valid_ngrams2_li

# 抽取核心词
def extract_key_word(eng_word_li):
    global core_word_stop_word_set
    key_word_li = [w for w in eng_word_li if w not in stop_word]
    return key_word_li

if __name__ == "__main__":
    t0 = time.time()
    outfile = open('../out/eng_comment.txt', 'wb')                                            # 核心评论文件
    with codecs.open('../data/sensortower_reviews_launcher.csv', 'rb', 'utf-8', 'ignore') as infile:    # 输入评论文件
        infile.readline()
        for line_ser, line in enumerate(infile):
            if line_ser % 5000 == 0:
                print(line_ser)
            line = line.strip()
            if line:
                items_li = line.split(u',')
                if len(items_li) == 10:
                    content = items_li[7].strip('"')    # 评论内容
                    review_ser = items_li[0].strip('"') # 评论序号
                    # 对原始评论做预处理，返回预处理分词以及词性标注序列
                    word_li = preprocess(content)
                    if not word_li:
                        continue
                    # 单词序列
                    eng_word_li = [w[0] for w in word_li]
                    # 计算评论情感分
                    pos_scores = 0
                    for word in eng_word_li:
                        if word in sentiment_word_dict:
                            pos_scores += sentiment_word_dict[word]
                    # 抽取2grams关键词序列
                    ngrams2_li = extract_ngrams2(word_li)
                    key_words = filter_ngrams2_li(ngrams2_li)
                    # 能抽取出ngrams2序列，则认为是核心评论
                    wether_has_info = False
                    if key_words:
                        wether_has_info = True
                    key_word = u''
                    if wether_has_info:
                        # 抽取核心词
                        key_word = extract_key_word(eng_word_li)
                    out_str = u'{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(review_ser, u' '.join(eng_word_li), pos_scores, wether_has_info, u','.join(key_words), u','.join(key_word))
                    outfile.write(out_str.encode('utf-8', 'ignore'))
                  
    outfile.close()
    t1 = time.time()
    print('\n\n\ntime elpased %.2f mins\n\n\n'%((t1-t0)/60.0))

# # 关键词聚类
# # 关键词集合的向量矩阵
# key_phrase_array = np.zeros((len(key_word_dict), 100))
# row = 0
# key_phrase_li = []
# for key_phrase, freq in key_word_dict.items():
#     key_word_li = key_phrase.split()
#     key_phrase_vector = np.zeros((100,))
#     valid_key_word_count = 0
#     for key_word in key_word_li:
#         if key_word in word_vector_dict:
#             key_phrase_vector += word_vector_dict[key_word]
#             valid_key_word_count += 1
#     key_phrase_array[row, :] = key_phrase_vector/(valid_key_word_count*1.0)
#     key_phrase_li.append(key_phrase)
#     row += 1

# # 聚类
# cluster_number = 50 # 簇数量变量
# print "cluster number = %d" % cluster_number
# km_model = KMeans(n_clusters=cluster_number, init='random', n_init=10, max_iter=500, tol=1e-04, random_state=0)  # 构造聚类实例
# km_model.fit(key_phrase_array)  # 聚类

# # 输出聚类结果
# clustering = collections.defaultdict(list)
# for idx, label in enumerate(km_model.labels_):
#     clustering[label].append(key_phrase_li[idx])
