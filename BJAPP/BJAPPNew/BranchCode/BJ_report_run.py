#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_report_run.py
# @Author: Lmm
# @Date  : 2017-09-09
# @Desc  : 用与获取年报中财务信息
from lxml import etree
import requests
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
import logging
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
from PublicCode.Public_code import Judge_status
import hashlib
import time

run_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,loan,if_loan,subsidy,if_subsidy,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


def name(url, cookies, headers):
	info = []
	content, status_code = Send_Request().send_request3(url, cookies, headers)
	if status_code == 200:
		flag = 1
		result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
		dl = result.xpath("//div[@class= 'viewBox']/dl")[0]
		list = dl.xpath(".//dt")
		if len(list) > 0:
			if u'资产总额' in content:
				string = u'资产总额'
				asset = deal_dd_content(string, dl)
				if u'不公示' in asset:
					asset = 0
					if_asset = 0
				else:
					asset = deal_html_code.match_finger(asset)
					if_asset = 1
			
			else:
				asset = None
				if_asset = 0
			if u"权益合计" in content:
				string = u'权益合计'
				benifit = deal_dd_content(string, dl)
				if u'不公示' in benifit:
					benifit = 0
					if_benifit = 0
				else:
					benifit = deal_html_code.match_finger(benifit)
					if_benifit = 1
			else:
				benifit = None
				if_benifit = 0
			if u"利润总额" in content:
				string = u"利润总额"
				profit = deal_dd_content(string, dl)
				if u"不公示" in content:
					profit = 0
					if_profit = 0
				else:
					profit = deal_html_code.match_finger(profit)
					if_profit = 1
			else:
				profit = None
				if_profit = 0
			if u'主营业务收入' in content:
				string = u'主营业务收入'
				main_income = deal_dd_content(string, dl)
				if u"不公示" in main_income:
					main_income = 0
					if_main = 0
				else:
					main_income = deal_html_code.match_finger(main_income)
					if_main = 1
			else:
				main_income = None
				if_main = 0
			if u"净利润" in content:
				string = u"净利润"
				net_income = deal_dd_content(string, dl)
				if u"不公示" in net_income:
					net_income = 0
					if_net = 0
				else:
					net_income = deal_html_code.match_finger(net_income)
					if_net = 1
			else:
				net_income = None
				if_net = 0
			if u"纳税总额" in content:
				string = u"纳税总额"
				tax = deal_dd_content(string, dl)
				if u"不公示" in content:
					tax = 0
					if_tax = 0
				else:
					tax = deal_html_code.match_finger(tax)
					if_tax = 1
			else:
				tax = None
				if_tax = 0
			if u"负债总额" in content:
				string = u'负债总额'
				debt = deal_dd_content(string, dl)
				if u"不公示" in content:
					debt = 0
					if_debt = 0
				else:
					if_debt = deal_html_code.match_finger(debt)
					if_debt = 1
			else:
				debt = None
				if_debt = 0
			if u"贷款" in content:
				string = u"贷款"
				loan = deal_dd_content(string, dl)
				if u"不公示" in content:
					loan = 0
					if_loan = 0
				else:
					loan = deal_html_code.match_finger(loan)
					if_loan = 1
			else:
				loan = None
				if_loan = 0
			if u"补助" in content:
				string = u"补助"
				subsidy = deal_dd_content(string, dl)
				if u"不公示" in content:
					subsidy = 0
					if_subsidy = 0
				else:
					subsidy = deal_html_code.match_finger(subsidy)
					if_subsidy = 1
			else:
				subsidy = None
				if_subsidy = 1
			if u"营业总收入" in content:
				string = u"营业总收入"
				income = deal_dd_content(string, dl)
				if u"不公示" in income:
					income = 0
					if_income = 0
				else:
					income = deal_html_code.match_finger(income)
					if_income = 1
			elif u"销售额" in content:
				string = u"销售额"
				income = deal_dd_content(string, dl)
				if u"不公示" in income:
					income = 0
					if_income = 0
				else:
					income = deal_html_code.match_finger(income)
					if_income = 1
			else:
				income = None
				if_income = 0
			
			info = [asset, if_asset, benifit, if_benifit, profit, if_profit, main_income, if_main, income, if_income,
					net_income, if_net, tax, if_tax, debt, if_debt, loan, if_loan, subsidy, if_subsidy]
		else:
			logging.info("无资产信息")
	else:
		flag = 100000004
	return info, flag


# 用于处理dd标签中的内容
def deal_dd_content(string, result):
	dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
	dd = dd[0]
	data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
	return data


def update_run_info(year, gs_report_id, gs_basic_id, cursor, connect, runinfo, province):
	asset, if_asset, benifit, if_benifit = runinfo[0], runinfo[1], runinfo[2], runinfo[3]
	profit, if_profit, main_income, if_main = runinfo[4], runinfo[5], runinfo[6], runinfo[7]
	income, if_income, net_income, if_net = runinfo[8], runinfo[9], runinfo[10], runinfo[11]
	tax, if_tax, debt, if_debt = runinfo[12], runinfo[13], runinfo[14], runinfo[15]
	loan, if_loan, subsidy, if_subsidy = runinfo[16], runinfo[17], runinfo[18], runinfo[19]
	m = hashlib.md5()
	m.update(str(gs_basic_id) + str(year))
	uuid = m.hexdigest()
	remark = 0
	try:
		updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
		count = cursor.execute(run_string, (
			gs_report_id, gs_basic_id, province, asset, if_asset, benifit, if_benifit, income, if_income, profit,
			if_profit,
			main_income, if_main, net_income, if_net, tax, if_tax, debt, if_debt, loan, if_loan, subsidy, if_subsidy,
			uuid,
			updated_time, updated_time))
		connect.commit()
	except Exception, e:
		print e
		remark = 100000006
		logging.error('%s run error:%s' % (year, e))
	finally:
		if remark < 100000001:
			remark = count
		# print 'update run :%s '%remark
		return remark
