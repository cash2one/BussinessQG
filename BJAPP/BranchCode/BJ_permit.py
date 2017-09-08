#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_permit.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 用于获取行政许可信息，并将数据库插入到数据库中
from PublicCode import config
import requests
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
from lxml import etree
url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=014167&ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&chr_id=4063636AFB1A01B2E053D400000501B2,&info_categ_name=%E8%AE%B8%E5%8F%AF%E8%B5%84%E8%B4%A8%E4%BF%A1%E6%81%AF%20%3E%3E%20%E8%A1%8C%E6%94%BF%E8%AE%B8%E5%8F%AF'
class Permit:
	def name(self,url):
		info = {}
		result = requests.get(url,headers=config.headers_detail)
		status_code = result.status_code
		if status_code ==200:
			content = result.content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			ddlist = result.xpath("//div[@class='viewBox']//dl")[0]
			string = u"主体名称"
			name = self.deal_dd_content(string,ddlist)
			string = u"项目名称"
			filename = self.deal_dd_content(string,ddlist)
			string = u"行政许可决定书文号"
			code = self.deal_dd_content(string,ddlist)
			string = u"审批类别"
			string = u"许可内容"
			content = self.deal_dd_content(string,ddlist)
			string = u"许可决定日期"
			decide_date = self.deal_dd_content(string,ddlist)
			string = u"当前状态"
			status = self.deal_dd_content(string,ddlist)
			string= u"许可机关"
			dov_dept = self.deal_dd_content(string,ddlist)
		print name,filename,code,content,decide_date,status,dov_dept
		info[0] = [name,filename,code,content,decide_date,status,dov_dept]
	
	def deal_dd_content(self,string,ddlist):
		dd = ddlist.xpath(".//dt[contains(.,'%s')]"%string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
		
		
	
object = Permit()
object.name(url)
