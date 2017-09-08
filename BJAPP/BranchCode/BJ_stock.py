#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_stock.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取股权出质信息
from lxml import etree
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import  deal_html_code
import requests
class Stock:
	def name(self,url):
		info = {}
		result = requests.get(url,config.headers_detail)
		status_code = result.status_code
		if status_code ==200:
			content = result.content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class ='viewBox']//dl")[0]
			tostringinfo = etree.tostring(dl)
			list = tostringinfo.split("<dd style='border-top:1px dashed #ccc;'>")
			list.remove(list[-1])
			for i,single in enumerate(list):
				single = etree.HTML(single,parser=etree.HTMLParser(encoding='utf-8'))
				string = u'质权登记编号'
				equityno = self.deal_dd_content(string,single)
				string = u'出质人'
				pledgor = self.deal_dd_content(string,single)
				string = u'出质人证照编号'
				pled_blicno = self.deal_dd_content(string,single)
				string = u'质权人'
				imporg = self.deal_dd_content(string,single)
				string = u"质权人证照编号"
				imporg_blicno = self.deal_dd_content(string,single)
				string = u"出质股权设立登记日期"
				equlle_date = self.deal_dd_content(string,single)
				string = u"出质状态"
				type = self.deal_dd_content(string,single)
				info[i] = [equityno,pledgor,pled_blicno,imporg,imporg_blicno,equlle_date,type]
		return info
	
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath("./dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data