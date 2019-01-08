#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/1/8 22:24
@File    : check_bad_case.py
@Desc    : 
"""

import os
from os.path import dirname
import sys
root_path = dirname(dirname(dirname(dirname(os.path.realpath(__file__)))))
class_path = dirname(dirname(os.path.realpath(__file__)))
sys.path.append(root_path)
sys.path.append(dirname(class_path))

