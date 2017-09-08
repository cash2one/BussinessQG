#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_clear.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取清算信息,并将清算信息插入到数据库中
from lxml import etree
from PublicCode import config
from PublicCode import  deal_html_code
from PublicCode.Public_code import Connect_to_DB
import requests
import re
import time

url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_clearInfo_wap.dhtml?reg_bus_ent_id=20e38b8b50c7d44f0150d043b6620ce2&clear=true'
class Clear:
	def name(self,url):
		info = {}
		result = requests.get(url,headers = config.headers_detail)
		status_code = result.status_code
		if status_code ==200:
			content = result.content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding="utf-8"))
			dl = result.xpath("//div[@class= 'viewBox']/dl")[0]
			string = u"清算组负责人"
			data = self.deal_dd_content(string,dl)
			if data!='':
				legal_list = data.split(u"、")
				for i,single in enumerate(legal_list):
					info[single] = string
			string= u"清算组成员"
			data = self.deal_dd_content(string,dl)
			if data!='':
				member_list = data.split(u"、")
				for i,single in enumerate(member_list):
					info[single]= string
		print info
    # 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath("./dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
		
	
object = Clear()
object.name(url)