#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 12/5/19 1:44 PM
@File    : tpos_polyglot.py
@Desc    : 

"""

from polyglot.text import Text

from keywords_extraction.multilanguage.core import base
from keywords_extraction.multilanguage.model.tokenization_pos.tpos_base import TokenizationPos
from keywords_extraction.multilanguage.util import file_utils


class TokenizationPosPolyglot(TokenizationPos):
    def __init__(self, stopwords=set()):
        self.__supportLanguages = set(file_utils.readLanguages(base.tokenizationPosPolyglotSupportLanguagePath))
        self.__stopwords = stopwords

    def tokenPos(self, text, language):
        assert language in self.__supportLanguages, 'TokenizationPosPolyglot do not support {} language.'.format(language)
        wordPoses = Text(text).pos_tags
        return [(word.lower(), pos) for word, pos in wordPoses if word.lower() not in self.__stopwords]

    def supportLanguages(self):
        return self.__supportLanguages