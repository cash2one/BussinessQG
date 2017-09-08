#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_except.py
# @Author: Lmm
# @Date  : 2017-09-07
# @Desc  : 用于获取异常名录信息，并将信息插入到数据库中

import sys
from lxml import etree
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
import requests

url = ''
class Except:
	def name(self,url):
		result = requests.get(url,headers=config.headers_detail)
		status_code = result.status_code
		info = {}
		if status_code ==200:
			content = result.content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding="utf-8"))
			dl = result.xpath("//div[@class = 'viewBox']//dl")[0]
			dlcontent = etree.tostring(dl)
			string = '<dd style="border-top:1px dashed #ccc;">'
			dllist = dlcontent.split(string)
			dllist.remove(dllist[-1])
			for i,single in enumerate(dllist):
				single = etree.HTML(single, parser=etree.HTMLParser(encoding="utf-8"))
				string = u'列入原因'
				in_reason = self.deal_dd_content(string,single)
				string = u'列入日期'
				in_date = self.deal_dd_content(string,single)
				string = u'作出决定机关(列入)'
				gov_dept = self.deal_dd_content(string,single)
				string = u'移出原因'
				out_reason = self.deal_dd_content(string,single)
				string = u'移出日期'
				out_date = self.deal_dd_content(string,single)
				info[i] = [in_reason,in_date,gov_dept,out_reason,out_date]
		return info
		
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath("./dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data