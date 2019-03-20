'''
Author: zhangheng04
Date: 2013-09-11

Description:
a common log module, use it to maintain log processing.

Featurs:
auto rotate
rotate detectable
odp-like addNotice method
ub-like setbasic method
generate logid
'''
import string
import sys
import os
import time
import glob
import random
import copy
import inspect

class Logfile(object):
    STDOUT = 1
    STDERR = 2

    ROTATE_NONE = 0
    ROTATE_HOUR = 1
    ROTATE_SIZE = 2
    ROTATE_CHECK_INTERVAL = 10
    KEEP_DAY = 3
    KEEP_CHECK_INTERVAL = 43200

    def __init__(self, file=STDOUT, rotate_type=ROTATE_NONE, rotate_value=0, clean=False):
        self.file = file
        self.rotate_type = rotate_type
        self.rotate_value = rotate_value
        if file == self.STDOUT:
            self.fp = sys.stdout
        elif file == self.STDERR:
            self.fp = sys.stderr
        else:
            self.filename = file
            self.curr_filename = self.gen_curr_filename()
            self.fp = open(self.curr_filename, 'a')

        self.clean = clean
        self.fd = self.fp.fileno()
        self.last_rotate_check = 0
        self.last_clean_check = 0

    def gen_curr_filename(self):
        if self.rotate_type == self.ROTATE_NONE or self.rotate_type == self.ROTATE_SIZE:
            ret = self.filename
        elif self.rotate_type == self.ROTATE_HOUR:
            ret = self.filename + '.' + time.strftime('%Y%m%d%H', time.localtime())
        return ret

    def fileno(self):
        return self.fd

    def reopen(self):
        if hasattr(self.fp, 'close'):
            self.fp.close()
        self.fp = open(self.curr_filename, 'a')
        self.fd = self.fp.fileno()
        if self.rotate_type == self.ROTATE_HOUR:
            if os.path.islink(self.filename):
                os.remove(self.filename)
                os.symlink(self.filename, self.curr_filename)

    def check_rotate(self):
        if os.isatty(self.fd):
            return
        elif time.time() - self.last_rotate_check < self.ROTATE_CHECK_INTERVAL:
            return
        else:
            self.last_rotate_check = time.time()
            if not os.path.isfile(self.filename):
                self.reopen()
                return
            elif self.rotate_type == self.ROTATE_NONE:
                return
            elif self.rotate_type == self.ROTATE_HOUR:
                curr_filename = self.gen_curr_filename() 
                if not curr_filename == self.curr_filename:
                    self.reopen()

    def check_clean(self):
        if os.isatty(self.fd):
            return
        elif not self.clean:
            return
        elif time.time() - self.last_clean_check < self.KEEP_CHECK_INTERVAL:
            return
        else:
            curr_filelist = glob.glob(self.filename + '.*')
            for f in curr_filelist:
                if time.time() - os.stat(f)[8] > self.KEEP_DAY * 86400:
                    os.remove(f)


    def write(self, str):
        self.check_rotate()
        self.check_clean()
        self.fp.write(str)
            
        

class Logger(object):
    LEVEL_FATAL = 1
    LEVEL_WARNING = 2
    LEVEL_NOTICE = 4
    LEVEL_TRACE = 8
    LEVEL_DEBUG = 16

    LEVELS = {
        LEVEL_FATAL: 'FATAL',
        LEVEL_WARNING: 'WARNING',
        LEVEL_NOTICE: 'NOTICE',
        LEVEL_TRACE: 'TRACE',
        LEVEL_DEBUG: 'DEBUG'
    }

    basic = []
    notice = []

    log_id = 0

    @classmethod
    def gen_log_id(cls):
        now = time.time()
        lnow = time.localtime(now)
        s1 = lnow[4] * 60 + lnow[5]
        s2 = int((now - int(now)) * 1000)
        s3 = int(random.random() * 1000)
        cls.log_id = s1 * 1000000 + s2 * 1000 + s3 

    @classmethod
    def get_log_id(cls):
        return cls.log_id
    
    @classmethod
    def set_log_id(cls, log_id):
        cls.log_id = log_id

    def __init__(self):
        self.formatter = string.Template('${level} ${date} ${time} file[${code_file}:${code_lineno}] func[${code_func}] logId[${log_id}] ${basic} ${notice} ${message} errno[${errno}]')
        self.level = self.LEVEL_FATAL|self.LEVEL_WARNING|self.LEVEL_NOTICE|self.LEVEL_TRACE|self.LEVEL_DEBUG
        self.fp = sys.stdout

    def set_level(self, level):
        self.level = level

    def set_fp(self, fp):
        if hasattr(fp, 'write'):
            self.fp = fp
        else:
            return False

    @classmethod
    def set_basic(cls, arr):
        if isinstance(arr, list):
            cls.basic = arr
        else:
            cls.basic = [arr]

    @classmethod
    def add_basic(cls, k, v):
        cls.basic.append([k, v])
 
    @classmethod
    def add_notice(cls, k, v):
        cls.notice.append([k, v])

    @classmethod
    def clean(cls):
        cls.basic = []
        cls.notice = []

    def format_kv(self, arr):
        tmparr = []
        ret = ''
        for i in arr:
            if isinstance(i, list):
                if len(i) < 2:
                    tmparr.append('[%s]' % i[0])
                else:
                    tmparr.append('%s[%s]' % (str(i[0]), str(i[1])))
            else:
                tmparr.append('[%s]' % str(i))
        ret = ' '.join(tmparr)
        return ret

    def get_caller(self):
        f = inspect.currentframe()
        log_module_file = os.path.basename(inspect.getfile(f))
        while True:
            current_file = os.path.basename(inspect.getfile(f))
            if log_module_file == current_file:
                f = f.f_back
            else:
                break
        self.caller_file = current_file
        self.caller_lineno = inspect.getlineno(f)
        self.caller_func = inspect.getframeinfo(f).function

    def write(self, level, msgstr, errno=0):
        now = time.time()
        if not level & self.level:
            return
        else:
            self.get_caller()
            d = {
                'level': self.LEVELS[level],
                'date': time.strftime('%Y-%m-%d', time.localtime(now)),
                'time': time.strftime('%H:%M:%S', time.localtime(now)),
                'log_id': self.log_id,
                'basic': self.format_kv(self.basic),
                'notice': '',
                'message': msgstr,
                'errno': errno,
                'code_file': self.caller_file,
                'code_lineno': self.caller_lineno,
                'code_func': self.caller_func
            }
            if level == self.LEVEL_NOTICE:
                d['notice'] = self.format_kv(self.notice)
            log_str = self.formatter.substitute(d).strip() + '\n'
            self.fp.write(log_str)

