#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: Lmm
# @Date  : 2017-09-05
# @Desc  :


#数据库配置-----------------------------------------
HOST, USER, PASSWD, DB, PORT = '127.0.0.1', 'root', '123456', 'test', 3306
#数据库配置-----------------------------------------

#日志保存路径Start-------------------------------------------------------------------------------
#log_path = './Public/Python'
log_path = '.'
#日志保存路径End---------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
host = 'http://qyxy.baic.gov.cn'
index_url = 'http://qyxy.baic.gov.cn/wap'
list_url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!QueryEnt20130412.dhtml?createTicket={0}'
list_parmas = 'queryStr={0}&module=&idFlag=qyxy'
branch_url = 'http://qyxy.baic.gov.cn/xycx/queryCreditAction!getEnt_Fzjgxx.dhtml?reg_bus_ent_id={0}&moreInfo=moreInfo&SelectPageSize=50&EntryPageNo=1&pageNo=1&pageSize=500&clear=true'
person_url ='http://qyxy.baic.gov.cn/xycx/queryCreditAction!queryTzrxx_all.dhtml?reg_bus_ent_id={0}&moreInfo=&SelectPageSize=100&EntryPageNo=1&pageNo=1&pageSize=100&clear=true'

#列表请求头仿照
headers = {
"Host": "qyxy.baic.gov.cn",
# "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate",
"Content-Type": "application/x-www-form-urlencoded",
"Content-Length": "74",
"Referer": "http://qyxy.baic.gov.cn/wap",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1",

}
#详情请求头
headers_detail = {
"Host": "qyxy.baic.gov.cn",
# "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1"
}
#首页请求头
headers_index = {
"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
"Connection": "keep-alive",
"Cache-Control": "max-age=0",
"Upgrade-Insecure-Requests": "1",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.8"
}

