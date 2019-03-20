#! /usr/bin/env python
# -*- coding:utf8 -*-
# author: zhangheng04
# date: 2013-10-08
# version: 2.0.0

import Log
import Conf
import sys
import os
import ConfigParser
import re
import glob
import string
import select
import subprocess
import errno
import getopt
import time
import copy
import fnmatch

MIN_IN_A_DAY = 1440
MIN_IN_AN_HOUR = 60
SEC_IN_A_DAY = 86400
SEC_IN_AN_HOUR = 3600
SEC_IN_A_MIN = 60

class SelectorLog(object):
    def get(self, a, b):
        if a.rotate_interval < b.rotate_interval:
            return a
        else:
            return b
            
class SelectorExe(object):
    def get(self, a, b):
        a.module_name += b.module_name
        return a

class ObjPool(object):
    def __init__(self, key='', selector=None):
        self.key = key
        self.data = {}   
        self.selector = selector
        
    def add_obj(self, obj):
        id = getattr(obj, self.key)
        if id in self.data.keys():
            if self.selector == None:
                return self.data[id]
            else:
                self.data[id] = self.selector.get(self.data[id], obj)
        else:
            self.data[id] = obj
        
    def set_obj(self, obj):
        id = getattr(obj, self.key)
        self.data[id] = obj
    
    def get_all_objs(self):
        ret = []
        for k in self.data.keys():
            ret.append(self.data[k])

        return ret

    def __str__(self):
        return ','.join(self.data.keys())