_log_conf = {
    'level': Logger.LEVEL_DEBUG,
    'log_path': '',
    'log_file': '',
    'auto_rotate': 'NONE',
    'rotate_value': 0,
    'auto_clean': 0
}

_ROTATE_TYPES = {
    'NONE': Logfile.ROTATE_NONE,
    'HOUR': Logfile.ROTATE_HOUR,
    'SIZE': Logfile.ROTATE_SIZE
}

_loggers = []

def _register_logger(logger):
    global _loggers
    _loggers.append(logger)

def add_notice(k, v=None):
    if v == None:
        v = k
        k = ''
    Logger.add_notice(k, v)

addNotice = add_notice

def set_basic(arr):
    Logger.set_basic(arr)

setBasic = set_basic
setbasic = set_basic

def add_basic(k, v=None):
    if v == None:
        v = k
        k = ''
    Logger.add_basic(k, v)
addBasic = add_basic

def fatal(msgstr, errno=0):
    global _loggers
    for logger in _loggers:
        logger.write(Logger.LEVEL_FATAL, msgstr, errno)

def warning(msgstr, errno=0):
    global _loggers
    for logger in _loggers:
        logger.write(Logger.LEVEL_WARNING, msgstr, errno)

warn = warning

def notice(msgstr, errno=0):
    global _loggers
    for logger in _loggers:
        logger.write(Logger.LEVEL_NOTICE, msgstr, errno)

def trace(msgstr, errno=0):
    global _loggers
    for logger in _loggers:
        logger.write(Logger.LEVEL_TRACE, msgstr, errno)

def debug(msgstr, errno=0):
    global _loggers
    for logger in _loggers:
        logger.write(Logger.LEVEL_DEBUG, msgstr, errno)

def get_log_id():
    return Logger.get_log_id() 

getLogId = get_log_id

def set_log_id(log_id):
    Logger.set_log_id(log_id)

setLogId = set_log_id

def gen_log_id():
    Logger.gen_log_id()

genLogId = gen_log_id

def init(log_conf):
    '''
    initialization of log module. 
    in this procedure, two logger pluged in the pool, a normal one and a 'wf' one, 
    as common in many services in baidu, inc.

    input:
    a dict
    {
        'level': (int),             # can be 1, 2, 4, 8, 16, means fatal, warning, notice, trace, debug
        'log_file': (string),       # file name of log, set as 'as', the file will be 'as.log' and 'as.log.wf'
        'log_path': (string),       # directory of log file would stored in, such as './log'
        'auto_rotate': (string),    # can be 'NONE', 'HOUR', 'SIZE'
        'rotate_value': (int),      # auto_rotate is NONE or HOUR, this will be omitted, in case of SIZE, it is bytes
        'auto_clean': (int),        # 0 or 1, close of open the auto clean feature
    }
    '''
    global _log_conf
    _log_conf.update(log_conf)
    _log_conf['auto_rotate'] = _log_conf['auto_rotate'].upper()
    _log_conf['level'] = int(_log_conf['level'])

    Logger.clean()
    
    level_wf = Logger.LEVEL_FATAL | Logger.LEVEL_WARNING
    level_info = (_log_conf['level'] * 2 - 1) ^ level_wf

    file_info = _log_conf['log_path'] + '/' + _log_conf['log_file'] + '.log'
    file_wf = file_info + '.wf'

    auto_rotate_type = _ROTATE_TYPES[_log_conf['auto_rotate']]
    auto_rotate_value = str(_log_conf['rotate_value']).upper()

    if _log_conf['auto_clean'] == 0:
        auto_clean = False
    else:
        auto_clean = True
    
    logger_info = Logger()
    logger_info.set_level(level_info)
    logfile_info = Logfile(file=file_info, rotate_type=auto_rotate_type, rotate_value=auto_rotate_value, clean=auto_clean)
    logger_info.set_fp(logfile_info)

    logger_wf = Logger()
    logger_wf.set_level(level_wf)
    logfile_wf = Logfile(file=file_wf, rotate_type=auto_rotate_type, rotate_value=auto_rotate_value, clean=auto_clean)
    logger_wf.set_fp(logfile_wf)

    _register_logger(logger_info)
    _register_logger(logger_wf)

    gen_log_id()

def initLog(log_conf):
    '''
    similar with init, but compatable the ancient conf format.
    not recommend
    '''
    log_conf['log_file'] = log_conf['filename']
    log_conf['log_path'] = './log'
    init(log_conf)


