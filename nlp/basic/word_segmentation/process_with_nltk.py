#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/11/8 22:13
@File    : process_with_nltk.py
@Desc    : 
"""

import os
import sys
from os.path import dirname

_dirname = dirname(os.path.realpath(__file__))
sys.path.append(dirname(_dirname))

import time
from os.path import dirname
import logging

import string
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')


class WordSegmenPreprocess(object):
    """整体流程：
    分割成句子:SenToken()raw to sents
    (词性标注):POSTagger()sent to words[]
    句子分割成词:TokenToWords()将句子分割成词 sent to word[]
    （拼写检查）：WordCheck() 错误的去掉或是等人工改正
    去掉标点，去掉非字母内容:CleanLines()句子，line to cleanLine
    去掉长度小于3的词，小写转换，去停用词：CleanWords(),words[] to cleanWords[]
    词干化:StemWords()把词词干化返回，words to stemWords
    二次清理:再执行一次CleanWords()，使句子更加纯净
    """
    def __init__(self, text, logger=None, stopwordsfile=None):
        self.text = text
        self.stopword_file = stopwordsfile

        if logger:
            self.log = logger
        else:
            self.log = logging.getLogger('word-segmen-preprocess')
        print('English token and stopwords remove...')


    def get_words(self):
        """入口"""
        sents = self._sen_token()
        cleanLines = [self._clean_lines(sent) for sent in sents]
        words = [self._word_tokener(cl) for cl in cleanLines]
        print(words)
        # checkedWords=self.WordCheck(words)#暂不启用拼写检查
        cleanWordsList = self._clean_words(words)
        print(cleanWordsList)
        # stemWords = self._stem_words(cleanWords)
        # cleanWords=self.CleanWords(stemWords)#第二次清理出现问题，暂不启用
        strLine = self._words2list(cleanWordsList)
        print(strLine)
        return strLine

    def _sen_token(self):
        """分割成句子"""
        sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sents = sent_tokenizer.tokenize(self.text)
        return sents

    def _pos_tagger(self, sents):
        """词性标注"""
        taggedLine = [nltk.pos_tag(sent) for sent in sents]
        return taggedLine

    def _word_tokener(self, sent):
        """将单句字符串分割成词"""
        return nltk.word_tokenize(sent)

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

    def _clean_lines(self, line):
        delEStr = string.punctuation + string.digits  # ASCII 标点符号，数字
        remove_punctuation_map = dict((ord(char), None) for char in delEStr)
        # cleanLine= line.translate(remove_punctuation_map) #去掉ASCII 标点符号和空格
        cleanLine = line.translate(remove_punctuation_map)  # 去掉ASCII 标点符号
        return cleanLine

    def _get_stopwords(self):
        """Get stopwords from nltk and stopword_file
        Args:
            stopword_file: path of stopword_file
        Returns:
            a set of stopwords
        """
        my_stopword = ''
        if self.stopword_file:
            if os.path.exists(self.stopword_file):
                try:
                    with open(self.stopword_file, 'r') as f:
                        my_stopword = f.read().split("\n")
                except Exception as e:
                    pass
                    # self.log.error('打开停用词文件失败{}'.format(e))
            # self.log.warming('停用词文件不存在')

        return set(stopwords.words('english')).union(my_stopword)

    def _clean_words(self, sents_words_list):
        """去掉标点符号，长度小于3的词以及non-alpha词，小写化"""
        cleanWords=[]
        # stopwords = {}.fromkeys([line.rstrip() for line in open(stopword_file)])
        stopwords = self._get_stopwords()
        for words in sents_words_list:
           cleanWords += [[w.lower() for w in words if w.lower() not in stopwords and 3 <= len(w)]]
        return cleanWords

    def _stem_words(self, sents_words_list):
        """词干化"""
        stemWords=[]
        # porter =nltk.PorterStemmer()  # 有博士说这个词干化工具效果不好，不是很专业
        # result=[porter.stem(t) for t in cleanTokens]
        for word_list in sents_words_list:
            stemWords += [[wn.morphy(w) for w in word_list]]
        return stemWords

    def _words2list(self, sents_words_list):
        strLine=[]
        for words in sents_words_list:
            strLine += [w for w in words if w]
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

    def _standard_tokener(self, raw):
        result = ''
        #还没弄好
        return result


if __name__ == '__main__':
    stopwordsDir = dirname(dirname(os.path.realpath(__file__)))
    stopword_file = os.path.join(stopwordsDir, 'stopwords_en.txt')
    print(stopword_file)
    text = """Representatives of wireless carriers and banks met an inter-ministerial group comprising officials from finance and telecom ministries over the week to discuss the sector’s problems. Older operators have been challenged by an aggressive new rival in Reliance Jio Infocomm Ltd. and the central bank has raised concerns that loans to the sector were at a risk of turning bad. Here are the issues raised during the meetings, based on what officials from banks, companies and the government said... Reliance Jio: Rivals To Blame For Financial Stress Rival telecom operators only had themselves to blame for financial stress. Rivals’ debt has gone up because they didn’t invest in new technology. Opposed any relaxation on spectrum payments. Contribution to the Universal Service Obligation Fund (USoF) should be relaxed. Any measures should be implemented prospectively, not retrospectively. (Source: Company officials present in the meeting to BloombergQuint) Bharti Airtel: 5-Year Moratorium On Spectrum Payments Reliance Jio has misrepresented reality. Industry revenue has declined by 20 percent in three quarters. Fixed termination charges should be on a full-cost basis. Increase moratorium on spectrum payments from two to five years. Allow installments for 15 years instead of 10. Need for a single licence for carriers operating pan-India. (Source: Company officials present in the meeting to BloombergQuint) Vodafone: No Cut In Termination Charge Mobile termination charge at 14 paise is way below costs; any more cuts will impact rural services. Spectrum usage charges are among the highest in the world; need to consider whether these are required. Contribution to USoF should be brought down from 5 percent of the adjusted gross revenue to 3 percent. Licence fees should be subsumed into into Goods and Services Tax. If not that, then GST should be brought to 5 percent from 18 percent like other core sectors. (Source: Vodafone official present in the meeting to BloombergQuint) Idea Cellular: Floor Price For Tariffs The government must ensure a stable tariff regime; suggested a floor price. Interconnection usage charges, which carriers pay for cross-network calls, should be high enough for operators to recover costs. Telecom a highly taxed industry. Data prices should come down. (Source: People present in the meeting to BloombergQuint) MTNL: Capital Infusion Facing legacy issues. Employee costs at Rs 2,800 crore are 90 percent of the income. Competition requires capital; looking for an infusion of Rs 8,000-10,000 crore over a period of time. (Source: MTNL’s chairman and managing director while interacting with the media) Lenders: Risk Of Defaults High levels of stressed assets in the telecom sector; flagged the possibility of default by operators. Declining revenues adding to stress. Debt resolution measures, capital infusion needed to boost liquidity. Inter-ministerial group may call another meeting with banks. (Source: Officials present in the meeting to BloombergQuint)"""
    preprocess = WordSegmenPreprocess(text, stopwordsfile=stopword_file)
    words = preprocess.get_words()