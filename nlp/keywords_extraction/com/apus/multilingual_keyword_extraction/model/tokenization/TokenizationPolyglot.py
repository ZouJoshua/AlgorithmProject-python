# coding:utf-8
# Created by houcunyue on 2017/9/20

from polyglot.text import Text

from com.apus.multilingual_keyword_extraction.core import Base
from com.apus.multilingual_keyword_extraction.model.tokenization.Tokenization import Tokenization
from com.apus.multilingual_keyword_extraction.util import FileUtil


class TokenizationPolyglot(Tokenization):
    def __init__(self, stopwords=set()):
        self.__supportLanguages = set(FileUtil.readLanguages(Base.languagePath))
        self.__stopwords = stopwords

    def token(self, text, language):
        assert language in self.__supportLanguages, 'TokenizationPolyglot do not support {} language.'.format(language)
        words = Text(text).words
        return [word.lower() for word in words if word.lower() not in self.__stopwords]

    def supportLanguages(self):
        return self.__supportLanguages