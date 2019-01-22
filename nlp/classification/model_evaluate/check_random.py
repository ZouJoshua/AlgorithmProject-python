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
    lines = f.readlines()
    check_lines = random.sample(lines, 100)
    return