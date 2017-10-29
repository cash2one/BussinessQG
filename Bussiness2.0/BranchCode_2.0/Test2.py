#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : GetUrl.py
# @Author: Lmm
# @Date  : 2017-07-30
# @Desc  : 获取链接

import json
import logging
import re
import sys
import time
import urllib
import requests
from bs4 import BeautifulSoup

from PublicCode import config
from PublicCode.Bulid_Log import Log
from PublicCode.Public_code import Connect_to_DB
from PublicCode.deal_html_code import remove_symbol


# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# string = '上海集团1212'
# pattern = re.compile('.*公司.*|.*中心.*|.*集团.*|.*企业.*')
# result= re.findall(pattern,string)
# print result[0]

# string = '"60436520",'
# if "60436520" in string:
#     print "1"
# current_timestamp
# import time
# now = time.time()
# n = 1
# before = now - n * 24 * 3600  #可以改变n 的值计算n天前的
#
# date = time.strftime("%Y-%m-%d %H:%M:%S ",  time.localtime(now))
# print date
# beforeDate = time.strftime("%Y-%m-%d %H:%M:%S ",  time.localtime(before))
# print beforeDate

# import random
# from PublicCode import config
# print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# start = time.time()
#
# url = 'http://s.zdaye.com/?api=201709221507363322&px=2'
#
# result = requests.get(url)
# print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
#
# string = result.content
# list = string.split("\n")
# print list
# a = random.randint(0,4)
# ip = list[a]
# ip = ip.replace("\r","")
# print ip
# #url = 'http://www.baidu.com'
# url = 'http://www.gsxt.gov.cn/index.html'
# proxies = {
# 	"http":"http://%s"%ip,
#
# }
# print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# start = time.time()
# html = requests.get(url,proxies=proxies, headers=config.headersfirst)
# print html.status_code
# print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
#
# html = requests.get(url,headers = config.headersfirst)
# print html.status_code
#
# print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
url = 'http://cq.gsxt.gov.cn/caic/pub/api/s?t=1507884086031'
def tre(numb,num=None):
	print numb,num
numb = 1
num = 1
tre(numb)

