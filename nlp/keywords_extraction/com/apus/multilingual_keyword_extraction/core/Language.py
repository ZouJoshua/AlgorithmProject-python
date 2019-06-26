# coding:utf-8
# Created by houcunyue on 2017/9/20

class Language():
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return self.code.__hash__()

    def __str__(self):
        return self.code + '|' + self.name

unknownLanguage = Language('un', 'unknown')
