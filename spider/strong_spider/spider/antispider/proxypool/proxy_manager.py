#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/5 18:42
@File    : proxy_manager.py
@Desc    : 代理池管理，调度抓取、验证、入库
"""

from multiprocessing import Value, Queue, Process
from api.apiServer import start_api_server
from proxy_pipeline import SqlitePipeline

from proxy_validator import ValidatorScheduler, Validator
from proxy_crawler import start_proxycrawl

from setting import TASK_QUEUE_SIZE

def start_all():
    myip = Validator.get_myip()
    DB_PROXY_NUM = Value('i', 0)
    task_queue = Queue(maxsize=TASK_QUEUE_SIZE)
    verified_queue = Queue()

    process_list =[]
    p0 = Process(target=start_api_server)
    process_list.append(p0)
    p1 = Process(target=start_proxycrawl, args=(task_queue, DB_PROXY_NUM, myip))
    process_list.append(p1)
    p2 = Process(target=ValidatorScheduler.validator, args=(task_queue, verified_queue, myip))
    process_list.append(p2)
    p3 = Process(target=SqlitePipeline.save_data, args=(verified_queue, DB_PROXY_NUM))
    process_list.append(p3)

    for i in process_list:
        i.daemon = True
        i.start()

    for i in process_list:
        i.join()

if __name__ == "__main__":
    start_all()