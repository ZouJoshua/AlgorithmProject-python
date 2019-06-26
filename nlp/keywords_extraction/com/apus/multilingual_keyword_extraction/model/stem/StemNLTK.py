# coding:utf-8
# Created by houcunyue on 2017/9/20

from nltk.stem import SnowballStemmer

from com.apus.multilingual_keyword_extraction.core import Base
from com.apus.multilingual_keyword_extraction.model.stem.Stem import Stem
from com.apus.multilingual_keyword_extraction.util import FileUtil

class StemNLTK(Stem):
    def __init__(self):
        self.__supportLanguages = set(FileUtil.readLanguages(Base.stemNLTKSupportLanguagePath))

    def stem(self, words, language):
        assert language in self.__supportLanguages, 'StemPolyglot do not support {} language.'.format(language)
        stemmer = SnowballStemmer(language.name)
        return [stemmer.stem(word) if type(word) == str else (stemmer.stem(word[0]), word[1])  for word in words]

    def supportLanguages(self):
        return self.__supportLanguages