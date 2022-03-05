#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2017 Samsung Electronics Co., Ltd. All rights reserved.

    CloudUI project

    Filename: podManager.py
    Description:
    Contact: Yu Qiang <johnny.yu@samsung.com>

    history:
        v0.1
            init version;
'''

import logging
import time
import threading

from podStatus import *
from podInfo import podInfo

from config import config

class podManager:
    def __init__(self):
        self.mutex = threading.Lock()
        self.appget_timeout = config.getint('s3', 'appget_timeout')
        self.pods = dict()  # pods['name'] = podInfo
        ##self.waitting_list = dict()

    def add_pod(self, docker_name, timeout, vdi_port, rpc_port, appid, contentid, server_token, client_token, status):
        self.mutex.acquire()
        self.pods[docker_name] = podInfo(docker_name, timeout, vdi_port, rpc_port, appid, contentid,
                                               server_token, client_token, status)
        #try:
        #    if docker_name in self.waitting_list:
        #        for waitting in self.waitting_list[docker_name]:
        #            waitting.set()
        #        del self.waitting_list[docker_name]
        #except Exception as e:
        #    logging.error(e)
        self.mutex.release()
        return True

    def try_add_pod(self, docker_name, vdi_port, rpc_port, timeout=None, appid=None, contentid=None,
                    server_token=None, client_token=None, status=status_running):
        if docker_name in self.pods:
            return False

        return self.add_pod(docker_name, timeout, vdi_port, rpc_port, appid, contentid,
                            server_token, client_token, status)

    def remove_pod(self, docker_name):
        self.mutex.acquire()
        if docker_name in self.pods:
            del self.pods[docker_name]
        #if docker_name in self.waitting_list:
        #    for waitting in self.waitting_list[docker_name]:
        #        waitting.set()
        #   del self.waitting_list[docker_name]
        self.mutex.release()
        return True

    def set_status(self, docker_name, status):
        self.mutex.acquire()
        if docker_name in self.pods:
            self.pods[docker_name].status = status
        self.mutex.release()
        return True

    def timeout(self, docker_name):
        ret = False
        if docker_name in self.pods:
            if self.pods[docker_name].status == status_wait_app_run:
                now = time.time()
                start = self.pods[docker_name].wait_start_time
                timeout = self.pods[docker_name].timeout
                if now - start > timeout:
                    ret = True
        return ret

    def getappid(self, docker_name):
        appid = ''
        contentid = ''

        if docker_name in self.pods:
            appid = self.pods[docker_name].appid
            contentid = self.pods[docker_name].contentid
            return appid, contentid
        
        #waitting = threading.Event()
        #if appid in self.waitting_list:
        #    self.waitting_list[docker_name].append(waitting)
        #else:
        #    self.waitting_list[docker_name] = list()
        #    self.waitting_list[docker_name].append(waitting)

        #waitting.wait(timeout=self.appget_timeout)
        #if waitting.isSet():
        #    appid = self.pods[docker_name].appid
        #    contentid = self.pods[docker_name].contentid

        return appid, contentid

    def verify_token(self, docker_name, token):
        ret = 401
        client_token = ''

        if docker_name in self.pods:
            if token == self.pods[docker_name].server_token:
                ret = 200
                client_token = self.pods[docker_name].client_token
        else:
            logging.error('%s not exist???' % docker_name)
            ret = 404

        return ret, client_token

    def get_token(self, docker_name):
        ret = 401
        client_token = ''
        server_token = ''

        if docker_name in self.pods:
                client_token = self.pods[docker_name].client_token
                server_token = self.pods[docker_name].server_token
                if client_token is None or server_token is None:
                    ret = 404
                else:
                    ret = 200
        else:
            logging.error('%s not exist???' % docker_name)
            ret = 404

        return ret, client_token, server_token


    def list_pods(self):
        return self.pods


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(filename)s:%(lineno)d %(message)s')
