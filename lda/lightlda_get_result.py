#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 18-11-25 下午10:19
@File    : lightlda_get_result.py
@Desc    : 

"""

"""
从lightlda获取topic结果
"""

class LDAResult:

    @staticmethod
    def loadVocabs(ori_path):
        """
        得到所有原始词
        :param ori_path: 词汇量文件
        :return: list
        """
        out = []
        with open(ori_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                out.append(line.strip())
        return out

    @staticmethod
    def loadDocTopicModel(doc_topic_path):
        """
        得到文档-主题概率分布,得到每篇文章的所属主题（top3）
        :param doc_topic_path: lightlda 模型生成的doc_topic.0文件
        :return:
        """
        result = []
        with open(doc_topic_path, 'r', encoding='utf-8') as f:
            while True:
                line = f.readline().strip('\n').split('  ')  # 两个空格分割
                if line:
                    docID = line[0]
                    topic_list = line[1:][0].split(' ')  # 一个空格分割
                    topic_dic = {}
                    for topic in topic_list:
                        if topic:
                            kv = topic.split(':')
                            topic_dic[kv[0]] = kv[1]
                    line_json = dict()
                    line_json["docid"] = docID
                    line_json["topic"] = topic_dic
                    result.append(line_json)
                else:
                    break
        return result




    def loadTopicWordModel(self, topic_word_path, topic_summary):
        pass

    # 得到文档-主题概率分布
    def loadDocTopicModel(self, doc_topic_path):
        pass

    # 每个主题的前10个关键词写入到output_topic_topn_words中
    def dump_topic_topn_words(self,output_topic_topn_words,topn=20):
        pass


if __name__ == "__main__":


    doc_topic_path = "doc_topic.0"
    topic_word_path = "server_0_table_0.model"
    topic_summary = "server_0_table_1.model"
    ori_word_path = "vocab.news.txt"
    output_doc_topn_words = "doc.topn"
    output_topic_topn_words = "topic.topn"

    # lda = LDAResult(alpha=0.1 , beta=0.01 , topic_num=500 , vocab_num=1479643 , doc_num=26893850)
    # lda.loadVocabs(ori_word_path)
    # print("加载完毕!")
    # lda.loadTopicWordModel(topic_word_path, topic_summary)
    # lda.loadDocTopicModel(doc_topic_path)
    # lda.dump_topic_topn_words(output_topic_topn_words, 10)

    def loadDocTopicModel(doc_topic_path):
        """
        得到每篇文章的所属主题（top3）
        :param doc_topic_path: lightlda 模型生成的doc_topic.0文件
        :return:
        """
        result = []
        with open(doc_topic_path, 'r', encoding='utf-8') as f:
            i = 0
            while True:
                line = f.readline().strip('\n').split('  ')  # 两个空格分割
                docID = line[0]
                topic_list = line[1:][0].split(' ')  # 一个空格分割
                topic_dic = {}
                for topic in topic_list:
                    if topic:
                        kv = topic.split(':')
                        topic_dic[kv[0]] = int(kv[1])
                line_json = {}
                x = sorted(topic_dic.items(), key=lambda item: item[1])
                print(x)
                line_json["docid"] = docID
                line_json["topic"] = topic_dic
                result.append(line_json)
                i += 1
                if i == 10:
                    break
        return result
    out = loadDocTopicModel(doc_topic_path)
    print(len(out))
    print(out)