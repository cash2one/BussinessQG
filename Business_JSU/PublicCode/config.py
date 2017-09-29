#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: Lmm
# @Date  : 2017-09-20
# @Desc  : 用于一些常用的配置，便于灵活改动
import random
import os
#------------------------------------------------------------
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
#------------------------------------------------------------

#数据库用户名配置Start-----------------------------------------------------------
HOST, USER, PASSWD, DB, PORT = '127.0.0.1', 'root', '123456', 'test', 3306
#数据库用户名配置end-------------------------------------------------------------


#定义省份Start-------------------------------------------------------------------
province = 'JSU'
#定义省份End---------------------------------------------------------------------



#日志文件路径start---------------------------------------------------------------
#log_path = './Public/Python'
log_path = '.'
#日志文件路径end------------------------------------------------------------------
#各部分请求链接Start--------------------------------------------------------------
host = 'http://112.25.222.4:58888'
index_url = 'http://112.25.222.4:58888/province/'
first_url = 'http://112.25.222.4:58888/province/infoQueryServlet.json?checkCode=true&verifyCode=&name={0}'
second_url = 'http://112.25.222.4:58888/province/infoQueryServlet.json?queryCinfo=true&name={0}&searchType=qyxx&pageNo=1&pageSize=10'
basic_url = 'http://112.25.222.4:58888/ecipplatform/publicInfoQueryServlet.json?pageView=true&org={0}&id={1}&seqId={2}&abnormal=&activeTabId=&tmp={3}'
main_branch_url = 'http://112.25.222.4:58888/ecipplatform/publicInfoQueryServlet.json?'

#不需要翻页的参数
branch_params = '{0}&org={1}&id={2}&seqId={3}&regNo={4}'
#需要翻页的参数
params = '{0}&org={1}&id={2}&seqId={3}&regNo={4}&pageSize=5&curPage={5}'
#年报各部分信息所带参数
report_params1 = '{0}&id={1}'
report_params2 = '{0}&reportId={1}&org={2}&id={3}&seqId={4}&regNo={5}&pageSize=5&curPage={6}'
report_params3 = '{0}&id={1}&pageSize=5&curPage={2}'
#各部分关键参数-----------------------------------------------------------------------、
key_params = {
	"branch": "queryFzjg=true",
	"brand": "querySbzc=true",
	"change": "queryBgxx=true",
	"check": "queryCcjc=true",
    "clear": "queryQsxx=true",
	"except": "queryJyyc=true",
	"freeze": "querySfxz=true",
	"mort": "queryDcdy=true",
	"mort_person": "queryDcdyDyqrgk=true",
	"mort_goods": "",
	"permit": "queryXzxk=true",
	"permit2": "queryQyjsxxXzxk=true",
	"person": "queryZyry=true",
	"punish": "queryXzcf=true",
	"punish2": "queryQyjsxxXzcf=true",
	"report": "queryQynbxxYears=true",
	"shareholder": "queryGdcz=true",
	"stock": "queryGqcz=true",
	"report_basic": "queryQynbxxJbxx=true",
	"report_assure": "queryQynbxxDwdb=true",
	"report_invest": "queryQynbxxDwtz=true",
	"report_permit": "queryQynbxxXzxk=true",
	"report_schange": "queryQynbxxGqbg=true",
	"report_share": "queryQynbxxGdcz=true",
	"report_web": "queryQynbxxWzwd=true",
	"report_lab": "queryQyshebaoxx=true"
}
#各部分关键参数-----------------------------------------------------------------------

#各部分请求链接End----------------------------------------------------------------


#请求头模拟-----------------------------------------------------------------------

list = []

for i in range(0, 20):
    temp = random.randint(0, 9)
    list.append(temp)
user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/%s%s%s.%s%s (KHTML, like Gecko) Chrome/%s%s.%s.%s%s%s%s.%s%s%s Safari/%s%s%s.%s%s\
        ' % (
    list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8], list[9], list[10], list[11],
    list[12], list[13], list[14], list[15], list[16], list[17], list[18], list[19])

headers = {
"Host": "www.jsgsj.gov.cn:58888",
"User-Agent": user_agent,
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate",
"Connection": "keep-alive"
}


#请求头模拟-----------------------------------------------------------------