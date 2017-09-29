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
url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_czlsxx_wap.dhtml?reg_bus_ent_id=26B8239E652E4DA1AD3FFADE573DC6E8&clear=true&fqr='
select_string= 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s'
insert_string = 'insert into gs_shareholder(gs_shareholder_id,name,types,reg_amount,ra_ways,ra_date,true_amount,ta_ways,ta_date,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Share_History:
	def name(self,url):
		headers = config.headers_detail
		content, status_code = Send_Request().send_request(url, headers)
		info = {}
		
		if status_code ==200:
			# print content
			flag = 1
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class='viewBox']//dl")[0]
			datalsit = deal_html_code.remove_space(etree.tostring(dl)).split('<br/>')
			datalsit.remove(datalsit[-1])
			for i,single in enumerate(datalsit):
				single = etree.HTML(single,parser=etree.HTMLParser(encoding='utf-8'))
				name = single.xpath("//dt[@style='color:#333;margin-bottom:10px;']/text()")
				string = u"投资人类型"
				types = self.deal_dd_content(string,single)
				string = u"认缴出资金额"
				reg_amount = self.deal_dd_content(string, single)
				string = u"认缴出资方式"
				ra_ways = self.deal_dd_content(string,single)
				string = u"认缴出资时间"
				ra_date = self.deal_dd_content(string,single)
				string = u"实缴出资金额"
				true_amount = self.deal_dd_content(string,single)
				string = u"实缴出资方式"
				ta_ways = self.deal_dd_content(string,single)
				string = u"实缴出资时间"
				ta_date = self.deal_dd_content(string,single)
				info[i] = [name,types,reg_amount,ra_ways,ra_date,true_amount,ta_ways,ta_date]
		else:
			flag = 100000004
		return info,flag
	# 用于处理dd标签中的内容
	def deal_dd_content(self,string, result):
		dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
			
	def upadte_to_db(self,info,gs_basic_id):
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				name, types, reg_amount = info[key][0], info[key][1], info[key][2]
				ra_ways, ra_date, true_amount = info[key][3],info[key][4],info[key][5]
				ta_ways, ta_date = info[key][6],info[key][7]
				
				count = cursor.execute(select_string, (gs_basic_id,name,types))
				if int(count) == 1:
					gs_shareholder_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					cursor.execute(insert_string, (gs_shareholder_id,name,types,reg_amount,ra_ways,ra_date,true_amount,ta_ways,ta_date,updated_time))
					# insert_flag += rows_count
					connect.commit()
				else:
					pass
		except Exception, e:
			logging.info("update branch error:%s" % e)
			flag = 100000006

		finally:
			cursor.close()
			connect.close()
def main(gs_py_id,gs_basic_id,url):
	Log().found_log(gs_py_id,gs_basic_id)
	name = 'share_history'
	flag = Judge_status().judge(gs_basic_id, name,Share_History, url)
	
