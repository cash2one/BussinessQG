#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import json
import re
import time
import urllib

import requests

import config
from Public_code import Send_Request

# url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-baseinfo-PROVINCENODENUM410000ff8080815b26a218015bb413cbb36469.html'
# result, status_code = Send_Request().send_requests(url)
# print type(json.loads(result)["data"][0])
tel = '010-85109619（投资者联系电话）'

pattern = re.compile(
    u'((\d{11})|^((\d{7,8})|(\d{4}|\d{3})-(\d{7,8})|(\d{4}|\d{3})-(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1})|(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1}))).*')
tel = re.findall(pattern, tel)[0][0]
print tel
