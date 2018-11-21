#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author   : Joshua_Zou
@Contact  : joshua_zou@163.com
@Time     : 2018/8/19 16:18
@Software : PyCharm
@File     : log.py
@Desc     :日志信息
"""

import time
import logging
import os
import inspect

class BaseLogger(object):

    def __init__(self, logname, loglevel, logger, logpath):
        '''
           指定保存日志的文件路径，日志级别，以及调用文件
           将日志存入到指定的文件中
        '''
        self.logpath = logpath
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def getlog(self):
        return self.logger

if __name__ == "__main__":
    logger = BaseLogger()
    logger.debug("this is a debug !")
    # logger = spiderLog()
    logger.info("this is a info !")
    logger = BaseLogger()
    logger.warning("this is a warning !")
    logger = BaseLogger()
    logger.error("this is a error !")
