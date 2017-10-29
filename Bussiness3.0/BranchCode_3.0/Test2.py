#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : GetUrl.py
# @Author: Lmm
# @Date  : 2017-07-30
# @Desc  : 获取链接


import sys
import logging
import MySQLdb


# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# 用于连接数据库
class Connect_to_DB:
    def ConnectDB(self, HOST, USER, PASSWD, DB, PORT):
        "Connect MySQLdb and Print version."
        connect, cursor = None, None
        i = 10
        while i>0:
            try:
                connect = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, port=PORT, charset='utf8')
                cursor = connect.cursor()
                logging.info("connect is success!")
                break
            except Exception, e:
                i = i-1
                logging.error(e)
        return connect, cursor


