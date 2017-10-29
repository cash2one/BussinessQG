#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Test1.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  :
import re
from lxml import etree
from PublicCode import config
import requests
import sys
import chardet
from lxml import etree
import random
from PublicCode.Public_code import Send_Request

# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
string = '<table><tr>\
<td style="height:auto;border-left:1px dashed #ccc;">31</td>\
<td style="height:auto;text-align:left;padding:0 5px;">\
<td style="height:auto;">110115018335783</td>\
<td style="height:auto;text-align:center;padding:0 5px;">刘旺</td>\
<td style="height:auto;text-align:left;padding:0 5px;">北京市大兴区黄村镇兴华南路1号</td>\
<td style="height:auto;text-align:left;padding:0 5px;">大兴分局</td>\
</tr><table>'
result = etree.HTML(string,parser=etree.HTMLParser(encoding='utf-8'))
string = u'分局'
list = result.xpath("//table//tr[contains(.,'%s')]"%string)
print list
# list = ["1","2","3"]
# print list[-1]
# list.remove(list[-1])
# print list
# string = "window.location.href='/wap/creditWapAction!view_bgxx_wap.dhtml?reg_bus_ent_id=E7ED34FAFBA5417894ECC6DF21970FC1&bgxxFlag=bgxxFlag&alt_itemenName=法定代表人&approve_date=2016-06-30'"
# pattern = re.compile(".*href='(.*?)'")
# result = re.findall(pattern,string)
# print result
# string = "http://qyxy.baic.gov.cn/wap/creditWapAction!view_bgxx_wap.dhtml?reg_bus_ent_id=E7ED34FAFBA5417894ECC6DF21970FC1&bgxxFlag=bgxxFlag&alt_itemenName=经营范围&approve_date=2016-06-30"
#
# pattern = re.compile(".*alt_itemenName=(.*?)&.*")
# result = re.findall(pattern,string)
# print result[0]
# string1 = '1213\n'
# string2 = '1213\n'
# print string1
# print string2
# if string1==string2:
# 	print 1

# url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_bgxx_wap.dhtml?reg_bus_ent_id=a1a1a1a029ce96270129cfbd20b43cd8&clear=true'
# result = requests.get(url,headers =config.headers_detail)
# cookies = result.cookies
# cookies = requests.utils.dict_from_cookiejar(cookies)
# print cookies
# content = result.content
# dd = etree.HTML(content,parser = etree.HTMLParser(encoding='utf-8'))
# single = dd.xpath(".//dl/dd/@onclick")[7]
# pattern = re.compile(".*href='(.*?)'")
# href = config.host + re.findall(pattern,single)[0]
# print href
# result = requests.get(href,headers=config.headers_detail,cookies = cookies)
# print result.content
# result = etree.HTML(result.content,parser = etree.HTMLParser(encoding='utf-8'))
# # print etree.tostring(result)
# string = u'变更前'
# before_table = result.xpath(".//table[contains(.,'%s')]"%string)
# string = u'变更时间'
# plist = result.xpath(".//p[contains(.,'%s')]"%string)[0].xpath('string(.)')
# print plist.split("：")[-1]
# headers1 = {
# "Host": "qyxy.baic.gov.cn",
# "Connection": "keep-alive",
# "Content-Length": "151",
# "Cache-Control": "max-age=0",
# #Origin: http://qyxy.baic.gov.cn
# "Upgrade-Insecure-Requests": "1",
# #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
# "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
# "Content-Type": "application/x-www-form-urlencoded",
# "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
# #Referer: http://qyxy.baic.gov.cn/wap/creditWapAction!QueryEnt20130412.dhtml?createTicket=3118CED97BC9668D039770D6FFCF44A6
# "Accept-Encoding": "gzip, deflate",
# "Accept-Language": "zh-CN,zh;q=0.8",
# #"Cookie": "UM_distinctid=15e50b82e8069b-090b21237a717e-e313761-100200-15e50b82e81744; JSESSIONID=zbRwBNxKSPGjUnecm8mDxodr6v9f8msA6DK0GKGregIuM0gh-gUG!436931522; CNZZDATA1257386840=423204356-1505090125-http%253A%252F%252Fqyxy.baic.gov.cn%252F%7C1505117127"
# "Cookie": "JSESSIONID=lqZzjl8FAUhPcWImWicuhJYkFH-Wi1yUE_0rlIoTcKbqw4Ohj5wX!-1493595138;"
# }
#
# # url = 'http://c.cnzz.com/core.php?web_id=1257386840&t=z'
# # result = requests.get(url,headers = headers2)
# # print result.content
# # 翻页测试
# # url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!QueryEnt20130412.dhtml?createTicket=F2CDDF816A02ADF8ABF728AE0FDB4CDD'
# # string = "queryStr=%E4%B8%AA%E4%BD%93%E6%88%B7&module=&idFlag=qyxy&key_word=%E4%B8%AA%E4%BD%93%E6%88%B7&EntryPageNo=2&pageNo=1&pageSize=50&clear="
# # result = requests.post(url,string,headers = headers1,timeout = 5)
# # print result.content
# #
# # print chardet.detect(result.content)["encoding"]
# # result = etree.HTML(result.content)
# # print len(result.xpath("//li"))
# # headers = config.headers
# # headers["User-Agent"] = random.choice(config.USER_AGENTS)
# #
# # url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!QueryEnt20130412.dhtml?createTicket=E90BD4BCFAB2AFDE17922534D0AA3F57'
# # params = 'queryStr=%E4%B8%AA%E4%BD%93%E6%88%B7&module=&idFlag=qyxy'
# # result = requests.post(url,params,headers=headers)
# # s =  chardet.detect(result.content)["encoding"]
# # print s
# url = u'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=030103&ent_id=20e38b8c44baf1250144d7c08cca2947&chr_id=1AFB38484EF500E0E053A06400C300E0&info_categ_name=\u63d0\u793a\u4fe1\u606f >> \u62bd\u67e5\u4fe1\u606f'
# if u"抽查信息" in url:
# 	print 1
# else:
# 	print 0
import datetime
import time

