#coding:utf-8
"""
4种特征抽取方法在3种机器学习方法上的对比
"""
import nltk
from nltk.collocations import  BigramCollocationFinder
from nltk.metrics import  BigramAssocMeasures
from nltk.probability import  FreqDist,ConditionalFreqDist
from random import shuffle
from nltk.classify.scikitlearn import  SklearnClassifier
from sklearn.svm import SVC, LinearSVC,  NuSVC
from sklearn.naive_bayes import  MultinomialNB, BernoulliNB
from sklearn.linear_model import  LogisticRegression
from sklearn.metrics import  accuracy_score
import codecs
import pickle
from preprocess import preprocess
import time

# 将1个文件中的所有单词读到列表中返回
def text(file_name):
    word_li = []
    with codecs.open(file_name, 'rb', 'utf-8', 'ignore') as infile:
        for line_ser, line in enumerate(infile):
            if line_ser % 500 == 0:
                print line_ser
            line = line.strip()
            if not line:
                continue
            items = line.split(u' ')
            label = items[0]
            comment_text = u' '.join(items[1::])
            eng_word_li = preprocess(comment_text)
            if not eng_word_li:
                continue
            word_li.extend(eng_word_li)
    return word_li

# 将特征列表转化成BOW词典
def bag_of_words(words):
    return dict([(word,True) for word in words])

# 抽取2grams的特征字典（训练和测试共用）
def  bigram(words,score_fn=BigramAssocMeasures.chi_sq,n=1000):
    bigram_finder=BigramCollocationFinder.from_words(words)  #把文本变成双词搭配的形式
    bigrams = bigram_finder.nbest(score_fn,n)  #使用卡方统计的方法，选择排名前1000的双词
    newBigrams = [u+v for (u,v) in bigrams]
    return bag_of_words(newBigrams)

# 抽取1gram和2grams的特征词典（训练和测试共用）
def  bigram_words(words,score_fn=BigramAssocMeasures.chi_sq,n=1000):
    bigram_finder=BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn,n)
    newBigrams = [u+v for (u,v) in bigrams]
    a = bag_of_words(words)
    b = bag_of_words(newBigrams)
    a.update(b)  #把字典b合并到字典a中
    return a 

# 抽取chi-square的特征词典（训练和测试共用）
def chi_square_feature(file_name, number):
    word_fd = FreqDist()                   # 可统计所有词的词频
    cond_word_fd = ConditionalFreqDist()   # 可统计积极文本中的词频和消极文本中的词频 
    
    with codecs.open(file_name, 'rb', 'utf-8', 'ignore') as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            items = line.split(u' ')
            label = items[0]
            word_li = items[1::]

            if label == "__label__1":           # 负面评价
                for word in word_li:
                    word_fd[word] += 1
                    cond_word_fd['neg'][word] += 1
            else:                               # 正面评价
                for word in word_li:
                    word_fd[word] += 1
                    cond_word_fd['pos'][word] += 1

    pos_word_count = cond_word_fd['pos'].N()            # 积极词的数量
    neg_word_count = cond_word_fd['neg'].N()            # 消极词的数量
    total_word_count = pos_word_count + neg_word_count

    word_scores = {}                                    # 包括了每个词和这个词的信息量
    for word, freq in word_fd.items():
        pos_score = BigramAssocMeasures.chi_sq(cond_word_fd['pos'][word],  (freq, pos_word_count), total_word_count) # 计算积极词的卡方统计量，这里也可以计算互信息等其它统计量
        neg_score = BigramAssocMeasures.chi_sq(cond_word_fd['neg'][word],  (freq, neg_word_count), total_word_count) 
        word_scores[word] = pos_score + neg_score                                                                    # 一个词的信息量等于积极卡方统计量加上消极卡方统计量

    best_vals = sorted(word_scores.items(), key=lambda item:item[1],  reverse=True)[:number] # 把词按信息量倒序排序。number是特征的维度，是可以不断调整直至最优的
    best_words = set([w for w,s in best_vals])
    return dict([(word, True) for word in best_words])

# 批量生成训练数据或测试数据
def build_features(file_name, extract_feature_method=4, feature_number = 500, build_type="train"):
    if build_type == "train":               # 训练时，生成特征vocabulary
        if extract_feature_method == 1:     # 抽取 1gram 词汇表
            vocabulary = bag_of_words(text(file_name))
        elif extract_feature_method == 2:   # 抽取 2gram 词汇表
            vocabulary = bigram(text(file_name), score_fn=BigramAssocMeasures.chi_sq,n=feature_number) 
        elif extract_feature_method == 3:   # 抽取1gram和2gram 词汇表
            vocabulary =  bigram_words(text(file_name),score_fn=BigramAssocMeasures.chi_sq,n=feature_number)
        else:                               # 抽取chi-square 词汇表
            vocabulary = chi_square_feature(file_name, feature_number) 
        print "feature vocabulary has %d words" % len(vocabulary)
        with open('../out/feature_vocabulary.dic', 'wb') as outfile:
            pickle.dump(vocabulary, outfile)
    else:                                   # 测试时，加载特征vocabulary
        with open('../out/feature_vocabulary.dic', 'rb') as infile:
            vocabulary = pickle.load(infile)
        print "feature vocabulary has %d words" % len(vocabulary)
    
    # 分别生成正面评论数据和负面评论数据BOW
    posFeatures = []
    negFeatures = []
    with codecs.open(file_name, 'rb', 'utf-8', 'ignore') as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            items = line.split(u' ')
            label = items[0]
            word_li = items[1::]
            a = {}
            if extract_feature_method == 1:     # 抽取 1gram 词汇表
                bow = bag_of_words(word_li)
            elif extract_feature_method == 2:   # 抽取 2gram 词汇表
                bow = bigram(word_li, score_fn=BigramAssocMeasures.chi_sq,n=feature_number) 
            elif extract_feature_method == 3:   # 抽取1gram和2gram 词汇表
                bow =  bigram_words(word_li,score_fn=BigramAssocMeasures.chi_sq,n=feature_number)
            else:                               # 抽取chi-square 词汇表
                bow = chi_square_feature(file_name, feature_number) 
            for feature in bow:
                if feature in vocabulary.keys():
                    a[feature]='True'
            if not a:                           # 评论中没有vocabulary中的词汇，则丢弃该条数据
                continue
            if label == "__label__1":           # 负面评价集添加该条评论特征字典
                negFeatures.append([a, "neg"])
            else:                               # 正面评价集添加该条评论特征字典
                posFeatures.append([a, "pos"])
    return posFeatures, negFeatures

