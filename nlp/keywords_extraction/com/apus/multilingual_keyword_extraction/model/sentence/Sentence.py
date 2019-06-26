# coding:utf-8
# Created by houcunyue on 2017/9/22

from abc import ABCMeta, abstractmethod

class Sentence(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def token(self, text):
        pass

    @abstractmethod
    def supportLanguages(self):
        pass