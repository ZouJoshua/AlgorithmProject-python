#coding:utf-8
"""
测试关键词提取 mz_entropy 算法
"""
import codecs
from preprocess import preprocess
from gensim.summarization.mz_entropy import mz_keywords

keywords_dict = dict()
with codecs.open('../data/sensortower_reviews.csv', 'rb', 'utf-8', 'ignore') as infile:
    infile.readline()
    for line_ser, line in enumerate(infile):
        if line_ser % 5000 == 0:
            print(line_ser)
        line = line.strip()
        if line:
            items_li = line.split(u',')
            if len(items_li) == 10:
                country = items_li[2].strip('"')
                content = items_li[7].strip('"')
                # 对原始评论做预处理，返回预处理并分词后的结果
                eng_word_li = preprocess(content)
                if not eng_word_li:
                    continue
                text = u' '.join(eng_word_li)
                try:
                    key_word_li = mz_keywords(text, blocksize=4, scores=False, split=False, weighted=False, threshold=0.0).split('\n')
                except :
                    continue
                if key_word_li:
                    for key_word in key_word_li:
                        key_word = key_word.strip()
                        if key_word:
                            if key_word in keywords_dict:
                                keywords_dict[key_word] += 1
                            else:
                                keywords_dict[key_word] = 1

with open('../out/key_word_gensim_mz_entropy.txt', 'wb') as outfile:
    for key_word, freq in keywords_dict.items():
        out_str = u'%s\t%d\n' % (key_word, freq)
        outfile.write(out_str.encode('utf-8', 'ignore'))
