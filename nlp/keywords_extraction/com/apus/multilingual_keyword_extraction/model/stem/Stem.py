# coding:utf-8
# Created by houcunyue on 2017/9/20

from abc import ABCMeta, abstractmethod

class Stem(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def stem(self, words, language):
        pass

    @abstractmethod
    def supportLanguages(self):
        pass