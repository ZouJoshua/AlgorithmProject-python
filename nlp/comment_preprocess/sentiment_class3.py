#coding:utf-8
"""
NLTK SentimentAnalyser 情感分析
"""
import codecs
from preprocess import preprocess
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

outfile = open('../out/result_SentimentAnalyser.txt', 'wb')
with codecs.open('../data/sensortower_reviews.csv', 'rb', 'gbk', 'ignore') as infile:
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
                eng_word_li = preprocess(content)
                if not eng_word_li: 
                    continue
                sentence = u' '.join(eng_word_li)
                ss = sid.polarity_scores(sentence)
                out_str = u'%s\t%s\n' % (ss['compound'], sentence)
                outfile.write(out_str.encode('gbk', 'ignore'))
outfile.close()
