#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/1/22 10:08
@File    : check_random.py
@Desc    : 
"""

import random
import json

def check_random(file, newfile):
    f = open(file, 'r', encoding='utf-8')
    outf = open(newfile, 'w', encoding='utf-8')
    lines = f.readlines()
    random.shuffle(lines)
    check_lines = random.sample(lines, 100)
    for line in check_lines:
        outf.write(line)
        outf.write('\n')
        outf.flush()
    f.close()
    outf.close()
    return


file = '/data/zoushuai/news_content/sub_classification_model/business/business_model_3/data/test_check_pred.json'
newfile = '/data/zoushuai/news_content/check/business_test_check_random'
check_random(file, newfile)