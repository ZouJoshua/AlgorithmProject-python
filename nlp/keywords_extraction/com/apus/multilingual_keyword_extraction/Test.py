# coding:utf-8
# Created by houcunyue on 2017/9/19

import os

from com.apus.multilingual_keyword_extraction.core.Language import unknownLanguage, Language
from com.apus.multilingual_keyword_extraction.model.sentence.SentencePolyglot import SentencePolyglot
from com.apus.multilingual_keyword_extraction.model.keyword_extraction.KeywordExtractionTFIDF import KeywordExtractionTFIDF
from com.apus.multilingual_keyword_extraction.model.language_detection.LanguageDetectionPolyglot import \
    LanguageDetectionPolyglot
from com.apus.multilingual_keyword_extraction.model.stem.StemNLTK import StemNLTK
from com.apus.multilingual_keyword_extraction.model.tokenization.TokenizationPolyglot import TokenizationPolyglot
from com.apus.multilingual_keyword_extraction.model.tokenization_pos.TokenizationPosPolyglot import \
    TokenizationPosPolyglot
from com.apus.multilingual_keyword_extraction.util import FileUtil, DataUtil
from com.apus.multilingual_keyword_extraction.core import Base

# englishPunctuations = "!\"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~"
# chinesePunctuations = "\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）：；《）《》“”()»〔〕-"
# puncs = set()
# for punc in englishPunctuations + chinesePunctuations:
#     puncs.add(str(punc))
# print(len(puncs))
# FileUtil.writeLines(Base.punctuationStopwordPath, puncs)
#
# import pycld2 as cld2
# languages = [ code.lower() + '\t' + name.lower() for name, code in cld2.LANGUAGES if not name.startswith("X_")]
# print(len(languages))
# FileUtil.writeLines(Base.languageInfoPath, languages)

# languages = FileUtil.readLanguages(Base.languagePath)
# print('languages:', [language.__str__() for language in languages])

# tokenizationPosSupportLanguages = [dir + '\t' + languages[dir] for dir in os.listdir('C:/Users/houcunyue/Downloads/polyglot_data/pos2') if dir in languages.keys()]
# print(len(tokenizationPosSupportLanguages))
# FileUtil.writeLines(Base.tokenizationPosSupportLanguagePath, tokenizationPosSupportLanguages)

# from nltk.stem_nltk import SnowballStemmer
# print(SnowballStemmer.languages)
# print(len(SnowballStemmer.languages))
# stemSupportLanguages = [languagesReverse[v] + '\t' + v for v in SnowballStemmer.languages if v in languagesReverse.keys()]
# print(stemSupportLanguages)
# print(len(stemSupportLanguages))
# FileUtil.writeLines(Base.stemSupportLanguagePath, stemSupportLanguages)

text = """Apache Spark is an open-source cluster-computing framework. Originally developed at the University of California, Berkeley's AMPLab, the Spark codebase was later donated to the Apache Software Foundation, which has maintained it since. Spark provides an interface for programming entire clusters with implicit data parallelism and fault-tolerance."""
text += """ Apache Spark provides programmers with an application programming interface centered on a data structure called the resilient distributed dataset (RDD), a read-only multiset of data items distributed over a cluster of machines, that is maintained in a fault-tolerant way. It was developed in response to limitations in the MapReduce cluster computing paradigm, which forces a particular linear dataflow structure on distributed programs: MapReduce programs read input data from disk, map a function across the data, reduce the results of the map, and store reduction results on disk. Spark's RDDs function as a working set for distributed programs that offers a (deliberately) restricted form of distributed shared memory."""
print('text:', text)

languageDetection = LanguageDetectionPolyglot()
language = languageDetection.detect(text)
print('LanguageDetectionPolyglot:', language)

stem = StemNLTK()

stopwords = FileUtil.readStopwords(Base.punctuationStopwordPath)
englishStopwords = FileUtil.readStopwords(Base.englishStopwordPath)
stopwords |= englishStopwords

sentence = SentencePolyglot()
if (language in sentence.supportLanguages()):
    tokens = sentence.sentence(text, language)
    print('SentencePolyglot:', tokens)
else:
    print('SentencePolyglot do not support {} language.'.format(language))

tokenization = TokenizationPolyglot(stopwords)
if (language in tokenization.supportLanguages()):
    tokens = tokenization.token(text, language)
    print('TokenizationPolyglot:', tokens)
else:
    print('TokenizationPolyglot do not support {} language.'.format(language))

if(language in stem.supportLanguages()):
    tokenStems = stem.stem(tokens, language)
    print('StemPolyglot:', tokenStems)
else:
    print('StemPolyglot do not support {} language.'.format(language))

tokenizationPos = TokenizationPosPolyglot()
if(language in tokenizationPos.supportLanguages()):
    tokenPoses = tokenizationPos.tokenPos(text, language)
    print('TokenizationPosPolyglot:', tokenPoses)
    if (language in stem.supportLanguages()):
        tokenPosStems = stem.stem(tokenPoses, language)
        print('StemPolyglot:', tokenPosStems)
    else:
        print('StemPolyglot do not support {} language.'.format(language))

else:
    print('TokenizationPosPolyglot do not support {} language.'.format(language))

docs = [tokenization.token(t, language) for t in text.split('.') if len(t) > 0]
keywordExtraction = KeywordExtractionTFIDF()
keywordExtraction.train(docs)
for doc in docs:
    print('KeywordExtractionTFIDF', keywordExtraction.extract(doc, 5))

# keywordExtraction.saveModel(Base.modelPath + 'tfidf')
# keywordExtraction.loadModel(Base.modelPath + 'tfidf')
# for doc in docs:
#     print('KeywordExtractionTFIDF', keywordExtraction.extract(doc, 5))
