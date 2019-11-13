# -*- coding: utf-8 -*-
import re

from topic_modeling.constants.hindi import hindi_numbers, hindi_stop_words_list, hindi_custom_stop_words_list


class Hindi:

    hindi_stop_words_list += hindi_custom_stop_words_list

    def clean_text(self, text):
        text=text.replace(",", " ")
        text=text.replace("\"", " ")
        text=text.replace("(", " ")
        text=text.replace(")", " ")
        text=text.replace(":", " ")
        text=text.replace("'", " ")
        text=text.replace("‘‘", " ")
        text=text.replace("’’", " ")
        text=text.replace("''", " ")
        text=text.replace(".", " ")
        text=text.replace("/", " ")
        text=text.replace("-", " ")
        text=text.replace('।', " ")
        text=text.replace('|', " ")
        text=text.replace('\n', " ")
        text=text.replace('!', " ")
        text=text.replace('‘', " ")
        text=text.replace('’', " ")
        text=text.replace('?', " ")
        text=text.replace('#', " ")
        text=text.replace('@', " ")
        return text


    def tokenize(self, text):
        article_vocab_list = []

        for hindi_number in hindi_numbers:
            text = text.replace(hindi_number, ' ')

        #remove english numbers
        text = re.sub(r'\d+', ' ', text)

        #remove english letters from text
        text = re.sub(r'[a-zA-Z]', ' ', text)


        cleaned_text = self.clean_text(text)
        tokenize_text = cleaned_text.split()

        for word in tokenize_text:
            if word in self.hindi_stop_words_list:
                continue

            article_vocab_list.append(word)

        return article_vocab_list