# date1 = '2015-06-23'
# date2 = '2015-06-23'
#
# date1 = time.strptime(date1, "%Y-%m-%d")
# date2 = time.strptime(date2, "%Y-%m-%d")
# date1 = datetime.datetime(date1[0], date1[1], date1[2])
# date2 = datetime.datetime(date2[0], date2[1], date2[2])
# print (date2-date1).days
# url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=030103&ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&chr_id=1AFB38483F0E00E0E053A06400C300E0,&info_categ_name=提示信息 >> 抽查信息'
# if u'抽查' in url:
# 	print 1
# else:
# 	print 2
# url = 'http://qyxy.baic.gov.cn/wapnb/wapnbAction!wapgdcz_bj.dhtml'
# string = 'entid=15360F6123414BDAB5F04E1C5A29CD1F&cid=3855408ad9554d248e5f4084587fbc45&pageNo=1&pageSize=100&clear='
# headers = config.headers_detail
# UA = random.choice(config.USER_AGENTS)
# headers["User-Agent"] = UA
# result= requests.get(url, string,headers=headers,timeout=5)
# print result.content
# list = [1,2,3]
# for i,single in enumerate(list,0):
# 	print i,single
# for i in xrange(2,11+1):
# 	print i
# with open("user-agent.txt",'a') as f:
#
# 	for j in xrange(200):
# 		list = []
# 		for i in range(0, 20):
# 			temp = random.randint(0, 9)
# 			list.append(temp)
#
# 		s ='Mozilla/5.0 (MeeGo; NokiaN9) AppleWebKit/%s%s%s.%s%s (KHTML, like Gecko) Chrome/%s%s.%s.%s%s%s%s.%s%s%s Mobile Safari/%s%s%s.%s%s'%(list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8], list[9], list[10], list[11],list[12], list[13], list[14], list[15], list[16], list[17], list[18], list[19])
# 		f.write(s+'\n')
# print s
# file = open("user-agent.txt")
# UA = file.readline()
# print UA
# import linecache
# a = random.randrange(1, 1001) #1-9中生成随机数
# #从文件poem.txt中对读取第a行的数据
# theline = linecache.getline(r'user-agent.txt', a)
# print theline
print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
start = time.time()
url = 'http://qyxy.baic.gov.cn/wap'
result = requests.get(url, headers=config.headers_index)
print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)

result = etree.HTML(result.content, parser=etree.HTMLParser(encoding='utf-8'))
id = result.xpath('//span[@class = "shouButton"]/@onclick')[0]
pattern = re.compile(".*QueryIndex\('','(.*?)'\).*")
match = re.findall(pattern, id)[0]
print id, match
print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
