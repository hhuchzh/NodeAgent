#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2017 Samsung Electronics Co., Ltd. All rights reserved.

    CloudUI project

    Filename: loadtest.py
    Description:
        loading test
    Contact: Yu Qiang <johnny.yu@samsung.com>
'''


import urllib,urllib2
import logging
import json
import threading
import time
import random

def GET(url, i):
    s = time.time()
    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req, timeout=10)
        e = time.time()
        code = res.getcode()
        body = res.read()
        print '(%04d)(%d)(%s)(%f)(%s)' % (i, code, body, e-s, url)
    except Exception, e:
        print '(%04d)500' % i


def putapp(appid, dockername, contentid, timeout, token, i):
    url = 'http://127.0.0.1:4999/api/v1/pod/putinfo/' + urllib.quote(dockername) + '?appid=' + urllib.quote(appid) \
           + '&timeout=%d' % timeout + '&contentid=' + urllib.quote(contentid) + '&server_token=asd' + \
          urllib.quote(token) + '&client_token=jkl' + urllib.quote(token)
    GET(url, i)


def getapp(dockername, i):
    url = 'http://127.0.0.1:4999/api/v1/pod/getinfo/' + urllib.quote(dockername)
    t = threading.Thread(target=GET, args=(url, i))
    t.setDaemon(True)
    t.start()


def apprun(dockername, i):
    url = 'http://127.0.0.1:4999/api/v1/pod/apprun/' + urllib.quote(dockername)
    GET(url, i)


def timeout(dockername, i):
    url = 'http://127.0.0.1:4999/api/v1/pod/timeout/' + urllib.quote(dockername)
    GET(url, i)


def dockerstop(dockername, i):
    url = 'http://127.0.0.1:4999/api/v1/pod/terminated/' + urllib.quote(dockername)
    GET(url, i)


def checktoken(dockername, token, i):
    url = 'http://127.0.0.1:4999/api/v1/pod/verifytoken/' + urllib.quote(dockername) + '?token=asd' + urllib.quote(token)
    GET(url, i)


def getdockers():
    url = 'http://127.0.0.1:4999/api/v1/pod/list'
    GET(url, i)


def put():
    for i in range(100):
        if i%2:
            putapp('3201711015081', 'cloudtv-%d' % i, 'content-%d' % i, random.uniform(5, 30), 'qwe', i)
        else:
            putapp('3201707014389', 'cloudtv-%d' % i, 'content-%d' % i, random.uniform(5, 30), 'asd', i)


def get():
    for i in range(100):
        getapp('cloudtv-%d' % i, i)


def run():
    for i in range(100):
        if i % 2:
            apprun('cloudtv-%d' % i, i)
            pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(filename)s:%(lineno)d %(message)s')

    #getapp('cloudui-1', 1)
    #time.sleep(1)
    #putapp('3201707014389', 'cloudui-1', 'content-1', 10, 'asd', 1)
    #time.sleep(10)
    #exit(0)
    #get()
    #time.sleep(2)
    put()
#
    #run()
    #time.sleep(10)
    #exit(0)


    #for i in range(15):
    #    for i in range(100):
    #        timeout('cloudtv-%d' % i, i)
    #    time.sleep(1)


    for i in range(100):
        if not i % 2:
            checktoken('cloudtv-%d' % i, 'asd', i)
        else:
            checktoken('cloudtv-%d' % i, 'asd', i)

    for i in range(100):
        if not i % 2:
            dockerstop('cloudtv-%d' % i, i)

    getdockers()