# -*- coding: utf-8 -*-
"""训练词向量"""
import logging
import json
import os
from gensim.models import word2vec


logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO)

'''
class generateCorpus():
    def __init__(self, fname, max_sentence_length):
        self.fname = fname
        self.max_sentence_length = max_sentence_length
        
    def __iter__(self):
        # 整个corpus是一个line，没有句子的标点
        sentence, rest = [], b''
        with utils.smart_open(self.fname) as fin:
            while True:
                text = rest + fin.read(8192)  # 避免读入全部文本
                if text == rest:
                    words = utils.to_unicode(text).split()
                    sentence.extend(words)
                    if sentence:
                        yield sentence
                    break
                last_token = text.rfind(b' ')
                words, rest = (utils.to_unicode(text[:last_token]).split(),
                               text[last_token:].strip()) if last_token >= 0 else ([], text)
                sentence.extend(words)
                while len(sentence) >= self.max_sentence_length:
                    yield sentence[:self.max_sentence_length]
                    sentence = sentence[self.max_sentence_length:]
                    
'''


def generate_sentences(dirname):
    fnames = os.listdir(dirname)
    fnames.remove('.DS_Store')
    sentences = []
    for fname in fnames:
        print(os.path.join(dirname, fname))
        with open(os.path.join(dirname, fname), "r") as f:
            for line in f.readlines():
                line = json.loads(line)
                title = line["content"].replace("\t", "").replace("\n", "").replace("\r", "")
                word_list = []
                for word in title.split(" "):
                    if word.isalpha():
                        word_list.append(word.lower())
                # word_list = [word if word.isalpha() else pass for word in title.split(" ")]
                sentences.append(word_list)
    return sentences

'''
class MySentences():
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        fnames = os.listdir(self.dirname)
        fnames.remove('.DS_Store')
        for fname in fnames:
            with codecs.open(os.path.join(self.dirname, fname), "r", encoding='utf-8', errors='ignore') as f:
                for line in f.readlines():
                    line = json.loads(line)
                    title = line["title"].replace("\t", "").replace("\n", "").replace("\r", "")
                    yield title.split(" ")

'''
# sentences = MySentences("/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/data")  # 新闻数据存储路径
sentences = generate_sentences("/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/data")
# sentences = [s.encode('utf-8').split(" ") for s in raw_sentences]

model = word2vec.Word2Vec(sentences, size=300)  # 默认训练词向量的时候把频次小于5的单词从词汇表中剔除掉
model.save("/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/ft/word2vec_content_model")

model.wv.save_word2vec_format("content_word_vector.bin", binary=True)


