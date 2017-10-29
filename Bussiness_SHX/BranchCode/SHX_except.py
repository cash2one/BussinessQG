#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_except.py
# @Author: Lmm
# @Date  : 2017-10-19 10:41
# @Desc  : 用于获取页面中的经营异常信息
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from lxml import etree
import logging
import time

except_string = 'insert into gs_except(gs_basic_id,types, in_reason, in_date,out_reason, out_date, gov_dept,out_gov,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_except = 'select gs_except_id from gs_except where gs_basic_id = %s and in_date = %s'
update_except = 'update gs_except set gs_except_id = %s,types = %s ,in_reason = %s,out_reason = %s ,out_date=%s,gov_dept = %s ,out_gov = %s,updated = %s where gs_except_id = %s'
url = 'http://sn.gsxt.gov.cn/ztxy.do?method=qyinfo_jyycxx&pripid={0}&random=1508725286354'


class Except:
	def __init__(self, pripid, url):
		self._pripid = pripid
		self._url = url
	
	#
	def get_info(self):
		headers = config.headers
		url = self._url.format(self._pripid)
		result, status_code = Send_Request().send_requests(url, headers)
		info = {}
		if status_code == 200:
			data = etree.xpath(result, parser=etree.HTMLParser(encoding='utf-8'))
			tr_list = data.xpath("//table[id= 'table_jyyc']//tr[@name = 'jyyc']")
			for i, singledata in enumerate(tr_list):
				temp = {}
				td_list = singledata.xpath("./td")
				temp["types"] = '经营异常'
				temp["in_reason"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
				in_date = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
				temp["in_date"] = deal_html_code.change_chinese_date(in_date)
				temp["out_reason"] = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
				out_date = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
				temp["out_date"] = deal_html_code.change_chinese_date(out_date)
				temp["gov_dept"] = deal_html_code.remove_symbol(td_list[6].xpath("string(.)"))
				temp["out_gov"] = deal_html_code.remove_symbol(td_list[7].xpath("string(.)"))
				info[i] = temp
		return info
	
	def update_to_db(self, info, gs_basic_id):
		update_flag, insert_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key, value in info.iteritems():
				types, in_reason, in_date = value["types"], value["in_reason"], value["in_date"]
				out_reason, out_date, gov_dept = value["out_reason"], value["out_date"], value["gov_dept"]
				out_gov = value["out_gov"]
				count = cursor.execute(select_except, (gs_basic_id, in_date))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(except_string, (
						gs_basic_id, types, in_reason, in_date, out_reason, out_date, gov_dept, out_gov, updated_time))
					insert_flag += rows_count
					connect.commit()
				elif count == 1:
					gs_except_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(update_except, (
						gs_except_id, types, in_reason, out_reason, out_date, gov_dept, out_gov, updated_time,
						gs_except_id))
					update_flag += rows_count
					connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error("except error: %s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag + update_flag
			
			return remark, total, insert_flag, update_flag
