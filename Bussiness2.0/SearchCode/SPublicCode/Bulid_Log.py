#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Bulid_Log.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于创建日志文件

import config
import logging
import time
class Log:
    def found_log(self,gs_py_id, gs_basic_id):
        log_path = config.log_path
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + '/log/py_update_%s_%s_%s.log' % (
                            time.strftime("%Y-%m-%d", time.localtime()), gs_basic_id, gs_py_id),
                            filemode='a')
    def found_search_log(self,gs_search_id,gs_basic_id):
        log_path = config.log_path
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + '/log/py_search_%s_%s_%s.log' % (
                                time.strftime("%Y-%m-%d", time.localtime()), gs_basic_id, gs_search_id),
                            filemode='a')

