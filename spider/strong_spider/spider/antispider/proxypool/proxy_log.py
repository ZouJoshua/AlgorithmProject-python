#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/20 18:14
@File    : proxy_log.py
@Desc    : 抓取代理日志信息
"""

import sys
import os
import logging
import logging.config


# CURRENT_DIR_PATH = os.getcwd()
CURRENT_DIR_PATH = os.path.split(os.path.realpath(__file__))[0]
HOME_DIR_PATH = os.path.dirname(os.path.dirname(CURRENT_DIR_PATH))
print CURRENT_DIR_PATH
print HOME_DIR_PATH
CURRENT_DIRS = CURRENT_DIR_PATH.split(os.sep)
if os.path.basename(HOME_DIR_PATH) == 'spider':
    PROXY_LOG_DIR_PATH = os.path.join(HOME_DIR_PATH, 'data', 'logs', 'proxy')
    PROXY_CONF_DIR_PATH = os.path.join(HOME_DIR_PATH, 'conf', 'proxy_log.conf')
    if not os.path.exists(PROXY_LOG_DIR_PATH):
        os.makedirs(PROXY_LOG_DIR_PATH)
    if not os.path.exists(PROXY_CONF_DIR_PATH):
        print 'Please check proxy config!'
    logging.config.fileConfig(PROXY_CONF_DIR_PATH)
    logger = logging.getLogger('proxy.log')
else:
    print 'Please check current path!'
# print PROXY_LOG_DIR_PATH

logger.info('This is a info message')
logger.debug('This is a debug message')
logger.error('This is a error message')
logger.warning('This is a warning message')


