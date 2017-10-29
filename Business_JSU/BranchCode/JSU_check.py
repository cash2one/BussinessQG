#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_check.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获取抽查检查信息,并将信息插入到数据库中
#          此项信息需要翻页
from PublicCode import config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Log
from PublicCode import deal_html_code
from PublicCode.Public_Code import Judge
import logging
import json
import re
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

check_string = 'insert  into gs_check(gs_basic_id,types,result,check_date,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_check = 'select gs_check_id from gs_check where gs_basic_id = %s and check_date = %s and types = %s'
update_check_py = 'update gs_py set gs_py_id = %s,gs_check = %s,updated = %s where gs_py_id = %s'

class Check:
	#用于处理单条信息
	def deal_single_info(self,data,info):
		for i,single in enumerate(data):
			types = single["CHECK_TYPE"]
			result = single["CHECK_RESULT"]
			check_date = single["CHECK_DATE"]
			check_date = deal_html_code.change_chinese_date(check_date)
			gov_dept = single["CHECK_ORG"]
			info[i] = [types, result, check_date, gov_dept]
	#用于将数据插入到数据库中
	def update_to_db(self, information,gs_basic_id):
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(information)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				types, result = information[key][0], information[key][1]
				check_date, gov_dept = information[key][2], information[key][3]
				
				count = cursor.execute(select_check, (gs_basic_id, check_date, types))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					
					rows_count = cursor.execute(check_string,
												(gs_basic_id, types, result, check_date, gov_dept, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			cursor.close()
			connect.close()
			flag = 100000006
			logging.error("check error: %s" % e)
		finally:
			if flag < 100000001:
				flag = insert_flag
			return flag,total, insert_flag, update_flag


def main(org, id, seqid, regno, gs_basic_id, gs_py_id):
	pattern = "check"
	flag = Judge().update_info2(pattern, org, id, seqid, regno, Check, gs_basic_id)
	Judge().update_py(gs_py_id, update_check_py, flag)


