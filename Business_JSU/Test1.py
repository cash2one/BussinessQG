#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Test1.py
# @Author: Lmm
# @Date  : 2017-09-28
# @Desc  :
import re
import decimal
# finger = '11万'
# pattern = re.compile(u"[-+]?[0-9]*\.?[0-9]+")
# finger = re.findall(pattern, finger)
# print finger
# finger = decimal.Decimal(finger[0])
# print finger
string = '123||1213||112'
print string.split("||")
