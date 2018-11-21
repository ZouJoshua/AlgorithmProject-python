#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/11/12 17:58
@File    : basic.py
@Desc    : 
"""
import sys
import os
from os.path import dirname

_dirname = dirname(os.path.realpath(__file__))
sys.path.append(dirname(_dirname))

try:
    import configparser
except:
    from six.moves import configparser

from utils.logger import Logger


# project root
PROJECT_ROOT = dirname(_dirname).replace('\\', '/')
# conf root
confpath = os.path.join(dirname(_dirname), 'conf') + os.sep + 'Default.conf'

# log root
LOG_PATH = dirname(PROJECT_ROOT) + '/logs/'
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# read conf
config = configparser.ConfigParser()
config.read(confpath, encoding='utf-8')

# setting news log
logfilename = config.get('DEFAULT.log', 'DEFAULT_LOGGING_FILE')
PROJECT_LOG_FILE = LOG_PATH + logfilename
log = Logger('newslogger', log2console=False, log2file=True, logfile=PROJECT_LOG_FILE).get_logger()

