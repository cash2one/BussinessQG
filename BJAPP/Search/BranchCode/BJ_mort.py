#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_mort.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取动产抵押信息
from lxml import etree
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
from PublicCode.Public_code import Judge_status
import time
import re
import hashlib
import logging

url = ''
gs_basic_id = ''
gs_py_id = ''

select_mort = 'select gs_mort_id from gs_mort where gs_basic_id = %s and code = %s'
mort_string = 'insert into gs_mort(gs_basic_id,id,code, dates, dept, amount, cates,period, ranges, updated)' \
			  'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_mort = 'update gs_mort set gs_mort_id = %s ,dates = %s, dept = %s, amount = %s, cates = %s,period = %s, ranges = %s,updated = %s ' \
			  'where gs_mort_id = %s'
update_mort_py = 'update gs_py set gs_py_id = %s,gs_mort = %s,updated = %s where gs_py_id = %s'


class Mort:
	def name(self, url):
		info = {}
		content, status_code = Send_Request().send_request(url)
		if status_code == 200:
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class ='viewBox']//dl")[0]
			datalist = etree.tostring(dl).split('<dd style="border-top:1px dashed #ccc;">')
			datalist.remove(datalist[-1])
			for i, single in enumerate(datalist):
				single = etree.HTML(single, parser=etree.HTMLParser(encoding="utf-8"))
				if u"登记编号" in content:
					string = u'登记编号'
					code = self.deal_dd_content(string, single)
				else:
					code = None
				if u"登记日期" in content:
					string = u"登记日期"
					dates = self.deal_dd_content(string, single)
				else:
					dates = '0000-00-00'
				if u"登记机关" in content:
					string = u"登记机关"
					dept = self.deal_dd_content(string, single)
				else:
					dept = None
				string = u"抵押权人名称"
				person_name = self.deal_dd_content(string, single)
				string = u"抵押权人注册号"
				number = self.deal_dd_content(string, single)
				string = u"被担保债权种类"
				cates = self.deal_dd_content(string, single)
				string = u"被担保债权数额"
				amount = self.deal_dd_content(string, single)
				string = u"担保范围"
				ranges = self.deal_dd_content(string, single)
				string = u"履行债务开始日期"
				start_date = self.deal_dd_content(string, single)
				string = u"履行债务结束日期"
				end_date = self.deal_dd_content(string, single)
				period = start_date + '至' + end_date
				info[i] = [code, dates, dept, person_name, number, cates, amount, ranges, period]
		return info
	
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
	
	def update_to_db(self, info, gs_basic_id):
		update_flag, insert_flag = 0, 0
		mort_flag = 0
		recordstotal = len(info)
		logging.info("mort total:%s" % recordstotal)
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		try:
			for key in info.keys():
				code, dates, dept, person_name = info[key][0], info[key][1], info[key][2], info[key][3]
				number, cates, amount, ranges, period = info[key][4], info[key][5], info[key][6], info[key][7], \
														info[key][8]
				count = cursor.execute(select_mort, (gs_basic_id, code))
				if count == 0:
					m = hashlib.md5()
					m.update(code)
					id = m.hexdigest()
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(mort_string, (
						gs_basic_id, id, code, dates, dept, amount, cates, period, ranges, updated_time))
					gs_mort_id = connect.insert_id()
					insert_flag += flag
					connect.commit()
				
				elif int(count) == 1:
					gs_mort_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(update_mort, (gs_mort_id,
														dates, dept, amount, cates, period, ranges,
														updated_time, gs_mort_id))
					update_flag += flag
					connect.commit()
		except Exception, e:
			logging.info('mort error :%s' % e)
			mort_flag = 100000006
		finally:
			total = insert_flag + update_flag
			if mort_flag < 100000001:
				mort_flag = total
				logging.info("execute mort:%s" % mort_flag)
			return mort_flag, recordstotal, update_flag, insert_flag


def main(gs_py_id, gs_basic_id, url):
	Log().found_log(gs_py_id, gs_basic_id)
	name = 'person'
	flag = Judge_status().judge(gs_basic_id, name, Mort, url)
