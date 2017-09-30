#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_report_basic.py
# @Author: Lmm
# @Date  : 2017-09-23
# @Desc  : 用于获得江苏企业年报中的基本信息和财务信息,并将信息插入到数据库中
from PublicCode import config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Log
from PublicCode import deal_html_code
import logging
import time
import hashlib
import json

basic_string = 'insert into gs_report(gs_basic_id,year,province,name,uuid, tel, address, email, postcode, status, employee, if_empnum, womennum,\
 if_womennum, holding, if_holding,mainbus,code,ccode,source,runner,amount,fill_date,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
run_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,loan, if_loan, subsidy, if_subsidy,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_address = 'update gs_basic set gs_basic_id = %s,tel = %s,address = %s,email = %s where gs_basic_id = %s'
update_report_py ='update gs_py set gs_py_id = %s ,report = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
update_run_py = 'update gs_py set gs_py_id = %s ,report_run = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
class Report_Basic:
	def __init__(self, url, headers,gs_py_id):
		self.url = url
		self.headers = headers
		self.gs_py_id = gs_py_id
	def get_info(self):
		result,status_code = Send_Request(self.url,self.headers).send_request()
		info = {}
		runinfo = {}
		if status_code ==200:
			flag = 1
			data = json.loads(result.content)
			code = data["REG_NO"]
			if code.startswith("9"):
				ccode = code
			else:
				ccode = ''
			name = data["CORP_NAME"]
			tel = data["TEL"]
			address = data["ADDR"]
			email = data["E_MAIL"]
			postcode = data["ZIP"]
			status = data["PRODUCE_STATUS"]
			employee = data["PRAC_PERSON_NUM"]
			if employee ==None:
				if_empnum =0
			elif u"不公示" in employee:
				if_empnum = 0
			else:
				if_empnum = 1
			
			womennum = data["WOM_EMP_NUM"]
			if womennum ==None:
				if_womennum = 0
			elif u"不公示" in womennum:
				if_womennum = 0
			else:
				if_womennum = 1
			holding = data["HOLDINGS_MSG"]
			if holding ==None:
				if_holding = 0
			elif u"不公示" in holding:
				if_holding = 0
			
			else:
				if_holding = 1
			mainbus = data["MAIN_BUSIACT"]
			runner = data["OPER_MAN_NAME"]
			amount = data["REG_CAPI"]
			fill_date = data["REPORT_DATE"]
			
			info[0] = [name,  tel, address, email, postcode, status, employee, if_empnum, womennum,
							  if_womennum, holding, if_holding, mainbus, code, ccode,runner, amount, fill_date]
			asset = data["NET_AMOUNT"]
			if_asset = self.judge_if_public(asset)
			
			asset = deal_html_code.match_float(asset)
			benifit = data["TOTAL_EQUITY"]
			if_benifit = self.judge_if_public(benifit)
			benifit = deal_html_code.match_float(benifit)
			income = data["SERV_FARE_INCOME"]
			if_income = self.judge_if_public(income)
			income = deal_html_code.match_float(income)
			
			profit = data["PROFIT_TOTAL"]
			if_profit = self.judge_if_public(profit)
			profit = deal_html_code.match_float(profit)
			
			main_income = data["SALE_INCOME"]
			if_main = self.judge_if_public(main_income)
			main_income = deal_html_code.match_float(main_income)
			net_income = data["PROFIT_RETA"]
			if_net = self.judge_if_public(net_income)
			net_income = deal_html_code.match_float(net_income)
			tax = data["TAX_TOTAL"]
			if_tax = self.judge_if_public(tax)
			tax = deal_html_code.match_float(tax)
			debt = data["DEBT_AMOUNT"]
			if_debt = self.judge_if_public(debt)
			debt = deal_html_code.match_float(debt)
			loan = data["LOAN"]
			if_loan = self.judge_if_public(loan)
			loan = deal_html_code.match_float(loan)
			subsidy = data["SUBSIDY"]
			if_subsidy = self.judge_if_public(subsidy)
			subsidy = deal_html_code.match_float(subsidy)
			runinfo[0] = [asset, if_asset, benifit, if_benifit, income, if_income, profit, if_profit, main_income,
						  if_main, net_income, if_net, tax, if_tax, debt, if_debt,loan,if_loan,subsidy,if_subsidy]
			
		else:
			flag = 100000004
		return info, runinfo, flag
    #用来判断是否公示
	def judge_if_public(self,asset):
		if asset == None:
			if_asset = 0
		else:
			if u"元" in asset:
				if_asset = 1
			else:
				if_asset = 0
		return if_asset
		
	def update_report_basic(self,cursor,connect,gs_basic_id,baseinfo,year):
		name, tel, address, email = baseinfo[0][0], baseinfo[0][1], baseinfo[0][2], baseinfo[0][3]
		postcode, status, employee, if_empnum = baseinfo[0][4], baseinfo[0][5], baseinfo[0][6], baseinfo[0][7]
		womennum,if_womennum, holding, if_holding = baseinfo[0][8], baseinfo[0][9], baseinfo[0][10], baseinfo[0][11]
		mainbus, code = baseinfo[0][12], baseinfo[0][13]
		ccode, runner = baseinfo[0][14], baseinfo[0][15]
		amount,fill_date = baseinfo[0][16], baseinfo[0][17]
		
		m = hashlib.md5()
		m.update(str(gs_basic_id) + str(year))
		uuid = m.hexdigest()
		if email == '无' :
			email = None
		if tel == '无':
			tel = None
		if address == '无':
			address = None
		cursor.execute(update_address, (gs_basic_id, tel, address, email, gs_basic_id))
		connect.commit()
		remark = 0
		source = 0
		try:
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			row_count = cursor.execute(basic_string, (gs_basic_id, year, config.province,
													  name, uuid, tel, address, email, postcode, status, employee,
													  if_empnum, womennum, if_womennum,
													  holding, if_holding, mainbus, code, ccode, source,
													  runner, amount, fill_date, updated_time, updated_time))
			gs_report_id = connect.insert_id()
			connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error('report basic error %s' % e)
		finally:
			if remark < 100000001:
				remark = row_count
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			cursor.execute(update_report_py, (self.gs_py_id, remark, updated_time, gs_basic_id, self.gs_py_id))
			connect.commit()
		return gs_report_id
		
			
	def update_report_run(self,cursor,connect,gs_basic_id,runinfo,gs_report_id,year):
		asset, if_asset, benifit, if_benifit = runinfo[0][0], runinfo[0][1], runinfo[0][2], runinfo[0][3]
		income, if_income, profit, if_profit = runinfo[0][4], runinfo[0][5], runinfo[0][6], runinfo[0][7]
		main_income, if_main, net_income, if_net = runinfo[0][8], runinfo[0][9], runinfo[0][10], runinfo[0][11]
		tax, if_tax, debt, if_debt = runinfo[0][12], runinfo[0][13], runinfo[0][14], runinfo[0][15]
		loan, if_loan, subsidy, if_subsidy = runinfo[0][16],runinfo[0][17],runinfo[0][18],runinfo[0][19]
		m = hashlib.md5()
		m.update(str(gs_basic_id) + str(year))
		uuid = m.hexdigest()
		remark = 0
		try:
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			row_count = cursor.execute(run_string, (
			gs_report_id, gs_basic_id, config.province, asset, if_asset, benifit, if_benifit, income, if_income, profit,
			if_profit, main_income, if_main, net_income, if_net, tax, if_tax, debt, if_debt, uuid, loan, if_loan, subsidy, if_subsidy,updated_time,
			updated_time))
			connect.commit()
		
		except Exception, e:
			remark = 100000006
			logging.error('report run error %s' % e)
		
		finally:
			if remark < 100000001:
				remark = row_count
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			cursor.execute(update_run_py, (self.gs_py_id, remark, updated_time, gs_basic_id, self.gs_py_id))
			connect.commit()
		
	
		
		