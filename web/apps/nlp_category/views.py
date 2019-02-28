from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse, Http404

import os
from os.path import dirname
import sys

root_path = dirname(dirname(dirname(dirname(os.path.realpath(__file__)))))
apps_path = dirname(dirname(os.path.realpath(__file__)))
sys.path.append(root_path)
sys.path.append(dirname(apps_path))
sys.path.append(apps_path)

# from nlp.processer.nlp_preprocess import ClassificationProccesser

import datetime

# Create your views here.

def index_view(request):
    return HttpResponse("Hello World!")


def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
    return HttpResponse(html)


def category(request):
    """
    返回新闻分类
    :param request:
    :return:
    """
    data = {"title": "", "content": ""}
    if request.method == "POST":
        # print(request.POST)  # 查看客户端发来的请求内容
        return JsonResponse(data)  # 通过 django内置的Json格式 丢给客户端数据

def topcategory(request):
    """
    只返回新闻一级分类
    :param request:
    :return:
    """
    data = {}  # 返回给客户端的数据
    if request.method == "POST":
        # print(request.POST)  # 查看客户端发来的请求内容
        return JsonResponse(data)  # 通过 django内置的Json格式 丢给客户端数据

def subcategory(request):
    """
    只返回新闻二级分类
    :param request:
    :return:
    """
    data = {"topcategory": "xxx", "title": "", "content": ""}
    if request.method == "POST":
        # print(request.POST)  # 查看客户端发来的请求内容
        return JsonResponse(data)  # 通过 django内置的Json格式 丢给客户端数据


