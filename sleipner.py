import json
import sys
from random import random
from functools import partial
from operator import add
from time import sleep
from itertools import izip_longest
from types import FunctionType, LambdaType

import gevent
import grequests
from lxml import etree, html
from lxml.cssselect import CSSSelector


def bar(percent, n_bars=20):
    percent *= 100
    divisor = 100.0/n_bars
    bars = '['+'='*int(percent/divisor)+(n_bars-int(percent/divisor))*' '+']'
    bars = '\r%d%% %s' % (percent,bars)
    print '\033[F\033[J\033[F'
    print bars
    sys.stdout.flush()


def i(x):
    return hasattr(x, '__iter__')

def e(x, y):
    return type(x) == type(y)

def select(sel,elem):
    sel = CSSSelector(sel)
    return sel(elem)

def write_out(name, ll, dump=True):
    f=open(name, 'a')
    for item in ll:
        if dump==False:
            f.write(item+'\n')
        else:
            f.write(json.dumps(item)+'\n')
    f.close()

def load_urls(fname, delimiter='\n'):
    f = open(fname, 'r')
    entries = f.read().split(delimiter)[:-1]
    f.close()
    return entries

def get(urls, selectors, callbacks=None, n_requests=10, wait_ms=0):
    if isinstance(urls, str):
        urls = [urls]
    iu = i(urls)
    ic = i(callbacks) and not isinstance(callbacks, dict)
    ds = e({1:2}, selectors)
    total = float(len(urls))
    rval = []
    if not ds and not isinstance(selectors, str):
        raise Exception('error selectors must be dictionary or string')
    if not iu and not isinstance(urls, str):
        raise Exception('error urls must be iterable or string')
    if not ic and not (e(callbacks, FunctionType) or e(callbacks, LambdaType) or e({1:2}, callbacks)):
        raise Exception('error callbacks must be a function or iterable')
    epochs = 0
    urls = [grequests.get(x) for x in urls]
    for c in izip_longest(*[iter(urls)]*n_requests, fillvalue=None):
        c = filter(None, c)
        epochs += len(c)
        data = grequests.map(c)
        bar(epochs / total)
        data = [(html.fromstring(x.content)).getroottree() for x in data]
        if ds:
            data = [{k: select(v, x)} for k, v in selectors.items() for x in data]
        else:
            data = [select(selectors, x) for x in data]
        if callbacks is not None:
            if not ic and not isinstance(callbacks, dict):
                data = [callbacks(x) for x in data]
            elif ic:
                for funk in callbacks:
                    data = [funk(x) for x in data]
            else:
                data = [dict([(k, callbacks[k](v)) if (callbacks[k] is not None) else (k, v) for k, v in n.items()]) for n in data]
        rval += data
    return rval



if __name__ == '__main__':
    print get('http://news.ycombinator.com', {'name': '.title>a'}, callbacks={'name': lambda x: [n.text for n in x]})
