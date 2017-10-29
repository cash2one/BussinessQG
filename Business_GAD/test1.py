#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : test1.py
# @Author: Lmm
# @Date  : 2017-10-17 14:23
# @Desc  :
import logging

'''
日志级别：
critical > error > warning > info > debug,notset
级别越高打印的日志越少，反之亦然，即
debug    : 打印全部的日志(notset等同于debug)
info     : 打印info,warning,error,critical级别的日志
warning  : 打印warning,error,critical级别的日志
error    : 打印error,critical级别的日志
critical : 打印critical级别
'''

import logging
import sys


def test_log_level():
	# set default logging configuration
	logger = logging.getLogger()  # initialize logging class
	logger.setLevel(logging.INFO)  # default log level
	format = logging.Formatter("%(asctime)s - %(message)s")  # output format
	sh = logging.StreamHandler(stream=sys.stdout)  # output to standard output
	sh.setFormatter(format)
	logger.addHandler(sh)
	
	# use logging to generate log ouput
	logger.info("this is info")
	logger.debug("this is debug")
	logger.warning("this is warning")
	logging.error("this is error")
	logger.critical("this is critical")


test_log_level()