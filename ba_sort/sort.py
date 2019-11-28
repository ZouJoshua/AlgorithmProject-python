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

def bubble_sort_v1(arr):
    """
    算法复杂度：
    时间复杂度：O(n2),O(n),O(n2)
    空间复杂度：O(1)
    稳定性：稳定
    :param arr:
    :return:
    """
    for i in range(1, len(arr)):
        for j in range(len(arr) - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def bubble_sort(arr):
    """
    :param arr:
    :return:
    """
    for i in range(len(arr)):
        for j in range(i, len(arr)):
            if arr[i] > arr[j]:
                arr[i], arr[j] = arr[j], arr[i]
    return arr


## 选择排序

def select_sort(arr):
    """
    算法复杂度：
    时间复杂度：O(n2),O(n2),O(n2)
    空间复杂度：O(I)
    稳定性：不稳定
    :param arr:
    :return:
    """
    n = len(arr)
    for i in range(n-1):
        # 记录最小数的索引
        min_index = i
        for j in range(i+1, n):
            if arr[j] < arr[min_index]:
                min_index = j
        # i不是最小数时，将i和最小数进行交换
        if i != min_index:
            arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr
