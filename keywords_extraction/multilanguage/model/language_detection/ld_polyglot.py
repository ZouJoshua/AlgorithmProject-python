#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 12/5/19 1:29 PM
@File    : ld_polyglot.py
@Desc    : 

"""

from polyglot.text import Text

from keywords_extraction.multilanguage.core import base
from keywords_extraction.multilanguage.model.language_detection.ld_base import LanguageDetection
from keywords_extraction.multilanguage.core.language import unknownLanguage
from keywords_extraction.multilanguage.util import file_utils

class LanguageDetectionPolyglot(LanguageDetection):
    def __init__(self):
        languages = file_utils.readLanguages(base.languagePath)
        self.__supportLanguages = dict([(language.code, language) for language in languages])

    def detect(self, text):
        text = Text(text)
        code = text.language.code
        return self.__supportLanguages.get(code, unknownLanguage)

    def supportLanguages(self):
        return self.__supportLanguages