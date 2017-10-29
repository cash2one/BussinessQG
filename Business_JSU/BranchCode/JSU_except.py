#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_except.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获得经营异常信息
from PublicCode import config
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Log
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Judge
from PublicCode import deal_html_code
import logging
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()




except_string = 'insert into gs_except(gs_basic_id,types, in_reason, in_date,out_reason, out_date, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_except = 'select gs_except_id from gs_except where gs_basic_id = %s and in_date = %s'
select_except_py = 'select  updated from gs_except where gs_basic_id = %s order by updated desc  LIMIT 1'
update_except = 'update gs_except set gs_except_id = %s,types = %s ,in_reason = %s,out_reason = %s ,out_date=%s,gov_dept = %s ,updated = %s where gs_except_id = %s'
update_except_py = 'update gs_py set gs_py_id = %s,gs_except = %s,updated =%s where gs_py_id = %s'



class Except:
	def deal_single_info(self,data,info):
		for i,singledata in enumerate(data):
			types = '经营异常'
			in_reason = singledata["FACT_REASON"]
			in_date = singledata["MARK_DATE"]
			in_date = deal_html_code.change_chinese_date(in_date)
			out_reason = singledata["REMOVE_REASON"]
			out_date = singledata["CREATE_DATE"]
			out_date =deal_html_code.change_chinese_date(out_date)
			gov_dept = singledata["CREATE_ORG"]
			RN = singledata["RN"]
			info[RN] = [types, in_reason, in_date, out_reason, out_date, gov_dept]
	
	def update_to_db(self,  info,gs_basic_id):
		update_flag, insert_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				types, in_reason, in_date = info[key][0], info[key][1], info[key][2]
				out_reason, out_date, gov_dept = info[key][3], info[key][4], info[key][5]
				
				count = cursor.execute(select_except, (gs_basic_id, in_date))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(except_string, (
						gs_basic_id, types, in_reason, in_date, out_reason, out_date, gov_dept, updated_time))
					insert_flag += rows_count
					connect.commit()
				elif count == 1:
					gs_except_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(update_except, (
						gs_except_id, types, in_reason, out_reason, out_date, gov_dept, updated_time, gs_except_id))
					update_flag += rows_count
					connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error("except error: %s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag + update_flag
			
			return remark, total,insert_flag, update_flag


def main(org, id, seqid, regno, gs_basic_id, gs_py_id):
	pattern = "except"
	flag = Judge().update_info2(pattern, org, id, seqid, regno, Except, gs_basic_id)
	Judge().update_py(gs_py_id, update_except_py, flag)



