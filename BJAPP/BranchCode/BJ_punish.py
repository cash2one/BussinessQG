#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_punish.py
# @Author: Lmm
# @Date  : 2017-09-07
# @Desc  : 获取行政处罚信息，并将信息插入到数据库中
import requests
from PublicCode import config
from lxml import etree
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=040404&ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&chr_id=4D7B2EE62EDE0170E053D40000050170,4D7B2EE62E020170E053D40000050170&info_categ_name=%E8%AD%A6%E7%A4%BA%E4%BF%A1%E6%81%AF%20%3E%3E%20%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A'
class Punish:
	def name(self,url):
		info = {}
		result = requests.get(url,headers = config.headers_detail)
		status_code = result.status_code
		if status_code ==200:
			content = result.content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding="utf-8"))
			dl= result.xpath("//div[@class = 'viewBox']//dl")[0]
			dlcontent = etree.tostring(dl)
			string = '<dd style="border-top:1px dashed #ccc;">'
			dllist = dlcontent.split(string)
			dllist.remove(dllist[-1])
			for i,single in enumerate(dllist):
				single = etree.HTML(single,parser=etree.HTMLParser(encoding="utf-8"))
				string = u"主体名称"
				name = self.deal_dd_content(string,single)
				string = u"行政处罚决定书文号"
				number = self.deal_dd_content(string,single)
				string = u"处罚事由"
				types = self.deal_dd_content(string,single)
				string = u"处罚依据"
				basis = self.deal_dd_content(string,single)
				string = u"处罚结果"
				result = self.deal_dd_content(string,single)
				string = u"处罚决定日期"
				date = self.deal_dd_content(string,single)
				string = u"处罚机构"
				gov_dept = self.deal_dd_content(string,single)
				info[i] = [name,number,types,basis,result,date,gov_dept]
				
				
	#用于处理dd标签中的内容
	def deal_dd_content(self,string,result):
		dd = result.xpath("./dt[contains(.,'%s')]"%string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
object = Punish()
object.name(url)