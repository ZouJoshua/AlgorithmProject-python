# by lauchingjun@baidu
import re

def _parse_from_generator(gen):
    g = {}
    groupstack = [('',g)]
    cur = g

    re_groups = re.compile('^\[[ \\t]*(\.*)((?:[a-zA-Z0-9_]+\.)*)(@?)([a-zA-Z0-9_]+)[ \\t]*\][ \\t]*(?:#.*)?$')
    re_items = re.compile('^[ \r\t]*(@?)([a-zA-Z0-9_]+)[ \t]*:[ \t]*(.*)$')
    for line in gen:
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            continue
        if re_groups.match(line) != None:
            #remove comments
            line = line.split('#', 1)[0].strip()
            line = line.strip('[]')
            groups = line.split('.')
            level = 0
            cur = g
            for i in groups:
                if i == '':
                    cur = groupstack[level+1][1]
                else:
                    if i[0] == '@': #list
                        i = i[1:]
                        if i not in cur:
                            cur[i] = []
                        if type(cur[i]) is not list:
                            return None
                        tmp = {}
                        cur[i].append(tmp)
                        cur = tmp
                        del groupstack[level+1:]
                        groupstack.append( (i,cur) )
                    else: #normal group
                        if i not in cur:
                            cur[i] = {}
                        if type(cur[i]) is not dict:
                            return None
                        cur = cur[i]
                        if groupstack[level][0] != i:
                            del groupstack[level+1:]
                            groupstack.append( (i,cur) )
                level += 1
            del groupstack[level+1:]
        elif re_items.match(line) != None:
            part = line.split(':', 1)
            key = part[0].strip()
            value = part[1].strip()
            if len(value) == 0:
                value = ''
            elif value[0] == '"': #quoted mode
                value = value[1:].rsplit('"', 1)[0]
            else:
                value = value.split('#', 1)[0].strip()

            if key[0] == '@': #list type
                key = key[1:]
                if key not in cur:
                    cur[key] = []
                if type(cur[key]) is not list:
                    return None
                cur[key].append(value)
            else:
                cur[key] = value
        else:
            return None
    return g

def parse_file(file):
    return _parse_from_generator(open(file))

def parse(str):
    return _parse_from_generator(str.split('\n'))

if __name__ == '__main__':
    from pprint import pprint
    import sys
    pprint (parse_file(sys.argv[1]))
