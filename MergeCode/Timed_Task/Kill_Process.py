#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Kill_Process.py
# @Author: Lmm
# @Date  : 2017-10-13 9:31
# @Desc  : 结束python 程序

import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
path = sys.path[0]
try:
	with open(path+"/kill.txt","a+") as f:
		f.writelines("the kill process is started!")
	command = 'taskkill /f /im python.exe /t'
	status = os.system(command)
except Exception,e:
	print e

