#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_report_invest.py
# @Author: Lmm
# @Date  : 2017-09-23
# @Desc  : 用于获得江苏企业年报中的对外投资信息
from PublicCode import config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Judge
import json
import logging
import time
out_invest_string = 'insert into gs_report_invest(gs_basic_id,gs_report_id,province,name, code, ccode,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'





class Report_Invest:
	def __init__(self, url, headers):
		self.url = url
		self.headers = headers
	def get_info(self):
		info = {}
		result,status_code = Send_Request(self.url, self.headers).send_request()
		if status_code ==200:
			flag = 1
			data = json.loads(result.content)
			for i,singledata in enumerate(data):
				name = singledata["INVEST_NAME"]
				code = singledata["INVEST_REG_NO"]
				if code ==None:
					ccode = None
				elif code.startswith("9"):
					ccode = code
				else:
					ccode = None
				info[i] = [name, code, ccode]
		else:
			flag = 100000004
		return info, flag
	
	def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, info):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			for key in info.keys():
				name = info[key][0]
				code = info[key][1]
				ccode = info[key][2]
				uuid = ''
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(out_invest_string, (
					gs_basic_id, gs_report_id, config.province, name, code, ccode, uuid, updated_time, updated_time))
				connect.commit()
				insert_flag += flag
		except Exception, e:
			remark = 100000006
			logging.error('invest error %s' % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
def main(report_id,gs_report_id,cursor,connect,gs_basic_id):
	url = config.main_branch_url
	headers = config.headers
	pattern = "report_invest"
	types = config.key_params["report_invest"]
	url = url + config.report_params1.format(types,report_id)
	object = Report_Invest(url,headers)
	info, flag = object.get_info()
	flag = Judge().update_report_info(flag, info, gs_report_id, gs_basic_id, cursor, connect, pattern)
	