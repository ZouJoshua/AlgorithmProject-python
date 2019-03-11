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

import os
import sys
import time
import logging
import inspect

handlers = {
            logging.DEBUG: "/home/zoushuai/wdj_spider/log/1-debug.log",
            logging.INFO: "/home/zoushuai/wdj_spider/log/1-info.log",
            logging.WARNING: "/home/zoushuai/wdj_spider/log/1-warning.log",
            logging.ERROR: "/home/zoushuai/wdj_spider/log/1-error.log",
            }

# handlers = {
#             logging.DEBUG: r"D:\Work2018\pythonwork\Python2\spider_test\app_spider\data\log\LOG4-debug.log",
#             logging.INFO: r"D:\Work2018\pythonwork\Python2\spider_test\app_spider\data\log\LOG4-info.log",
#             logging.WARNING: r"D:\Work2018\pythonwork\Python2\spider_test\app_spider\data\log\LOG4-warning.log",
#             logging.ERROR: r"D:\Work2018\pythonwork\Python2\spider_test\app_spider\data\log\LOG4-error.log",
#             }

# handlers = {
#             logging.DEBUG: r"C:\Users\ZS\Desktop\LOG-debug.log",
#             logging.INFO: r"C:\Users\ZS\Desktop\LOG-info.log",
#             logging.WARNING: r"C:\Users\ZS\Desktop\LOG-warning.log",
#             logging.ERROR: r"C:\Users\ZS\Desktop\LOG-error.log",
#             }

def createHandlers():
    logLevels = handlers.keys()
    for level in logLevels:
        path = os.path.abspath(handlers[level])
        handlers[level] = logging.FileHandler(path)


# 加载模块时创建全局变量
createHandlers()

class spiderLog(object):

    def __init__(self, level=logging.INFO):
        self.__loggers = {}
        logLevels = handlers.keys()
        for level in logLevels:
            logger = logging.getLogger(str(level))
            # 如果不指定level，获得的handler似乎是同一个handler?
            logger.addHandler(handlers[level])
            logger.setLevel(level)
            self.__loggers.update({level: logger})

    def printfNow(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def getLogMessage(self, level, message):
        frame, filename, lineNo, functionName, code, unknowField = inspect.stack()[2]
        '''日志格式：[时间] [类型] [记录代码] 信息'''
        return "[%s] [%s] [%s - %s - %s] %s" % (self.printfNow(), level, filename, lineNo, functionName, message)

    def info(self, message):
        message = self.getLogMessage("info", message)
        self.__loggers[logging.INFO].info(message)

    def error(self, message):
        message = self.getLogMessage("error", message)
        self.__loggers[logging.ERROR].error(message)

    def warning(self, message):
        message = self.getLogMessage("warning", message)
        self.__loggers[logging.WARNING].warning(message)

    def debug(self, message):
        message = self.getLogMessage("debug", message)
        self.__loggers[logging.DEBUG].debug(message)

if __name__ == "__main__":
    logger = spiderLog()
    logger.debug("this is a debug !")
    # logger = spiderLog()
    logger.info("this is a info !")
    logger = spiderLog()
    logger.warning("this is a warning !")
    logger = spiderLog()
    logger.error("this is a error !")
