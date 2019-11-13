#!/usr/bin python
# -*- coding: utf-8 -*-
# @Date    : 2017-06-20 21:21:22
# @Author  : Liulichao (liulichao@apusapps.com)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
from os.path import isfile, join
import argparse
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from topic_modeling.topic_model import TopicModelUse

def log_perplexity(language, corpus, model_path):
    topic_use_obj = TopicModelUse(language.upper(), "LDA", model_path)
    topic_use_obj.load()

    chunk = []
    all_files = [f for f in os.listdir(corpus) if isfile(join(corpus, f))]

    for file_name in all_files:
        file_obj = open(corpus + '/' + file_name, 'r')
        text_bow = topic_use_obj.algo_obj.text_to_bow(topic_use_obj.dictionary, file_obj.read())
        chunk.append(text_bow)
    return topic_use_obj.model.log_perplexity(chunk=chunk)

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-logp', '--logpath', help='logpath', default='./train.log')
    parser.add_argument('-l', '--language', help='language', default='english')
    parser.add_argument('-c', '--corpus', help='corpus path', default='./en_articles')
    parser.add_argument('-m', '--model_path', help='model save path', default='./en_lda/')
    args = parser.parse_args()

    return args

def main():
    args = arg_parse()
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=args.logpath,
                        filemode='w')
    print log_perplexity(args.language, args.corpus, args.model_path)

if __name__ == '__main__':
    main()
