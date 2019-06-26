# coding:utf-8
# Created by houcunyue on 2017/9/20

from polyglot.text import Text

from com.apus.multilingual_keyword_extraction.core import Base
from com.apus.multilingual_keyword_extraction.model.language_detection.LanguageDetection import LanguageDetection
from com.apus.multilingual_keyword_extraction.core.Language import unknownLanguage
from com.apus.multilingual_keyword_extraction.util import FileUtil

class LanguageDetectionPolyglot(LanguageDetection):
    def __init__(self):
        languages = FileUtil.readLanguages(Base.languagePath)
        self.__supportLanguages = dict([(language.code, language) for language in languages])

    def detect(self, text):
        text = Text(text)
        code = text.language.code
        return self.__supportLanguages.get(code, unknownLanguage)

    def supportLanguages(self):
        return self.__supportLanguages