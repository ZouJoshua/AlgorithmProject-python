from __future__ import division
import os
import json

from gensim import corpora, models, similarities

from lang.hindi import Hindi

from constants.models import file_name



class EvaluateLDAMOdel:

    def __init__(self, model_dir_path, lang):
        """
        model_dir_path is path where models are saved.

        init function loads dictionary and model which are previously trained.

        on the  basis of language we assign lang_obj which contains utility functions
        like tokenizing and cleanup of code for that particluar lang.
        """
        self.lang = lang
        self.dictionary = corpora.Dictionary.load(model_dir_path + file_name[self.lang]['dict_file_name'])
        self.corpus = corpora.MmCorpus(model_dir_path + file_name[self.lang]['corpus_file_name'])
        self.model = models.LdaMulticore.load(model_dir_path + file_name[self.lang]['model_file_name'])

        if self.lang == 'HINDI':
            self.lang_obj = Hindi()



    def load_test_corpus(self, sim_index_path, article_index_mapping_path):

        self.test_corpus_index = similarities.MatrixSimilarity.load(sim_index_path)

        file_obj = open(article_index_mapping_path, 'r')
        file_text = file_obj.read()
        self.article_index_mapping = json.loads(file_text)



    def create_sim_index(self, dir_path, sim_index_path, article_index_mapping_path):
        all_file_list ={}
        corpus_articles = []
        count = 0

        dir_list = [f for f in os.listdir(dir_path)]

        for category in dir_list:

            category_path = dir_path + "/" + category

            all_files = [f for f in os.listdir(category_path)]

            category_corpus_articles = []

            for file_name in all_files:

                file_obj = open(category_path + '/' + file_name, 'r')
                file_text = file_obj.read()
                tokenized_article = self.lang_obj.tokenize(file_text)

                all_file_list[count] = category + '/' + file_name
                category_corpus_articles.append(tokenized_article)

                count += 1

            corpus_articles += category_corpus_articles

        corpus = [self.dictionary.doc2bow(article) for article in corpus_articles]
        index = similarities.MatrixSimilarity(self.model[corpus])

        index.save(sim_index_path)

        with open(article_index_mapping_path, 'w') as outfile:
            json.dump(all_file_list, outfile)


    def get_document(self, document, minimum_probability = 0):
        chunk = self.dictionary.doc2bow(document)
        top_dist = self.model[chunk]

        return [(idx, prob) for (idx, prob) in top_dist if prob >= minimum_probability]


    def analysis(self, dir_path, similarity_count=10):

        category_analysis = {}

        list_dirs = os.listdir(dir_path)

        for dir_name in list_dirs:

            category_list = []

            article_files = os.listdir(dir_path + '/' + dir_name)

            for article_name in article_files:

                similar_article_count = 0

                file_obj = open(dir_path + '/' + dir_name + '/' + article_name, 'r')
                article_text = file_obj.read()

                chunk = self.lang_obj.tokenize(article_text)

                test_data_vec = self.get_document(chunk)

                sims = self.test_corpus_index[test_data_vec]
                sims = sorted(enumerate(sims), key=lambda item: -item[1])

                result = []
                for similar_articles in sims[:similarity_count]:
                    article_index  = similar_articles[0]
                    article_file_name = self.article_index_mapping[str(article_index)]
                    
                    category_name = article_file_name.split('/')[0]

                    if category_name == dir_name:
                        similar_article_count += 1

                category_list.append((article_name, similar_article_count))

            category_analysis[dir_name] = category_list

        print category_analysis
        self.evaluate(category_analysis, similarity_count)



    def evaluate(self, data, similarity_count=10):

        for category in data:

            article_list = data[category]
            scores_list = []

            for article in article_list:
                scores_list.append(article[1])

            score = sum(scores_list) / len(scores_list)

            print '{0}    {1}'.format(category, score* (10 / similarity_count))

