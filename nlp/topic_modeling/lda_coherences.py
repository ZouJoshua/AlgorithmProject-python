#!/usr/bin python
# -*- coding: utf-8 -*-
# @Date    : 2017-06-20 21:23:50
# @Author  : Liulichao (liulichao@apusapps.com)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from gensim import corpora,models

corpus = corpora.MmCorpus(sys.argv[1]+'/chinese_corpus.mm')
model = models.ldamodel.LdaModel.load(sys.argv[1]+'/chinese_model.model.out')
top_topics = model.top_topics(corpus, num_words=10)

# Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
avg_topic_coherence = sum([t[1] for t in top_topics]) / model.num_topics
print('Average topic coherence: %.4f.' % avg_topic_coherence)

from pprint import pprint
pprint(top_topics)

