# coding:utf-8
# Created by houcunyue on 2017/9/20
from com.apus.multilingual_keyword_extraction.core import Base
from com.apus.multilingual_keyword_extraction.model.keyword_extraction.third_party import rake

from com.apus.multilingual_keyword_extraction.model.keyword_extraction.KeywordExtraction import KeywordExtraction

class KeywordExtractionRake(KeywordExtraction):
    def __init__(self, stopwordPath=Base.englishStopwordPath, minLength=5, maxWordNum=3, minTimes=2):
        self.__stopwordPath = stopwordPath
        self.__minLength = minLength
        self.__maxWordNum = maxWordNum
        self.__minTimes = minTimes

    def train(self, docs):
        pass

    # text: string text
    def extract(self, text, topK=-1):
        rake_object = rake.Rake(self.__stopwordPath, self.__minLength, self.__maxWordNum, self.__minTimes)
        keywords = rake_object.run(text)
        return keywords[:topK if topK != -1 else len(keywords)]

    def saveModel(self, dirPath):
        pass

    def loadModel(self, dirPath):
        pass
