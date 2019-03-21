#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/3/21 13:48
@File    : get_india_ administrative_division.py
@Desc    : 抓取印度行政区划
"""

from __future__ import division
import requests
from requests.exceptions import ReadTimeout, ConnectTimeout, HTTPError, ConnectionError, RequestException
from lxml import etree
import json,hashlib,re
import random,time




root_url = "https://en.wikipedia.org/wiki/India#Subdivisions"
header = {"User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36"}


INFO_XPATH = '''//div[@id='mw-content-text']'''
# TABLE_XPATH = '''.//table[@class= 'wikitable sortable mw-collapsible floatleft']/tbody/tr'''
# TEXT_XPATH = '''.//td/a/text()'''
# HREF_XPATH = '''.//td/a/@href'''
#
# html = requests.get(url, headers=header)
# pt = etree.HTML(html.text.lower(), parser=etree.HTMLParser(encoding='utf-8'))
# tb = pt.xpath(INFO_XPATH)
all_states = dict()
# if len(tb):
#     dl = tb[0]
#     states = dl.xpath(TABLE_XPATH)
#     for i in states:
#         hrefs = i.xpath(HREF_XPATH)
#         names = i.xpath(TEXT_XPATH)
#         for j in range(2):
#             all_states[names[j].title()] = 'https://en.wikipedia.org{}'.format(hrefs[j])
# print(all_states)


# List_of_districts_of_Bihar
# https://en.wikipedia.org/wiki/List_of_districts_of_Gujarat
# https://en.wikipedia.org/wiki/List_of_districts_of_Haryana
# url_test = 'https://en.wikipedia.org/wiki/List_of_districts_of_Bihar'
# url_test = 'https://en.wikipedia.org/wiki/List_of_districts_of_Gujarat'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Haryana'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Himachal_Pradesh'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_in_Jammu_and_Kashmir'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Karnataka'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_in_Kerala'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Madhya_Pradesh'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Maharashtra'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Mizoram'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Nagaland'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Odisha'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Punjab,_India'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Rajasthan'
# url = 'https://en.wikipedia.org/wiki/Tamil_Nadu'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_in_Telangana'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Uttar_Pradesh'
# url = 'https://en.wikipedia.org/wiki/List_of_districts_of_Uttarakhand'
url = 'https://en.wikipedia.org/wiki/List_of_districts_of_West_Bengal'
# TABLE_XPATH = ".//table[@class='wikitable sortable plainrowheaders']"
# DISTRICTS_XPATH = ".//tbody/tr"
# DISTRICT_XPATH = ".//td/a/text()"
# html = requests.get(url_test, headers=header)
# pt = etree.HTML(html.text.lower(), parser=etree.HTMLParser(encoding='utf-8'))
# tb = pt.xpath(INFO_XPATH)
# districts_list = list()
# headquarters_list = list()
# if len(tb):
#     dl = tb[0]
#     table = dl.xpath(TABLE_XPATH)
#     districts = table[0].xpath(DISTRICTS_XPATH)
#     for i in districts:
#         dis = i.xpath(DISTRICT_XPATH)
#         if dis:
#             districts_list.append(dis[0].title())
#             headquarters_list.append(dis[1].title())
#
# print(districts_list)
# print(headquarters_list)

# https://en.wikipedia.org/wiki/Chhattisgarh#Divisions
# url_test = 'https://en.wikipedia.org/wiki/Chhattisgarh#Divisions'
# TABLE_XPATH = ".//table[@class='wikitable sortable']"
# TABLE_XPATH = ".//table[@class='wikitable sortable mw-collapsible']"
TABLE_XPATH = ".//table[@class='wikitable']"
DISTRICT_XPATH = ".//td/div/ul/li/a/text()"

def get_districts_and_headquarters(url,table_path=None):
    if not table_path:
        TABLE_XPATH = ".//table[@class='wikitable sortable']"
    else:
        TABLE_XPATH = table_path
    DISTRICTS_XPATH = ".//tbody/tr"
    DISTRICT_XPATH = ".//td/a/text()"
    html = requests.get(url, headers=header)
    pt = etree.HTML(html.text.lower(), parser=etree.HTMLParser(encoding='utf-8'))
    tb = pt.xpath(INFO_XPATH)
    districts_list = list()
    headquarters_list = list()
    largest_city_list = list()
    if len(tb):
        dl = tb[0]
        tables = dl.xpath(TABLE_XPATH)
        for table in tables:
            districts = table.xpath(DISTRICTS_XPATH)
            for i in districts:
                dis = i.xpath(DISTRICT_XPATH)
                if dis:
                    # districts_list.append(dis[0].title() if len(dis) == 3 else '')
                    # headquarters_list.append(dis[1].title() if len(dis) == 3 else '')
                    # largest_city_list.append(dis[2].title() if len(dis) == 3 else '')
                    districts_list.append(dis[0].title())
                    if len(dis) != 1:
                        headquarters_list.append(dis[1].title())
                    else:
                        headquarters_list.append('')
    return districts_list, headquarters_list

def get_districts_and_headquarters_v1(url,table_path=None, district_xpath=None):
    if not table_path:
        TABLE_XPATH = ".//table[@class='wikitable sortable']"
    else:
        TABLE_XPATH = table_path
    DISTRICTS_XPATH = ".//tbody/tr"
    if not district_xpath:
        DISTRICT_XPATH = ".//td/a/text()"
    else:
        DISTRICT_XPATH = district_xpath
    html = requests.get(url, headers=header)
    pt = etree.HTML(html.text.lower(), parser=etree.HTMLParser(encoding='utf-8'))
    tb = pt.xpath(INFO_XPATH)
    districts_list = list()
    headquarters_list = list()
    largest_city_list = list()
    if len(tb):
        dl = tb[0]
        tables = dl.xpath(TABLE_XPATH)
        for table in tables:
            districts = table.xpath(DISTRICTS_XPATH)
            for i in districts:
                dis = i.xpath(DISTRICT_XPATH)
                if dis:
                    # districts_list.append(dis[0].title() if len(dis) == 3 else '')
                    # headquarters_list.append(dis[1].title() if len(dis) == 3 else '')
                    # largest_city_list.append(dis[2].title() if len(dis) == 3 else '')
                    for i in dis:
                        districts_list.append(i.title())

    return districts_list, headquarters_list



a,b = get_districts_and_headquarters(url)
# a,b = get_districts_and_headquarters_v1(url, TABLE_XPATH, DISTRICT_XPATH)
print(a)
print(b)


