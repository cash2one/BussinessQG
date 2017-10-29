#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_report.py
# @Author: Lmm
# @Date  : 2017-10-24 15:32
# @Desc  : 用于获取年报信息，一次性获取所有的年报信息

from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode import deal_html_code
import SHX_report_assure
import SHX_report_basic
import SHX_report_invest
import SHX_report_lab
import SHX_report_permit
import SHX_report_run
import SHX_report_share
import SHX_report_schange
import SHX_report_web

import logging
import time


select_basic_year = 'select reg_date from gs_basic where gs_basic_id = %s'

report_dict = {
	u"社保信息":"report_lab",
	u"基本信息":"report_basic",
	u"担保信息":"report_assure",
	u"网站":"report_web",
	u"投资信息":"report_invest",
	u"资产状况":"report_run1",
	u"经营状况":"reoprt_run2",
	u"行政许可":"report_permit",
	u"股东及出资":"report_share"
}
class Report:
	def __init__(self,data, fill_date,cursor,connect,gs_basic_id):
		self._data = data
		self._fill_date = fill_date
		self._cursor = cursor
		self._connect = connect
		self.gs_basic_id = gs_basic_id
		
	
	#用于获得相应年份的对应的分项信息
	def get_year_info(self):
		year = self._fill_date[0:4]
		string = u'%s年度报告'%year
		data = self._data.xpath('//p[contains(text(),"%s")]/../../following-sibling::*[1]' % string)
		info = {}
		for key,value in config.report_dict.iteritems():
			info[value] = deal_html_code.match_info(key,data)
		if info["report_run1"] !='':
			info["report_run"] = info["report_run1"]
		elif info["report_run2"]!='':
			info["report_run"] = info["report_run2"]
		del info["report_run1"]
		del info["report_run2"]
		return info
	
	# 这一部分也可以写成一个循环,年报情况较多，暂时不改
	def update_all_info(self,info_dict):
	
		try:
			remark = 1
			year = self._fill_date[0:4]
			if "report_basic" in info_dict.keys():
				info = SHX_report_basic.Report_Basic().get_info(info_dict["basic"])
				gs_report_id = SHX_report_basic.Report_Basic().update_to_db(info, self.gs_basic_id, self.cursor, self.connect,
																			self.fill_date)
			if int(year) == 2016:
				if "report_lab" in info_dict.keys():
					info = SHX_report_lab.Report_Lab().get_info(info_dict["report_lab"])
					if len(info) == 0:
						flag = -1
					else:
						flag = SHX_report_lab.Report_Lab().update_to_db(info, self.gs_basic_id, gs_report_id, self._cursor,
																		self._connect)
					logging.info("report_lab:%s" % flag)
			if "report_run" in info_dict.keys():
				info = SHX_report_run.Report_Run().get_info(info_dict["report_run"])
				if len(info) == 0:
					flag = -1
				else:
					flag = SHX_report_run.Report_Run().update_to_db(info, self.gs_basic_id, gs_report_id, year, self._cursor,
																	self._connect)
				logging.info("report_run:%s" % flag)
			if "report_permit" in info_dict.keys():
				self.update_info(SHX_report_permit.Report_Permit, "report_permit", info_dict)
			if "report_web" in info_dict.keys():
				self.update_info(SHX_report_web.Report_Web, "report_web", info_dict)
			if "report_invest" in info_dict.keys():
				self.update_info(SHX_report_invest.Report_Invest, "report_invest", info_dict)
			if "report_share" in info_dict.keys():
				self.update_info(SHX_report_share.Report_Share, "report_share", info_dict)
			if "report_assure" in info_dict.keys():
				self.update_info(SHX_report_assure, "report_assure", info_dict)
			if "report_schange" in info_dict.keys():
				self.update_info(SHX_report_schange.Report_Schange, "report_schange", info_dict)
			
			
			def update_info(self,class_object,pattern,info_dict):
				info = class_object().get_info(info_dict[pattern])
				if len(info)==0:
					flag = -1
					logging.info("%s 无信息 "%pattern)
				else:
					flag, total, insert_flag, update_flag = class_object().update_to_db(info,self.gs_basic_id,self.gs_report_id,self._cursor,self._connect)
					
				logging.info( "%s:"%pattern +str(flag) +'||' + str(total) +'||'+str(insert_flag)+'||'+str(update_flag))
		except Exception,e:
			remark = 100000006
			logging.info("%s report error:%s"%(year,e))
		finally:
			print "%s:%s"%(year,remark)
def get_all_report_info(data,cursor,connect,fill_data,gs_basic_id):
	for key,value in enumerate(fill_data):
		object = Report(data, value,cursor,connect,gs_basic_id)
		info_dict = object.get_year_info()
		object.update_all_info(info_dict)
		
	
def main(data,fill_data,gs_basic_id):
	try:
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		# 从数据库中选择成立日期
		now_year = time.localtime(time.time())[0]
		select_string = select_basic_year % gs_basic_id
		cursor.execute(select_string)
		reg_date = cursor.fetchall()[0][0]
		if reg_date == None or reg_date == '':
			logging.info("数据库中无成立日期")
		else:
			reg_year = str(reg_date)[0:4]
		#这个思路认为reg_year已经存在，不存在的情况没有再写代码，而是接下来的出错，不运行，以表示异常
		#因为目前还没有见到有的企业没有注册日期
		if now_year == int(reg_year):
			flag = -1
			logging.info("该企业无年报")
		else:
			if len(fill_data) == 0:
				flag = -1
			else:
				get_all_report_info(data,cursor,connect,fill_data,gs_basic_id)
			
	except Exception, e:
		flag = 100000005
		logging.error("error:%s" % e)
	finally:
		print "report:%s" % flag
		cursor.close()
		connect.close()

