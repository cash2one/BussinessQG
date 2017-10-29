#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_freeze.py
# @Author: Lmm
# @Date  : 2017-10-19 10:42
# @Desc  : 用于获取页面中的司法协助信息

from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode import deal_html_code
from lxml import etree
import logging
import time

freeze_string = 'insert into gs_freeze(gs_basic_id,executor, stock_amount, court, notice_no,status,items, rule_no, enforce_no,cert_cate,cert_code, start_date, end_date,period, pub_date,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_freeze = 'select gs_freeze_id from gs_freeze where gs_basic_id = %s and rule_no = %s and executor = %s'


class Freeze:
	def __init__(self, pripid, url):
		self._pripid = pripid
		self._url = url
	
	# 若是多省统一代码该如何修改？
	# data.xpath("//table[@id = 'table_sfxz']//tr[@name = 'sfxz']"
	def get_info(self, data):
		info = {}
		tr_list = data.xpath(".//table[@id='table_sfxz']//tr[@name = 'sfxz']")
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			if len(td_list) == 0:
				continue
			executor = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["exceutor"] = executor
			stock_amount = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["stock_amount"] = stock_amount
			court = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["court"] = court
			notice_no = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			temp["notice_no"] = notice_no
			temp["enforce_no"] = notice_no
			status = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
			temp["status"] = status
			onclik = td_list[6].xpath("./a/@onclick")[0]
			tuple = deal_html_code.match_key_content(str(onclik))
			xh = tuple[0]
			lx = tuple[1]
			detail_url = self._url.format(self._pripid, lx, xh)
			self.get_deatail_info(detail_url, info)
			info[i] = temp
		return info
	
	def get_deatail_info(self, detail_url, info):
		dict = {
			u"执行事项": "items",
			u"裁定书文号": "rule_no",
			u"证照种类": "cert_cate",
			u"证照号码": "cert_code",
			u"冻结期限自": "start_date",
			u"冻结期限至": "end_date",
			u"冻结期限": "period",
			u"公示日期": "pub_date"
		}
		headers = config.headers
		result, status_code = Send_Request().send_requests(detail_url, headers)
		if status_code == 200:
			data = result.xpath(result, parser=etree.HTMLParser(encoding='utf-8'))
			for key, value in dict:
				content = deal_html_code.get_match_info(key, data)
				info[value] = content
		else:
			logging.info("获取司法协助详情信息失败！")
	
	def update_to_db(self, info, gs_basic_id):
		
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(info)
		try:
			
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key, value in info.iteritems():
				executor, stock_amount, court, notice_no = value["executor"], value["stock_amount"], value["court"], \
														   value["notice_no"]
				status, items, rule_no, enforce_no = value["status"], value["items"], value["rule_no"], value[
					"enforce_no"]
				cert_cate, cert_code, start_date, end_date = value["cert_cate"], value["cert_code"], value[
					"start_date"], value["end_date"]
				period, pub_date = value["period"], value["pub_date"]
				count = cursor.execute(select_freeze, (gs_basic_id, rule_no, executor))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(freeze_string, (
						gs_basic_id, executor, stock_amount, court, notice_no, status, items, rule_no, enforce_no,
						cert_cate, cert_code, start_date, end_date, period, pub_date, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			logging.error("freeze error: %s" % e)
			flag = 100000006
		finally:
			cursor.close()
			connect.close()
			if flag < 100000001:
				flag = insert_flag
			return flag, total, insert_flag, update_flag
