#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: Lmm
# @Date  : 2017-09-05
# @Desc  :


#数据库配置-----------------------------------------
HOST, USER, PASSWD, DB, PORT = '127.0.0.1', 'root', '123456', 'test', 3306
#数据库配置-----------------------------------------

#--------------------------------------------------------------------------------------------
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
# 代理服务器-----------------------------------------------------------------------
proxyHost = "proxy.abuyun.com"
proxyPort = "9010"
#----------------------------------------------------------------------------------


# 代理隧道验证信息-----------------------------------------------------------------
proxyUser = "HQRMZT62299COJ2P"
proxyPass = "1B668ADB969075FD"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
      "host": proxyHost,
      "port": proxyPort,
      "user": proxyUser,
      "pass": proxyPass,
    }

proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
}
#-------------------------------------------------------------------------------------------
#常用的User-Agent-------------------------------------------------------------------------------------------

#常用的User-Agent-------------------------------------------------------------------------------------------