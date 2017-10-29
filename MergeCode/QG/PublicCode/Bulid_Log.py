#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Bulid_Log.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于创建日志文件

import logging
import time
class Log:
    def __init__(self,gs_basic_id):
        self.gs_basic_id = gs_basic_id
    # 自动创建文件夹检查是否存在文件夹返回当前路径，不存在则创建文件
    def mkdir_floder(self):
        import os
        import sys
        # 这个获取其实是python 解释器的路径
        # current_path = os.getcwd()
        # 用于获取当前被执行文件的路径
        current_path = sys.path[0]
        # 判断路径是否存在，存在True,不存在False
        isExists = os.path.exists(current_path + '/log')
        if not isExists:
            os.mkdir('log')
        
        return current_path
    def found_log(self):
        log_path = self.mkdir_floder()
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + '/log/py_QG_update_%s_%s.log' % (
                            time.strftime("%Y-%m-%d", time.localtime()),self.gs_basic_id),
                            filemode='a')
