#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_permit2.py
# @Author: Lmm
# @Date  : 2017-09-25
# @Desc  : 用于获得企业公示的行政许可信息
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import GetBranchInfo
from PublicCode.Public_Code import Judge
import logging
import time
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_string = 'select gs_permit_id from gs_permit where gs_basic_id = %s and filename = %s and code = %s and start_date = %s and end_date = %s and source = 0'
permit_string = 'insert into gs_permit(gs_basic_id,id,name, code, filename, start_date, end_date, content, gov_dept,status,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Permit:
	def deal_single_info(self,data,info):
		for i,singledata in enumerate(data):
			name = ''
			code = singledata["AUDIT_NO"]
			filename = singledata["AUDIT_NAME"]
			if filename ==None:
				filename = ''
			start_date = singledata["VALID_START_DATE"]
			start_date = deal_html_code.change_chinese_date(start_date)
			end_date = singledata["VALID_END_DATE"]
			end_date = deal_html_code.change_chinese_date(end_date)
			content = singledata["VALID_CONTENT"]
			gov_dept = singledata["VALID_ORG"]
			status = singledata["STATUS"]
			RN = singledata["RN"]
			info[RN] = [name, code, filename, start_date, end_date, content, gov_dept,status]
	
	def update_to_db(self, info, gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		source = 0
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				name, code, filename, start_date = info[key][0], info[key][1], info[key][2], info[key][3]
				end_date, content, gov_dept = info[key][4], info[key][5], info[key][6]
				status = info[key][7]
				count = cursor.execute(select_string, (gs_basic_id, filename, code, start_date, end_date))
				m = hashlib.md5()
				m.update(code)
				id = m.hexdigest()
				
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(permit_string, (
						gs_basic_id, id, name, code, filename, start_date, end_date, content, gov_dept, status, source,
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
	pattern = "permit2"
	flag = Judge().update_info2(pattern, org, id, seqid, regno, Permit, gs_basic_id)
	
	

