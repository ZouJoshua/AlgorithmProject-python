#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author   : Joshua_Zou
@Contact  : joshua_zou@163.com
@Time     : 2018/5/9 16:03
@Software : PyCharm
@File     : feature_engineer.py
@Desc     : 特征工程处理
"""

from sklearn.datasets import load_iris

#导入IRIS数据集
iris = load_iris()

#特征矩阵
iris.data

#目标向量
iris.target

# 标准化
from sklearn.preprocessing import StandardScaler
# 标准化，返回值为标准化后的数据
StandardScaler().fit_transform(iris.data)

#区间缩放
from sklearn.preprocessing import MinMaxScaler
#区间缩放，返回值为缩放到[0, 1]区间的数据
MinMaxScaler().fit_transform(iris.data)