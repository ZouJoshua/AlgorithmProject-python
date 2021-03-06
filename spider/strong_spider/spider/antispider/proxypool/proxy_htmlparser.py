#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/4 17:06
@File    : proxy_htmlparser.py
@Desc    : 解析html，抽取proxy
"""

import base64
from setting import QQWRY_PATH, CHINA_AREA
from spider.tools.ipaddress import IPAddresss
from spider.tools.utils import text_

import re
from lxml import etree


class HtmlParser(object):

    def __init__(self):
        self.ips = IPAddresss(QQWRY_PATH)

    def parse(self, response, parser):
        '''
        :param response: 响应
        :param type: 解析方式
        :return:
        '''
        if parser['type'] == 'xpath':
            return self.xpath_praser(response, parser)
        elif parser['type'] == 'regular':
            return self.regular_praser(response, parser)
        elif parser['type'] == 'module':
            return getattr(self, parser['moduleName'], None)(response, parser)
        else:
            return None

    def judge_country(self, addr):
        '''
        用来判断地址是哪个国家的
        :param addr:
        :return:
        '''
        for area in CHINA_AREA:
            if text_(area) in addr:
                return True
        return False

    def xpath_praser(self, response, parser):
        '''
        针对xpath方式进行解析
        :param response:
        :param parser:
        :return:
        '''
        proxylist = []
        root = etree.HTML(response)
        proxys = root.xpath(parser['pattern'])
        for proxy in proxys:
            try:
                ip = proxy.xpath(parser['info']['ip'])[0].text
                port = proxy.xpath(parser['info']['port'])[0].text
                type = 0
                protocol = 0
                addr = self.ips.getIpAddr(self.ips.str2ip(ip))
                country = text_('')
                area = text_('')
                if text_('省') in addr or self.judge_country(addr):
                    country = text_('国内')
                    area = addr
                else:
                    country = text_('国外')
                    area = addr
            except Exception as e:
                continue
            proxy = {'ip': ip, 'port': int(port), 'types': int(type), 'protocol': int(protocol), 'country': country,
                     'area': area, 'speed': 100}
            proxylist.append(proxy)
        return proxylist

    def regular_praser(self, response, parser):
        '''
        针对正则表达式进行解析
        :param response:
        :param parser:
        :return: proxylist
        '''
        proxylist = []
        pattern = re.compile(parser['pattern'])
        matchs = pattern.findall(response)
        if matchs != None:
            for match in matchs:
                try:
                    ip = match[parser['info']['ip']]
                    port = match[parser['info']['port']]
                    # 网站的类型一直不靠谱所以还是默认，之后会检测
                    type = 0
                    protocol = 0
                    addr = self.ips.getIpAddr(self.ips.str2ip(ip))
                    country = text_('')
                    area = text_('')
                    if text_('省') in addr or self.judge_country(addr):
                        country = text_('国内')
                        area = addr
                    else:
                        country = text_('国外')
                        area = addr
                except Exception as e:
                    continue
                proxy = {'ip': ip, 'port': port, 'types': type, 'protocol': protocol, 'country': country, 'area': area,
                         'speed': 100}
                proxylist.append(proxy)
            return proxylist

    # 自定义module，针对proxy-list
    def proxy_listPraser(self, response, parser):
        proxylist = []
        pattern = re.compile(parser['pattern'])
        matchs = pattern.findall(response)
        if matchs:
            for match in matchs:
                try:
                    ip_port = base64.b64decode(match.replace("Proxy('", "").replace("')", ""))
                    ip = ip_port.split(':')[0]
                    port = ip_port.split(':')[1]
                    type = 0
                    protocol = 0
                    addr = self.ips.getIpAddr(self.ips.str2ip(ip))
                    country = text_('')
                    area = text_('')
                    if text_('省') in addr or self.judge_country(addr):
                        country = text_('国内')
                        area = addr
                    else:
                        country = text_('国外')
                        area = addr
                except Exception as e:
                    continue
                proxy = {'ip': ip, 'port': int(port), 'types': type, 'protocol': protocol, 'country': country,
                         'area': area, 'speed': 100}
                proxylist.append(proxy)
            return proxylist

    # 自定义module，针对cnproxy
    def cnproxyPraser(self, response, parser):
        proxylist = self.regular_praser(response, parser)
        chardict = {'v': '3', 'm': '4', 'a': '2', 'l': '9', 'q': '0', 'b': '5', 'i': '7', 'w': '6', 'r': '8', 'c': '1'}

        for proxy in proxylist:
            port = proxy['port']
            new_port = ''
            for i in range(len(port)):
                if port[i] != '+':
                    new_port += chardict[port[i]]
            new_port = int(new_port)
            proxy['port'] = new_port
        return proxylist