#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Public_code.py
# @Author: Lmm
# @Date  : 2017-09-01
# @Desc  : 用于公共函数的编写
import config
import MySQLdb
import logging
import time

# 用于连接数据库
class Connect_to_DB:
    def ConnectDB(self, HOST, USER, PASSWD, DB, PORT):
        "Connect MySQLdb and Print version."
        connect, cursor = None, None
        i = 10
        while i > 0:
            try:
                connect = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, port=PORT, charset='utf8')
                cursor = connect.cursor()
                logging.info("connect is success!")
                break
            except Exception, e:
                i = i - 1
                logging.error(e)
        return connect, cursor
class Log:
    def found_log(self,gs_py_id, gs_basic_id):
        log_path = config.log_path
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + '/log/py_update_%s_%s_%s.log' % (
                            time.strftime("%Y-%m-%d", time.localtime()), gs_basic_id, gs_py_id),
                            filemode='a')
    def found_patent_log(self):
        log_path = config.log_path
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + '/log/py_update_%s_%s_%s.log' % (
                                time.strftime("%Y-%m-%d", time.localtime()), gs_basic_id, gs_py_id),
                            filemode='a')
        
