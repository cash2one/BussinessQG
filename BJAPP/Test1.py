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
# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# string = '<table><tr>\
# <td style="height:auto;border-left:1px dashed #ccc;">31</td>\
# <td style="height:auto;text-align:left;padding:0 5px;">\
# <td style="height:auto;">110115018335783</td>\
# <td style="height:auto;text-align:center;padding:0 5px;">刘旺</td>\
# <td style="height:auto;text-align:left;padding:0 5px;">北京市大兴区黄村镇兴华南路1号</td>\
# <td style="height:auto;text-align:left;padding:0 5px;">大兴分局</td>\
# </tr><table>'
# result = etree.HTML(string,parser=etree.HTMLParser(encoding='utf-8'))
# string = u'分局'
# list = result.xpath("//table//tr[contains(.,'%s')]"%string)
# print list
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

url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_bgxx_wap.dhtml?reg_bus_ent_id=a1a1a1a029ce96270129cfbd20b43cd8&clear=true'
result = requests.get(url,headers =config.headers_detail)
cookies = result.cookies
cookies = requests.utils.dict_from_cookiejar(cookies)
print cookies
content = result.content
dd = etree.HTML(content,parser = etree.HTMLParser(encoding='utf-8'))
single = dd.xpath(".//dl/dd/@onclick")[7]
pattern = re.compile(".*href='(.*?)'")
href = config.host + re.findall(pattern,single)[0]
print href
result = requests.get(href,headers=config.headers_detail,cookies = cookies)
print result.content
result = etree.HTML(result.content,parser = etree.HTMLParser(encoding='utf-8'))
# print etree.tostring(result)
string = u'变更前'
before_table = result.xpath(".//table[contains(.,'%s')]"%string)
string = u'变更时间'
plist = result.xpath(".//p[contains(.,'%s')]"%string)[0].xpath('string(.)')
print plist.split("：")[-1]

