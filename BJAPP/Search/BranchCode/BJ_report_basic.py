#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_report_basic.py
# @Author: Lmm
# @Date  : 2017-09-09
# @Desc  : 用与获取企业年报中基本信息
import requests
from lxml import etree
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
from PublicCode.Public_code import Send_Request

import logging
import re
import time
import logging
import hashlib

basic_string = 'insert into gs_report(gs_basic_id,year,province,name, uuid, tel, address, email, postcode, status, employee, code, ccode,  if_invest,if_website,\
 runner,amount,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_address = 'update gs_basic set gs_basic_id = %s,tel = %s,address = %s,email = %s  where gs_basic_id = %s'


# province = 'BEJ'
def name(url, cookies, headers):
	info = {}
	content, status_code = Send_Request().send_request3(url, cookies, headers)
	if status_code == 200:
		flag = 1
		result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
		if u"企业名称" in content:
			string = u"企业名称"
			name = deal_dd_content(string, result)
		if u"注册号" in content:
			string = u"注册号"
			code = deal_dd_content(string, result)
		else:
			code = None
		if u"统一社会信用代码" in content:
			string = u'统一社会信用代码'
			ccode = deal_dd_content(string, result)
		elif u"统一社会信用代码/注册号" in content:
			string = u"统一社会信用代码/注册号"
			ccode = deal_dd_content(string, result)
		else:
			ccode = ''
		if u'联系电话' in content:
			string = u"联系电话"
			tel = deal_dd_content(string, result)
		else:
			tel = None
		if u'邮政编码' in content:
			string = u"邮政编码"
			postcode = deal_dd_content(string, result)
		else:
			postcode = None
		if u'邮箱' in content:
			string = u"邮箱"
			email = deal_dd_content(string, result)
		else:
			email = None
		if u'状态' in content:
			string = u"状态"
			status = deal_dd_content(string, result)
		else:
			status = None
		if u"地址" in content:
			string = u"地址"
			address = deal_dd_content(string, result)
		else:
			address = None
		if u"网站或网店" in content:
			string = u"网站或网店"
			if_website = deal_dd_content(string, result)
			if if_website == u"是":
				if_website = 1
			else:
				if_website = 0
		else:
			if_website = 0
		if u"投资" in content:
			string = u"投资"
			if_invest = deal_dd_content(string, result)
			if if_invest == u"是":
				if_invest = 1
			else:
				if_invest = 0
		else:
			if_invest = 0
		if u"从业人数" in content:
			string = u"从业人数"
			employee = deal_dd_content(string, result)
		else:
			employee = 0
		if u"姓名" in content:
			string = u"姓名"
			runner = deal_dd_content(string, result)
		else:
			runner = None
		if u"资金数额" in content:
			string = u"资金数额"
			amount = deal_dd_content(string, result)
		else:
			amount = None
		info[0] = [name, code, ccode, tel, postcode, email, status, address, if_website, if_invest, employee, runner,
				   amount]
	else:
		flag = 100000004
	return info, flag


# 用于处理dd标签中的内容
def deal_dd_content(string, result):
	dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
	dd = dd[0]
	data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
	return data


def update_to_db(gs_basic_id, info, year, cursor, connect, province):
	try:
		name, code, ccode, tel = info[0][0], info[0][1], info[0][2], info[0][3]
		postcode, email, status, address = info[0][4], info[0][5], info[0][6], info[0][7]
		if_website, if_invest, employee = info[0][8], info[0][9], info[0][10]
		runner, amount = info[0][11], info[0][12]
		m = hashlib.md5()
		m.update(str(gs_basic_id) + str(year))
		uuid = m.hexdigest()
		remark = 0
		cursor.execute(update_address, (gs_basic_id, tel, address, email, gs_basic_id))
		connect.commit()
		updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
		count = cursor.execute(basic_string, (
			gs_basic_id, year, province, name, uuid, tel, address, email, postcode, status, employee, code, ccode,
			if_invest, if_website, runner, amount, updated_time, updated_time))
		gs_report_id = connect.insert_id()
		connect.commit()
	except Exception, e:
		print e
		remark = 100000006
		logging.error('report basic error:%s' % e)
	finally:
		if remark < 100000001:
			remark = count
		return gs_report_id, remark
