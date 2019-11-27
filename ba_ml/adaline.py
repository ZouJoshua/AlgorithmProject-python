#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author   : Joshua_Zou
@Contact  : joshua_zou@163.com
@Time     : 2018/3/14 13:56
@Software : PyCharm
@File     : adaline.py
@Desc     :感知器学习算法(平方误差之和损失函数下的感知机的梯度下降解)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot  as plt


class Adaline(object):
    """
    输入参数：
    :param eta: 学习率，默认为0.01
    :param n_iter: 迭代次数，默认为10次
    :return:
    """
    def __init__(self,eta=0.01, n_iter=10):
        self.eta = eta
        self.n_iter = n_iter

    def fit(self,X,y):
        self.w_ = np.zeros(1 +X.shape[1])
        self.J_ =[]
        for _ in range(self.n_iter):
            errors = y - self.activation(X)
            self.w_[0] += self.eta * errors.sum()
            self.w_[1:] += self.eta * X.T.dot(errors)
            J = errors.dot(errors)/2.
            self.J_.append(J)

    def net_input(self,X):
        return X.dot(self.w_[1:]) + self.w_[0]

    def activation(self,X):
        return self.net_input(X)

    def predict(self,X):
        return np.where(self.net_input(X) >= 0,1,-1)

if __name__ == '__main__':
    """
    用鸢尾花Iris数据集来训练感知机模型。加载两类花：Setosa和Versicolor。属性选定为：sepal length和petal length。
    """
    df = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data', header=None)  # 读取数据还可以用request这个包
    print(df.tail())  # 输出最后五行数据，看一下Iris数据集格式
    #抽取出前100条样本，这正好是Setosa和Versicolor对应的样本，我们将Versicolor对应的数据作为类别1，Setosa对应的作为-1。
    y = df.iloc[0:100, 4].values
    y = np.where(y == 'Iris-setosa', -1, 1)
    X = df.iloc[0:100, [0, 2]].values
    plt.scatter(X[:50, 0], X[:50, 1], color='red', marker='o', label='setosa')
    plt.scatter(X[50:100, 0], X[50:100, 1], color='blue', marker='x', label='versicolor')
    plt.xlabel('petal length')
    plt.ylabel('sepal lenght')
    plt.legend(loc='upper left')
    plt.show()

    #考虑不同学习率下的损失函数
    fig ,ax = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))  # 一行两列的子图分布
    ada1 = Adaline(eta=0.01, n_iter=10)
    ada1.fit(X, y)
    ax[0].plot(range(1, 1 + len(ada1.J_)), np.log10(ada1.J_), marker = 'o')
    ax[0].set_xlabel('Epochs')
    ax[0].set_ylabel('SSE')
    ax[0].set_title('Learning rate: 0.01')
    ada2 = Adaline(eta=0.0001, n_iter=10)
    ada2.fit(X,y)
    ax[1].plot(range(1, 1 + len(ada2.J_)), ada2.J_, marker='o')
    ax[1].set_xlabel('Epochs')
    ax[1].set_ylabel('SSE')
    ax[1].set_title('Learning rate: 0.0001')
    plt.grid(True)
    plt.show()