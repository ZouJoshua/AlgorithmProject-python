# coding:utf-8
# Created by houcunyue on 2017/9/20

from abc import ABCMeta, abstractmethod

class KeywordExtraction(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def train(self, docs):
        pass

    @abstractmethod
    def extract(self, doc, topK):
        pass

    @abstractmethod
    def saveModel(self, filePath):
        pass

    @abstractmethod
    def loadModel(self, filePath):
        pass