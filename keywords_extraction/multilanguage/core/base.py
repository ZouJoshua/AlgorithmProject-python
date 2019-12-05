#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 12/5/19 1:10 PM
@File    : base.py
@Desc    : 

"""



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