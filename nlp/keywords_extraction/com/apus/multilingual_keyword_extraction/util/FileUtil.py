# coding:utf-8
# Created by houcunyue on 2017/9/19
from com.apus.multilingual_keyword_extraction.core.Language import Language


def writeLines(filePath, lines):
    writer = open(filePath, 'w', encoding='utf-8')
    for line in lines:
        writer.write(line + '\n')
    writer.close()

def readLines(filePath):
    reader = open(filePath, 'r', encoding='utf-8')
    return [line.strip() for line in reader.readlines()]

def readLanguages(filePath):
    return [Language(kv[0], kv[1]) for kv in [line.split('\t') for line in readLines(filePath)]]

def readStopwords(filePath):
    return set(readLines(filePath))