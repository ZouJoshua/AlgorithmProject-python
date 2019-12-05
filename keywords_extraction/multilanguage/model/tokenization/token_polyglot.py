#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 12/5/19 1:42 PM
@File    : token_polyglot.py
@Desc    : 

"""

from polyglot.text import Text

from keywords_extraction.multilanguage.core import base
from keywords_extraction.multilanguage.model.tokenization.token_base import Tokenization
from keywords_extraction.multilanguage.util import file_utils


class TokenizationPolyglot(Tokenization):
    def __init__(self, stopwords=set()):
        self.__supportLanguages = set(file_utils.readLanguages(base.languagePath))
        self.__stopwords = stopwords

    def token(self, text, language):
        assert language in self.__supportLanguages, 'TokenizationPolyglot do not support {} language.'.format(language)
        words = Text(text).words
        return [word.lower() for word in words if word.lower() not in self.__stopwords]

    def supportLanguages(self):
        return self.__supportLanguages