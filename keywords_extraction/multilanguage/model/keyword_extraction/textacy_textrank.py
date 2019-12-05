#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 12/5/19 1:23 PM
@File    : textacy_textrank.py
@Desc    : 

"""

import textacy

from keywords_extraction.multilanguage.model.keyword_extraction.ke_base import KeywordExtraction

class KeywordExtractionTextacyTextrank(KeywordExtraction):
    def __init__(self):
        pass

    def train(self, docs):
        pass

    # text: string text
    def extract(self, text, topK=-1):
        doc = textacy.Doc(text)
        keywords = textacy.keyterms.textrank(doc, n_keyterms=1.0 if topK == -1 else topK)
        return keywords

    def saveModel(self, dirPath):
        pass

    def loadModel(self, dirPath):
        pass