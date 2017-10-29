#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Start_Task.py
# @Author: Lmm
# @Date  : 2017-10-11
# @Desc  :无限循环指定程序令每隔一分钟执行一次

import time,os
import sys
def re_exe(cmd ,inc =6):
	path = sys.path[0]
	while True:
		with open(path +"/process.txt","a+") as f:
			f.write("now the time is %s,I am alive \n"%time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		os.system(cmd)
		time.sleep(inc)
if __name__ == '__main__':
	command = "python E:\MergeCode\APP\Get_Info_new.py"
	re_exe(command)

