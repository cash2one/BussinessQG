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

string = '"60436520",'
if "60436520" in string:
    print "1"
current_timestamp
