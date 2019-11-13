#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 11/10/19 3:45 PM
@File    : test1.py
@Desc    : 

"""
try:
    import configparser
except:
    from six.moves import configparser
from os.path import dirname
import os

root_dir = dirname(dirname(os.path.realpath(__file__)))
print(root_dir)
lda_conf_file = os.path.join(root_dir, 'conf', 'lda', 'Default.conf')
print(lda_conf_file)
conf = configparser.ConfigParser()
conf.read("/home/joshua/PycharmProjects/AlgorithmProject-python/conf/lda/Default.conf", encoding='utf-8')

file = conf.get("DEFAULT.data", "DEFAULT_DATA_ROOT_PATH")
print(file)