#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: Lmm
# @Date  : 2017-10-17 11:18
# @Desc  : 用于一些常用配置
import random

#链接Start--------------------------------------------------------------------------------------------------------------
index_url = 'http://gsxt.gdgs.gov.cn/aiccips//verify/start.html?t=1508217286926'
tansform_key = 'http://gsxt.gdgs.gov.cn/aiccips/verify/sec.html?textfield={0}&\
geetest_challenge=d2ddea18f00665ce8623e36bd4e3c7c5b6&geetest_validate=575117555ff_115751153c_551715755156b\
&geetest_seccode=575117555ff_115751153c_551715755156b|7Cjordan'
list_url = 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showCheck.html?textfield={0}&type=nomal&type=nomal&total=50&pageNo={1}'
#链接End----------------------------------------------------------------------------------------------------------------



#头部信息仿照Start------------------------------------------------------------------------------------------------------
list = []

for i in range(0, 20):
    temp = random.randint(0, 9)
    list.append(temp)
user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/%s%s%s.%s%s (KHTML, like Gecko)Chrome/%s%s.%s.%s%s%s%s.%s%s%s Safari/%s%s%s.%s%s '\
		% (list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8], list[9], list[10], list[11],
    list[12], list[13], list[14], list[15], list[16], list[17], list[18], list[19])

headers = {
"Host": "gsxt.gdgs.gov.cn",
"Connection": "keep-alive",
"Cache-Control": "max-age=0",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
"Upgrade-Insecure-Requests": "1",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.8"
}
#头部信息仿照End--------------------------------------------------------------------------------------------------------
