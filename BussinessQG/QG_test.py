#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
import json
import logging
import re
import requests
import time


import requests

# 要访问的目标页面
targetUrl = "http://www.gsxt.gov.cn/index.html"


#阿布云配置信息Start---------------------------------------------------------------

# 代理服务器-----------------------------------------------------------------------
proxyHost = "proxy.abuyun.com"
proxyPort = "9020"
#----------------------------------------------------------------------------------


# 代理隧道验证信息-----------------------------------------------------------------
proxyUser = "H34EUV31HZZO616D"
proxyPass = "9385E1506CFFD951"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
      "host" : proxyHost,
      "port" : proxyPort,
      "user" : proxyUser,
      "pass" : proxyPass,
    }

proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
}
#阿布云配置信息end------------------------------------------------------------------

resp = requests.get(targetUrl, proxies=proxies,timeout= 5)

print resp.status_code
print resp.text


