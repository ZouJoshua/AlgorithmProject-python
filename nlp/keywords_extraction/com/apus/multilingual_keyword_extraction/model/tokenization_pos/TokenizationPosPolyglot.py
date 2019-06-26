# coding:utf-8
# Created by houcunyue on 2017/9/20

from polyglot.text import Text

from com.apus.multilingual_keyword_extraction.core import Base
from com.apus.multilingual_keyword_extraction.model.tokenization_pos.TokenizationPos import TokenizationPos
from com.apus.multilingual_keyword_extraction.util import FileUtil


class TokenizationPosPolyglot(TokenizationPos):
    def __init__(self, stopwords=set()):
        self.__supportLanguages = set(FileUtil.readLanguages(Base.tokenizationPosPolyglotSupportLanguagePath))
        self.__stopwords = stopwords

    def tokenPos(self, text, language):
        assert language in self.__supportLanguages, 'TokenizationPosPolyglot do not support {} language.'.format(language)
        wordPoses = Text(text).pos_tags
        return [(word.lower(), pos) for word, pos in wordPoses if word.lower() not in self.__stopwords]

    def supportLanguages(self):
        return self.__supportLanguages