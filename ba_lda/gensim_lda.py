#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/11/8 22:13
@File    : gensim_lda.py
@Desc    : 
"""

import os
import sys
from os.path import dirname

_dirname = dirname(os.path.realpath(__file__))
sys.path.append(dirname(_dirname))

import string
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim import corpora, models

import json
import time
from ast import literal_eval

from ba_lda.lda import log


class EnPreprocess(object):
    """整体流程：
    读取文件：FileRead()filepath to raw
    分割成句子:SenToken()raw to sents
    (词性标注):POSTagger()sent to words[]
    句子分割成词:TokenToWords()将句子分割成词 sent to word[]
    （拼写检查）：WordCheck() 错误的去掉或是等人工改正
    去掉标点，去掉非字母内容:CleanLines()句子，line to cleanLine
    去掉长度小于3的词，小写转换，去停用词：CleanWords(),words[] to cleanWords[]
    词干化:StemWords()把词词干化返回，words to stemWords
    二次清理:再执行一次CleanWords()，使句子更加纯净
    """
    def __init__(self):
        print('English token and stopwords remove...')

    def FileRead(self, filePath):
        """读取内容"""
        _content = []
        with open(filePath, encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                d = json.loads(line)
                text = d['html']
                _content.append(text.strip())
        return _content

    def FileReadBase(self,filePath):
        """读取内容"""
        with open(filePath, 'r', encoding='utf-8') as f:
            raw = f.read()
        return raw

    def WriteResult(self, results, resultPath):
        """将结果保存到另一个文档中"""
        self.mkdir(str(dirname(resultPath)))
        with open(resultPath, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(str(result))
                f.write('\n')

    def SenToken(self, raw):
        """分割成句子"""
        sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sents = sent_tokenizer.tokenize(raw)
        return sents

    def POSTagger(self, sents):
        """词性标注"""
        taggedLine = [nltk.pos_tag(sent) for sent in sents]
        return taggedLine

    def WordTokener(self, sent):
        """将单句字符串分割成词"""
        result = ''
        wordsInStr = nltk.word_tokenize(sent)
        return wordsInStr

    # def WordCheck(self, words):
    #     """拼写检查"""
    #     d = enchant.Dict("en_US")
    #     checkedWords=()
    #     for word in words:
    #         if not d.check(word):
    #             d.suggest(word)
    #             word = input()
    #         checkedWords = (checkedWords, '05')
    #     return checkedWords

    def CleanLines(self, line):
        delEStr = string.punctuation + string.digits #ASCII 标点符号，数字
        remove_punctuation_map = dict((ord(char), None) for char in delEStr)
        # cleanLine= line.translate(remove_punctuation_map) #去掉ASCII 标点符号和空格
        cleanLine = line.translate(remove_punctuation_map) #去掉ASCII 标点符号
        return cleanLine

    def GetStopwords(self, stopword_file=None):
        """Get stopwords from nltk and stopword_file
        Args:
            stopword_file: path of stopword_file
        Returns:
            a set of stopwords
        """
        if stopword_file:
            try:
                with open(stopword_file, 'r') as f:
                    my_stopword = f.read().split("\n")
            except Exception as e:
                my_stopword = ''
        else:
            my_stopword = ''
        return set(stopwords.words('english')).union(my_stopword)

    def CleanWords(self, wordsInStr, stopword_file):
        """去掉标点符号，长度小于3的词以及non-alpha词，小写化"""
        cleanWords=[]
        # stopwords = {}.fromkeys([line.rstrip() for line in open(stopword_file)])
        stopwords = self.GetStopwords(stopword_file=stopword_file)
        for words in wordsInStr:
           cleanWords += [[w.lower() for w in words if w.lower() not in stopwords and 3 <= len(w)]]
        return cleanWords

    def StemWords(self, cleanWordsList):
        """词干化"""
        stemWords=[]
        # porter =nltk.PorterStemmer()#有博士说这个词干化工具效果不好，不是很专业
        # result=[porter.stem(t) for t in cleanTokens]
        for words in cleanWordsList:
            stemWords += [[wn.morphy(w) for w in words]]
        return stemWords

    def WordsToStr(self, stemWords):
        strLine=[]
        for words in stemWords:
            strLine += [w for w in words]
        return strLine

    def mkdir(self, path):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 判断路径是否存在
        # 存在    True
        # 不存在  False
        isExists=os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            print(path+' 创建成功')
            # 创建目录操作函数
            if not os.path.isdir(path):
                os.makedirs(path)
            return True
        else:
            # 如果目录存在则不创建，并提示目录已存在
            print(path + ' 目录已存在')
            return False

    def EnPreMain(self, dir):
        """入口"""
        stopword_file = os.path.join(os.path.abspath(__file__), 'stopwords_en.txt')
        for root, dirs, files in os.walk(dir):
            NLTKRESULTPATH = dirname(root) + os.sep + 'result'
            for eachfiles in files:
                s = time.time()
                log.info('正在处理文件{}'.format(eachfiles))
                croupPath = os.path.join(root, eachfiles)
                # print(croupPath)
                resultPath = os.path.join(NLTKRESULTPATH, eachfiles)
                raws = self.FileRead(croupPath)
                result = list()
                for raw in raws:
                    sents = self.SenToken(raw.lower())
                    # taggedLine=self.POSTagger(sents)#暂不启用词性标注
                    cleanLines = [self.CleanLines(line) for line in sents]
                    words = [self.WordTokener(cl) for cl in cleanLines]
                    # checkedWords=self.WordCheck(words)#暂不启用拼写检查
                    cleanWords = self.CleanWords(words, stopword_file)
                    stemWords = self.StemWords(cleanWords)
                    # cleanWords=self.CleanWords(stemWords)#第二次清理出现问题，暂不启用
                    strLine = self.WordsToStr(stemWords)
                    result.append(strLine)
                log.info("正在写入文件{}".format(resultPath))
                self.WriteResult(result, resultPath) #一个文件暂时存成一行
                e = time.time()
                log.info("耗时{}".format(e-s))

    def StandardTokener(self, raw):
        result = ''
        #还没弄好
        return result

def test_enpreprocess(filepath, num):
    prepro = EnPreprocess()
    corpus = prepro.FileRead(filepath)
    stopword_file = os.path.join(os.path.abspath(__file__), 'stopwords_en.txt')
    results = list()
    for raw in corpus[:num]:
        sents = prepro.SenToken(raw)
        # print(sents)
        cleanLines = [prepro.CleanLines(line) for line in sents]
        # print(cleanLines)
        words = [prepro.WordTokener(cl) for cl in cleanLines]
        # print(words)
        cleanWords = prepro.CleanWords(words, stopword_file)
        # print(cleanWords)
        stemWords = prepro.StemWords(cleanWords)
        # print(stemWords)
        strLine = prepro.WordsToStr(stemWords)
        print(strLine)
        results.append(strLine)

    root = os.path.dirname(filepath)
    NLTKRESULTPATH = dirname(root) + os.sep + 'result'
    resultPath = os.path.join(NLTKRESULTPATH, 'test.txt')
    prepro.WriteResult(results, resultPath)
    return True

if __name__ == "__main__":

    # 存储读取语料 一行语料为一个文档
    log.info('读取存储语料，一行为一个文档')
    filepath = r'C:\Users\zoushuai\Desktop\new9'
    # prepro = EnPreprocess()
    # corpus = prepro.FileRead(filepath)
    # log.info('正在处理{}行文档'.format(len(corpus)))
    #
    # # 语料预处理，分词，去停用词
    # log.info('语料预处理，分词，去停用词')
    # test_enpreprocess(filepath, 3)
    # prepro.EnPreMain(filepath)

    # 读取分词结果，构建词频矩阵
    # log.info('读取分词结果，用gensim库计算文档词频矩阵')
    train_set = []
    corpusfile = r'C:\Users\zoushuai\Desktop\result\part-00000'
    for line in open(corpusfile, 'r').readlines():
        # print(line)
        train_set.append([li for li in literal_eval(line.strip()) if li is not None])
    print(len(train_set))
    print(train_set[:10])
    #
    dictionary = corpora.Dictionary(train_set)
    # print(dictionary)
    # log.info('将训练字典保存下来')
    # dictionary.save('./train_set.dict')
    # corpus = [dictionary.doc2bow(text) for text in train_set]
    # print(corpus[0])  #查看第一篇文档词频 （单词 ID，词频）
    # print(dictionary.token2id)  # 来查看每个单词的 ID
    # log.info('将corpus持久化到磁盘中')
    # corpora.MmCorpus.serialize('train_set.mm', corpus)
    # 从磁盘中读取corpus
    log.info('从磁盘中读取corpus')
    corpus = corpora.MmCorpus('./train_set.mm')

    lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=100)
    # 打印前20个topic的词分布
    lda.print_topics(20)
    # 打印id为20的topic的词分布
    lda.print_topic(20)

    # 模型的保存/ 加载
    lda.save('news_lda.model')
    # lda = models.ldamodel.LdaModel.load('news_lda.model')


