# coding:utf-8
# Created by houcunyue on 2017/9/22

from polyglot.text import Text

from com.apus.multilingual_keyword_extraction.core import Base
from com.apus.multilingual_keyword_extraction.model.sentence.Sentence import Sentence
from com.apus.multilingual_keyword_extraction.util import FileUtil

class SentencePolyglot(Sentence):
    def __init__(self):
        self.__supportLanguages = set(FileUtil.readLanguages(Base.languagePath))

    def sentence(self, text, language):
        assert language in self.__supportLanguages, 'SentencePolyglot do not support {} language.'.format(language)
        sentences = Text(text).sentences
        return [sentence.raw for sentence in sentences]

    def supportLanguages(self):
        return self.__supportLanguages