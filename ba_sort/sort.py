#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 11/13/19 11:17 PM
@File    : sort.py
@Desc    : 排序算法

"""


## 直接插入排序
def insert_sort(array):
    """
    算法复杂度：
    时间复杂度：O(n2),O(n2),O(n)
    空间复杂度：O(I)
    稳定性：稳定
    :param array:
    :return:
    """
    for i in range(len(array)):
        for j in range(i):
            if array[i] < array[j]:
                array.insert(j, array.pop(i))
                break
    return array

## 希尔排序
def shell_sort(array):
    """
    算法复杂度：
    时间复杂度：O(n1.3),O(n2),O(n)
    空间复杂度：O(I)
    稳定性：不稳定
    :param array:
    :return:
    """
    gap = len(array)
    while gap > 1:
        gap = gap // 2
        for i in range(gap, len(array)):
            for j in range(i % gap, i, gap):
                if array[i] < array[j]:
                    array[i], array[j] = array[j], array[i]
    return array

## 冒泡排序
def bubble_sort(array):
    """
    算法复杂度：
    时间复杂度：O(n2),O(n2),O(n)
    空间复杂度：O(I)
    稳定性：不稳定
    :param array:
    :return:
    """
    for i in range(len(array)):
        for j in range(i, len(array)):
            if array[i] > array[j]:
                array[i], array[j] = array[j], array[i]
    return array


