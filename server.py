#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from gevent.pywsgi import WSGIServer
from gevent import monkey;
monkey.patch_all()
import requests
import json
import urlparse
import mtrexpress
import sl

def application(env, start_response):
    if env['PATH_INFO'] == '/sl/':
        return sl.findprice(env, start_response)
    if env['PATH_INFO'] == '/mtr/':
        return mtrexpress.findprice(env, start_response)
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return '<h1>Not Found</h1>'

if __name__ == '__main__':
    print('Serving on 8088...')
    WSGIServer(('', 8088), application).serve_forever()
