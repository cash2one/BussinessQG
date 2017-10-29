#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Task_test1.py
# @Author: Lmm
# @Date  : 2017-10-12 11:46
# @Desc  :

# -*- coding: utf-8 -*-
# SmallestService.py
#
# A sample demonstrating the smallest possible service written in Python.

import win32serviceutil
import win32service
import win32event

import time
import logging
import os
logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(levelname)s %(message)s',
					filename='log234.log',
					filemode='a+')



class SmallestPythonService(win32serviceutil.ServiceFramework):
	_svc_name_ = "Sologin Monitor Service"
	_svc_display_name_ = "Sologin Monitor Service"
	
	def __init__(self, args):
		
		win32serviceutil.ServiceFramework.__init__(self, args)
		# Create an event which we will use to wait on.
		# The "service stop" request will set this event.
		self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
		self.isAlive = True
	
	def SvcStop(self):
		# Before we do anything, tell the SCM we are starting the stop process.
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		# And set my event.
		
		win32event.SetEvent(self.hWaitStop)
	
	def SvcDoRun(self):
		# 把你的程序代码放到这里就OK了
		while self.isAlive:
			logging.error("I am alive.")
			comand = "python E:\MergeCode\APP\Get_Info_new.py"
			try:
				logging.info("start_task")
				os.system(comand)
			except Exception,e:
				logging.info(e)
			logging.info("end task")
			time.sleep(1)
		
		#win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)


if __name__ == '__main__':
	win32serviceutil.HandleCommandLine(SmallestPythonService)
	# 括号里的名字可以改成其他的，必须与class名字一致；