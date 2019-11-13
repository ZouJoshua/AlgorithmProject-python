# -*- coding: utf-8 -*-
import os
from os.path import isfile, join
import re
import logging

from gensim import corpora, similarities, models

from topic_modeling.lang.hindi import Hindi as HindiClass
from topic_modeling.lang.tamil import Tamil as TamilClass
from topic_modeling.lang.chinese import Chinese as ChineseClass
from topic_modeling.lang.english import English as EnglishClass
from topic_modeling.lang.telugu import Telugu as TeluguClass
from topic_modeling.lang.kannada import Kannada as KannadaClass
from topic_modeling.lang.malayalam import Malayalam as MalayalamClass

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)


class LDA:

    def __init__(self, language):
        language = language.lower()
        if language == "hindi":
            self.lang_obj = HindiClass()

        elif language == "tamil":
            self.lang_obj = TamilClass()

        elif language == "chinese":
            self.lang_obj = ChineseClass()

        elif language == "english":
            self.lang_obj = EnglishClass()

        elif language == "malayalam":
            self.lang_obj = MalayalamClass()

        elif language == "telugu":
            self.lang_obj = TeluguClass()

        elif language == "kannada":
            self.lang_obj = Kannada()

        else:
            logging.warning("LDA do not support language: "+language)



    def generate_corpus(self, dir_path):
        all_files = [f for f in os.listdir(dir_path) if isfile(join(dir_path, f))]

        all_vocab_list = []

        for index, file_name in enumerate(all_files):
            article_vocab_list = []

            file_obj = open(dir_path + '/' + file_name, 'r')
            file_text = file_obj.read()
            logging.info("filename  -   - " + file_name)

            article_vocab_list = self.lang_obj.tokenize(file_text)
            all_vocab_list.append(article_vocab_list)

        dictionary = corpora.Dictionary(all_vocab_list)
        logging.info("length of the dictionary   " + str(len(dictionary)))

        dictionary.filter_extremes(no_below=10)
        logging.info("length of dictionary after filtering extremes   " + str(len(dictionary)))

        corpus = [dictionary.doc2bow(article_vocab) for article_vocab in all_vocab_list]

        return (dictionary, corpus)


    def generate_model(self, dictionary, corpus, ntops):
        model = models.LdaMulticore(corpus, id2word=dictionary, num_topics=ntops, workers=4, passes=5)
        return  model


    def generate_similarity_index(self, corpus, model):
        index = similarities.MatrixSimilarity(model[corpus])
        return index


    def update_model(self, dir_path, model):
        _, corpus = self.generate_corpus(dir_path)
        model.update(corpus)


    def text_to_bow(self, dictionary, text):
        article_vocab_list = self.lang_obj.tokenize(text)
        return dictionary.doc2bow(article_vocab_list)
