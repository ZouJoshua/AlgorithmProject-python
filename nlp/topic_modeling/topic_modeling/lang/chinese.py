#!/usr/bin python
# -*- coding: utf-8 -*-
# @Date    : 2017-06-09 15:30:53
# @Author  : Liulichao (liulichao@apusapps.com)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..")
import re

import jieba

from topic_modeling.constants.chinese import zh_stop_words_list

class Chinese:

    def tokenize(self, text):
        article_vocab_list = []

        #remove english numbers
        text = re.sub(r'\d+', '', text)

        tokenize_text = jieba.cut(text)

        for word in tokenize_text:
            word = word.encode('utf-8')
            if word in zh_stop_words_list:
                continue
            article_vocab_list.append(word)

        return article_vocab_list

def main(text):
    lang_obj = Chinese()
    words = lang_obj.tokenize(text)
    print '|'.join(words)

if __name__ == '__main__':
    text = "我爱【$98】北京天安门666山东。！哈哈哈"
    print text
    main(text)
