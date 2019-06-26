# -*- coding: utf-8 -*-
import re
from polyglot.text import Text, Word


class Tamil:

    def load_stop_words(self):
        stop_word_list = []
        f_obj = open('topic_modeling/stopwords/tamil_stop_words.txt', 'r')
        stop_words = f_obj.readlines()

        for word in stop_words:
            tamil_word, _ = word.split('    ')
            stop_word = tamil_word.strip()

            stop_word_list.append(stop_word)

        return stop_word_list


    def clean_text(self, text):
        text = text.replace(",", " ")
        text = text.replace("\"", " ")
        text = text.replace("(", " ")
        text = text.replace(")", " ")
        text = text.replace(":", " ")
        text = text.replace("'", " ")
        text = text.replace("\"", " ")
        text = text.replace("‘‘", " ")
        text = text.replace("’’", " ")
        text = text.replace("''", " ")
        text = text.replace(".", " ")
        text = text.replace("/", " ")
        text = text.replace("-", " ")
        text = text.replace('\n', " ")
        text = text.replace('‘', " ")    
        text = text.replace('’', " ")
        text = text.replace('#', " ")
        text = text.replace('@', " ")
        text = text.replace('!', " ")
        text = text.replace('–', " ")
        text = text.replace('*', " ")
        text = text.replace('%', " ")
        text = text.replace('|', " ")
        text = text.replace('$', " ")
        text = text.replace('+', " ")
        text = text.replace('?', " ")
        text = text.replace('\xc2\xa0', " ")
        return text


    def tokenize(self, text):
        article_vocab_list = []

        #remove english numbers 
        text = re.sub(r'\d+', ' ', text)

        #remove english letters from text
        text = re.sub(r'[a-zA-Z]', ' ', text)

        cleaned_text = self.clean_text(text)
        cleaned_text = unicode(cleaned_text, 'utf-8')
        tokenize_text = cleaned_text.split()

        tamil_stop_words = self.load_stop_words()

        for word in tokenize_text:

            # steming
            w = Word(word, language="ta")
            if len(w.morphemes) > 1:
                word = ("").join(w.morphemes[:-1])
            else:
                word = w.morphemes[0]

            word = word.encode('utf-8')
            if word in tamil_stop_words:
                continue

            word = word.strip()
            if word:
                article_vocab_list.append(word)

        return article_vocab_list
