#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author   : Joshua_Zou
@Contact  : joshua_zou@163.com
@Time     : 2018/3/14 14:24
@Software : PyCharm
@File     : adalineSGD.py
@Desc     :感知器学习算法(感知机的随机梯度下降解)
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.random import seed
from sklearn.preprocessing import scale

class AdaLineSGD(object):
    """
    输入参数：
    :param eta: 学习率，默认为0.01
    :param n_iter: 迭代次数，默认为10次
    :return:
    """
    def __init__(self, eta=0.01, n_iter=10, shuffle=True, random_state=None):
        self.eta = eta
        self.n_iter = n_iter
        self.shuffle = shuffle
        self.w_initilized = False
        if self.shuffle:
            seed(random_state)

    def fit(self, X, y):
        self.w_ = self._initilized_weights(X.shape[1])
        self.J_ = []
        for _ in range(self.n_iter):
            if self.shuffle:
                X, y = self._shuffle(X, y)
            J = 0
            for xi, yi in zip(X, y):
                error = yi - self.activation(xi)
                self.w_[1:] += self.eta * error * xi
                self.w_[0] += self.eta * error
                J += error**2
            self.J_.append(J/2./len(y))
        return self

    def net_input(self, X):
        return X.dot(self.w_[1:]) + self.w_[0]

    def activation(self, X):
        return self.net_input(X)

    def _initilized_weights(self, d):
        self.w_initilized = True
        return np.zeros(1 + d)

    def _shuffle(self, X, y):
        r = np.random.permutation(X.shape[0])
        return X[r, :], y[r]

    def predict(self, X):
        return self.net_input(X)


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
    X_scaled = scale(X)
    plt.scatter(X_scaled[:50, 0], X_scaled[:50, 1], color='red', marker='o', label='setosa')
    plt.scatter(X_scaled[50:100, 0], X_scaled[50:100, 1], color='blue', marker='x', label='versicolor')
    plt.xlabel('petal length')
    plt.ylabel('sepal lenght')
    plt.legend(loc='upper left')
    plt.show()

    ppn = AdaLineSGD(eta=0.1, n_iter=100)
    ppn.fit(X_scaled, y)
    plt.plot(range(1, len(ppn.J_) + 1), ppn.J_, marker='o')
    plt.xlabel('Epoches')
    plt.ylabel('Number of misclassifications')
    plt.show()