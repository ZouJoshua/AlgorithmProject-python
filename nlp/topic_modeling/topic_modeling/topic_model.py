from algo.lda.lda import LDA
from algo.topicvec import topicvec
from gensim import corpora, similarities, models
import numpy as np

from constants.models import file_name


class TopicModelTrain:
    LDA = "LDA"
    CHINESE = "CHINESE"
    ENGLISH = "ENGLISH"
    HINDI = "HINDI"
    TAMIL = "TAMIL"
    MALAYALAM = "MALAYALAM"
    TELUGU = "TELUGU"
    KANNADA = "KANNADA"


    def __init__(self, lang, algo, dir_path):
        self.lang = lang
        self.dir_path = dir_path
        self.algo = algo

        if self.algo == self.LDA:
            self.algo_obj = LDA(self.lang)

    # train_params will be specific to algo and the language
    def generate_corpus(self):
        if self.lang == self.HINDI and self.algo == self.LDA:
            self.dictionary, self.corpus = self.algo_obj.generate_corpus(self.dir_path)

        elif self.lang == self.TAMIL and self.algo == self.LDA:
            self.dictionary, self.corpus = self.algo_obj.generate_corpus(self.dir_path)

        elif self.lang == self.MALAYALAM and self.algo == self.LDA:
            self.dictionary, self.corpus = self.algo_obj.generate_corpus(self.dir_path)

        elif self.lang == self.TELUGU and self.algo == self.LDA:
            self.dictionary, self.corpus = self.algo_obj.generate_corpus(self.dir_path)

        elif self.lang == self.KANNADA and self.algo == self.LDA:
            self.dictionary, self.corpus = self.algo_obj.generate_corpus(self.dir_path)

        elif self.lang == self.ENGLISH and self.algo == self.LDA:
            self.dictionary, self.corpus = self.algo_obj.generate_corpus(self.dir_path)

        elif self.lang == self.CHINESE and self.algo == self.LDA:
            self.dictionary, self.corpus = self.algo_obj.generate_corpus(self.dir_path)


    # train_params will be specific to algo and the language
    def train(self, ntops=300):
        if self.lang == self.HINDI and self.algo == self.LDA:
            self.model = self.algo_obj.generate_model(self.dictionary, self.corpus, ntops)

        elif self.lang == self.TAMIL and self.algo == self.LDA:
            self.model = self.algo_obj.generate_model(self.dictionary, self.corpus, ntops)

        elif self.lang == self.MALAYALAM and self.algo == self.LDA:
            self.model = self.algo_obj.generate_model(self.dictionary, self.corpus, ntops)

        elif self.lang == self.TELUGU and self.algo == self.LDA:
            self.model = self.algo_obj.generate_model(self.dictionary, self.corpus, ntops)

        elif self.lang == self.KANNADA and self.algo == self.LDA:
            self.model = self.algo_obj.generate_model(self.dictionary, self.corpus, ntops)

        elif self.lang == self.ENGLISH and self.algo == self.LDA:
            self.model = self.algo_obj.generate_model(self.dictionary, self.corpus, ntops)

        elif self.lang == self.CHINESE and self.algo == self.LDA:
            self.model = self.algo_obj.generate_model(self.dictionary, self.corpus, ntops)


    # train_params will be specific to algo and the language
    def similarity_index(self):
        if self.lang == self.HINDI and self.algo == self.LDA:
            self.model_similarity_index = self.algo_obj.generate_similarity_index(self.corpus, self.model)

        elif self.lang == self.TAMIL and self.algo == self.LDA:
            self.model_similarity_index = self.algo_obj.generate_similarity_index(self.corpus, self.model)

        elif self.lang == self.MALAYALAM and self.algo == self.LDA:
            self.model_similarity_index = self.algo_obj.generate_similarity_index(self.corpus, self.model)

        elif self.lang == self.TELUGU and self.algo == self.LDA:
            self.model_similarity_index = self.algo_obj.generate_similarity_index(self.corpus, self.model)

        elif self.lang == self.KANNADA and self.algo == self.LDA:
            self.model_similarity_index = self.algo_obj.generate_similarity_index(self.corpus, self.model)

        elif self.lang == self.ENGLISH and self.algo == self.LDA:
            self.model_similarity_index = self.algo_obj.generate_similarity_index(self.corpus, self.model)

        elif self.lang == self.CHINESE and self.algo == self.LDA:
            self.model_similarity_index = self.algo_obj.generate_similarity_index(self.corpus, self.model)


    # save the model to a file
    def save(self, saving_path, file_type="corpus"):
        if self.lang == self.HINDI and self.algo == self.LDA:
            if file_type == "corpus":
                corpora.MmCorpus.serialize(saving_path + file_name[self.lang]['corpus_file_name'], self.corpus)

            if file_type == "dictionary":
                self.dictionary.save(saving_path + file_name[self.lang]['dict_file_name'])

            if file_type == "model":
                self.model.save(saving_path + file_name[self.lang]['model_file_name'])

            if file_type == "model_similarity_index":
                self.model_similarity_index.save(saving_path + file_name[self.lang]['model_similarity_index_file_name'])


        elif self.lang == self.TAMIL and self.algo == self.LDA:
            if file_type == "corpus":
                corpora.MmCorpus.serialize(saving_path + file_name[self.lang]['corpus_file_name'], self.corpus)

            if file_type == "dictionary":
                self.dictionary.save(saving_path + file_name[self.lang]['dict_file_name'])

            if file_type == "model":
                self.model.save(saving_path + file_name[self.lang]['model_file_name'])

            if file_type == "model_similarity_index":
                self.model_similarity_index.save(saving_path + file_name[self.lang]['model_similarity_index_file_name'])


        elif self.lang == self.MALAYALAM and self.algo == self.LDA:
            if file_type == "corpus":
                corpora.MmCorpus.serialize(saving_path + file_name[self.lang]['corpus_file_name'], self.corpus)

            if file_type == "dictionary":
                self.dictionary.save(saving_path + file_name[self.lang]['dict_file_name'])

            if file_type == "model":
                self.model.save(saving_path + file_name[self.lang]['model_file_name'])

            if file_type == "model_similarity_index":
                self.model_similarity_index.save(saving_path + file_name[self.lang]['model_similarity_index_file_name'])


        elif self.lang == self.TELUGU and self.algo == self.LDA:
            if file_type == "corpus":
                corpora.MmCorpus.serialize(saving_path + file_name[self.lang]['corpus_file_name'], self.corpus)

            if file_type == "dictionary":
                self.dictionary.save(saving_path + file_name[self.lang]['dict_file_name'])

            if file_type == "model":
                self.model.save(saving_path + file_name[self.lang]['model_file_name'])

            if file_type == "model_similarity_index":
                self.model_similarity_index.save(saving_path + file_name[self.lang]['model_similarity_index_file_name'])


        elif self.lang == self.KANNADA and self.algo == self.LDA:
            if file_type == "corpus":
                corpora.MmCorpus.serialize(saving_path + file_name[self.lang]['corpus_file_name'], self.corpus)

            if file_type == "dictionary":
                self.dictionary.save(saving_path + file_name[self.lang]['dict_file_name'])

            if file_type == "model":
                self.model.save(saving_path + file_name[self.lang]['model_file_name'])

            if file_type == "model_similarity_index":
                self.model_similarity_index.save(saving_path + file_name[self.lang]['model_similarity_index_file_name'])

        else:
            if file_type == "corpus":
                corpora.MmCorpus.serialize(saving_path + file_name[self.lang]['corpus_file_name'], self.corpus)
            if file_type == "dictionary":
                self.dictionary.save(saving_path + file_name[self.lang]['dict_file_name'])
            if file_type == "model":
                self.model.save(saving_path + file_name[self.lang]['model_file_name'])
            if file_type == "model_similarity_index":
                self.model_similarity_index.save(saving_path + file_name[self.lang]['model_similarity_index_file_name'])

    # update the model.
    def update(self, dir_path):
        if self.lang == self.HINDI and self.algo == self.LDA:
            self.model = self.algo_obj.update_model(dir_path, self.model)

        elif self.lang == self.TAMIL and self.algo == self.LDA:
            self.model = self.algo_obj.update_model(dir_path, self.model)

        elif self.lang == self.MALAYALAM and self.algo == self.LDA:
            self.model = self.algo_obj.update_model(dir_path, self.model)

        elif self.lang == self.TELUGU and self.algo == self.LDA:
            self.model = self.algo_obj.update_model(dir_path, self.model)

        elif self.lang == self.KANNADA and self.algo == self.LDA:
            self.model = self.algo_obj.update_model(dir_path, self.model)


