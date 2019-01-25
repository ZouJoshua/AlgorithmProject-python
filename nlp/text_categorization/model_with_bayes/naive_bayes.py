# -*- coding: utf8 -*-

# import sys
import numpy as np
import random
import collections
import re
import json


def word_generator(content):
    # 清洗html标签
    #doc = PyQuery(content)
    text = content
    # 去除网址和邮箱
    text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ").replace("&#13;", " ").lower()
    url_list = re.findall(r'http://[a-zA-Z0-9.?/&=:]*', text)
    for url in url_list:
        text = text.replace(url, " ")
    email_list = re.findall(r"[\w\d\.-_]+(?=\@)", text)
    for email in email_list:
        text = text.replace(email, " ")
    # 去除标点符号和停用词
    cleaned_text = ""
    stopWord_path = "/Users/caifuli/PycharmProjects/News_Recommandation/data/stopwords.txt"
    with open(stopWord_path, "r") as stop_f:
        lines = stop_f.readlines()
        stop_word_list = [line.replace("\n", "") for line in lines]
    for c in text:
        if (ord(c) >= 32 and ord(c) <= 236):
            if c.isalpha():
                cleaned_text += c
            else:
                cleaned_text += " "
    result = cleaned_text.split(" ")
    new_result = []
    for r in result:
        if r not in stop_word_list:
            new_result.append(r)
    while '' in new_result:
        new_result.remove('')
    return new_result


