#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Public_code.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 创建了几个公共类用于连接数据库，发送请求等


import json
import logging
import random
import time
import config
import MySQLdb
import requests
import re

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








