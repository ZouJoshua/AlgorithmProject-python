#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/2/18 10:51
@File    : requests_topic_server.py
@Desc    : 
"""

import codecs
import urllib
import urllib2
import json
import sys
from datetime import datetime


def request_pos(content):
    # url = "http://10.19.180.57:8080/segment/seg.jsp"
    # url = "http://10.19.49.226:12013/segment/seg.jsp"
    url = "http://10.2.47.155:12015/segment/quality_doc.jsp"
    values = {"doc": content, "pos": "0"}
    # values = {"sentences" : content, "pos" : "0"}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()


def request_docprofile(jsonbody):
    url = "http://10.65.33.169:12016/segment/doc_profile.jsp"
    values = {"body": jsonbody, "newsid": "0", "type": "news"}
    # values = {"sentences" : content, "pos" : "0"}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()


def request_stanfordseg(text):
    url = "http://10.65.33.169:12016/segment/segment2.jsp"
    values = {"text": text}
    # values = {"sentences" : content, "pos" : "0"}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()


def request_seg1(content):
    url = "http://10.19.180.57:8080/segment/segfull1.jsp"
    values = {"sentences": content, "pos": "1"}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()


def request_seg(content):
    url = "http://tuijian31:12012/segment/segfull.jsp"
    values = {"sentences": content}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()


def request_title_keywords(content):
    url = "http://10.19.13.119:12012/segment/keywords.jsp"
    values = {"sentences": content, "topn": 2}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()


def request_keywords(content):
    # url = "http://10.19.90.178:12013/segment/keywords.jsp"
    url = "http://10.19.101.130:12013/segment/keywords.jsp"  # video vip
    values = {"sentences": content, "topn": 10}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    result = response.read()
    reslist = result.split(",")
    result2 = []
    for x in reslist:
        t = x.split(":")
        if len(t) == 2:
            result2.append((t))
    # result2 = [(x.split(":")) for x in result.split(",")]
    sorted_result2 = []
    if len(result2) > 0:
        sorted_result2 = sorted(result2, key=lambda d: d[1], reverse=True)
        return ",".join([str(k) + ":" + str(v) for k, v in sorted_result2])
    else:
        return ""
    # return ",".join([x.split(":")[0] + ":" + str(round(float(x.split(":")[1]), 5)) for x in result.split(",")])


def request_lda(port, content):
    url = "http://10.65.33.163:{}/TopicService/Topicpro".format(port)
    values = {"context": content,"resultnum":"20","threshold":"0.1"}
    data = json.dumps(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()

def get_topic_server(content, is_sort=False):
    topic_server_port = {"topic1000":"11091",
                        "topic512":"11092",
                        "topic256":"11093",
                        "topic128":"11094",
                        "topic64":"11095"}
    topic_server_out = dict()
    for topic_server, port in topic_server_port.items():
        result = request_lda(port, content)
        result_json = json.loads(result)
        topic_server_out[topic_server] = json.loads(result_json['topicres'])
    return topic_server_out



for line in sys.stdin:
    if line != "":
        # line = line.strip("\n")
        line = line.strip()
        # tokens = line.split('\t')
        # if len(tokens)<2: continue
        segjson = request_stanfordseg(line)
        print(segjson)
        continue
        # kwline =  request_keywords(tokens[1])
        try:
            json_dict = json.loads(line, encoding='utf-8')
            title = ''
            content = ''
            titlejson = ''
            contentjson = ''
            if 'title' in json_dict:
                title = json_dict['title']
            if 'article' in json_dict:
                content = json_dict['article'][:400]
            print(title)
            print(content)
            titlejson = request_stanfordseg(title)
            contentjson = request_stanfordseg(content)
            print(titlejson, contentjson)
            seg_dict = {}
            print('aa')

            title_dict = json.loads(titlejson, encoding='utf-8')
            # content_dict = json.loads(contentjson,encoding='utf-8')
            print('bb')
            seg_dict['titleseg'] = title_dict
            # seg_dict['contentseg'] = title_dict
            print(seg_dict)
            print(json.dumps(seg_dict, ensure_ascii=False))
        except:
            pass

        # 	kwline =  request_docprofile(line)
        #         #print kwline+'\t'+line
        #         print kwline
        '''
        try:
            tokens = line.split("\t")
            aid = tokens[0]
            title = tokens[1]
            content = tokens[2]
            print aid + "\t" + title + "\t" + content + "\t" + request_seg(title + " " + content)
        except:
            print line

        tokens = line.split("\t")
        id = tokens[0]
        title = tokens[1]
        content = tokens[2]
        new_seg = tokens[4]
        print id + "\t" + title + "\t" + content + "\t" + request_lda(title + " " + content).replace("\n", " ") + "\t" + request_lda1(new_seg).replace("\n", " ")
	'''
