#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 12/5/19 1:47 PM
@File    : file_utils.py
@Desc    : 

"""


from keywords_extraction.multilanguage.core.language import Language


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