# coding:utf-8
# Created by houcunyue on 2017/9/20

def reverseDictionary(map):
    return dict([(kv[1], kv[0]) for kv in map.items()])
