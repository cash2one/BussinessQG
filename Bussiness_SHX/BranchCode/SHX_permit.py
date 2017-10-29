#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_permit.py
# @Author: Lmm
# @Date  : 2017-10-19 10:45
# @Desc  : 用于获取页面中的行政许可信息
from PublicCode.Public_code import Send_Request
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
from lxml import etree
import logging
import time
import re

select_string = 'select gs_permit_id from gs_permit where gs_basic_id = %s and filename = %s and code = %s and start_date = %s and end_date = %s '
permit_string = 'insert into gs_permit(gs_basic_id,id,name, code, filename, start_date, end_date, content, gov_dept,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Permit:
	def __init__(self, pripid, url):
		self._pripid = pripid
		self._url = url
	def get_info(self):
		url = self._url.format(self._pripid)
		headers = config.headers
		result, status_code = Send_Request().send_requests(url, headers=headers)
		data = etree.HTML(result, parser=etree.HTMLParser(encoding='utf-8'))
		tr_list = data.xpath("//table[@id ='table_xzxk']//tr[name = 'xzxk']")
		info = {}
		for i,singledata in enumerate(tr_list):
			td_list = singledata.xpath("./td")
			if len(td_list) ==0:
				continue
			temp = {}
			# number = deal_html_code.remove_symbol(td_list[0].xpath("string(.)"))
			temp["name"] = ''
			temp["code"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["filename"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			start_date = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["start_date"] = deal_html_code.change_chinese_date(start_date)
			end_date = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			temp["end_date"] = deal_html_code.change_chinese_date(end_date)
			temp["gov_dept"] = deal_html_code.remove_symbol(td_list[6].xpath("string(.)"))
			temp["content"] = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
			info[i] = temp
		return info
	
	def update_to_db(self, gs_basic_id, cursor, connect, info):
		insert_flag, update_flag = 0, 0
		remark = 0
		source = 0
		
		for key,value in info.iteritems():
			name, code, filename, start_date = value["name"], value["code"], value["filename"], value["start_date"]
			end_date, content, gov_dept = value["end_date"], value["content"], value["gov_dept"]
			count = cursor.execute(select_string, (gs_basic_id, filename, code, start_date, end_date))
			id = ''
			try:
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(permit_string, (
						gs_basic_id, id, name, code, filename, start_date, end_date, content, gov_dept, source,
						updated_time))
					insert_flag += rows_count
					connect.commit()
			
			except Exception, e:
				remark = 100000006
				logging.error("permit error: %s" % e)
		if remark < 100000001:
			remark = insert_flag
		return remark, insert_flag, update_flag
