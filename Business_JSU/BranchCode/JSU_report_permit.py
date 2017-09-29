#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_report_permit.py
# @Author: Lmm
# @Date  : 2017-09-25
# @Desc  : 用于获得年报中的行政许可信息



from PublicCode.Public_Code import config
from PublicCode import deal_html_code
from PublicCode.Public_Code import GetBranchInfo
from PublicCode.Public_Code import Judge
import logging
import hashlib
import time

permit_string = 'insert into gs_report_permit(gs_basic_id,gs_report_id,uuid,province,types,valto,created,updated)' \
                'values(%s,%s,%s,%s,%s,%s,%s,%s)'
permit_py = 'update gs_py set gs_py_id = %s ,report_permit = %s ,updated = %s where  gs_py_id = %s'

class Report_Permit:
	def deal_single_info(self,data,info):
		for i,singledata in enumerate(data):
			types = singledata["AUDIT_NAME"]
			valto = singledata["VALID_END_DATE"]
			valto = deal_html_code.change_chinese_date(valto)
			info[i] = [types, valto]
	def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, info):
		insert_flag,update_flag = 0,0
		remark = 0
		total = len(info)
		try:
			for key in info.keys():
				
				types, valto = info[key][0], info[key][1]
				m = hashlib.md5()
				m.update(str(gs_basic_id)+str(gs_report_id)+str(key))
				uuid = m.hexdigest()
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(permit_string,(gs_basic_id, gs_report_id, uuid, config.province, types, valto, updated_time, updated_time))
				insert_flag += flag
				connect.commit()
		except Exception, e:
			remark = 100000006
			logging("permit error %s" % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
def main(report_id,gs_report_id,cursor,connect,gs_basic_id,gs_py_id):
	pattern = "report_permit"
	types = config.key_params["report_permit"]
	url = config.main_branch_url
	headers = config.headers
	object = Report_Permit()
	info,flag = GetBranchInfo(url,headers,object,types).get_report_info(report_id)
	
	flag = Judge().update_report_info(flag, info, gs_report_id, gs_basic_id, cursor, connect, pattern)
	Judge().update_py(gs_py_id, permit_py, flag)