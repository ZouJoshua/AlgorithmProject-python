#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/8/28 17:49
@File    : log.py
@Desc    : 
"""

import logging

try:
    import curses
except ImportError:
    curses = None

from tornado.log import LogFormatter as _LogFormatter


class LogFormatter(_LogFormatter, object):
    """Init tornado.log.LogFormatter from logging.config.fileConfig"""
    def __init__(self, fmt=None, datefmt=None, color=True, *args, **kwargs):
        if fmt is None:
            fmt = _LogFormatter.DEFAULT_FORMAT
            datefmt = _LogFormatter.DEFAULT_DATE_FORMAT
        super(LogFormatter, self).__init__(color=color, fmt=fmt, *args, **kwargs)


class SaveLogHandler(logging.Handler):
    """LogHandler that save records to a list"""

    def __init__(self, saveto=None, *args, **kwargs):
        self.saveto = saveto
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        if self.saveto is not None:
            self.saveto.append(record)

    handle = emit


def enable_pretty_logging(logger=logging.getLogger()):
    channel = logging.StreamHandler()
    channel.setFormatter(LogFormatter())
    logger.addHandler(channel)