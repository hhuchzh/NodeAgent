#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2017 Samsung Electronics Co., Ltd. All rights reserved.

    CloudUI project

    Filename: main.py
    Description:
    Contact: Yu Qiang <johnny.yu@samsung.com>

    history:
        v0.9
            change some API path
            use config ini
            use uwsgi
        v0.8 2017/11/08
            remove unnecessary lock in podmanager
        v0.7 2017/11/02
            rollback to use app id instead of the app name
            rename to nodeAgent
            remove nodelifecycle
            add docker status API
            add token check API
            merge S3Agent
        v0.6 2017/10/20
            limit log output
        v0.5 2017/10/14
            use role instead of the aws_access_key;
            add region param
        v0.4 2017/10/09
            enable nodeLifeCycle, change reserve 600->900
        v0.3 2017/09/27
            add node life cycle
            use block mode for getappname
        v0.2
            add contentid
        v0.1
            init version;
'''
version = '0.9'

api_version = 'v1'

import os
import sys
import logging
import getopt
import time
import ConfigParser
from flask import Flask, jsonify, make_response, request

from podManager import *
from s3cache import *
from config import config


app = Flask(__name__)

pm = None
s3 = None


def response(body='', status=200):
    resp = make_response(body, status)
    resp.headers['X-API-VERSION'] = version
    return resp


@app.errorhandler(404)
def page_not_found(e):
    return response('request API not exist(v%s)' % version, 404)


@app.route('/')
def index():
    return response(jsonify({'version': version}))


# test: curl -v "http://127.0.0.1:4999/api/v1/pod/getinfo/cloudui-99"
# from docker(web simulator): get app path, id and contentid(if exist)
@app.route('/api/%s/pod/getinfo/<dockername>' % api_version)
def app_get(dockername):
    ret = dict()
    status = 404

    appid, contentid = pm.getappid(dockername)
    logging.debug('getapp %s %s' % (appid, contentid))
    
    if not appid:
        appid='bixbycapsuleviewer'

    if appid:
        path = s3.getapp(appid)
        if path:
            status = 200
            ret['appid'] = appid
            ret['path'] = path
            if contentid:
                ret['contentid'] = contentid
        else:
            logging.error('get app %s fail for %s' % (appid, dockername))


    return response(jsonify(ret), status)


# test: curl -v "http://127.0.0.1:4999/api/v1/app/update/3201707014389"
# from django: notify the app updated in S3. need sync on node
@app.route('/api/%s/app/update/<appid>' % api_version)
def app_update(appid):
    path = s3.getapp(appid, True)
    if path:
        return response(jsonify({'path': path}), 200)
    else:
        return response('', 404)


# test: curl -v "http://127.0.0.1:4999/api/v1/pod/apprun/cloudui-99"
# from docker(web simulator): notify the app running in docker, stop the timeout detect
@app.route('/api/%s/pod/apprun/<dockername>' % api_version)
def pod_apprun(dockername):
    logging.debug('apprun %s' % dockername)
    pm.set_status(dockername, status_app_running)
    return response()


# test: curl -v "http://127.0.0.1:4999/api/v1/pod/putinfo/cloudui-99?appid=3201707014389&timeout=60&vdi_port=3001&rpc_port=3002&contentid=content&server_token=stoken&client_token=ctoken"
# from django: notify the app info which will run in docker
@app.route('/api/%s/pod/putinfo/<dockername>' % api_version)
def pod_putinfo(dockername):
    timeout = request.args.get('timeout', type=int, default=0)
    appid = request.args.get('appid', type=str, default=None)
    vdi_port = request.args.get('vdi_port', type=int, default=None)
    rpc_port = request.args.get('rpc_port', type=int, default=None)
    server_token = request.args.get('server_token', type=str, default=None)
    client_token = request.args.get('client_token', type=str, default=None)
    contentid = request.args.get('contentid', type=str, default='')
    logging.debug('putinfo %s %s %d %s %s %s' % (dockername, appid, timeout, contentid, server_token, client_token))
    if not timeout or not dockername or not server_token or not client_token:
        logging.error('miss params')
        return response('miss params', 400)

    #pm.add_pod(dockername, timeout, vdi_port, rpc_port, appid, contentid, server_token, client_token, status_wait_app_run)
    pm.add_pod(dockername, timeout, vdi_port, rpc_port, appid, contentid, server_token, client_token, status_app_running)
    return response()


# test: curl -v "http://127.0.0.1:4999/api/v1/pod/timeout/cloudui-99?vdi_port=3001&rpc_port=3002"
# from docker(entrypoint.sh): Check whether the target connect timeout after allocate the docker, and collect free dockers
@app.route('/api/%s/pod/timeout/<dockername>' % api_version)
def pod_timeout(dockername):
    #  for collect free dockers
    vdi_port = request.args.get('vdi_port', type=int, default=0)
    rpc_port = request.args.get('rpc_port', type=int, default=0)
    pm.try_add_pod(dockername, vdi_port, rpc_port)

    if pm.timeout(dockername):
        return response('', 201)
    return response()


# test: curl -v "http://127.0.0.1:4999/api/v1/pod/terminated/cloudui-99"
# from django: notify the docker already terminated
@app.route('/api/%s/pod/terminated/<dockername>' % api_version)
def pod_terminated(dockername):
    pm.remove_pod(dockername)
    return response()


# test: curl -v "http://127.0.0.1:4999/api/v1/pod/verifytoken/cloudui-99?token=MTUxMDI5ODU3NS41NDpiYjg3NGQ1MTI1MDAwZGRhOTI0YTQzMjk3NDU2NWNhMjk3YzExOTI"
# from docker(VDI server): check the server token, and return the client token
@app.route('/api/%s/pod/verifytoken/<dockername>' % api_version)
def pod_verifytoken(dockername):
    token = request.args.get('token', type=str, default=None)
    if not token:
        logging.error('miss params')
        return response('miss params', 401)

    ret, client_token = pm.verify_token(dockername, token)
    if ret == 200:
        return response('{"client_token": "%s"}' % client_token, 200)
    else:
        return response('', ret)

# test: curl -v "http://127.0.0.1:4999/api/v1/pod/gettoken/cloudui-99"
# from docker(VDI server): get client token, server token
@app.route('/api/%s/pod/gettoken/<dockername>' % api_version)
def pod_gettoken(dockername):
    ret, client_token, server_token  = pm.get_token(dockername)
    if ret == 200:
        tokens = dict()
        tokens['client'] = client_token
        tokens['server'] = server_token
        return response(jsonify(tokens), 200)
    else:
        return response('', ret)

# test: curl -v "http://127.0.0.1:4999/api/v1/pod/list"
# from django: show current pods status, for restore the pool
@app.route('/api/%s/pod/list' % api_version)
def pod_list():
    ret = list()
    pods = pm.list_pods()
    for name in pods:
        pod = dict()
        pod['name'] = pods[name].name
        pod['status'] = pods[name].status
        pod['vdi_port'] = pods[name].vdi_port
        pod['rpc_port'] = pods[name].rpc_port
        ret.append(pod)

    return response(jsonify(ret), 200)


log_format = '[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(threadName)s(%(thread)d) %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

logging.info('nodeAgent start')

pm = podManager()
try:
    s3 = s3cache()
    logging.info('s3 init finish')
except Exception as error:
    logging.fatal('s3 init error %s' % error)
    exit(-1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.getint('common', 'port'), threaded=True, debug=False)
