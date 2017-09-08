#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_freeze.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取司法协助信息
from lxml import etree
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
import requests
url = ''
class Freeze:
	def name(self,url):
		info = {}
		result = requests.get(url,headers = config.headers_detail)
		status_code = result.status_code
		if status_code == 200:
			content = result.content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class='viewBox']//dl")[0]
			string = u'执行法院'
			court = self.deal_dd_content(string,dl)
			string = u'被执行人'
			executor = self.deal_dd_content(string,dl)
			string = u'执行书文号'
			rule_no = self.deal_dd_content(string,dl)
			string = u'执行事项'
			items = self.deal_dd_content(string,dl)
			string = u'冻结开始日期'
			start_date = self.deal_dd_content(string,dl)
			string = u'冻结结束日期'
			end_date = self.deal_dd_content(string,dl)
			string = u'公示日期'
			pub_date = self.deal_dd_content(string,dl)
			string = u"被执行人持有股权"
			stock= self.deal_dd_content(string,dl)
			string = u'被执行人证件种类'
			cert_cate = self.deal_dd_content(string,dl)
			string = u'被执行人证件号码'
			cert_code = self.deal_dd_content(string,dl)
			info[0] = [court,executor,rule_no,items,start_date,end_date,pub_date,stock,cert_cate,cert_code]
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath("./dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
object = Freeze()
object.name(url)