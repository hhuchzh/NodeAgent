#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2018 Samsung Electronics Co., Ltd. All rights reserved.

    CloudUI project

    Filename: podStatus.py
    Description:
    Contact: Yu Qiang <johnny.yu@samsung.com>
'''

# !!! this file need sync with django/NodeAgent !!!

'''
docker status:
    pending -> running -> app_running -> terminated
'''

status_invaild = 'invaild'  #
status_pending = 'pending'  # docker initialize
status_running = 'running'  # docker initialize finish
status_wait_app_run = 'wait_app_run'  # docker assign for app
status_app_running = 'app_running'  # app running in docker
status_terminated = 'terminated'  # docker stop
