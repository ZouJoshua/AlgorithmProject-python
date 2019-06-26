# coding:utf-8
# Created by houcunyue on 2017/9/19

import os

from com.apus.multilingual_keyword_extraction.core import Base
from com.apus.multilingual_keyword_extraction.model.keyword_extraction.KeywordExtractionRake import \
    KeywordExtractionRake
from com.apus.multilingual_keyword_extraction.model.keyword_extraction.KeywordExtractionTextacySinglerank import \
    KeywordExtractionTextacySinglerank
from com.apus.multilingual_keyword_extraction.model.keyword_extraction.KeywordExtractionTextacyTextrank import KeywordExtractionTextacyTextrank
from com.apus.multilingual_keyword_extraction.model.keyword_extraction.KeywordExtractionTFIDF import \
    KeywordExtractionTFIDF
from com.apus.multilingual_keyword_extraction.model.language_detection.LanguageDetectionPolyglot import \
    LanguageDetectionPolyglot
from com.apus.multilingual_keyword_extraction.model.stem.StemNLTK import StemNLTK
from com.apus.multilingual_keyword_extraction.model.tokenization.TokenizationPolyglot import TokenizationPolyglot
from com.apus.multilingual_keyword_extraction.util import FileUtil

articlePath = Base.dataPath + 'experience/en/articles/'
keywordPath = Base.dataPath + 'experience/en/keywords/'

texts = [(fileName[0:fileName.find('.')], '.'.join(FileUtil.readLines(articlePath + fileName))) for fileName in os.listdir(articlePath)]
print('texts:', texts)
oriKeywords = [(fileName[0:fileName.find('.')], ', '.join(FileUtil.readLines(keywordPath + fileName))) for fileName in os.listdir(articlePath)]
print('oriKeywords:', oriKeywords)

languageDetection = LanguageDetectionPolyglot()
language = languageDetection.detect('\n'.join([text[1] for text in texts]))
print('language:', language)

stopwords = FileUtil.readStopwords(Base.punctuationStopwordPath)
tokenization = TokenizationPolyglot(stopwords)
stem = StemNLTK()

docs = [(text[0], stem.stem(tokenization.token(text[1], language), language)) for text in texts]

keywordExtractionTFIDF = KeywordExtractionTFIDF()
keywordExtractionTFIDF.train([doc[1] for doc in docs])

keywordExtractionTextacyTextrank = KeywordExtractionTextacyTextrank()
keywordExtractionTextacySinglerank = KeywordExtractionTextacySinglerank()
keywordExtractionRake = KeywordExtractionRake()
for i in range(len(docs)):
    print('OriKeywords:', oriKeywords[i][0], oriKeywords[i][1])
    print('KeywordExtractionTFIDF:', docs[i][0], ', '.join([keyword[0] for keyword in keywordExtractionTFIDF.extract(docs[i][1], 10)]))
    print('KeywordExtractionTextacyTextrank:', texts[i][0], ', '.join([keyword[0] for keyword in keywordExtractionTextacyTextrank.extract(texts[i][1], 10)]))
    print('KeywordExtractionTextacySinglerank:', texts[i][0], ', '.join([keyword[0] for keyword in keywordExtractionTextacySinglerank.extract(texts[i][1], 10)]))
    print('KeywordExtractionRake:', texts[i][0], ', '.join([keyword[0] for keyword in keywordExtractionRake.extract(texts[i][1], 10)]))
    print()
