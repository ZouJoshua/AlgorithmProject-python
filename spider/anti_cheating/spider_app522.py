#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 19-7-1 下午3:21
@File    : spider_app522.py
@Desc    : 手赚汇下载赚钱app
            https://www.app522.com/
"""


import requests
from lxml import etree


header = {"User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36"}

root_url = "https://www.app522.com/"


def get_html_app522(url, table_path=None):
    if not table_path:
        TABLE_XPATH = ".//div[@class='app-list boutique-cnt']"
    else:
        TABLE_XPATH = table_path
    APP_LIST_XPATH = ".//div[@class='app-cnt']"
    APP_XPATH = ".//a[@class='app-title']/text()"
    html = requests.get(url, headers=header)
    pt = etree.HTML(html.text.lower(), parser=etree.HTMLParser(encoding='utf-8'))
    tb = pt.xpath(TABLE_XPATH)
    app_list = list()
    if len(tb):
        dl = tb[0]
        tables = dl.xpath(APP_LIST_XPATH)
        for table in tables:
            app_name = table.xpath(APP_XPATH)
            app_list.append(app_name[0])

    return app_list

def get_anzhuo_app_list(outfile):
    print(">>>>> 正在写入app列表文件")
    out = open(outfile, 'w')
    anzhuo_app_list = list()
    for i in range(1, 17):
        url = root_url + "down/anzhuo/{}.html".format(i)
        app_list = get_html_app522(url)
        anzhuo_app_list += app_list
        print("已抓取到第{}页".format(i))
    for name in anzhuo_app_list:
        out.write(name + "\n")
    out.close()
    print("<<<<< 列表文件【{}】已写入".format(outfile))


def get_ios_app_list(outfile):
    print(">>>>> 正在写入app列表文件")
    out = open(outfile, 'w')
    ios_app_list = list()
    for i in range(1, 15):
        url = root_url + "down/ios/{}.html".format(i)
        app_list = get_html_app522(url)
        ios_app_list += app_list
        print("已抓取到第{}页".format(i))
    for name in ios_app_list:
        out.write(name + "\n")
    out.close()
    print("<<<<< 列表文件【{}】已写入".format(outfile))



if __name__ == "__main__":
    anzhuo_txt = "anzhuo_app_list.txt"
    ios_txt = "ios_app_list.txt"
    get_anzhuo_app_list(anzhuo_txt)
    get_ios_app_list(ios_txt)