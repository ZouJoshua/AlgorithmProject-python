#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-5-13 下午4:47
@File    : tmp.py
@Desc    : 
"""

import requests
import json

def get_video_category():
    """从api获取视频分类体系的一二级分类"""
    url = 'http://cms-news-api.apuscn.com/classify/getList/1'
    idx2label = dict()
    _result = requests.get(url).text
    result = json.loads(_result)
    idx2label["top_category"] = dict()
    idx2label["sub_category"] = dict()
    for i in result['data']:
        # if i["bizType"] == int(b_type):
        idx2label["top_category"][i["classifyId"]] = i["classifyName"]
        if i["children"]:
            for j in i["children"]:
                idx2label["sub_category"][j["classifyId"]] = j["classifyName"]
    with open("tmp", 'w') as f:
        f.writelines(json.dumps(idx2label, indent=4))


get_video_category()
