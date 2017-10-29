#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_share_history.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取投资历史信息

from lxml import etree
import requests
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
from PublicCode.Public_code import Judge_status
import logging
import time

# url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_czlsxx_wap.dhtml?reg_bus_ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&clear=true&fqr=fqr'
# gs_basic_id = '1'
# gs_py_id = '122'
select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s'
insert_string = 'update gs_shareholder set gs_shareholder_id = %s,gs_basic_id = %s,name = %s,types = %s,reg_amount = %s,ra_ways = %s,ra_date = %s,true_amount = %s,ta_ways = %s,ta_date = %s,updated = %s where gs_shareholder_id = %s'


class Share_History:
	def name(self, url):
		headers = config.headers_detail
		content, status_code = Send_Request().send_request(url, headers)
		info = {}
		if status_code == 200:
			# print content
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class='viewBox']//dl")[0]
			datalsit = etree.tostring(dl).split('<br/>')
			datalsit.remove(datalsit[-1])
			for i, single in enumerate(datalsit):
				single = etree.HTML(single, parser=etree.HTMLParser(encoding='utf-8'))
				name = single.xpath("//dt[@style='color:#333;margin-bottom:10px;']/text()")[0]
				string = u"投资人类型"
				types = self.deal_dd_content(string, single)
				string = u"认缴出资金额"
				reg_amount = self.deal_dd_content(string, single)
				string = u"认缴出资方式"
				ra_ways = self.deal_dd_content(string, single)
				string = u"认缴出资时间"
				ra_date = self.deal_dd_content(string, single)
				if ra_date == '':
					ra_date = '0000-00-00'
				string = u"实缴出资金额"
				true_amount = self.deal_dd_content(string, single)
				string = u"实缴出资方式"
				ta_ways = self.deal_dd_content(string, single)
				string = u"实缴出资时间"
				ta_date = self.deal_dd_content(string, single)
				if ta_date == '':
					ta_date = '0000-00-00'
				info[i] = [name, types, reg_amount, ra_ways, ra_date, true_amount, ta_ways, ta_date]
		else:
			flag = 100000004
		if len(info) > 0:
			info = deal_html_code.remove_repeat(info)
		return info, flag
	
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
	
	def upadte_to_db(self, info, gs_basic_id):
		insert_flag = 0
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				name, types, reg_amount = info[key][0], info[key][1], info[key][2]
				ra_ways, ra_date, true_amount = info[key][3], info[key][4], info[key][5]
				ta_ways, ta_date = info[key][6], info[key][7]
				count = cursor.execute(select_string, (gs_basic_id, name, types))
				
				if int(count) == 1:
					gs_shareholder_id = cursor.fetchall()[0][0]
					
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					
					rows_count = cursor.execute(insert_string, (
					gs_shareholder_id, gs_basic_id, name, types, reg_amount, ra_ways, ra_date, true_amount, ta_ways,
					ta_date, updated_time, gs_shareholder_id))
					insert_flag += rows_count
					connect.commit()
				else:
					pass
		except Exception, e:
			# print e
			logging.info("update branch error:%s" % e)
			flag = 100000006
		finally:
			cursor.close()
			connect.close()


def main(gs_py_id, gs_basic_id, url):
	try:
		Log().found_log(gs_py_id, gs_basic_id)
		info, flag = Share_History().name(url)
		if flag == 1:
			Share_History().upadte_to_db(info, gs_basic_id)
	except Exception, e:
		logging.info("sharehistory error:%s" % e)
