#!/usr/bin python
# -*- coding: utf-8 -*-
# @Date    : 2017-06-16 16:20:32
# @Author  : Liulichao (liulichao@apusapps.com)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import argparse
import logging

from topic_modeling.topic_model import TopicModelTrain, TopicModelUse


def training(language, corpus_path, saving_path, num_topics, load_flag=False):
    train_model_obj = TopicModelTrain(language.upper(), TopicModelTrain.LDA, corpus_path)

    #generating corpus
    if load_flag:
        train_model_obj.load_corpus(saving_path)
    else:
        logging.info("start generate corpus")
        train_model_obj.generate_corpus()
        logging.info("end generate corpus")
        train_model_obj.save(saving_path=saving_path, file_type='dictionary')
        train_model_obj.save(saving_path=saving_path, file_type='corpus')

    #train_model
    train_model_obj.train(ntops=num_topics)
    train_model_obj.save(saving_path=saving_path, file_type='model')


    #similarity_index
    train_model_obj.similarity_index()
    train_model_obj.save(saving_path=saving_path, file_type='model_similarity_index')

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-logp', '--logpath', help='logpath', default='./train.log')
    parser.add_argument('-l', '--language', help='language', default='english')
    parser.add_argument('-c', '--corpus', help='corpus path', default='./en_articles')
    parser.add_argument('-o', '--output', help='model save path', default='./en_lda/')
    parser.add_argument('-ntopic', '--num_topics', help='num topics', default=300)
    args = parser.parse_args()

    return args

def main():
    args = arg_parse()
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=args.logpath,
                        filemode='w')
    training(args.language, args.corpus, args.output, args.num_topics)

if __name__ == '__main__':
    main()
