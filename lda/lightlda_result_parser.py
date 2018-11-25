#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 18-11-26 上午12:53
@File    : lightlda_result_parser.py
@Desc    : 

"""

import commands
import os

main = "./lightlda_result_parser"
if os.path.exists(main):
    rc, out = commands.getstatusoutput(main)
    print('rc = %d, \nout = %s' % (rc, out))

print('*' * 10)
f = os.popen(main)
data = f.readlines()
f.close()
print(data)

print('*' * 10)
os.system(main)