#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-4-19 下午2:22
@File    : v_topic_preprocess.py
@Desc    : 视频topic服务文本预处理
"""


import json
import langid
import re
import math
import string
import os
import sys

from nltk.corpus import stopwords
from collections import Counter
from nltk.stem.porter import*


from langdetect import detect
import nltk
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
nltk.download('punkt')
nltk.download('stopwords')


def read_data(file, stopline=None):
    v_file = open(file, 'r')
    countFlag = 0
    while True:
        countFlag += 1
        _line = v_file.readline().strip()
        if countFlag == stopline or not _line:
            v_file.close()
            break
        else:
            line = json.loads(_line)
            line['lang'] = langid.classify(line['article_title'])[0]
            # line['lang'] = detect(line['article_title'])
            if line['resource_type'] == 20002 or line['resource_type'] == 6:
                line['url'] = "https://www.youtube.com/watch?v=" + line['source_url']
            else:
                line['url'] = line['source_url']

            yield line
            # _out.append(line)


class CleanText(object):

    def __init__(self, text, lower=False):
        if lower:
            self._text = text.lower()
        else:
            self._text = text
        self.clean_text = self.clean()


    def clean(self):
        # print(self._text)
        no_html = self._clean_html(self._text)
        # print("_______________________________________________")
        # print(no_html)
        no_mail = self._clean_mail(no_html)
        # print("_______________________________________________")
        # print(no_mail)
        no_ads = self._remove_ads(no_mail)
        # print("_______________________________________________")
        # print(no_ads)
        return self._remove_emoji(no_ads)

    @staticmethod
    def _remove_ads(text):
        ads_list = ['google plus', 'google', 'facebook', 'twitter', 'instagram', 'youtube', 'thank you',
                    'subscribe', 'website', 'for more details', "email address",
                    "for more videos", "free download", "download app", "app link",
                    "app download link", "android app", "playstore", "download", "follow me", "follow us"
                    "for business enquiries contact here", "thanks for watching", "thanks", "visit my blog"]
        for i in ads_list:
            text = text.replace(i, " ")

        return text

    @staticmethod
    def _remove_emoji(text):
        cleaned_text = ""
        for c in text:
            if (ord(c) >= 65 and ord(c) <= 126) or (ord(c) >= 32 and ord(c) <= 63):
                cleaned_text += c
        return cleaned_text

    @staticmethod
    def _clean_html(text):
        # 去除网址
        pattern = re.compile(r'(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
        # pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-zA-Z][0-9a-zA-Z]))+')
        url_list = re.findall(pattern, text)
        for url in url_list:
            text = text.replace(url, " ")
        return text.replace("( )", " ")

    @staticmethod
    def _clean_mail(text):
        # 去除邮箱
        pattern = re.compile(r"\w+[-_.]*[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}")
        mail_list = re.findall(pattern, text)
        for mail in mail_list:
            # if type(mail) != str:
            #     print(mail)
            #     print(text)
            text = text.replace(mail, " ")
        return text



class PreProcessing(object):

    def __init__(self, text, stopwords):
        """Preprocessing of text
        Args:
            text: string of text
            stopwords: list of stopwords
        Returns：

        """
        self._text = text
        self.stopwords = stopwords

    def split_text_by_symbol(self):
        symbol_list = ["\n", "|"]
        paragraph_list = [i.split("|") for i in self._text.split("\n")]
        sens = list()
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        for _line_list in paragraph_list:
            _sen = [line.strip().translate(remove_punctuation_map) for line in _line_list if line.strip()]
            sens.append(_sen)

        return sens

    def get_ngrams_feature(self, n=4):
        ngs = list()
        for i in range(n):
            ng_ = list()
            for lines in self.split_text_by_symbol():
                if lines:
                    for line in lines:
                        if line:
                            _ng = self._ngrams(line, i+1)
                            ng_ += _ng
            ngs.append(ng_)
        return ngs


    def _ngrams(self, text, n):
        n_grams = ngrams(word_tokenize(text), n)
        return ['_'.join(grams) for grams in n_grams]


    def count_term(self):
        """Calculate the word frequency after cleaning"""
        filtered = [w for i in self.get_ngrams_feature(n=3) for w in i if not w in self.stopwords]
        count = Counter(filtered)
        return count


class CalculateTFIDF(object):

    def __init__(self, word, count, count_list=None):
        """Calculate word frequency
        Args:
            word:
            count:
            count_list
        Returns:
            TF-IDF of some keywords
        """
        self.word = word
        self.count = count

        if count_list:
            self.count_list = count_list
        else:
            self.count_list = count

    def _tokens_frequency(self):
        """Calculate tokens frequency"""
        return self.count[self.word] / sum(self.count.values())

    def _n_containing(self):
        return sum(1 for count in self.count_list if self.word in count)

    def _inverse_document_frequency(self):
        """Calculate the inverse document frequency"""
        return math.log(len(self.count_list) / (1 + self._n_containing()))

    def tfidf(self):
        """Calculate TF-IDF"""
        return self._tokens_frequency() * self._inverse_document_frequency()




class LdaProcess(object):

    def __init__(self, file, outfile, filtered_outfile, tf_idf_file,
                 vocab_file, docword_file, word_countfile):
        self._f = file
        self._of = outfile
        self._fo = filtered_outfile
        self._tif = tf_idf_file
        self._vf = vocab_file
        self._df = docword_file
        self._wcf = word_countfile

    def get_ldaprocess_result_file(self):
        self.write_corpus_to_localfile(self._f, self._of)
        # corpus_list = read_corpus_from_localfile(outfile)
        self.filter_tf(self._of, self._fo, self._wcf, limitnum=6)
        # get_words_tfidf(filtered_outfile, tf_idf_file)
        self.gen_vocab(self._fo, self._vf)
        self.gen_docword(self._fo, self._vf, self._df)

    def get_stopwords(self, stopword_file=None):
        """Get stopwords from nltk and stopword_file
        Args:
            stopword_file: path of stopword_file
        Returns:
            a set of stopwords
        """
        if stopword_file:
            try:
                my_stopword = open(stopword_file).read().split("\n")
            except Exception as e:
                my_stopword = ''
        else:
            my_stopword = ''
        return set(stopwords.words('english')).union(my_stopword)

    def produce_corpus(self, file):
        sw = self.get_stopwords(stopword_file='../data/video_stopwords.txt')
        for i in read_data(file):
            if 'id' in i.keys():
                if i['lang'] != 'hi':
                    # print(i['url'])
                    _id = i['id']
                    title = CleanText(i['article_title'], lower=True).clean_text
                    content = CleanText(i['text'], lower=True).clean_text
                    text = title + "\n" + content
                    # print(text)
                    # print("********************")
                    counter_term = PreProcessing(text, sw).count_term()
                    yield {"id": _id, "tf": counter_term}

    def write_corpus_to_localfile(self, datafile, outfile):
        print(">>> 正在写语料到本地文件...")
        _outf = open(outfile, 'w')
        for doc in self.produce_corpus(datafile):
            # print(doc)
            _outf.write(json.dumps(doc) + '\n')
            sys.stdout.flush()
            _outf.flush()
        _outf.close()
        print(">>> 本地文件已写入:{}".format(outfile))

    def read_corpus_from_localfile(self, corpusfile):
        print(">>> 正在读取本地语料文件...")
        _corpus = list()
        _cf = open(corpusfile, 'r')
        while True:
            _line = _cf.readline().strip()
            if _line:
                line = json.loads(_line)
                _corpus.append(line)
            else:
                _cf.close()
                break
        print(">>> 本地文件已读取完成")
        return _corpus

    def get_words_tfidf(self, corpusfile, outfile):
        """Get tfidf of text's top k keywords
        Args:
            text: string of text
            stopword_file: path of stopword_file
            corpus: a list of
            topk: k words after sorting
        Returns:
            a dict (keyword, TFIDF) of text's topk keywords
        """
        print(">>> 准备计算tfidf...")
        corpus = self.read_corpus_from_localfile(corpusfile)

        _of = open(outfile, 'w')
        for i, counter_term in enumerate(corpus):
            result = dict()
            word_score = {word: CalculateTFIDF(word, counter_term['tf'], count_list=corpus).tfidf() for word in
                          counter_term['tf'].keys()}
            # print("第{}文章的tfidf结果\n{}".format(i, word_score))
            result['id'] = counter_term['id']
            result['tf-idf'] = word_score
            _of.write(json.dumps(result) + '\n')
        _of.close()
        print(">>> 计算已完成，已写入文件:{}".format(outfile))

    def filter_tf(self, corpusfile, new_corpusfile, word_countfile, limitnum=2):
        print(">>> 正在过滤词频、长度，重新生成语料文件...")
        _count = dict()
        corpus_list = self.read_corpus_from_localfile(corpusfile)
        for _doc in corpus_list:
            for k, v in _doc['tf'].items():
                if k in _count.keys():
                    _count[k] += v
                else:
                    _count[k] = 1
        count = dict()
        for _k, _v in _count.items():
            if _v < limitnum or len(_k) > 50:
                count[_k] = _v
        _nf = open(new_corpusfile, 'w')
        for doc in corpus_list:
            new_tf = dict()
            for k, v in doc['tf'].items():
                if k not in count.keys():
                    new_tf[k] = v
            doc.update({'tf': new_tf})
            _nf.write(json.dumps(doc) + '\n')
            sys.stdout.flush()
            _nf.flush()
        print(">>> 语料文件已重新生成:{}".format(new_corpusfile))
        print(">>> 生成统计词汇文件")
        wcf = open(word_countfile, 'w')
        sorted_words = sorted(_count.items(), key=lambda x:x[1], reverse=True)
        for word in sorted_words:
            wcf.write("{}\t{}\n".format(word[0], word[1]))
        wcf.close()
        print(">>> 统计词汇文件已生成：{}".format(word_countfile))
        return

    def gen_vocab(self, tf_file, vocab_file):
        print(">>> 正在生成词汇文件...")
        corpus = self.read_corpus_from_localfile(tf_file)
        vf = open(vocab_file, 'w')
        vocab_set = set()
        for _doc in corpus:
            for k, v in _doc['tf'].items():
                vocab_set.add(k)
        for word in sorted(vocab_set):
            vf.write(word + "\n")
        vf.close()
        print(">>> 词汇文件已生成:{}".format(vocab_file))

    def gen_docword(self, tf_file, vocab_file, docword_file):
        print(">>> 正在生成文档词汇文件...")
        with open(vocab_file, 'r') as f:
            # vocab_list = [vocab.strip() for vocab in f.readlines()]
            vocab_dict = dict()
            for i, vocab in enumerate(f.readlines()):
                vocab_dict[vocab.strip()] = i

        df = open(docword_file, 'w')
        corpus = self.read_corpus_from_localfile(tf_file)
        did_count = 0
        for _doc in corpus:
            did_count += 1
            _did = _doc['id']
            for k, v in _doc['tf'].items():
                # wid = vocab_list.index(k)
                if k in vocab_dict.keys():
                    wid = vocab_dict[k]
                    df.write("{}|{}|{}\n".format(did_count, wid, v))
        df.close()
        print(">>> 文档词汇文件已生成:{}".format(docword_file))


def main():
    base_dir = os.path.dirname(os.path.realpath(__file__))

    # test
    # print(base_dir)
    # file = os.path.join(base_dir, 'data', 'test')
    # outfile = os.path.join(base_dir, 'data', 'tf')
    # file = './lightlda_data/test'
    # outfile = './lightlda_data/test_tf'
    # filtered_outfile = './lightlda_data/test_filtered_tf'
    # tf_idf_file = './lightlda_data/test_tf_idf'
    # vocab_file = './lightlda_data/test_vocab.video.txt'
    # docword_file = './lightlda_data/test_docword.video.txt'
    # wordcount_file = "./lightlda_data/test_vocabcount"

    # prod
    file = '/data/zoushuai/video/v_topic/v_topic.json'
    outfile = '/data/zoushuai/video/v_topic/v_tf'
    filtered_outfile = '/data/zoushuai/video/v_topic/v_filtered_tf'
    tf_idf_file = '/data/zoushuai/video/v_topic/v_tf_idf'
    vocab_file = '/data/zoushuai/video/v_topic/vocab.video.txt'
    docword_file = '/data/zoushuai/video/v_topic/docword.video.txt'
    wordcount_file = "/data/zoushuai/video/v_topic/v_vocabcount"
    lp = LdaProcess(file, outfile, filtered_outfile,
                    tf_idf_file, vocab_file, docword_file, wordcount_file)
    lp.get_ldaprocess_result_file()

if __name__ == '__main__':
    main()


