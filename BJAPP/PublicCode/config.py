#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: Lmm
# @Date  : 2017-09-05
# @Desc  :

host = 'http://qyxy.baic.gov.cn'

list_url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!QueryEnt20130412.dhtml?createTicket=04E80E842B6D160D5A5A39DBC70E4FD5'
list_parmas = 'queryStr={0}&module=&idFlag=qyxy'

#列表请求头仿照
headers = {
"Host": "qyxy.baic.gov.cn",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate",
"Content-Type": "application/x-www-form-urlencoded",
"Content-Length": "74",
"Referer": "http://qyxy.baic.gov.cn/wap",
#"Cookie": "JSESSIONID=SAZQ1su5vXRgd0bfxGBoYJbo6AB13Y60ijX4jHp9Z3XN_mxtgeQ9!-287689337; UM_distinctid=15e50d7aa4b9-0174aa7f9f9695-12656e4a-100200-15e50d7aa4c15; CNZZDATA1257386840=155776785-1504589909-http%253A%252F%252Fqyxy.baic.gov.cn%252F%7C1504596309",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1"
}
#详情请求头
headers_detail = {
"Host": "qyxy.baic.gov.cn",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1"
}
