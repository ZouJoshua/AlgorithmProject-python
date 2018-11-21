#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/5 10:56
@File    : log.py
@Desc    : 日志信息
"""

import logging
import logging.config
import sys
import re
import os

_debug_logger = None
_info_logger = None
_warning_logger = None
_error_logger = None
debug = None
info = None
warning = None
error = None
exception = None

server_name = sys.argv[0].replace('.py', '')
def replace(m):
    global server_name
    ret = m.group(0) + '.' + server_name
    return ret

def init(path):
    global _debug_logger, _info_logger, _warning_logger, _error_logger
    global debug, info, warning, error, exception
    global server_name
    pat = "(?<=)(log/[a-z]+\.log)(?=)"
    log_path=path + 'logger.conf'
    new_log_path = log_path + '.' + server_name
    old_fp = open(log_path, 'r' )
    new_fp = open(new_log_path, 'w')
    content = old_fp.read()
    new_content = re.sub(pat, replace, content)
    new_fp.write(new_content)
    old_fp.close()
    new_fp.close()
    logging.config.fileConfig(new_log_path)
    _debug_logger = logging.getLogger('debug')
    _info_logger = logging.getLogger('info')
    _warning_logger = logging.getLogger('warning')
    _error_logger= logging.getLogger('error')
    debug = _debug_logger.debug
    info = _info_logger.info
    warning = _warning_logger.warning
    error = _error_logger.error
    exception = _error_logger.exception

def setLevel(level,path):
    init(path)
    global _debug_logger, _info_logger, _warning_logger, _error_logger
    _debug_logger.setLevel(getattr(logging, level))
    _info_logger.setLevel(getattr(logging, level))
    _warning_logger.setLevel(getattr(logging, level))
    _error_logger.setLevel(getattr(logging, level))
