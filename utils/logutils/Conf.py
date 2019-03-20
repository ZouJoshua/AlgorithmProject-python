'''
author: zhangehng04
usage: 
    parse configure files in a dir like odp do it
    all configure file end with '.conf' in the syntax of public/configure
    in the conf dir will merge in a dict.
    the global.conf will treat as the top level, the same as conf root dir.
    if a dir has the same name of a file without .conf, the content in the 
    file will be ignore, unless the dir is empty.
    and also, if a file cannot be parse normally, the key of the file will
    not exist in the conf data.
requirement:
    this module requires configure lib by lauchingjun@baidu

'''

import configure
import os
import glob
import re
import sys
import shlex
import dictmerge

_CONF_FILE_PATTERN = re.compile(r'(.+)\.conf$')
_GLOBAL_CONF = 'global.conf'
_root_path = os.path.abspath(os.path.dirname(sys.argv[0] + '/../conf'))
_encoding='utf8'
_data = {}

_include_pattern = re.compile(r'^\$include(\s|:)')

def init(path, encoding='utf8'):
    ''' 
    param:
        path: dir of configure files, the top dir
    return value:
        None or True: success
        False: failed
    '''
    global _GLOBAL_CONF
    global _root_path
    global _data

    _encoding = encoding

    if not os.path.isdir(path):
        return False
    
    _root_path = path

    data = {}

    parse_res = _recursive_parse(_root_path)
    if isinstance(parse_res, dict):
        data = dictmerge.merge(data, parse_res)
    _data = data

initConf = init

def _recursive_parse(path):
    global _CONF_FILE_PATTERN
    global _root_path
    global _GLOBAL_CONF
    ret = {}
    d_dir = {}
    d_file = {}

    files = os.listdir(path)
    global_conf_fullpath = path + '/' + _GLOBAL_CONF
    if os.path.isfile(global_conf_fullpath):
        ret = configure._parse_from_generator(_generator(global_conf_fullpath))
        if not isinstance(ret, dict):
            ret = {}
    for f in files:
        if f == _GLOBAL_CONF:
            continue
        fullpath = path + '/' + f
        if f[0] == '.':
            continue
        if os.path.isfile(fullpath):
            r = _CONF_FILE_PATTERN.search(f)
            if not r == None:
                d = configure._parse_from_generator(_generator(fullpath))
                k = r.groups()[0]
                if isinstance(d, dict):
                    d_file[k] = d
        else:
            d = _recursive_parse(fullpath)
            if isinstance(d, dict):
                d_dir[f] = d

    d_file = dictmerge.merge(d_file, d_dir)

    if len(d_file) == 0:
        ret = None
    else:
        ret = d_file
    
    return ret

def _generator(file):
    global _include_pattern
    global _encoding
    content = []
    try:
        fp = open(file, 'r')
    except IOError, e:
        return content

    dir = os.path.dirname(file)
    content = []
    for l in fp:
        l = l.strip()
        if len(l) == 0:
            continue
        if l[0] == '#':
            continue
        if not _include_pattern.search(l) == None:
            f = l.split(':', 1)[1]
            f = shlex.split(f)[0]
            included_file = dir + '/' + f
            content += _generator(included_file)
        else:
            content.append(l)
    fp.close()
    return content


def getConf(pattern):
    '''
    param string, path-like pattern to descripe conf level
    such as, if the arrConf is something like {"log": {"level": "4"}},
    Conf.getConf('log/level') will return a string "4", 
    and Conf.getConf('log') will return a dict {"level": "4"}
    None means the pattern is not correct.
    Different from the conf in odp,
    the last '/' will be ignore, more than treat it as a directory.
    '''
    global _data
    items = pattern.strip('/').split('/')
    exp = '_data["' + '"]["'.join(items) + '"]'
    try:
        ret = eval(exp)
    except (KeyError, TypeError), e:
        ret = None
    return ret
