#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-4-19 下午2:22
@File    : v_topic_preprocess.py
@Desc    : 视频topic服务文本预处理
"""


import json
import langid
import re

from langdetect import detect


def read_data(file, stopline=None):
    v_file = open(file, 'r')
    countFlag = 0
    while True:
        countFlag += 1
        _line = v_file.readline().strip()
        if countFlag == stopline or not _line:
            v_file.close()
            break
        else:
            line = json.loads(_line)
            line['lang'] = langid.classify(line['article_title'])[0]
            # line['lang'] = detect(line['article_title'])
            if line['resource_type'] == 20002 or line['resource_type'] == 6:
                line['url'] = "https://www.youtube.com/watch?v=" + line['source_url']
            else:
                line['url'] = line['source_url']

            yield line
            # _out.append(line)


def clean_string(text):

    # 去除诡异的标点符号
    cleaned_text = ""
    for c in text:
        if (ord(c) >= 32 and ord(c) <= 126):
            cleaned_text += c
        else:
            cleaned_text += " "
    return cleaned_text


def _clean_html(text):
    # 去除网址
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    url_list = re.findall(pattern, text)
    for url in url_list:
        text = text.replace(url, " ")
    return text.replace("()", "")

def _clean_mail(text):
    # 去除邮箱
    pattern = re.compile(r"^\w+[-_.]*[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$")
    mail_list = re.findall(pattern, text)
    for mail in mail_list:
        text = text.replace(mail, " ")
    return text


if __name__ == '__main__':
    file = './data/test'
    for i in read_data(file,10):
        print(i)


