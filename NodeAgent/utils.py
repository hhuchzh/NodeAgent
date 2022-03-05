#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2017 Samsung Electronics Co., Ltd. All rights reserved.

    CloudUI project

    Filename: utils.py
    Description:
    Contact: Yu Qiang <johnny.yu@samsung.com>
'''
import logging
import os
import re
import shutil
import zipfile
import socket
import threading
from datetime import datetime
from dateutil.tz import tzlocal


def backup(path):
    backup_path = '%s.bk' % path
    if not os.path.exists(path):
        return
    if os.path.exists(backup_path):
        if os.path.isdir(backup_path):
            shutil.rmtree(backup_path)
        else:
            os.remove(backup_path)
    shutil.move(path, backup_path)


def restore(path):
    backup_path = '%s.bk' % path
    if not os.path.exists(backup_path):
        return
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    shutil.move(backup_path, path)


def unzip(zip_file, target_path):
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    f = zipfile.ZipFile(zip_file, 'r')
    for filename in f.namelist():
        f.extract(filename, target_path)
    f.close()


def get_latest_version(versions):
    latest_version = ''
    if versions:
        latest_version = versions[0]
        if len(versions) != 1:
            for version in versions:
                if version_compare(version, latest_version):
                    latest_version = version

    return latest_version


def version_compare(v1="1.1.1", v2="1.2"):
    # if v1 > v2 return True
    #v1_list = v1.split(".")
    #v2_list = v2.split(".")
    v1_list = re.split(r'[.-]', v1)
    v2_list = re.split(r'[.-]', v2)
    #for name in v1_list:
    #    logging.info("------%s------", name)
    v1_len = len(v1_list)
    v2_len = len(v2_list)
    if v1_len > v2_len:
        v2_list = v2_list + ['0'] * (v1_len - v2_len)

    if v2_len > v1_len:
        v1_list = v1_list + ['0'] * (v2_len - v1_len)

    for i in range(len(v1_list)):
        try:
            if int(v1_list[i]) > int(v2_list[i]):
                return True
            if int(v1_list[i]) < int(v2_list[i]):
                return False
        except:
            return True
    return False


def start_thread(fn, name, *args):
    t = threading.Thread(target=fn, name=name, args=args)
    t.setDaemon(True)
    t.start()

    
def gethostname():
    return socket.gethostname()

    
def local2UTC(local_time):
    offset = local_time.utcoffset()
    tmp_time = local_time
    if offset:
        tmp_time = local_time - offset

    return datetime(year=tmp_time.year, month=tmp_time.month, day=tmp_time.day,
                             hour=tmp_time.hour, minute=tmp_time.minute, second=tmp_time.second)


if __name__ == '__main__':
    now = datetime.utcnow()
    print now
    print local2UTC(now)
    #####################
    now = datetime.now(tzlocal())
    print now
    print local2UTC(now)
