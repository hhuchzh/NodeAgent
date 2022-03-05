#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2017 Samsung Electronics Co., Ltd. All rights reserved.

    CloudUI project

    Filename: s3cache.py
    Description:
    Contact: Yu Qiang <johnny.yu@samsung.com>
'''

import os
import threading
import logging
import shutil
from apscheduler.schedulers.background import BackgroundScheduler

from s3client import *
from utils import *
from config import config


class s3cache:
    def __init__(self):
        self.cache_path = config.get('s3', 'cache')
        self.bucket = config.get('s3', 'bucket_name')
        self.mutex = threading.Lock()
        self.appdownload_timeout = config.getint('s3', 'appdownload_timeout')
        self.waitting_list = dict()
        self.result_list = dict()
        self.scheduler = BackgroundScheduler()
        self.preload_apps = config.get('s3', 'preload_apps').split(',')
        logging.debug(self.preload_apps)

        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

        self.s3 = s3client(self.bucket)

        self.scheduler.add_job(self.update_apps, 'cron', hour=config.getint('s3', 'app_sync_corn_hour'))
        self.scheduler.start()

        start_thread(self.preload_apps_thread, 'preload_apps_thread')

    def update_apps(self):
        logging.debug('update_apps start')
        try:
            for app in os.listdir(self.cache_path):
                if os.path.isdir(os.path.join(self.cache_path, app)):
                    logging.info('update %s' % app)
                    self.getapp(app, force_sync=True)
        except Exception as e:
            logging.error(e)
        logging.debug('update_apps end')

    def preload_apps_thread(self):
        for app in self.preload_apps:
            self.getapp(app, force_sync=True)

    def get_cached_versions(self, app_path):
        versions = list()
        try:
            for filename in os.listdir(app_path):
                path = os.path.join(app_path, filename)
                if os.path.isdir(path):
                    versions.append(filename)
        except Exception as e:
            logging.error(e)
        return versions

    def clear_needless_files(self, app_cache, remain_version, remain_app_name):
        try:
            for filename in os.listdir(app_cache):
                path = os.path.join(app_cache, filename)
                if os.path.isdir(path):
                    if remain_version != filename:
                        try:
                            shutil.rmtree(path)
                        except:
                            pass
                else:
                    if remain_app_name != filename:
                        try:
                            os.remove(path)
                        except:
                            pass
        except:
            pass
        return




    def update_cache_thread(self, appid, force_sync):
        result = ''

        app_cache = os.path.join(self.cache_path, appid)
        if not os.path.exists(app_cache):
            try:
                os.makedirs(app_cache)
            except Exception as e:
                logging.error(e)

        if os.path.exists(app_cache):

            cached_versions = self.get_cached_versions(app_cache)
            cached_latest_version = get_latest_version(cached_versions)
            logging.debug(cached_versions)

            remote_version = ''
            app_postfix = ''
            if force_sync or not cached_latest_version:
                #remote_version = self.s3.get_version(appid)
                remote_version, app_postfix = self.s3.get_version_format(appid)

            if not remote_version:
                if cached_latest_version:
                    logging.error('use cached version %s' % cached_latest_version)
                    result = os.path.join(app_cache, cached_latest_version)
                else:
                    logging.error('no cached version and get latest version fail')
            else:
                logging.debug('download remote_version %s' % remote_version)
                app_path = os.path.join(app_cache, '%s_%s.%s' % (appid, remote_version, app_postfix))
                if self.s3.download_app(appid, app_path, app_postfix):
                    result = os.path.join(app_cache, remote_version)
                    try:
                        shutil.rmtree(result)
                    except:
                        pass
                    logging.debug('start unzip %s to %s' % (app_path, result))
                    try:
                        unzip(app_path, result)
                        logging.debug('unzip %s success' % app_path)
                        remain_app_name = appid + "_" + remote_version + "." + app_postfix
                        self.clear_needless_files(app_cache, remote_version, remain_app_name)
                    except Exception as e:
                        logging.error(e)
                        if cached_latest_version:
                            logging.error('unzip app fail, use cached version %s' % cached_latest_version)
                            result = os.path.join(app_cache, cached_latest_version)
                        else:
                            logging.error('unzip app fail')
                            try:
                                shutil.rmtree(result)
                            except:
                                pass
                            result = ''
                else:
                    if cached_latest_version:
                        result = os.path.join(app_cache, cached_latest_version)
                        logging.error('download app fail, use cached version %s' % cached_latest_version)
                    else:
                        logging.error('download app fail')
                        result = ''

        self.result_list[appid] = result

        self.mutex.acquire()
        for waitting in self.waitting_list[appid]:
            waitting.set()
        del self.waitting_list[appid]
        self.mutex.release()

    def getapp(self, appid, force_sync=False):
        waitting = threading.Event()
        self.mutex.acquire()
        if appid in self.waitting_list:
            self.waitting_list[appid].append(waitting)
            self.mutex.release()
        else:
            self.waitting_list[appid] = list()
            self.waitting_list[appid].append(waitting)
            self.mutex.release()
            start_thread(self.update_cache_thread, 'update_cache_thread(%s)' % appid, appid, force_sync)

        waitting.wait(timeout=self.appdownload_timeout)
        if waitting.isSet():
            return self.result_list[appid]

        logging.error('getapp wait timeout')
        return ''


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)d %(message)s')
    c = s3cache('/tmp/s3')
    print c.get_cached_versions('/tmp/S3cache/TV Plus')
