#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : test2.py.py
# @Author: Lmm
# @Date  : 2017-10-17 17:50
# @Desc  :
import requests
url = 'http://gsxt.gzaic.gov.cn/aiccips/print/printView.html?entNo=440101101012009092100063&regOrg=440100'

result = requests.get(url)
print result.content