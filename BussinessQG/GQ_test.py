#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author liangmengmeng

from PublicCode.Public_code import Send_Request
url = 'http://www.gsxt.gov.cn'
result = Send_Request().send_requests(url)
print result