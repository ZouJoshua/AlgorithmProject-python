from django.shortcuts import render
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


class TopCategory(object):
    pass


class SubCategory(object):
    pass

