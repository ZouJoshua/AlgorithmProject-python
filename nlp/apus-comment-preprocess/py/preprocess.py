#coding:utf-8
"""
预处理
"""
import langid
import re
import codecs
from textblob import TextBlob
import time
import textblob
from nltk.stem.snowball import SnowballStemmer
import spacy
from nltk import pos_tag

nlp = spacy.load("en")
stemmer = SnowballStemmer("english")

# 加载停用词表
print("load stop_word ...")
stop_word = set()
with codecs.open('../data/stopwords.dic', 'rb', 'utf-8', 'ignore') as infile:
    for line in infile:
        line = line.strip()
        if line:
            stop_word.add(line)

# 文本预处理
def preprocess(content):
    """
    去掉网页字符，评论内容大写转小写，只处理英文评论，
    空格分词，保留字母序列单词，评论中单词数量>=3,
    返回 带词性标注的单词序列
    """
    # 去掉网页字符
    content = re.sub(u'&#\d+;', u'', content)

    # 转小写
    content = content.lower()

    # 语种检测，只处理英文评论
    language_label, confidence = langid.classify(content)
    if language_label != u'en':
        return None
    
    # 分词且只保留英文单词
    eng_word_li = []
    for word in [w for w in content.split(u' ')]:
        matches_word_li = re.findall(u'[a-zA-Z]+\'?[a-zA-Z]*', word)
        eng_word_li.extend(matches_word_li)
    
    # 只处理英文单词数量在3个以上的评论
    if len(eng_word_li) <= 3:
        return None

    # 对评论做词性标注
    word_li = pos_tag(eng_word_li, tagset='universal')

    return word_li
