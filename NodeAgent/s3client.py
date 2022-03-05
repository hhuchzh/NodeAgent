#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2017 Samsung Electronics Co., Ltd. All rights reserved.

    CloudUI project

    Filename: s3client.py
    Description:
        refer http://boto3.readthedocs.io/en/latest/reference/services/s3.html
    Contact: Yu Qiang <johnny.yu@samsung.com>
'''

import time
import sys
import json
import os
import logging

import boto3
import botocore

from utils import *


class s3client:
    def __init__(self, bucket):
        self.client = boto3.client('s3')
        self.resource = boto3.resource('s3')
        self.bucket = self.resource.Bucket(bucket)

    def download_app(self, appid, target, format="wgt"):
        try:
            #key = '%s/%s.wgt' % (appid, appid)
            key = '%s/%s.%s' % (appid, appid, format)
            logging.info('start download %s -> %s' % (key, target))
            self.bucket.download_file(key, target)
        except Exception as e:
            logging.error(e)
            return False
        return True

    def download_meta(self, appid, target):
        try:
            key = '%s/%s.meta' % (appid, appid)
            logging.info('start download %s -> %s' % (key, target))
            self.bucket.download_file(key, target)
        except Exception as e:
            logging.error(e)
            return False
        return True

    def get_version_format(self, appid):
        version = ''
        if appid=='bixbycapsuleviewer':
            app_postfix = 'zip'
        else:
            app_postfix= 'wgt'
        meta_path = '/tmp/%s.%f.meta' % (appid, time.time())
        if self.download_meta(appid, meta_path):
            with open(meta_path, 'rb') as f:
                try:
                    jd = json.loads(f.read())
                    version = jd['version']
                    if "format" in jd:
                        app_postfix=jd['format']
                except Exception as e:
                    logging.error(e)
            try:
                os.remove(meta_path)
            except:
                pass

        return version, app_postfix


    def get_version(self, appid):
        version = ''
        meta_path = '/tmp/%s.%f.meta' % (appid, time.time())
        if self.download_meta(appid, meta_path):
            with open(meta_path, 'rb') as f:
                try:
                    jd = json.loads(f.read())
                    version = jd['version']
                except Exception as e:
                    logging.error(e)
            try:
                os.remove(meta_path)
            except:
                pass
        return version


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)d %(message)s')
    #s3 = s3client('yuqiangs3')
    s3 = s3client('srcn-dev-app')
    s3.download_meta('bixbycapsuleviewer','/tmp/bixbycapsuleviewer.meta')
    s3.download_app('bixbycapsuleviewer','/tmp/bixbycapsuleviewer.zip','zip')
    print s3.get_version_format('bixbycapsuleviewer')
    #s3.download_meta('3201711015081','/tmp/3201711015081.meta')
    #s3.download_app('3201711015081','/tmp/3201711015081.wgt')
    #print s3.get_version('3201711015081')
