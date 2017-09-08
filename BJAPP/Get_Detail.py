#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Get_Detail.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 用于获取详情信息
from PublicCode import config
import requests

url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!qy.dhtml?id=0CD1263D6BB2009EE053A0630264009E&scztdj=&credit_ticket=C21C513ACC64B7D142F14F3088F1C180'
result = requests.get(url,headers = config.headers_detail)


print result.content
def get_urllist(url):
	hreflist = {}
	result = requests.get(url,config.headers_detail)
	status_code = result.status_code
	if status_code ==200:
		content = result.content
		list = content.xpath(".//")
	

