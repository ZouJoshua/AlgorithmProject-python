#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/8/17 16:27
@File    : getContent.py
@Desc    : 请求html
"""
from __future__ import division

import requests
from requests.exceptions import ReadTimeout, ConnectTimeout, HTTPError, ConnectionError, RequestException
from lxml import etree
import json,hashlib,re
import random,time

import User_Agent
import log
from WcSender import WcSender

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

log = log.spiderLog()


def build_task(info):
    tasks = dict()
    tasks['tasks'] = list()
    for item in info:
        task = init_task(item)
        tasks["tasks"].append(task)
    return tasks

def do_all_task(tasks):
    proxy = get_proxy()
    while tasks["tasks"]:
        task = tasks["tasks"].pop()
        new_task = do_task(task,proxy)
        if new_task:
            WcSender()._send(new_task)
        else:
            WcSender()._send(task)
    else:
        time.sleep(0.5)

def do_task(task,proxy):
    task = GetHtml(task,proxy)
    new_task = extract_detail(task)
    log.info("Do task (%s)" %(task["url"]))
    return new_task

def init_task(info):
    task = dict()
    task['url'] = info['url'].strip()
    task['task_id'] = md5(task['url'])
    task['html_text'] = ''
    if 'task_id' not in task.keys():
        task['task_id'] = md5(task['url'])
    # if 'hostload' not in task.keys():
    #     task['hostload'] = 0.05
    # if 'country' not in task.keys():
    #     task['country'] = 'CN'
    # if 'language' not in task.keys():
    #     task['language'] = 'zh'
    if 'proxy_code' not in task.keys():
        task['proxy_code'] = ""
    if 'status_code' not in task.keys():
        task['status_code'] = 10000
    # if 'user_agent' not in task.keys():
    #     task['user_agent'] = ''
    if 'doc_info' not in task.keys():
        task['doc_info'] = {}
    if 'links' not in task['doc_info'].keys():
        task['doc_info']['links'] = []
    log.info('Task id(%s) url(%s)' % (task['task_id'], task['url']))
    return task

def md5(src):
    m2 = hashlib.md5()
    m2.update(src)
    return m2.hexdigest()

def get_proxy():
    i = 0
    while True:
        i +=1
        # url = "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=d6e42ceefbb04f78966b58c675ebd482&count=5&expiryDate=0&format=1&newLine=2"
        url = "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=0cf1b27d8fd54c1896cf37361ac23c05&count=1&expiryDate=0&format=1&newLine=2"
        headers = random.choice(User_Agent.user_agents)
        try:
            # session = requests.session()
            res = requests.get(url, headers=headers)
            jsonData = res.text
            proxy = json.loads(jsonData)
            print("从代理API获取代理ip（%s）。。。" % jsonData)
        except Exception as e:
            log.error("Proxy url wrong (%s)!" % str(e))
        else:
            if proxy["code"] == "3001":
                time.sleep(1)
                #time.sleep(10)
            if proxy["code"] == "0":
                pro = proxy["msg"][0]["ip"]+ ":" + proxy["msg"][0]["port"]
            else:
                pro = ""
            proxies = {"http":"http://" + pro.strip(),"https":"https://" + pro.strip()}
            checkurl = "http://www.baidu.com"
            try:
                requests.packages.urllib3.disable_warnings()
                res = requests.get(checkurl, headers=headers, proxies=proxies, timeout=3, verify=False)
            except Exception as e:
                log.error("Checking proxy wrong (%s)!" % str(e))
            else:
                if res.status_code == 200:
                    log.info("Get useful proxies(%s)" % proxies)
                    return proxies
        if i > 100:
            log.error("Get API (%s) times,please check API url!" % i)
            break


def GetHtml(task,proxy):
    if True:
        url = task["url"]
        header = random.choice(User_Agent.user_agents)
        try:
            requests.packages.urllib3.disable_warnings()
            res = requests.get(url, headers=header, proxies=proxy,timeout=3,verify=False)
            if res.status_code:
                task["status_code"] = res.status_code
            else:
                task["status_code"] = ""
            log.info("Getting Html from (%s)-(%s)-(%s)" % (url, header, proxy))
        except ReadTimeout as e:
            log.error("Getting Html timeout (%s)" % str(e))
            task["proxy_code"] = 101
        except ConnectionError as e:
            log.error("Getting Html connecterror (%s)" % str(e))
            task["proxy_code"] = 102
        except RequestException as e:
            log.error("Getting Html requesterror (%s)" % str(e))
            task["proxy_code"] = 100
        # except Exception,e:
        #     log.error("Getting Html (%s)" % str(e))
        #     return task
        else:
            task["proxy"] = proxy
            if res.status_code == 200:
                task["html_text"] = res.text
            else:
                task["html_text"] = ""
        finally:
            return task

INFO_XPATH = '''//dl[@class='infos-list']'''
CATEGORY1_XPATH = '''.//a[@data-track='detail-click-appTag']'''
CATEGORY2_XPATH = '''.//dd[@class='tag-box']/a/text()'''
TAGS_XPATH = '''.//div[@class='tag-box']/a/text()'''
VERSION_XPATH = '''.//dd/text()'''
DEVELOPER_XPATH = '''.//span[@class='dev-sites']/text()'''

def extract_detail(task):
    try:
        if task['html_text']:
            pt = etree.HTML(task['html_text'].lower(), parser=etree.HTMLParser(encoding='utf-8'))
            tb = pt.xpath(INFO_XPATH)
            if len(tb):
                dl = tb[0]
                if dl.xpath(CATEGORY1_XPATH) or dl.xpath(CATEGORY2_XPATH):
                    if dl.xpath(CATEGORY1_XPATH):
                        task['doc_info']['category'] = ",".join([cg.strip() for cg in dl.xpath(CATEGORY1_XPATH)])
                    else:
                        task['doc_info']['category'] = ",".join([cg.strip() for cg in dl.xpath(CATEGORY2_XPATH)])
                if dl.xpath(TAGS_XPATH):
                    task['doc_info']['tags'] = ",".join([tg.strip() for tg in dl.xpath(TAGS_XPATH)])
                if dl.xpath(VERSION_XPATH):
                    task['doc_info']['version'] = ",".join([vs.strip() for vs in dl.xpath(VERSION_XPATH) if
                                                            vs and re.match(r"\d+[\.,0-9]*\d$", vs.strip())])
                if dl.xpath(DEVELOPER_XPATH):
                    task['doc_info']['developer'] = ",".join([dp.strip() for dp in dl.xpath(DEVELOPER_XPATH)])
                else:
                    check_text = task['doc_info'].get('category') or \
                                 task['doc_info'].get('tags') or \
                                 task['doc_info'].get('version') or \
                                 task['doc_info'].get('developer') or \
                                 ''
                    if not check_text:
                        task['doc_info']['real_lang'] = ''
                    else:
                        pass
            if not task['doc_info'].get('category') \
                    and not task['doc_info'].get('tags') \
                    and not task['doc_info'].get('version') \
                    and not task['doc_info'].get('developer'):
                log.warning('Fail to extract info from task(%s)' % (task["task_id"]))
            else:
                log.info('Success to extract info(%s) from (%s)' % (json.dumps(task['doc_info']), task["task_id"]))
    except Exception as e:
        log.error('Fail to extract info from task(%s), msg(%s)' % (task["task_id"], str(e)))
    finally:
        return task

if __name__ == "__main__":
    info = list()
    fh = open(r'1.txt')
    rows = fh.readlines()
    num = len(rows)
    i = 0
    count = 0
    for row in rows:
        item = dict()
        item['url'] = row.strip()
        info.append(item)
        i += 1
        count += 1
        if i >= 150:
            log.info("Complete percent (%.2f%%)" % (100 * count / num))
            tasks = build_task(info)
            #print tasks
            do_all_task(tasks)
            info = list()
            i = 0
            # time.sleep(0.1)
    if info:
        tasks = build_task(info)
        #print tasks
        do_all_task(tasks)
        log.info("All work down!")