def shuffle(inFile):
    """简单的乱序操作，用于生成训练集和测试集"""
    # textLines = [line.strip() for line in open(inFile)]
    textLines = []
    count = 0
    with open(inFile, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = json.loads(line)
            content = ' '.join(word_generator(line['content']))
            top_category = line['top_category']
            if content != '' and (top_category == 'tech' or top_category == 'auto' or top_category == 'science'):
                textLine = top_category + "\t" + content
                # print(textLine)
                textLines.append(textLine.strip())
            else:
                count += 1
                pass

    print("正在准备训练和测试数据，请稍后...")
    random.shuffle(textLines)
    num = len(textLines)
    trainText = textLines[:int(4*num/5)]
    testText = textLines[int(4*num/5):]
    print("准备训练和测试数据准备完毕，下一步...")
    return trainText, testText

# 总共有3种新闻类别，我们给每个类别一个编号
label_idx_map = {"tech": "7", "auto": "9", "science": "10"}
lables = ['7', '9', '10']


def lable2id(lable):
    """for i in range(len(lables)):
        if lable == lables[i]:
            return i
    raise Exception('Error lable %s' % (lable))"""
    return label_idx_map[lable]


def doc_dict():
    """构造和类别数等长的0向量"""
    docCount_map = {}  # 初始化每类的文档数为0
    for v in label_idx_map.values():
        if v not in docCount_map:
            docCount_map[v] = 0
    # return [0]*len(label_idx_map)
    return docCount_map


def mutual_info(N, Nij, Ni_, N_j):
    """计算互信息，这里log的底取为2"""
    return Nij * 1.0 / N * np.log(N * (Nij+1)*1.0/(Ni_*N_j)) / np.log(2)


def count_for_cates(trainText, featureFile):
    """遍历文件，统计每个词在每个类别出现的次数，和每类的文档数并写入结果特征文件"""
    docWordCount_map = doc_dict()  # 初始化每类的词数为0
    docCount_map = doc_dict()  # 初始化每类的文章数为0
    # for v in label_idx_map.values():
    #    if v not in docCount_map:
    #        docCount_map[v] = 0
    # docCount = [0] * len(label_idx_map)
    wordCount = collections.defaultdict(lambda: doc_dict())  # 每个单词的各类别初始化计数为0
    # 扫描文件和计数
    for line in trainText:
        lable, text = line.strip().split('\t', 1)
        index = lable2id(lable)
        docCount_map[index] += 1
        words = text.split(' ')
        for word in words:
            wordCount[word][index] += 1
            docWordCount_map[index] += 1   # 计算各个类别的总词数

    # 计算互信息值
    print("计算互信息，提取关键/特征词中，请稍后...")
    wordCount1 = {k: v for k, v in wordCount.items()}
    miDict = wordCount1
    N = sum(docWordCount_map.values())  # 所有文章总词数
    for k, vs in wordCount1.items():
        for class_index in vs.keys():
            N11 = vs[class_index]   # 词k在class_index中出现的次数
            N10 = sum(vs.values()) - N11   # 词k在其他类中出现的次数
            N01 = docWordCount_map[class_index] - N11   # 这类文章其他词的次数
            N00 = N - N11 - N10 - N01      # 其他词在其他类文章出现的次数
            mi = mutual_info(N, N11, N10+N11, N01+N11) + mutual_info(N, N10, N10+N11, N00+N10) + mutual_info(N, N01, N01+N11, N01+N00) + mutual_info(N, N00, N00+N10, N00+N01)
            miDict[k][class_index] = mi
    print("计算完互信息值，开始写入特征词...")
    fWords_dict = doc_dict()
    for k in docWordCount_map.keys():
        fWords = list()
        k_word_mi = {}
        for w, v in miDict.items():
            if w not in k_word_mi:
                k_word_mi[w] = v[k]
        sortedDict = sorted(k_word_mi.items(), key=lambda x: x[1], reverse=True)
        for j in range(200):
            fWords.append(sortedDict[j][0])
        fWords_dict[k] = fWords
    out = open(featureFile, 'w')  # todo:会不会出现同一个词是多个类的关键词的情况？
    # 输出各个类的文章数
    # out.write(json.dumps(docCount_map) + "\n")
    # 输出互信息最高的前100个词作为每个类的特征词
    # for fword in fWords:
    #    out.write(fword+"\n")
    out.write(json.dumps(fWords_dict))
    print("特征词写入完毕...")
    out.close()


def load_feature_words(featureFile):
    """从特征文件导入特征词"""
    f = open(featureFile)
    # 各个类的文章个数
    # docCounts = eval(f.readline())
    # science_auto_features = dict()
    # 读取特征词
    features = json.loads(f.readlines()[0])
    f.close()
    return features


def train_bayes(featureFile, trainText, modelFile):
    """训练贝叶斯模型，实际上计算每个类中特征词的出现次数"""
    print("使用朴素贝叶斯训练中...")
    features_dict = load_feature_words(featureFile)
    wordCount = collections.defaultdict(lambda: doc_dict())
    # 每类文档特征词出现的次数
    tCount = doc_dict()
    for line in trainText:
        lable, text = line.strip().split('\t', 1)
        label_index = lable2id(lable)
        tCount[label_index] += 1
        words = text.split(' ')
        for word in words:
            for class_index, features in features_dict.items():
                if word in features:
                    wordCount[word][label_index] += 1
    with open("/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/nb/total_doc_count", "w") as f:
        f.write(json.dumps(tCount))
    outModel = open(modelFile, 'w')
    # 拉普拉斯平滑
    print("训练完毕，写入模型...")
    for k, v in wordCount.items():
        scores = {k: (v[k]+1) * 1.0 / (tCount[k]+len(wordCount)) for k in v.keys()}
        outModel.write(k + "\t" + json.dumps(scores) + "\n")
    outModel.close()


def load_model(modelFile):
    """从模型文件中导入计算好的贝叶斯模型"""
    print("加载模型中...")
    f = open(modelFile)
    scores = {}
    for line in f:
        word, counts = line.strip().rsplit('\t', 1)
        scores[word] = json.loads(counts)
    f.close()
    return scores


def predict(featureFile, modelFile, testText):
    """预测文档的类别，标准输入每一行为一个文档"""
    originalCount = {"7": 0, "9": 0, "10": 0}
    # features_dict = load_feature_words(featureFile)
    docCounts = json.loads(open("/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/nb/total_doc_count", "r").readlines()[0])
    print(docCounts)
    # docScores = {k: np.log(count * 1.0 / sum(docCounts.values())) for k, count in docCounts.items()}
    docScores = {k: 0 for k, count in docCounts.items()}
    print(docScores)
    scores = load_model(modelFile)
    rCount = 0
    docCount = 0
    print("正在使用测试数据验证模型效果...")
    for line in testText:
        lable, text = line.strip().split('\t', 1)
        index = lable2id(lable)
        originalCount[index] += 1
        words = text.split(' ')
        preValues = docScores
        for word in words:
            if word in scores.keys():
                for k in preValues.keys():
                    preValues[k] += np.log(scores[word][k])
        pIndex = max(preValues, key=preValues.get)
        # pIndex = preValues.index(m)
        if pIndex == index:
            rCount += 1
        # print lable,lables[pIndex],text
        docCount += 1
    print(originalCount)
    print("总共测试文本量: %d , 预测正确的类别量: %d, 朴素贝叶斯分类器准确度:%f" % (rCount, docCount, rCount * 1.0 / docCount))


if __name__ == "__main__":
    # if len(sys.argv) != 4:
     #   print("Usage: python naive_bayes_text_classifier.py sougou_news.txt feature_file.out model_file.out")
      #  sys.exit()

    # inFile = sys.argv[1]
    # featureFile = sys.argv[2]
    # modelFile = sys.argv[3]
    # inFile = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/top_training_tech_auto_science_data"
    inFile = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/top_tech_auto_science"
    featureFile = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/nb/science_auto_features"
    modelFile = "/Volumes/Katherine_Cai/NLP/apus/real_data/news_classification/nb/model"

    trainText, testText = shuffle(inFile)
    # count_for_cates(trainText, featureFile)
    # train_bayes(featureFile, trainText, modelFile)
    predict(featureFile, modelFile, testText)
