#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_freeze.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取司法协助信息
from lxml import etree
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
from PublicCode import deal_html_code
import logging
import requests
import time

url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=030404&ent_id=197A3E86527C570DE050007F01007DB1&chr_id=20e38b8b50c7d44f0150db8397d14845,&info_categ_name='
gs_basic_id = '1212'
gs_py_id = '1'

freeze_string = 'insert into gs_freeze(gs_basic_id,executor, stock_amount, court, notice_no,status,items, rule_no, enforce_no,cert_cate,cert_code, start_date, end_date,period, pub_date,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_freeze = 'select gs_freeze_id from gs_freeze where gs_basic_id = %s and rule_no = %s'
update_freeze_py = 'update gs_py set gs_py_id = %s ,gs_freeze = %s ,updated = %s where gs_py_id = %s'


class Freeze:
	def name(self, url):
		info = {}
		content, status_code = Send_Request().send_request(url)
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class='viewBox']//dl")[0]
			string = u'执行法院'
			court = self.deal_dd_content(string, dl)
			string = u'被执行人'
			executor = self.deal_dd_content(string, dl)
			string = u'执行文书文号'
			rule_no = self.deal_dd_content(string, dl)
			string = u'执行事项'
			items = self.deal_dd_content(string, dl)
			string = u'冻结开始日期'
			start_date = self.deal_dd_content(string, dl)
			string = u'冻结结束日期'
			end_date = self.deal_dd_content(string, dl)
			string = u'公示日期'
			pub_date = self.deal_dd_content(string, dl)
			string = u"被执行人持有股权"
			stock = self.deal_dd_content(string, dl)
			string = u'被执行人证件种类'
			cert_cate = self.deal_dd_content(string, dl)
			string = u'被执行人证件号码'
			cert_code = self.deal_dd_content(string, dl)
			string = u"解冻日期"
			end_freeze = self.deal_dd_content(string, dl)
			info[0] = [court, executor, rule_no, items, start_date, end_date, pub_date, stock, cert_cate, cert_code,
					   end_freeze]
		else:
			flag = 100000004
		# print info,flag
		return info, flag
	
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
	
	def update_to_db(self, information, gs_basic_id):
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(information)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				court, executor, rule_no, items = information[key][0], information[key][1], information[key][2], \
												  information[key][3]
				start_date, end_date, pub_date, stock_amount = information[key][4], information[key][5], \
															   information[key][6], information[key][7]
				cert_cate, cert_code = information[key][8], information[key][9]
				end_freeze = information[key][10]
				if end_freeze == '':
					status = '冻结'
				else:
					status = '解冻'
				notice_no = rule_no
				enforce_no = rule_no
				period = deal_html_code.caltime(start_date, end_date)
				period = str(period) + '天'
				
				count = cursor.execute(select_freeze, (gs_basic_id, rule_no))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(freeze_string, (
						gs_basic_id, executor, stock_amount, court, notice_no, status, items, rule_no, enforce_no,
						cert_cate, cert_code, start_date, end_date, period, pub_date, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			print e
			logging.error("freeze error: %s" % e)
			flag = 100000006
		finally:
			if flag < 100000001:
				flag = insert_flag
			return flag, total, insert_flag, update_flag


def main(gs_py_id, gs_basic_id, url):
	Log().found_log(gs_py_id, gs_basic_id)
	name = 'Freeze'
	flag = Judge_status().judge(gs_basic_id, name, Freeze, url)
	
	# if __name__ == '__main__':
	#     main(gs_py_id,gs_basic_id,url)
