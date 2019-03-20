# author: zhangheng04

import copy

def merge(target, src):
    s = copy.deepcopy(src)
    t = copy.deepcopy(target)
    _merge(t, s)
    del s
    return t

def _merge(t, s):
    for k in t.keys():
        if s.has_key(k):
            if isinstance(t[k], dict) and isinstance(s[k], dict):
                _merge(t[k], s[k])
                del s[k]
            elif isinstance(t[k], list) and isinstance(s[k], list):
                t[k] += s[k]
                del s[k]
    t.update(s)
        
