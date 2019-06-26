# coding:utf-8
# Created by houcunyue on 2017/9/20

import textacy

from com.apus.multilingual_keyword_extraction.model.keyword_extraction.KeywordExtraction import KeywordExtraction

class KeywordExtractionTextacySinglerank(KeywordExtraction):
    def __init__(self):
        pass

    def train(self, docs):
        pass

    # text: string text
    def extract(self, text, topK=-1):
        doc = textacy.Doc(text)
        keywords = textacy.keyterms.singlerank(doc, n_keyterms=1.0 if topK == -1 else topK)
        return keywords

    def saveModel(self, dirPath):
        pass

    def loadModel(self, dirPath):
        pass
