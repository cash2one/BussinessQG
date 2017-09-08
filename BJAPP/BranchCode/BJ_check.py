#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_check.py
# @Author: Lmm
# @Date  : 2017-09-07
# @Desc  : 用于获取抽查检查信息，并将信息插入到数据库中
import requests
from lxml import etree
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=030103&ent_id=20e38b8c44baf1250144d7c08cca2947&chr_id=1AFB38484EF500E0E053A06400C300E0&info_categ_name=%E6%8F%90%E7%A4%BA%E4%BF%A1%E6%81%AF%20%3E%3E%20%E6%8A%BD%E6%9F%A5%E4%BF%A1%E6%81%AF'
cookies = {}
cookies["JSESSIONID"] = 'Hexclc3fkqp3_nZcIqmC_Cud2J6I7NWFaSYd9rqk3l8Xykbh2uE-!1793132858'
class Check:
	def name(self,url):
		info = {}
		result = requests.get(url,config.headers_detail,proxies = config.proxies,cookies= cookies)
		status_code = result.status_code
		if status_code ==200:
			content = result.content.decode("gb2312")
			print content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class='viewBox']//dl")[0]
			dlcontent = etree.tostring(dl)
			string = '<dd style="border-top:1px dashed #ccc;">'
			dllist = dlcontent.split(string)
			dllist.remove(dllist[-1])
			for i,single in enumerate(dllist):
				single = etree.HTML(single,parser=etree.HTMLParser(encoding='utf-8'))
				string = u"主体名称"
				name = self.deal_dd_content(string,single)
				string = u"抽查检查日期"
				check_date = self.deal_dd_content(string,single)
				string = u"检查实施机关"
				gov_dept = self.deal_dd_content(string,single)
				string = u"抽查检查结果"
				result = self.deal_dd_content(string,single)
				print name,check_date,gov_dept,result
				info[i] = [name,check_date,gov_dept,result]
		return info
		
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath("./dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
				
object = Check()
object.name(url)