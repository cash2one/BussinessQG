#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_report_schange.py
# @Author: Lmm
# @Date  : 2017-09-25
# @Desc  : 用于获得年报中的股权变更信息
from PublicCode import deal_html_code
from PublicCode.Public_Code import config
from PublicCode.Public_Code import GetBranchInfo
from PublicCode.Public_Code import Judge
import logging
import time
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

schange_string = 'insert into gs_report_schange(gs_basic_id,gs_report_id,province,name,percent_pre,percent_after,dates,uuid,created,updated)values' \
                 '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Report_Schange:
	def deal_single_info(self,data,info):
		for i,singledata in enumerate(data):
			uuid = singledata["ID"]
			name = singledata["STOCK_NAME"]
			percent_pre =singledata["CHANGE_BEFORE"]
			percent_after = singledata["CHANGE_AFTER"]
			dates = singledata["CHANGE_DATE"]
			dates = deal_html_code.change_chinese_date(dates)
			RN = singledata["RN"]
			info[RN] = [name, percent_pre, percent_after, dates,uuid]
	
	def update_to_db(self, gs_report_id, gs_basic_id, cursor, connect, info):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			for key in info.keys():
				name, percent_pre, percent_after, dates = info[key][0], info[key][1], info[key][2], info[key][3]
				uuid = info[key][4]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(gs_report_id) + str(uuid))
				uuid = m.hexdigest()
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(schange_string, (
					gs_basic_id, gs_report_id, config.province, name, percent_pre, percent_after, dates, uuid, updated_time,
					updated_time))
				connect.commit()
				insert_flag += flag
		
		except Exception, e:
			remark = 100000006
			logging.error('schange error %s' % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
def main(report_id,gs_report_id,cursor,connect,gs_basic_id):
	pattern = "report_schange"
	types = config.key_params["report_schange"]
	url = config.main_branch_url
	headers = config.headers
	object = Report_Schange()
	info,flag = GetBranchInfo(url,headers,object,types).get_report_info(report_id)
	flag = Judge().update_report_info(flag, info, gs_report_id, gs_basic_id, cursor, connect, pattern)
	