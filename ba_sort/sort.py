#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 11/13/19 11:17 PM
@File    : sort.py
@Desc    : 排序算法

"""


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
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def bubble_sort_v2(arr):
    n = len(arr)
    for i in range(n-1):  # 遍历n-1次
        for j in range(n-i-1):  # 已经排好序的部分不在遍历
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
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


## 快速排序

def quick_sort(arr):
    """
    算法复杂度：
    时间复杂度：O(nlogn),O(nlogn),O(n2)
    空间复杂度：O(nlogn)
    稳定性：不稳定
    :param arr:
    :return:
    """
    n = len(arr)
    if n <= 1:
        return arr
    base = arr[0]  # 基准值
    left = [arr[i] for i in range(1, n) if arr[i] < base]
    right = [arr[i] for i in range(1, n) if arr[i] >= base]
    return quick_sort(left) + [base] + quick_sort(right)

def quick_sort_v1(arr, left, right):
    """
    算法复杂度：
    时间复杂度：O(nlogn),O(nlogn),O(n2)
    空间复杂度：O(logn)
    稳定性：不稳定
    :param arr:
    :return:
    """
    # 分区操作
    def partition(arr, left, right):
        base = arr[left]
        while left < right:
            while left < right and arr[right] >= base:
                right -= 1
            arr[left] = arr[right]  # 比基准小的交换到前面
            while left < right and arr[left] <= base:
                left += 1
            arr[right] = arr[left]  # 比基准大的交换到后面
        arr[left] = base  #基准值的正确位置,也可以arr[right] = base
        return left  # 返回基准值的索引，也可以return right
    # 递归操作
    if left < right:
        base_index = partition(arr, left, right)
        quick_sort_v1(arr, left, base_index-1)
        quick_sort_v1(arr, base_index, right)

    return arr





## 归并排序

def merge_sort(arr):
    """
    算法复杂度：
    时间复杂度：O(nlogn),O(nlogn),O(nlogn)
    空间复杂度：O(n)
    稳定性：稳定
    :param arr:
    :return:
    """
    n = len(arr)
    if n < 2:
        return arr
    mid = n // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    def merge(left, right):
        result = []
        while left and right:
            if left[0] < right[0]:
                result.append(left.pop(0))
            else:
                result.append(right.pop(0))
        while left:
            result.append(left.pop(0))
        while right:
            result.append(right.pop(0))
        return result
    return merge(left, right)


def merge_sort_v1(arr):

    # 归并过程
    def merge(left, right):
        result = list()
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result = result + left[i:] + right[j:]
        return result

    # 递归过程
    n = len(arr)
    if n <= 1:
        return arr
    mid = n // 2
    left = merge_sort_v1(arr[:mid])
    right = merge_sort_v1(arr[mid:])
    return merge(left, right)


## 直接插入排序
def insert_sort(arr):
    """
    算法复杂度：
    时间复杂度：O(n2),O(n),O(n2)
    空间复杂度：O(I)
    稳定性：稳定
    :param arr:
    :return:
    """
    n = len(arr)
    for i in range(n):
        for j in range(i):
            if arr[i] < arr[j]:
                arr.insert(j, arr.pop(i))
                break
    return arr


def insert_sort_v1(arr):
    """

    :param arr:
    :return:
    """
    n = len(arr)
    for i in range(n):
        pre_index = i - 1
        current = arr[i]  # 保留当前待插入的数
        while pre_index >= 0 and arr[pre_index] > current:
            arr[pre_index + 1] = arr[pre_index]
            pre_index -= 1
        arr[pre_index + 1] = current
    return arr


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