# 训练和测试的准确率验证接口
def model_predict(classifier, data, tag):
    pred = classifier.classify_many(data) # 给出预测的标签
    n = 0
    s = len(pred)
    for i in range(0,s):
        if pred[i]==tag[i]:
            n = n+1
    return n*1.0/s                        # 分类器准确度

# 训练模型接口
def train_model(classifier, train):
    classifier = SklearnClassifier(classifier) 
    classifier.train(train)                     #训练分类器
    return classifier

if __name__ == "__main__":
    t0 = time.time()
    print "extract train data features ..."
    posFeatures,negFeatures =  build_features("../data/train.ft.txt", extract_feature_method = 1, feature_number = 300, build_type="train")
    print "postive corpus has %d valid samples" % len(posFeatures)
    print "negtive corpus has %d valid samples" % len(negFeatures)
    t1 = time.time()
    print "time elapsed %.2f s\n\n" % (t1-t0)

    print "create train data ..."
    train_data_number = min(len(posFeatures), len(negFeatures))
    print "real train data sample number = %d\n\n" % (2*train_data_number)
    train =  posFeatures[:train_data_number]+negFeatures[:train_data_number]    # 保证类间数据的平衡

    t0 = time.time()
    print "extract test data features ..."
    posFeatures,negFeatures =  build_features("../data/test.ft.txt", extract_feature_method = 1, feature_number = 300, build_type="test")
    print "postive corpus has %d valid samples" % len(posFeatures)
    print "negtive corpus has %d valid samples" % len(negFeatures)
    t1 = time.time()
    print "time elapsed %.2f s\n\n" % (t1-t0)

    test_data_number = min(len(posFeatures), len(negFeatures))
    print "real test data sample number = %d\n\n" % (2*test_data_number)
    if test_data_number == 0:
        print "test data has too many unknown word"
        exit(0)
    test = posFeatures[:test_data_number]+negFeatures[:test_data_number]
    data, tag = zip(*test)


    t0 = time.time()
    classifier = train_model(BernoulliNB(), train)
    # 保存训练模型
    with open('../out/BernoulliNB.model', 'wb') as outfile:
        pickle.dump(classifier, outfile)
    t1 = time.time()
    print "time elapsed %.2f s" % (t1-t0)
    print "BernoulliNB predict acc = %.2f\n\n" % model_predict(classifier, data, tag) 


    t0 = time.time()
    classifier = train_model(MultinomialNB(), train)
    # 保存训练模型
    with open('../out/MultinomiaNB.model', 'wb') as outfile:
        pickle.dump(classifier, outfile)
    t1 = time.time()
    print "time elapsed %.2f s" % (t1-t0)
    print "MultinomiaNB predict acc = %.2f\n\n" % model_predict(classifier, data, tag) 

    t0 = time.time()
    classifier = train_model(LogisticRegression(), train)
    # 保存训练模型
    with open('../out/LogisticRegression.model', 'wb') as outfile:
        pickle.dump(classifier, outfile)
    t1 = time.time()
    print "time elapsed %.2f s" % (t1-t0)
    print "LogisticRegression predict acc = %.2f\n\n" % model_predict(classifier, data, tag) 
    
    t0 = time.time()
    classifier = train_model(SVC(), train)
    # 保存训练模型
    with open('../out/SVC.model', 'wb') as outfile:
        pickle.dump(classifier, outfile)
    t1 = time.time()
    print "time elapsed %.2f s" % (t1-t0)
    print "SVC predict acc = %.2f\n\n" % model_predict(classifier, data, tag) 

    t0 = time.time()
    classifier = train_model(LinearSVC(), train)
    # 保存训练模型
    with open('../out/LinearSVC.model', 'wb') as outfile:
        pickle.dump(classifier, outfile)
    t1 = time.time()
    print "time elapsed %.2f s" % (t1-t0)
    print "LinearSVC predict acc = %.2f\n\n" % model_predict(classifier, data, tag) 
    
    t0 = time.time()
    classifier = train_model(NuSVC(), train)
    with open('../out/NuSVC.model', 'wb') as outfile:
        pickle.dump(classifier, outfile)
    t1 = time.time()
    print "time elapsed %.2f s" % (t1-t0)
    print "NuSVC predict acc = %.2f\n\n" % model_predict(classifier, data, tag) 