class TopicModelUse:
    LDA = "LDA"
    TAMIL = "TAMIL"
    HINDI = "HINDI"
    CHINESE = "CHINESE"
    ENGLISH = "ENGLISH"
    MALAYALAM = "MALAYALAM"
    TELUGU = "TELUGU"
    KANNADA = "KANNADA"


    def __init__(self, lang, algo, dir_path):
        # dir_path is path where model, corpus and dict file are saved.
        self.lang = lang
        self.algo = algo
        self.dir_path = dir_path

        if self.algo == self.LDA:
            self.algo_obj = LDA(self.lang)


    # load model from file
    def load(self):
        if self.algo == self.LDA:
            self.model = models.LdaMulticore.load(self.dir_path + file_name[self.lang]['model_file_name'])
            self.dictionary = corpora.Dictionary.load(self.dir_path + file_name[self.lang]['dict_file_name'])

    # returns a list of topics along with the relevant keywords in the topics
    def get_topics(self, topicid=None, topn=None, num_topics=None):
        if self.algo == self.LDA:
            if topicid:
                topic = self.model.show_topic(topicid=topicid, topn=topn)
                return topic

            all_topics = self.model.show_topics(num_topics=num_topics, num_words=topn)
            return all_topics

    # learns topics on the text, returns probability of each tupic for that distribution
    def get_topic_dist(self, text, np_array_flag=False, syn0norm=False):
        if self.algo == self.LDA:
            text_bow = self.algo_obj.text_to_bow(self.dictionary, text)
            # document_topics is a list of(topic_id, topic_probability) 2-tuples
            document_topics = self.model.get_document_topics(bow=text_bow)
            if not np_array_flag:
                return document_topics
            topic_dist = [0.0] * self.model.num_topics
            for t in document_topics:
                topic_id = t[0]
                topic_probability = t[1]
                topic_dist[topic_id] = topic_probability
            topic_dist = np.array(topic_dist, dtype=np.float32)
            if syn0norm:
                topic_dist /= np.sqrt((topic_dist ** 2).sum(-1))
            return topic_dist

