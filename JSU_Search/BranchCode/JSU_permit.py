#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_permit.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获得行政许可信息
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
from PublicCode import config

from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Judge
from PublicCode import deal_html_code
import logging
import time
import hashlib

select_string = 'select gs_permit_id from gs_permit where gs_basic_id = %s and filename = %s and code = %s and start_date = %s and end_date = %s and source = 0'
permit_string = 'insert into gs_permit(gs_basic_id,id,name, code, filename, start_date, end_date, content, gov_dept,status,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Permit:
	def deal_single_info(self,data,info):
		for i,singledata in enumerate(data):
			name = ''
			code = singledata["LIC_NO"]
			filename = singledata["LIC_NAME"]
			start_date = singledata["VAL_FROM"]
			start_date = deal_html_code.change_chinese_date(start_date)
			end_date = singledata["VAL_TO"]
			end_date = deal_html_code.change_chinese_date(end_date)
			content = singledata["LICC_ITEM"]
			gov_dept = singledata["LIC_ORG"]
			status = singledata["STATUS"]
			RN = singledata["RN"]
			info[RN] = [name, code, filename, start_date, end_date, content, gov_dept,status]
	
	def update_to_db(self, information, gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(information)
		source = 0
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				name, code, filename, start_date = information[key][0], information[key][1], information[key][2], \
												   information[key][3]
				end_date, content, gov_dept = information[key][4], information[key][5], information[key][6]
				status = information[key][7]
				count = cursor.execute(select_string, (gs_basic_id, filename, code, start_date, end_date))
				m = hashlib.md5()
				m.update(code)
				id = m.hexdigest()
				
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(permit_string, (
						gs_basic_id, id, name, code, filename, start_date, end_date, content, gov_dept, status,source,
						updated_time))
					insert_flag += rows_count
					connect.commit()

		except Exception, e:
			cursor.close()
			connect.close()
			remark = 100000006
			logging.error("permit error: %s" % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag


def main(org, id, seqid, regno, gs_basic_id):
	pattern = "permit"
	flag = Judge().update_info2(pattern, org, id, seqid, regno, Permit, gs_basic_id)
	
	
