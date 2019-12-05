#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 12/5/19 1:40 PM
@File    : stem_nltk.py
@Desc    : 

"""

from nltk.stem import SnowballStemmer

from keywords_extraction.multilanguage.core import base
from keywords_extraction.multilanguage.model.stem.stem_base import Stem
from keywords_extraction.multilanguage.util import file_utils

class StemNLTK(Stem):
    def __init__(self):
        self.__supportLanguages = set(file_utils.readLanguages(base.stemNLTKSupportLanguagePath))

    def stem(self, words, language):
        assert language in self.__supportLanguages, 'StemPolyglot do not support {} language.'.format(language)
        stemmer = SnowballStemmer(language.name)
        return [stemmer.stem(word) if type(word) == str else (stemmer.stem(word[0]), word[1])  for word in words]

    def supportLanguages(self):
        return self.__supportLanguages
