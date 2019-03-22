#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/3/22 11:23
@File    : regional_process.py
@Desc    : 地域性服务
"""

import os
from os.path import dirname
import sys
root_path = dirname(dirname(dirname(dirname(os.path.realpath(__file__)))))
root_nlp_path = dirname(dirname(dirname(os.path.realpath(__file__))))
sys.path.append(root_path)
sys.path.append(root_nlp_path)

import json
import re

def regional_preprocess(filename='india_division.json'):
    regi_file = os.path.join(root_nlp_path, 'data', filename)
    reader = open(regi_file, 'r', encoding='utf-8')
    line = json.load(reader)
    out = dict()
    # print(line)
    for key, v in line.items():
        if key in ['States', 'Union territories']:
            states = line[key]
            for _k, _v in states.items():
                out_result = {"regional": '',
                              'is_capital': False, 'is_regions': False,
                              'is_divisions': False, 'is_districts': False,
                              'is_headquarters': False, 'is_largest_city': False}
                for i, j in _v.items():
                    out_result['regional'] = _k
                    if j:
                        out_result['is_{}'.format(i)] = True
                        for _j in j:
                            out[_j.title()] = out_result
                    else:
                        continue
    reader.close()
    regi2map_file = os.path.join(root_nlp_path, 'data', 'india_names2regions.json')
    with open(regi2map_file, 'w') as f:
        json.dump(out, f)
    return


def read_map_file(mapfile='india_names2regions.json'):
    map_file = os.path.join(root_nlp_path, 'data', mapfile)
    if not os.path.exists(map_file):
        regional_preprocess()
    else:
        pass
    with open(map_file, 'r', encoding='utf-8') as reader:
        names_map = json.load(reader)
    return names_map


def get_regional(text):
    names_map = read_map_file()
    out = dict()
    for key, value in names_map.items():
        all = re.findall(key, text)
        if len(all):
            out[key] = len(all)
    result = _count_regional(out, names_map)
    return result

def _count_regional(result,names_map):
    out = dict()
    if result:
        for k, v in result.items():
            if k in ['Mumbai', 'Delhi', 'Bengaluru', 'Kolkata', 'Hyderabad']:
                region = k
            else:
                region = names_map[k]['regional']
            if region not in out:
                out[region] = v
            else:
                out[region] += v
    return out


def get_article(file, limit=100):
    reader = open(file, 'r', encoding='utf-8')
    i = 0
    while True:
        line = json.loads(reader.readline())
        yield line
        i += 1
        if i > limit:
            break


if __name__ == '__main__':
    # regional_preprocess()

    datafile = os.path.join(root_path, 'data', 'national')
    line = get_article(datafile)
    for i in line:
        out = get_regional(i['content'])
        print(out)