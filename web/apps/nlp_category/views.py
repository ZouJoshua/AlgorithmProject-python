from django.shortcuts import render
from django.http import HttpResponse

import os
from os.path import dirname
import sys

root_path = dirname(dirname(dirname(dirname(os.path.realpath(__file__)))))
apps_path = dirname(dirname(os.path.realpath(__file__)))
sys.path.append(root_path)
sys.path.append(dirname(apps_path))
sys.path.append(apps_path)

from nlp.processer.nlp_preprocess import ClassificationProccesser


# Create your views here.

def index_view(request):
    return HttpResponse("Hello World!")


class TopCategory(object):
    pass


class SubCategory(object):
    pass

