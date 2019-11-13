#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-4-24 下午6:38
@File    : basic_lda1.py
@Desc    :  基础lda(矩阵实现)
"""


import numpy as np
import optparse
from ba_lda import pre_corpus


class BaseLDA:

    def __init__(self, K, alpha, beta, docs, V, smartinit=True):
        self.K = K  # topic主题数
        self.alpha = alpha  # parameter of topics prior
        self.beta = beta   # parameter of words prior
        self.docs = docs  #
        self.V = V  # term数目

        self.z_m_n = []  # 第m篇文档中的第n个词来自哪个主题,M行,X列（X为相应文档长度）
        self.n_m_z = np.zeros((len(self.docs), K)) + alpha     # doc-topic矩阵,M行,K列,第d篇文档中第t个主题出现的次数
        self.n_m = np.zeros(len(self.docs)) + K * alpha  # 第m篇文档中词的数目,M维
        self.n_z_t = np.zeros((K, V)) + beta  # word-topic矩阵,K行,V列,第t个词是第z个主题的次数
        self.n_z = np.zeros(K) + V * beta    # 第z个主题在所有语料中出现的次数,K维

        self.N = 0  # word数目
        for doc_id, doc in enumerate(docs):
            doc_len = len(doc)
            self.n_m[doc_id] += doc_len
            self.N += doc_len
            z_n = []
            for word_id in doc:
                if smartinit:
                    p_z = self.n_z_t[:, word_id] * self.n_m_z[doc_id] / self.n_z
                    z = np.random.multinomial(1, p_z / p_z.sum()).argmax()
                else:
                    z = np.random.randint(0, K)
                z_n.append(z)
                self.n_m_z[doc_id, z] += 1
                self.n_z_t[z, word_id] += 1
                self.n_z[z] += 1
            self.z_m_n.append(np.array(z_n))


    def inference(self):
        """learning once iteration"""
        for m, doc in enumerate(self.docs):
            z_n = self.z_m_n[m]
            n_m_z = self.n_m_z[m]
            for n, t in enumerate(doc):
                # discount for n-th word t with topic z
                z = z_n[n]
                n_m_z[z] -= 1
                self.n_z_t[z, t] -= 1
                self.n_z[z] -= 1

                # sampling topic new_z for t
                p_z = self.n_z_t[:, t] * n_m_z / self.n_z
                new_z = np.random.multinomial(1, p_z / p_z.sum()).argmax()

                # set z the new topic and increment counters
                z_n[n] = new_z
                n_m_z[new_z] += 1
                self.n_z_t[new_z, t] += 1
                self.n_z[new_z] += 1

    def worddist(self):
        """get topic-word distribution"""
        return self.n_z_t / self.n_z[:, np.newaxis]

    def topicdist(self):
        """get doc-topic distribution"""
        return self.n_m_z / self.n_m[:, np.newaxis]

    def perplexity(self, docs=None):
        if docs == None:
            docs = self.docs
        phi = self.worddist()
        theta = self.topicdist()
        # print(type(phi))
        # print(phi.shape)
        # print(self.n_m_z.shape)
        log_per = 0
        N = 0
        # Kalpha = self.K * self.alpha
        for m, doc in enumerate(docs):
            # theta = self.n_m_z[m] / (len(self.docs[m]) + Kalpha)
            for w in doc:
                # print(phi[:, w])
                # log_per -= np.log(np.inner(phi[:, w], theta))
                log_per -= np.log(np.inner(phi[:, w], theta[m]))
            N += len(doc)
        return np.exp(log_per / N)

def lda_learning(lda, iteration, voca):
    pre_perp = lda.perplexity()
    print("initial perplexity=%f" % pre_perp)
    for i in range(iteration):
        lda.inference()
        perp = lda.perplexity()
        print(">>>iter %d, p=%f" % (i + 1, perp))
        if pre_perp:
            if pre_perp < perp:
                output_word_topic_dist(lda, voca)
                pre_perp = None
            else:
                pre_perp = perp
    output_word_topic_dist(lda, voca)

def output_word_topic_dist(lda, voca):
    zcount = np.zeros(lda.K, dtype=int)
    wordcount = [dict() for k in range(lda.K)]
    for xlist, zlist in zip(lda.docs, lda.z_m_n):
        for x, z in zip(xlist, zlist):
            zcount[z] += 1
            if x in wordcount[z]:
                wordcount[z][x] += 1
            else:
                wordcount[z][x] = 1

    phi = lda.worddist()
    for k in range(lda.K):
        print("\n-- topic: %d (%d words)" % (k, zcount[k]))
        for w in np.argsort(-phi[k])[:20]:
            print("%s: %f (%d)" % (voca[w], phi[k, w], wordcount[k].get(w, 0)))
            pass
    theta = lda.topicdist()
    for doc_id in range(len(lda.docs)):
        top5_topic = np.argsort(-theta[doc_id])[:5]
        print("-- doc%d top5_topic: %s" % (doc_id, top5_topic))


def main():

    parser = optparse.OptionParser()
    parser.add_option("-f", dest="filename", help="corpus filename", default=None)
    parser.add_option("-c", dest="corpus", help="using range of Brown corpus' files(start:end)", default=None)
    parser.add_option("--alpha", dest="alpha", type="float", help="parameter alpha", default=0.1)
    parser.add_option("--beta", dest="beta", type="float", help="parameter beta", default=0.01)
    parser.add_option("-k", dest="K", type="int", help="number of topics", default=10)
    parser.add_option("-i", dest="iteration", type="int", help="iteration count", default=10)
    parser.add_option("-s", dest="smartinit", action="store_true", help="smart initialize of parameters", default=False)
    parser.add_option("--stopwords", dest="stopwords", help="exclude stop words", action="store_true", default=True)
    parser.add_option("--seed", dest="seed", type="int", help="random seed")
    parser.add_option("--df", dest="df", type="int", help="threshold of document freaquency to cut words", default=0)
    (options, args) = parser.parse_args()
    # if not (options.filename or options.corpus):
    #     parser.error("need corpus filename(-f) or corpus range(-c)")

    if options.filename:
        corpus = pre_corpus.load_json_file(options.filename)
        print(corpus)
    else:
        if not options.corpus:
            # parser.error("corpus range(-c) forms 'start:end'")
            corpus_range = "0:100"
        else:
            corpus_range = options.corpus
        corpus = pre_corpus.load_corpus(corpus_range)


    if options.seed != None:
        np.random.seed(options.seed)

    voca = pre_corpus.Vocabulary(options.stopwords)
    docs = [voca.doc_to_ids(doc) for doc in corpus]
    # print(docs)
    if options.df > 0:
        docs = voca.cut_low_freq(docs, options.df)

    lda = BaseLDA(options.K, options.alpha, options.beta, docs, voca.size(), options.smartinit)
    print("corpus=%d, words=%d, K=%d, a=%f, b=%f" % (len(corpus), len(voca.vocas), options.K, options.alpha, options.beta))

    #import cProfile
    #cProfile.runctx('lda_learning(lda, options.iteration, voca)', globals(), locals(), 'lda.profile')
    lda_learning(lda, options.iteration, voca)

if __name__ == "__main__":
    main()