# coding:utf-8
# Created by houcunyue on 2017/11/27
from collections import defaultdict
from com.apus.multilingual_keyword_extraction.model.language_detection.LanguageDetectionPolyglot import \
    LanguageDetectionPolyglot

languageDetection = LanguageDetectionPolyglot()
num = defaultdict(lambda: 0)
for line in open('D:\\data\\video\\rec\\tmp\\tag\\part-00000', mode='r', encoding='utf-8'):
    language = languageDetection.detect(line.split(',')[0][1:])
    num[str(language)] += 1
    if language.code not in ['en', 'ko']:
        num['-KO-EN'] += 1
    num['all'] += 1
for k, v in sorted(num.items(), key=lambda d: d[1]):
    print(k, v)
