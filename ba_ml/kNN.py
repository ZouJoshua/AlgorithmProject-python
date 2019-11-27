#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author   : Joshua_Zou
@Contact  : joshua_zou@163.com
@Time     : 2018/3/30 11:29
@Software : PyCharm
@File     : kNN.py
@Desc     : k近邻算法
"""

import numpy as np
import operator


def createDataSet():
    array = np.array([[1.,1.1],[1.,1.],[0,0],[0,0.1]])
    labels = ["A","A","B","B"]
    return array,labels

def kNN0(inx,dataset,label,k):
    """
    对未知类别属性的数据集中的每个点依次执行以下操作：
    (1)计算已知类别数据集中的点与当前点之间的距离；
    (2)按照距离递增次序排序；
    (3)选取与当前点距离最小的走个点；
    (4)确定前灸个点所在类别的出现频率；
    (5)返回前女个点出现频率最高的类别作为当前点的预测分类。
    """
    m = dataset.shape[0]
    #计算欧氏距离
    diffmat = np.tile(inx,(m,1)) - dataset
    sqdiffmat = diffmat ** 2
    sqdistance = sqdiffmat.sum(axis = 1)
    distance = sqdistance ** 0.5
    #选择距离最小的点k
    sorteddistance = distance.argsort()
    classcount = {}
    for i in range(k):
        voteilabel = label[sorteddistance[i]]
        classcount[voteilabel] = classcount.get(voteilabel,0) + 1
    #排序
    sortedclasscount = sorted(classcount.items(),key = operator.itemgetter(1),reverse = True)
    return sortedclasscount[0][0]

if __name__ == "__main__":
    dataset,label = createDataSet()
    lab = kNN0([0,0],dataset,label, 2)
    print(lab)