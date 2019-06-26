# coding:utf-8
# Created by houcunyue on 2017/9/20

from abc import ABCMeta, abstractmethod

class Tokenization(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def token(self, text):
        pass

    @abstractmethod
    def supportLanguages(self):
        pass