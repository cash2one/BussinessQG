#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : test1.py
# @Author: Lmm
# @Date  : 2017-10-18 15:45
# @Desc  :
# import re
# string = "openView('8610502000005305','50','','')"
#
# pattern = re.compile("'(.*?)'+")
#
# list = re.findall(pattern,string)
# print list
# print list[0]
# print list[1]
# print type(list)
list = {"name": 1}
data = {}
data[0] = list
print type(data)
print data[0]
import hashlib
# gs_basic_id = 1
# gs_report_id = 1
# key = u'123'
# m = hashlib.md5()
# m.update(str(gs_basic_id)+str(gs_report_id)+str(key))
# uuid = m.hexdigest()
# print uuid
# m = hashlib.md5()
# m.update(str(gs_basic_id)+str(gs_report_id)+key)
# uuid = m.hexdigest()
# print uuid
import traceback

try:
	1 / 0
except Exception, e:
	# print 'str(Exception):\t', str(Exception)
	# print 'str(e):\t\t', str(e)
	# print 'repr(e):\t', repr(e)
	# print 'e.message:\t', e.message
	# print 'traceback.print_exc():';traceback.print_exc()
	print 'traceback.format_exc():\n%s' % traceback.format_exc()
# from PublicCode import config
# import requests
# url = 'http://sn.gsxt.gov.cn/ztxy.do?method=frInfoDetail&maent.xh=610000000000893121&maent.pripid=6100000000008931&isck=Y&random=1508406673399'
# result = requests.get(url,headers = config.headers)
# print result.text
