#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2018/9/4 15:36
@File    : setting.py
@Desc    : 代理抓取配置
"""

import os

# [基础配置]
CHINA_AREA = ['河北', '山东', '辽宁', '黑龙江', '吉林',
              '甘肃', '青海', '河南', '江苏', '湖北', '湖南',
              '江西', '浙江', '广东', '云南', '福建',
              '台湾', '海南', '山西', '四川', '陕西',
              '贵州', '安徽', '重庆', '北京', '上海',
              '天津', '广西', '内蒙', '西藏', '新疆',
              '宁夏', '香港', '澳门']
QQWRY_PATH = os.path.dirname(__file__) + "/data/qqwry.dat"  # 纯真ip文件路径

# [API 配置]
API_HOST = '0.0.0.0'
API_PORT = 5555  # API端口

# [html requests配置]
TIMEOUT = 5  # socket延时
RETRY_TIME = 3

# [数据库配置]

DB_CONFIG = {
    'DB_CONNECT_TYPE': 'sqlalchemy',
    'DB_CONNECT_STRING': 'sqlite:///' + os.path.dirname(__file__) + '/data/proxy.db'
}

# [代理配置]
UPDATE_TIME = 30 * 60  # 每半个小时检测一次是否有代理ip失效
MINNUM = 50  # 当数据库中有效的ip值小于该值时需要启动爬虫进行抓取
DEFAULT_SCORE = 10  # 默认给抓取的ip分配20分,每次连接失败,减一分,直到分数全部扣完从数据库中删除
TEST_URL = 'http://ip.chinaz.com/getip.aspx'
TEST_IP = 'http://httpbin.org/ip'
TEST_HTTP_HEADER = 'http://httpbin.org/get'
TEST_HTTPS_HEADER = 'https://httpbin.org/get'
CHECK_PROXY = {'function': 'checkProxy'}  # CHECK_PROXY变量是为了用户自定义检测代理的函数
# CHECK_PROXY = {'function':'baidu_check'}

# [调度配置]
TASK_QUEUE_SIZE = 50  # 任务队列SIZE
MAX_DOWNLOAD_CONCURRENT = 3  # 从免费代理网站下载时的最大并发
CHECK_WATI_TIME = 1  # 进程数达到上限时的等待时间
MAX_CHECK_PROCESS = 2  # CHECK_PROXY最大进程数
MAX_CHECK_CONCURRENT_PER_PROCESS = 30  # CHECK_PROXY时每个进程的最大并发
THREADNUM = 5  # 线程数量

# [解析方式配置]
"""
抓取代理规则：
{
    'urls': [], #url列表
    'type': 'xpath/regular/module', #解析方式
    'pattern': '', #抽取表达式
    'moduleName': '', #自定义抽取模块（如果解析方式为module）
    'info': 
    {
        'ip': '', 
        'port': '', #端口
        'types': '', #类型(0高匿名，1普通)
        'protocol': '', #传输协议(0 http,1 https)
        'country': '', #国家
        'area': '', #省市
        'updatetime': '', #更新时间
        'speed': '', #连接速度
            }
    }
"""

parserList = [
    {
        'urls': ['http://www.66ip.cn/%s.html' % n for n in ['index'] + list(range(2, 12))],
        'type': 'xpath',
        'pattern': ".//*[@id='main']/div/div[1]/table/tr[position()>1]",
        'info': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]', 'protocol': ''}
    },
    {
        'urls': ['http://www.66ip.cn/areaindex_%s/%s.html' % (m, n) for m in range(1, 35) for n in range(1, 10)],
        'type': 'xpath',
        'pattern': ".//*[@id='footer']/div/table/tr[position()>1]",
        'info': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]', 'protocol': ''}
    },
    {
        'urls': ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218'],
        'type': 'xpath',
        'pattern': ".//table[@class='sortable']/tbody/tr",
        'info': {'ip': './td[1]', 'port': './td[2]', 'type': '', 'protocol': ''}

    },
    {
        'urls': ['http://www.mimiip.com/gngao/%s' % n for n in range(1, 10)],
        'type': 'xpath',
        'pattern': ".//table[@class='list']/tr",
        'info': {'ip': './td[1]', 'port': './td[2]', 'type': '', 'protocol': ''}

    },
    {
        'urls': ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)],
        'type': 'module',
        'moduleName': 'proxy_listPraser',
        'pattern': 'Proxy\(.+\)',
        'info': {'ip': 0, 'port': -1, 'type': -1, 'protocol': 2}

    },
    {
        'urls': ['http://incloak.com/proxy-list/%s#list' % n for n in
                 ([''] + ['?start=%s' % (64 * m) for m in range(1, 10)])],
        'type': 'xpath',
        'pattern': ".//table[@class='proxy__t']/tbody/tr",
        'info': {'ip': './td[1]', 'port': './td[2]', 'type': '', 'protocol': ''}

    },
    {
        'urls': ['http://www.kuaidaili.com/proxylist/%s/' % n for n in range(1, 11)],
        'type': 'xpath',
        'pattern': ".//*[@id='index_free_list']/table/tbody/tr[position()>0]",
        'info': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]', 'protocol': './td[4]'}
    },
    {
        'urls': ['http://www.kuaidaili.com/free/%s/%s/' % (m, n) for m in ['inha', 'intr', 'outha', 'outtr'] for n in
                 range(1, 11)],
        'type': 'xpath',
        'pattern': ".//*[@id='list']/table/tbody/tr[position()>0]",
        'info': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]', 'protocol': './td[4]'}
    },
    {
        'urls': ['http://www.cz88.net/proxy/%s' % m for m in
                 ['index.shtml'] + ['http_%s.shtml' % n for n in range(2, 11)]],
        'type': 'xpath',
        'pattern': ".//*[@id='boxright']/div/ul/li[position()>1]",
        'info': {'ip': './div[1]', 'port': './div[2]', 'type': './div[3]', 'protocol': ''}

    },
    {
        'urls': ['http://www.ip181.com/daili/%s.html' % n for n in range(1, 11)],
        'type': 'xpath',
        'pattern': ".//div[@class='row']/div[3]/table/tbody/tr[position()>1]",
        'info': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]', 'protocol': './td[4]'}

    },
    {
        'urls': ['http://www.xicidaili.com/%s/%s' % (m, n) for m in ['nn', 'nt', 'wn', 'wt'] for n in range(1, 8)],
        'type': 'xpath',
        'pattern': ".//*[@id='ip_list']/tr[position()>1]",
        'info': {'ip': './td[2]', 'port': './td[3]', 'type': './td[5]', 'protocol': './td[6]'}
    },
    {
        'urls': ['http://www.cnproxy.com/proxy%s.html' % i for i in range(1, 11)],
        'type': 'module',
        'moduleName': 'cnproxyPraser',
        'pattern': r'<tr><td>(\d+\.\d+\.\d+\.\d+)<SCRIPT type=text/javascript>document.write\(\"\:\"(.+)\)</SCRIPT></td><td>(HTTP|SOCKS4)\s*',
        'info': {'ip': 0, 'port': 1, 'type': -1, 'protocol': 2}
    }
]