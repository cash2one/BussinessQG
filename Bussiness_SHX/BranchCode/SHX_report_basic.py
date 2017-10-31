# -*- coding: utf-8 -*-
# @File  : SHX_report_basic.py
# @Author: Lmm
# @Date  : 2017-10-24 15:32
# @Desc  :
from PublicCode import deal_html_code
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
import logging
import time
import hashlib
from lxml import etree

basic_string = 'insert into gs_report(gs_basic_id,year,province,name,uuid, tel, address, email, postcode, status, employee, if_empnum, womennum,\
 if_womennum, holding, if_holding,mainbus,code,ccode,source,runner,amount,fill_date,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
run_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,loan, if_loan, subsidy, if_subsidy,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_address = 'update gs_basic set gs_basic_id = %s,tel = %s,address = %s,email = %s where gs_basic_id = %s'


class Report_Basic:
	def __init__(self):
		pass
	
	# 用于获取基本信息
	def get_info(self, data):
		
		info = {}
		for key, value in config.report_basic_dict.iteritems():
			info[value] = deal_html_code.get_match_info(key, data)
		if u"不公示" in info["employee"] or info["employee"] == '':
			info["if_empnum"] = 0
		else:
			info["if_empnum"] = 1
		womennum = info["womennum"]
		if u"不公示" in womennum or womennum == '':
			info["if_womennum"] = 0
		else:
			info["if_womennum"] = 1
		holding = info["holding"]
		if u"不公示" in holding or holding == '':
			if_holding = 0
			info["if_holding"] = if_holding
		else:
			info["if_holding"] = 1
		info["if_invest"] = self.transform_ifornot(info["if_invest"])
		info["if_fwarnnt"] = self.transform_ifornot(info["if_fwarnnt"])
		info["if_website"] = self.transform_ifornot(info["if_website"])
		info["if_sharetrans"] = self.transform_ifornot(info["if_sharetrans"])
		
		return info
	
	# 由于数据库中的是否是用1和0表示的因此需要将是否转换为1和0来表示
	def transform_ifornot(self, string):
		if u'是' == string:
			trans_data = 0
		elif u"否" == string:
			trans_data = 0
		else:
			trans_data = 0
		return trans_data
	
	# 用于将数据更新到数据库中
	def update_to_db(self, info, gs_basic_id, cursor, connect, fill_date):
		
		year = int(str(fill_date)[0:4]) - 1
		name, tel, address, email = info["name"], info["tel"], info["address"], info["email"]
		postcode, status, employee, if_empnum = info["postcode"], info["status"], info["employee"], info["if_empnum"]
		womennum, if_womennum, holding, if_holding = info["womennum"], info["if_womennum"], info["holding"], info[
			"if_holding"]
		mainbus, code = info["mainbus"], info["code"]
		if code.startswith("9"):
			ccode = code
		else:
			ccode = ''
		runner = info["runner"]
		amount = info["amount"]
		
		m = hashlib.md5()
		m.update(str(gs_basic_id) + str(year))
		uuid = m.hexdigest()
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
		
		return gs_report_id
