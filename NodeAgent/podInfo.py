#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2018 Samsung Electronics Co., Ltd. All rights reserved.

    CloudUI project

    Filename: main.py
    Description:
    Contact: Yu Qiang <johnny.yu@samsung.com>
'''
import time
import logging

from podStatus import *


class podInfo:
    def __init__(self, name, timeout,  vdi_port, rpc_port, appid, contentid, server_token, client_token, status=status_running):
        self.name = name
        self.status = status
        self.timeout = timeout
        self.vdi_port = vdi_port
        self.rpc_port = rpc_port
        self.appid = appid
        self.contentid = contentid
        self.server_token = server_token
        self.client_token = client_token
        if status == status_wait_app_run:
            self.wait_start_time = time.time()
        else:
            self.wait_start_time = None

    def __str__(self):
        return '{"name": "%s", "status": "%s", "wait_start_time": "%s", "timeout": "%d",  "vdi_port": "%d", "rpc_port": "%d"' \
               '"appid": "%s",  "contentid": "%s", "server_token": "%s",  "server_token": "%s"}' % \
               (self.name, self.status, self.wait_start_time, self.timeout, self.vdi_port, self.rpc_port, self.appid, self.contentid, self.server_token, self.client_token)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s')

    di = podInfo('a', 10, 3001, 3002, '121113321', 'asdavas', 'asd', 'jkl', status_wait_app_run)

    print di.__str__
    print di.__dict__