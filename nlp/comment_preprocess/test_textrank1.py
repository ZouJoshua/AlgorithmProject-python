#coding:utf-8
"""
测试summanlp工具实现TextRank关键词抽取
"""

from summa import keywords
import codecs
from preprocess import preprocess
import re

# 测试逐个评论抽取关键词
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
                if eng_word_li:
                    preprocessed_text = u' '.join(eng_word_li)
                    keywords_str = keywords.keywords(preprocessed_text).strip()
                    if keywords_str:
                        keywords_li = keywords_str.split(u'\n')
                        for keyword in keywords_li:
                            if keyword in keywords_dict:
                                keywords_dict[keyword] += 1
                            else:
                                keywords_dict[keyword] = 1
                        
with open('../out/key_word_textrank.txt', 'wb') as outfile:
    for keyword, freq in keywords_dict.items():
        out_str = u'%s\t%d\n'%(keyword, freq)
        outfile.write(out_str.encode('utf-8', 'ignore'))     
