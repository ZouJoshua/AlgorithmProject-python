# [data]
## project schema
```angular2html
# NOTE: When get/get_all/check_update from database with default fields,
#       all following fields should be included in output dict.
{
    'project': {
        'name': str,
        'group': str,
        'status': str,
        'script': str,
        # 'config': str,
        'comments': str,
        # 'priority': int,
        'rate': int,
        'burst': int,
        'updatetime': int,
    }
}
```

## result schema

```angular2html
{
    'result': {
        'taskid': str,  # new, not changeable
        'project': str,  # new, not changeable
        'url': str,  # new, not changeable
        'result': str,  # json string
        'updatetime': int,
    }
}
```
# task schema
```angular2html
{
    'task': {
        'taskid': str,  # new, not change
        'project': str,  # new, not change
        'url': str,  # new, not change
        'status': int,  # change
        'schedule': {
            'priority': int,
            'retries': int,
            'retried': int,
            'exetime': int,
            'age': int,
            'itag': str,
            # 'recrawl': int
        },  # new and restart
        'fetch': {
            'method': str,
            'headers': dict,
            'data': str,
            'timeout': int,
            'save': dict,
        },  # new and restart
        'process': {
            'callback': str,
        },  # new and restart
        'track': {
            'fetch': {
                'ok': bool,
                'time': int,
                'status_code': int,
                'headers': dict,
                'encoding': str,
                'content': str,
            },
            'process': {
                'ok': bool,
                'time': int,
                'follows': int,
                'outputs': int,
                'logs': str,
                'exception': str,
            },
            'save': object,  # jsonable object saved by processor
        },  # finish
        'lastcrawltime': int,  # keep between request
        'updatetime': int,  # keep between request
    }
}
```

## task schema

```angular2html

```
# [proxy]
## proxy schema

```angular2html
{
    'urls': list, #url列表
    'type': str, #解析方式
    'pattern': str, #抽取表达式
    'moduleName': str, #自定义抽取模块（如果解析方式为module）
    'info': 
    {
        'ip': str, 
        'port': int, #端口
        'types': int, #类型(0高匿名，1普通)
        'protocol': int, #传输协议(0 http,1 https)
        'country': str, #国家
        'area': str, #省市
        'updatetime': str, #更新时间
        'speed': int, #连接速度
            }
    }
```