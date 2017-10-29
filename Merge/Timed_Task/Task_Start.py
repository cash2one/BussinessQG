#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Task_Start.py
# @Author: Lmm
# @Date  : 2017-10-11 14:44
# @Desc  : 基于python的windows服务编写

import win32service
import win32serviceutil
import win32event
import winerror
import servicemanager
import os
import sys
import time


class SmallestPythonService(win32serviceutil.ServiceFramework):
    # you can NET START/STOP the service by the following name
    _svc_name_ = "SmallestPythonService"
    # this text shows up as the service name in the Service
    # Control Manager (SCM)
    _svc_display_name_ = "APP Update Python Service"
    # this text shows up as the description in the SCM
    _svc_description_ = "simpile for scheduled tasks"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.isAlive = True

    def SvcDoRun(self):
        while self.isAlive:
            comand = "python E:\MergeCode\APP\Get_Info_new.py"
            self.main_task(comand)
        #win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    def SvcStop(self):
         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
         win32event.SetEvent(self.hWaitStop)
         self.isAlive = False
    def main_task(self,cmd,inc=1):
		os.system(cmd)
		time.sleep(inc)

		

if __name__ == "__main__":
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(SmallestPythonService)
            servicemanager.Initialize('SmallestPythonService', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(SmallestPythonService)

