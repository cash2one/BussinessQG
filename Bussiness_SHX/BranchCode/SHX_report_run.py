#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_report_run.py
# @Author: Lmm
# @Date  : 2017-10-24 16:13
# @Desc  : 用于获取年报中的财务信息

from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
import hashlib
from PublicCode import deal_html_code
import logging
import time

run_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,loan, if_loan, subsidy, if_subsidy,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
dict = {
	u"资产总额": "asset",
	u"权益合计": "benifit",
	u"总收入": "income",
	u"利润总额": "profit",
	u"主营业务收入": "main_income",
	u"净利润": "net_income",
	u"纳税总额": "tax",
	u"负债总额": "debt",
	u"金融贷款": "loan",
	u"政府补助": "subsidy"
}


class Report_Run:
	def get_info(self, data):
		info = {}
		for key, value in dict.iteritems():
			info[value] = deal_html_code.get_match_info(key, data)
		# 调用juege_if_public判断是否公示，判断是否公示是根据所取到的该部分信息中是否含有元
		# 进行判断的，可能总结不够全面，以后见到不含元的再更改函数
		info["if_asset"] = self.judge_if_public(info["asset"])
		# 判断完是否公示后调用match_float取里面的数字
		info["asset"] = deal_html_code.match_float(info["asset"])
		info["if_benifit"] = self.judge_if_public(info["benifit"])
		info["benifit"] = deal_html_code.match_float(info["benifit"])
		info["if_main"] = self.judge_if_public(info["main_income"])
		info["main_income"] = deal_html_code.match_float(info["main_income"])
		info["if_net"] = self.judge_if_public(info["net_income"])
		info["net_income"] = deal_html_code.match_float(info["net_income"])
		info["if_tax"] = self.judge_if_public(info["tax"])
		info["tax"] = deal_html_code.match_float(info["tax"])
		info["if_loan"] = self.judge_if_public(info["loan"])
		info["loan"] = deal_html_code.match_float(info["loan"])
		info["if_subsidy"] = self.judge_if_public(info["subsidy"])
		info["subsidy"] = deal_html_code.match_float(info["subsidy"])
		info["if_income"] = deal_html_code.match_float(info["income"])
		info["income"] = self.judge_if_public(info["income"])
		info["if_profit"] = deal_html_code.match_float(info["profit"])
		info["profit"] = self.judge_if_public(info["profit"])
		info["if_debt"] = deal_html_code.match_float(info["debt"])
		info["debt"] = self.judge_if_public(info["debt"])
		
		return info
	
	# 用来判断是否公示
	def judge_if_public(self, asset):
		if asset == '':
			if_asset = 0
		else:
			if u"元" in asset:
				if_asset = 1
			else:
				if_asset = 0
		return if_asset
	
	def update_to_db(self, info, gs_basic_id, gs_report_id, year, cursor, connect):
		asset, if_asset, benifit, if_benifit = info["asset"], info["if_asset"], info["benifit"], info["if_benifit"]
		income, if_income, profit, if_profit = info["income"], info["if_income"], info["profit"], info["if_profit"]
		main_income, if_main, net_income, if_net = info["main_income"], info["if_main"], info["net_income"], info[
			"if_net"]
		tax, if_tax, debt, if_debt = info["tax"], info["if_tax"], info["debt"], info["if_debt"]
		loan, if_loan, subsidy, if_subsidy = info["loan"], info["if_loan"], info["subsidy"], info["if_subsidy"]
		m = hashlib.md5()
		m.update(str(gs_basic_id) + str(year))
		uuid = m.hexdigest()
		remark = 0
		try:
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			row_count = cursor.execute(run_string, (
				gs_report_id, gs_basic_id, config.province, asset, if_asset, benifit, if_benifit, income, if_income,
				profit,
				if_profit, main_income, if_main, net_income, if_net, tax, if_tax, debt, if_debt, uuid, loan, if_loan,
				subsidy, if_subsidy, updated_time,
				updated_time))
			connect.commit()
		
		except Exception, e:
			remark = 100000006
			logging.error('report run error %s' % e)
		finally:
			# cursor.close()
			# connect.close()
			if remark < 100000001:
				remark = row_count
			return remark
