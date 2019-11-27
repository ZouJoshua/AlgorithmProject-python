#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author   : Joshua_Zou
@Contact  : joshua_zou@163.com
@Time     : 2018/3/13 14:47
@Software : PyCharm
@File     : perceptron.py
@Desc     :感知器学习算法(感知机的基本形式——以误分数为损失函数)
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys

sys.path.append(r"D:\Python\Project\TensorFlow\Algorithm")

class Perceptron(object):
    """
    输入参数：
    :param eta: 学习率，默认为0.01
    :param n_iter: 迭代次数，默认为10次
    :return:
    """
    def __init__(self, eta=0.01, n_iter=10):
        self.eta = eta
        self.n_iter = n_iter

    def fit(self, X, y):
        self.w_ = np.zeros(1 + X.shape[1])
        self.J_ = []        # 记录每次迭代的误分数
        for _ in range(self.n_iter):
            J = 0
            for xi, yi in zip(X, y):
                delta = yi - self.activation(xi)
                self.w_[0] += self.eta * delta
                self.w_[1:] += self.eta * delta * xi
                J += int(delta != 0.)
            self.J_.append(J)
        return self

    def net_input(self, X):
        return X.dot(self.w_[1:]) + self.w_[0]

    def activation(self, X):
        # python中的三目运算符
        return np.where(self.net_input(X) >= 0.0, 1, -1)

    def predict(self, X):
        return np.where(self.net_input(X) >= 0.0, 1, -1)

    #批梯度下降
    def __gradient_decent__(self, X, y):
        x_train = np.mat(X)
        y_train = np.mat(y)
        for i in range(self.n):
            self.theta = self.theta + self.alpha * x_train.T * y_train
            self.b = self.b + self.alpha * np.sum(y_train)
    #随机梯度下降
    def __stochastic_gradient_decent__(self, X, y):
        x_train = np.mat(X)
        y_train = np.mat(y)
        [m, n] = x_train.shape
        for i in range(self.n_iter):
            for j in range(m):
                self.theta = self.theta + self.alpha * x_train[j].T * y_train[j]
                self.b = self.b + self.alpha * y_train[j]


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

    ppn = Perceptron(eta=0.1, n_iter=10)
    ppn.fit(X, y)
    plt.plot(range(1, len(ppn.J_) + 1), ppn.J_, marker='o')
    plt.xlabel('Epoches')
    plt.ylabel('Number of misclassifications')
    plt.show()