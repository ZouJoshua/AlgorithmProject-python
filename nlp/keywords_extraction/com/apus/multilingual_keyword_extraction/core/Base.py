# coding:utf-8
# Created by houcunyue on 2017/9/19

import os
pwdDir = os.path.split(os.path.realpath(__file__))[0]
dataDir = pwdDir[0:pwdDir.rfind('com')]

dataPath = dataDir + '/data/'

languagePath = dataPath + 'support_language/language'

tokenizationPosPolyglotSupportLanguagePath = dataPath + 'support_language/tokenization_pos_polyglot'

stemNLTKSupportLanguagePath = dataPath + 'support_language/stem_nltk'

punctuationStopwordPath = dataPath + 'stopword/punctuation'

englishStopwordPath = dataPath + 'stopword/EnglishStoplist.txt'

modelPath = dataPath + 'model/'