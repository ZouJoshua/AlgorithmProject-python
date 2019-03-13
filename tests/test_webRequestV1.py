#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/3/13 18:16
@File    : test_webRequestV1.py
@Desc    : 
"""

import threading, time, http.client, random, json, string
import requests

# 需要测试的 url 列表，每一次的访问，我们随机取一个

port = "11091"
url = "http://10.65.33.163:{}/TopicService/Topicpro".format(port)
# SERVER_NAME = "http://10.65.33.163:{}".format(port)
MAX_PAGE = 10000

TEST_COUNT = 10000
# 创建一个 threading.Thread 的派生类
class RequestThread(threading.Thread):
    # 构造函数
    def __init__(self, thread_name):
        threading.Thread.__init__(self)
        self.test_count = 0

    # 线程运行的入口函数
    def run(self):
        # 不直接把代码写在run里面是因为也许我们还要做其他形式的测试
        i = 0
        while i < TEST_COUNT:
            self.test_performace()
            i += 1
            # self.test_other_things()

    def test_performace(self):
        # conn = http.client.HTTPConnection(SERVER_NAME)
        # 模拟 Keep-Alive 的访问, HTTP 1.1
        random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        content = "test" + random_str
        values = {"context": content, "resultnum": "3", "threshold": "0.1"}
        data = json.dumps(values)

        try:
            rsps = requests.post(url, data=data)
            # self.test_count += 1
            # print(rsps.status_code)
            if rsps.status_code == 200:
                # 读取返回的数据
                data = rsps.text
                print(data)
                self.test_count += 1
        except:
            pass

# main 代码开始

# 开始的时间
start_time = time.time()
threads = []
# 并发的线程数
thread_count = 100

i = 0
while i < thread_count:
    t = RequestThread("thread" + str(i))
    threads.append(t)
    t.start()
    i += 1

# 接受统计的命令
word = ""
while True:
    word = input("cmd:")
    if word == "s":
        time_span = time.time() - start_time
        all_count = 0
        for t in threads:
            all_count += t.test_count
        print("%s Request/Second" % str(all_count / time_span))
    elif word == "e":
        # 准备退出 其实 X 掉 窗口更加容易，没什么浪费的资源
        TEST_COUNT = 0
        for t in threads:
            t.join(0)
        break