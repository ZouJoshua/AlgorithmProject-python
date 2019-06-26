#!/usr/bin python
# -*- coding: utf-8 -*-
# @Date    : 2017-06-16 12:25:19
# @Author  : Liulichao (liulichao@apusapps.com)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import spacy

class English:

    def __init__(self):
        self.nlp = spacy.en.English()

    def tokenize(self, text):
        if isinstance(text, str):
            text = text.decode('utf-8')

        doc = self.nlp(text, tag=True, parse=False, entity=False)

        article_vocab_list = []
        for token in doc:
            if token.is_stop or token.is_punct or token.is_space or token.like_num:
                continue
            lemma = token.lemma_
            article_vocab_list.append(lemma)

        return article_vocab_list
