#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2017 Samsung Electronics Co., Ltd. All rights reserved.

    CloudUI project

    Filename: main.py
    Description:
    Contact: Yu Qiang <johnny.yu@samsung.com>
'''

import os
import ConfigParser


config = ConfigParser.ConfigParser()
config_path = os.path.join(os.getcwd(), 'config', 'base.ini')
config.read(config_path)