class ExeProxy(object):
    def __init__(self, cmdstr, module_name, timeout=5):
        self.cmdstr = cmdstr
        self.timeout = timeout
        self.deadline = time.time() + timeout
        self.returncode = 0
        self.cost = None
        self.output = None
        self.module_name = [module_name]
        self.invoked = False

    def execute(self):
        if not self.invoked:
            timer_start = time.time()
            p = subprocess.Popen(self.cmdstr, bufsize=-1, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            while True:
                returncode = p.poll()
                if returncode != None:
                    self.returncode = returncode
                    self.output = p.stdout.read()
                    break
                if time.time() > self.deadline:
                    self.returncode = errno.ETIMEDOUT
                    self.output = 'timeout'
                    break
                time.sleep(0.1)
            self.cost = int((time.time() - timer_start) * 1000)
            self.invoked = True
        return self.returncode

class LogFile(object):
    def __init__(self, filepath, module_name, rotate_interval=SEC_IN_AN_HOUR, keep_period=SEC_IN_A_DAY*7, format='', auto_touch=True):
        self.filepath = filepath
        self.module_name = module_name
        self.filename = os.path.basename(self.filepath)
        self.logdir = os.path.dirname(self.filepath)
        self.rotate_interval = int(rotate_interval)
        self.keep_period = keep_period
        self.auto_touch = auto_touch
        self.scheduled = False
        if format == '':
            self.gen_format()
        else:
            self.format = string.Template(format)
        
        self.rotate_ok = -1
        self.trace_back_result = []

    def gen_format(self):
        fmt_str = ''
        if self.rotate_interval % SEC_IN_A_DAY == 0:
            fmt_str = '${filename}.${date}'
        elif self.rotate_interval % SEC_IN_AN_HOUR == 0:
            fmt_str = '${filename}.${date}${hour}'
        else:
            fmt_str = '${filename}.${date}${hour}${min}'

        self.format = string.Template(fmt_str)

    def clean(self, now=time.time()):
        pat = self.filepath + '.*'
            
        if os.path.isdir(self.logdir):
            files = glob.glob(pat)
            expire = now - self.keep_period
            for f in files:
                if os.path.isfile(f) and not os.path.islink(f):
                    if os.stat(f).st_mtime < expire:
                        os.remove(f)

        return 0

    def get_dict(self, sec):
        t = time.localtime(sec)
        ret = {
            'filename': self.filepath,
            'date': time.strftime('%Y%m%d', t),
            'year': time.strftime('%Y', t),
            'mon': time.strftime('%m', t),
            'month': time.strftime('%m', t),
            'day': time.strftime('%d', t),
            'hour': time.strftime('%H', t),
            'min': time.strftime('%M', t),
        }  
         
        return ret

    def trace_back(self, now=time.time()):
        if os.path.isdir(self.logdir):
            end_point = int(now / self.rotate_interval) * self.rotate_interval - self.rotate_interval
            start_point = end_point - SEC_IN_A_DAY
            for p in range(start_point, end_point, self.rotate_interval):
                d = self.get_dict(p)
                target_file = self.format.substitute(d)
                if not os.path.isfile(target_file):
                    if self.auto_touch == True:
                        open(target_file, 'a').close()
                        self.trace_back_result.append(target_file)
                        Log.trace('a historical log file %s missed, touch it automatically' % (target_file))
                    else:
                        self.trace_back_result.append(target_file)
                        Log.warning('a historical log file %s missed, but auto touch disabled for some reason, check it manually' % (target_file))
        return 0

    def check_scheduled(self, now=time.time()):
        now = int(now / SEC_IN_A_MIN) * SEC_IN_A_MIN
        if now % self.rotate_interval == 0:
            self.scheduled = True
        Log.trace('check scheduled module[%s] log[%s] result[%s]' % (self.module_name, self.filepath, str(self.scheduled)))

    def rotate(self, now=time.time()):
        self.check_scheduled(now)
        ret = 0
        if self.scheduled == True:
            Log.trace('start to rotate log[%s] module[%s]' % (self.filepath, self.module_name))
            d = self.get_dict(now - self.rotate_interval)
            target_file = self.format.substitute(d)
            # log dir does not exist
            if not os.path.isdir(self.logdir):
                ret = 0
    
            # target file already exists
            elif os.path.isfile(target_file):
                ret = 0

            # log file does not exist
            elif not os.path.isfile(self.filepath):
                Log.trace('log file %s does not exist, touch %s' % (self.filepath, target_file))
                open(target_file, 'a').close()

            # log file is a symbol link
            elif os.path.islink(self.filepath):
                Log.trace('log file %s is a link, touch %s' % (self.filepath, target_file))
                open(target_file, 'a').close()

            # normal rename
            else:
                Log.trace('rename %s to %s' % (self.filepath, target_file))
                os.rename(self.filepath, target_file)
                
            # check result
            if os.path.isfile(target_file):
                ret = 0
                Log.trace('rotate %s to %s successfully' % (self.filepath, target_file))
            else:
                ret = 1
                Log.warning('rotate %s to %s failed, target file %s does not exist' % (self.filepath, target_file, target_file))
            
        self.rotate_ok = ret
        
        return ret

class ModuleConf(object):
    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.c = ConfigParser.ConfigParser()
        self.c.read(self.conf_file)

    def trim_hostname(self, str):
        ret = str.strip()
        ret = ret.rsplit('.baidu.com', 1)[0]
        return ret

    def get_all_modulenames(self):
        secs = self.c.sections()
        ignore_secs = ['Machine']
        ret = list(set(secs).difference(set(ignore_secs)))
        return ret

    def get_modulenames_by_hostname(self, hostname):
        attr = self.get_attr_by_hostname(hostname)
        all_modulenames = self.get_all_modulenames()
        ret = list(set(attr).intersection(set(all_modulenames)))
        return ret 
    
    def get_attr_by_hostname(self, hostname):
        hostname = self.trim_hostname(hostname)
        if hostname in self.c.options('Machine'):
            ret = self.c.get('Machine', hostname).split()
        else:
            ret = []
        return ret

    def get_all_hostnames(self):
        ret = self.c.options('Machine')
        return ret

    def get_module_conf_by_modulename(self, modulename):
        ret = dict(self.c.items(modulename))
        ret['name'] = modulename
        if ret.has_key('keep'):
            ret['keep'] = int(ret['keep'])
        if ret.has_key('log_keep'):
            ret['log_keep'] = int(ret['log_keep'])

        if ret.has_key('keep') and not ret.has_key('log_keep'):
            ret['log_keep'] = ret['keep']

        if ret.has_key('log_rotate_interval'):
            ret['log_rotate_interval'] = int(ret['log_rotate_interval'])

        if not ret.has_key('log_rotate_interval'):
            ret['log_rotate_interval'] = 60

        if not ret.has_key('log_keep'):
            ret['log_keep'] = 7

        if not ret.has_key('log_rotate_preop'):
            ret['log_rotate_preop'] = ''

        if not ret.has_key('log_rotate_postop'):
            ret['log_rotate_postop'] = ''

        if not ret.has_key('log_rotate'):
            ret['log_rotate'] = 1

        if not ret.has_key('log_clean'):
            ret['log_clean'] = 1

        if not ret.has_key('no_auto_touch'):
            ret['no_auto_touch'] = ''
        
        ret['no_auto_touch'] = ret['no_auto_touch'].split()
        
        if not ret.has_key('service_conf'):
            ret['service_conf'] = ''

        if not ret.has_key('log'):
            ret['log'] = []
        else:
            ret['log'] = ret['log'].split()
           
        return ret
        
class Rotator(object):
    def __init__(self, module_confs):
        logselector = SelectorLog()
        self.log_pool = ObjPool('filepath', logselector)
        exeselector = SelectorExe()
        self.pre_exe_pool = ObjPool('cmdstr', exeselector)
        self.post_exe_pool = ObjPool('cmdstr', exeselector)
        self.module_confs = module_confs
        self.prep()
        self.results = {} 

    def __str__(self):
        ret = ''
        ret += 'logs:\n'
        for l in self.log_pool.get_all_objs():
            ret += '%s|%d|%s\n' % (l.filepath, l.rotate_interval, l.module_name)

        ret += 'pre_cmd:\n'
        for ep in self.pre_exe_pool.get_all_objs():
            ret += '%s|%s\n' % (ep.cmdstr, ep.module_name)

        ret += 'post_cmd:\n'
        for ep in self.post_exe_pool.get_all_objs():
            ret += '%s|%s\n' % (ep.cmdstr, ep.module_name) 
        return ret
        
    def parse_service_conf(self, str, module_name):
        ret = []
        if ':' in str:
            stype = ''
            root = ''
            filters = []
            data = {} 
            for s in str.split(';'):
                a = s.split(':')
                if len(a) != 2:
                    continue
                (k, v) = a
                k = k.strip()
                v = v.strip()
                if k == 'type':
                    stype = v
                else:
                    data[k] = v

            tmp = []
            if stype == 'odp-app':
                if data.has_key('filter'):
                    filters = data['filter'].split()
                else:
                    filters = []

                if data.has_key('root'):
                    root = data['root']
                else:
                    root = os.path.expanduser('~/odp')

                app_dir = '%s/app' % root
                apps = []
                include_filters = []
                exclude_filters = []
                includes = []
                excludes = []
                    
                for pat in filters:
                    if pat[0] == '+':
                        include_filters.append(pat[1:])
                    elif pat[0] == '-':
                        exclude_filters.append(pat[1:])
                    else:
                        include_filters.append(pat)

                if include_filters == [] and exclude_filters != []:
                    include_filters = ['*']
                       
                for i in os.listdir(app_dir):
                    if not os.path.isdir(app_dir + '/' + i):
                        continue

                    for pat in include_filters:
                        if fnmatch.fnmatch(i, pat):
                            includes.append(i)
                    for pat in exclude_filters:
                        if fnmatch.fnmatch(i, pat):
                            excludes.append(i)
                   
                apps = list(set(includes).difference(set(excludes))) 
                for i in apps:
                    log_dir = '%s/log/%s' % (root, i)
                    if not os.path.isdir(log_dir):
                        os.makedirs(log_dir)
                        Log.trace('log dir %s does not exist while appending logs from a odp-app, make it' % (log_dir))
                    tmp.append('%s/%s.log' % (log_dir, i))
                    tmp.append('%s/%s.log.wf' % (log_dir, i))
                    tmp.append('%s/%s.log.new' % (log_dir, i))
                    tmp.append('%s/%s.log.wf.new' % (log_dir, i))                        
                    tmp.append('%s/%s.profiler' % (log_dir, i))
            
            elif stype == 'c-app':
                if data.has_key('root'):
                    root = data['root']
                else:
                    root = os.path.expanduser('~')

                if data.has_key('log_name'):
                    log_name = data['log_name']
                else:
                    log_name = module_name

                if data.has_key('filter'):
                    filters = data['filter'].split()
                else:
                    filters = []

                if filters != []:
                    app_dir = '%s/app' % root
                    apps = []
                    include_filters = []
                    exclude_filters = []
                    includes = []
                    excludes = []
                    app_dir = root

                    for pat in filters:
                        if pat[0] == '+':
                            include_filters.append(pat[1:])
                        elif pat[0] == '-':
                            exclude_filters.append(pat[1:])
                        else:
                            include_filters.append(pat)

                    if include_filters == [] and exclude_filters != []:
                        include_filters = ['*']
                       
                    for i in os.listdir(app_dir):
                        if not os.path.isdir(app_dir + '/' + i):
                            continue

                        for pat in include_filters:
                            if fnmatch.fnmatch(i, pat):
                                includes.append(i)
                        for pat in exclude_filters:
                            if fnmatch.fnmatch(i, pat):
                                excludes.append(i)
                   
                    apps = list(set(includes).difference(set(excludes))) 
                    for i in apps:
                        log_dir = '%s/%s/log' % (root, i)
                        tmp.append('%s/%s.log' % (log_dir, log_name))
                        tmp.append('%s/%s.log.wf' % (log_dir, log_name))
                
            ret += tmp
       
        return ret

    def parse_log_pattern(self, pats):
        ret = []
        for pat in pats:
            if pat[0] == '~':
                pat = os.path.expanduser(pat)
            if '*' in pat:
                ret += glob.glob(pat)
            else:
                ret.append(pat)    

        return ret
                        
    def prep(self):
        for c in self.module_confs:
            module_name = c['name']
            logs = []
            if len(c['log']) > 0:
                logs += self.parse_log_pattern(c['log'])

            service_conf = c['service_conf']
            if len(service_conf) > 0:
                logs += self.parse_service_conf(service_conf, module_name)

            Log.trace('module[%s] logs[%s]' % (module_name, ','.join(logs)))
            
            rotate_interval = c['log_rotate_interval'] * SEC_IN_A_MIN
            keep_period = c['log_keep'] * SEC_IN_A_DAY
            if c.has_key('log_rotate_format'):
                format_str = c['log_rotate_format']
            else:
                format_str = ''
 
            for filepath in logs:
                rotate_interval = c['log_rotate_interval'] * SEC_IN_A_MIN
                keep_period = c['log_keep'] * SEC_IN_A_DAY
                if c.has_key('log_rotate_format'):
                    format_str = c['log_rotate_format']
                else:
                    format_str = ''
                auto_touch = True
                for pat in c['no_auto_touch']:
                    if fnmatch.fnmatch(filepath, pat):
                        auto_touch = False
                        break
                logobj = LogFile(filepath, module_name, rotate_interval, keep_period, format_str, auto_touch)
                
                self.log_pool.add_obj(logobj)

            if c.has_key('log_rotate_preop'):
                if len(c['log_rotate_preop']) > 0:
                    ep = ExeProxy(c['log_rotate_preop'], module_name)
                    self.pre_exe_pool.add_obj(ep)

            if c.has_key('log_rotate_postop'):
                if len(c['log_rotate_postop']) > 0:
                    ep = ExeProxy(c['log_rotate_postop'], module_name)
                    self.post_exe_pool.add_obj(ep)
        Log.trace('all logs[%s]' % (str(self.log_pool)))

    def rotate(self, timestamp):
        self.scheduled_modulenames = []
        failed_pre_modulenames = []
        failed_rotate_modulenames = []
        failed_post_modulenames = []

        for l in self.log_pool.get_all_objs():
            l.check_scheduled(timestamp)
            if l.scheduled:
                self.scheduled_modulenames.append(l.module_name)

        Log.trace('preop[%s]' % self.pre_exe_pool)

        for ep in self.pre_exe_pool.get_all_objs():
            for module_name in ep.module_name:
                if module_name in self.scheduled_modulenames:
                    ep.execute()
                    Log.trace('execute pre op, module[%s] precmd[%s] cost[%d] returncode[%d] output[%s]' % (ep.module_name, ep.cmdstr, ep.cost, ep.returncode, ep.output))
                    if ep.returncode != 0:
                        Log.warning('Error[PREOP] Abstract[Unexpected Return Code] Detail[cost:%d, output:%s, cmdstr:%s, returncode:%d, modulename:%s]' % (ep.cost, ep.output, ep.cmdstr, ep.returncode, ep.module_name))
                        failed_pre_modulenames.append(ep.module_name)

        Log.trace('preexe failed[%s]' % str(failed_pre_modulenames))

        for l in self.log_pool.get_all_objs():
            if l.module_name in failed_pre_modulenames:
                continue
            l.rotate(timestamp)
            if l.scheduled:
                Log.trace('rename, module[%s] filepath[%s]' % (l.module_name, l.filepath))
                if l.rotate_ok != 0:
                    Log.warning('Error[ROTATE] Abstract[Uexpected Renaming Result] Detail[modulename:%s, filepath:%s]' % (l.module_name, l.filepath))
                    failed_rotate_modulenames.append(l.module_name)

        for ep in self.post_exe_pool.get_all_objs():
            for module_name in ep.module_name:
                if module_name in failed_pre_modulenames or module_name in failed_rotate_modulenames:
                    continue
                if module_name in self.scheduled_modulenames:
                    ep.execute()
                    Log.trace('execute post op, module[%s] postcmd[%s] cost[%d] returncode[%d] output[%s]' % (ep.module_name, ep.cmdstr, ep.cost, ep.returncode, ep.output))            
                    if ep.returncode != 0:
                        Log.warning('Error[POSTOP] Abstract[Unexpected Return Code] Detail[cost:%d, output:%s, cmdstr:%s, returncode:%d, modulename:%s]' % (ep.cost, ep.output, ep.cmdstr, ep.returncode, module_name))
                        failed_post_modulenames += ep.module_name
        self.failed_modulenames = list(set(failed_pre_modulenames + failed_rotate_modulenames + failed_post_modulenames))

    def trace_back(self):
        for l in self.log_pool.get_all_objs():
            l.trace_back()

    def clean_expired(self, timeout = 5):
        start_time = time.time()
        for l in self.log_pool.get_all_objs():
            l.clean()
            if time.time() - start_time > timeout:
                break

    def get_result(self):
        tmp_dict = {}
        res_skel = {
            'module_name': '',
            'scheduled': False,
            'success': True,
            'failed': [],
            'preop': {
                'cmdstr': '',
                'retcode': 0,
                'cost': 0,
                'output': ''
            },
            'rotate': {
                'success': [],
                'failed': []
            },
            'postop': {
                'cmdstr': '',
                'retcode': 0,
                'cost': 0,
                'output': ''
            },
            'trace_back': {
                'auto_touch': [],
                'no_auto_touch': []
            }
        }
        for l in self.log_pool.get_all_objs():
            res = None 
            if l.module_name in tmp_dict.keys():
                res = tmp_dict[l.module_name]
            else:
                res = copy.deepcopy(res_skel)
                res['module_name'] = l.module_name
                tmp_dict[l.module_name] = res
            if l.rotate_ok == 0:
                res['rotate']['success'].append(l.filepath)
            else:
                res['rotate']['failed'].append(l.filepath)
                res['failed'].append('rotate')
                res['success'] = False

            if l.auto_touch:
                res['trace_back']['auto_touch'] = l.trace_back_result
            else:
                res['trace_back']['no_auto_touch'] = l.trace_back_result

            if len(res['trace_back']['no_auto_touch']) > 0:
                res['success'] = False
                res['failed'].append('trace_back')

        for ep in self.pre_exe_pool.get_all_objs():
            if ep.module_name in tmp_dict.keys():
                res = tmp_dict[ep.module_name]
            else:
                res = copy.deepcopy(res_skel)
                res['module_name'] = ep.module_name
                tmp_dict[l.module_name] = res

            res['preop']['cmdstr'] = ep.cmdstr
            res['preop']['retcode'] = ep.returncode
            res['preop']['cost'] = ep.cost
            res['preop']['output'] = ep.output
            if res['preop']['retcode'] != 0:
                res['failed'].append('preop')
            

        for ep in self.post_exe_pool.get_all_objs():
            if ep.module_name in tmp_dict.keys():
                res = tmp_dict[ep.module_name]
            else:
                res = copy.deepcopy(res_skel)
                res['module_name'] = ep.module_name
                tmp_dict[l.module_name] = res

            res['postop']['cmdstr'] = ep.cmdstr
            res['postop']['retcode'] = ep.returncode
            res['postop']['cost'] = ep.cost
            res['postop']['output'] = ep.output
            if res['postop']['retcode'] != 0:
                res['failed'].append('postop')
            
        for k in tmp_dict.keys():
            if k in self.scheduled_modulenames:
                tmp_dict[k]['scheduled'] = True
            if k in self.failed_modulenames:
                tmp_dict[k]['success'] = False
             
        ret = tmp_dict
        return ret
            
class Main(object):
    def __init__(self, base_path):
        self.base_path = base_path
        self.conf_path = self.base_path + '/conf'
        Conf.init(self.conf_path)
        log_conf = Conf.getConf('log')
        Log.init(log_conf)

        self.module_conf = ModuleConf(Conf.getConf('module_conf/file_path'))
        self.modules = []
        self.modulenames = []
        self.scheduled_modulenames = []
        self.failed_modules = []
        self.cost = 0

    def parse_args(self):
        (opts, args) = getopt.getopt(sys.argv[1:], 't:', ['logid='])
        opts = dict(opts)
        if opts.has_key('-t'):
            self.timestamp = int(opts['-t'])
        else:
            self.timestamp = int(time.time())

        Log.add_notice('timestamp', self.timestamp)

        if opts.has_key('--logid'):
            Log.set_log_id(opts['--logid'])

    def get_hostname(self):
        ret = os.uname()[1].split('.baidu.com')[0]
        return ret

    def check_result(self):
        scheduled_modulenames = []
        failed_modulenames = []
        failed_modules = {}
        missed = []
        result = self.rotator.get_result()
        Log.trace('result[%s]' % result)
        for k in result.keys():
            mres = result[k]
            if mres['scheduled']:
                scheduled_modulenames.append(k)

            if not mres['success']:
                failed_modulenames.append(k)
                failed_modules[k] = ''
                for s in mres['failed']:
                    if s == 'rotate':
                        failed_modules[k] += 'failed to rename[%s];' % (','.join(mres['rotate']['failed']))
                    if s == 'preop' or s == 'postop':
                        failed_modules[k] += 'failed to execute %s, cmdstr[%s], returncode[%d], output[%s], cost[%d];' % (s, mres[s]['cmdstr'], mres[s]['retcode'], mres[s]['output'], mres[s]['cost'])
                    if s == 'trace_back':
                        failed_modules[k] += 'miss files [%s]' % (','.join(mres['trace_back']['no_auto_touch']))

        output_lines = []
        output_lines.append('BEGIN')
        output_lines.append('hostname: %s' % (self.get_hostname()))
        output_lines.append('cost: %s' % (self.cost))
        output_lines.append('modules: %s' % (','.join(self.modulenames)))
        output_lines.append('scheduled: %s' % (','.join(scheduled_modulenames)))
        output_lines.append('failed: %s' % (','.join(failed_modulenames)))
        for k in failed_modules.keys():
            output_lines.append('%s: %s' % (k, failed_modules[k]))

        output_lines.append('END')
        print '\n'.join(output_lines)

    
    def main(self):
        Log.trace('STAGE[enter main]')
        time_start = time.time()
        self.parse_args()
        hostname = self.get_hostname()

        modulenames = self.module_conf.get_modulenames_by_hostname(hostname)
        if(modulenames==None or len(modulenames)==0):
            hostname='local'
            modulenames = self.module_conf.get_modulenames_by_hostname(hostname)
        
        moduleconfs = []
        Log.add_notice('local_modules', ';'.join(modulenames))
        for modulename in modulenames:
            module_conf_dict = self.module_conf.get_module_conf_by_modulename(modulename)
            moduleconfs.append(module_conf_dict)
        self.rotator = Rotator(moduleconfs)

        Log.trace('STAGE[rotate]')
        self.rotator.rotate(self.timestamp)

        Log.trace('STAGE[trace back]')
        self.rotator.trace_back()

        Log.trace('STAGE[clean]')
        self.rotator.clean_expired()

        
        self.cost = int((time.time() - time_start) * 1000)
        self.check_result()
        Log.add_notice('cost', self.cost)
        Log.notice('')


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    app = Main(base_dir)
    app.main()
