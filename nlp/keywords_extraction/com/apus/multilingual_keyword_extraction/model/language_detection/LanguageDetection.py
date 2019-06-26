# coding:utf-8
# Created by houcunyue on 2017/9/20

from abc import ABCMeta, abstractmethod

class LanguageDetection(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def detect(self, text):
        pass

    @abstractmethod
    def supportLanguages(self):
        pass