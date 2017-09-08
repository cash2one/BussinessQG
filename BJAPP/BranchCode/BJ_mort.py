#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_mort.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取动产抵押信息
from lxml import etree
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
import requests
import time
import re
import logging
url = ''
class Mort:
	def name(self,url):
		info = {}
		result = requests.get(url, headers=config.headers_detail)
		status_code = result.status_code
		if status_code ==200:
			content = result.content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class ='viewBox']//dl")[0]
			datalist = etree.tostring(dl).split('<dd style="border-top:1px dashed #ccc;">')
			datalist.remove(datalist[-1])
			for i,single in enumerate(datalist):
				single = etree.HTML(single,parser=etree.HTMLParser(encoding="utf-8"))
				string = u'登记编号'
				code = self.deal_dd_content(string,single)
				string = u"登记日期"
				dates = self.deal_dd_content(string,single)
				string = u"登记机关"
				dept = self.deal_dd_content(string,single)
				string= u"抵押权人名称"
				person_name = self.deal_dd_content(string,single)
				string = u"抵押权人注册号"
				number = self.deal_dd_content(string,single)
				string = u"被担保债权种类"
				cates = self.deal_dd_content(string,single)
				string = u"被担保债权数额"
				amount = self.deal_dd_content(string,single)
				string = u"担保范围"
				ranges = self.deal_dd_content(string,single)
				string = u"履行债务开始日期"
				start_date = self.deal_dd_content(string,single)
				string = u"履行债务结束日期"
				end_date = self.deal_dd_content(string,single)
				period = start_date+'至'+end_date
				info[i] = [code,dates,dept,person_name,number,cates,amount,ranges,period]
		return info
		
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath("./dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
object = Mort()
object.name(url)