#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_basic.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获取北京的连接信息
from PublicCode import config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Connect_to_DB
from PublicCode import deal_html_code
from PublicCode.Public_Code import Log
from PublicCode.Public_Code import Judge
import random
import json
import logging
import time




update_string = 'update gs_basic set gs_basic_id = %s, name = %s ,ccode = %s,status = %s ,types = %s ,legal_person = %s, \
reg_date = %s ,appr_date = %s,reg_amount = %s, start_date = %s ,end_date = %s ,reg_zone = %s,reg_address = %s ,scope = %s ,del_date = %s,updated = %s where gs_basic_id = %s'

class Basic:
	def __init__(self,url,headers):
		self.url = url
		self.headers = headers
	def name(self):
		result,status_code = Send_Request(self.url,self.headers).send_request()
		if status_code ==200:
			#flag用于标记程序运行状态
			flag = 1
			data = json.loads(result.content)
			name = data["CORP_NAME"]
			ccode = data["REG_NO"]
			status = data["CORP_STATUS"]
			types = data["ZJ_ECON_KIND"]
			legal_person = data["OPER_MAN_NAME"]
			reg_date = data["START_DATE"]
			reg_date = deal_html_code.change_chinese_date(reg_date)
			appr_date = data["CHECK_DATE"]
			appr_date = deal_html_code.change_chinese_date(appr_date)
			reg_amount = data["REG_CAPI"]
			start_date = data["FARE_TERM_START"]
			start_date = deal_html_code.change_chinese_date(start_date)
			end_date = data["FARE_TERM_END"]
			end_date = deal_html_code.change_chinese_date(end_date)
			reg_zone = data["BELONG_ORG"]
			reg_address = data["ADDR"]
			scope = data["FARE_SCOPE"]
			del_date = data["WRITEOFF_DATE"]
			del_date = deal_html_code.change_chinese_date(del_date)
			encryed_code = data["REG_NO_EN"]
			
			info = [name, ccode, status, types, legal_person, reg_date, appr_date, reg_amount, start_date, end_date,
					reg_zone, reg_address, scope, del_date]
		else:
			encryed_code = ''
			flag = 100000004
		return info, flag, encryed_code
	
	def update_to_db(self, info, gs_basic_id):
		remark = 0
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			name, ccode, status, types = info[0], info[1], info[2], info[3]
			legal_person, reg_date, appr_date, reg_amount = info[4], info[5], info[6], info[7]
			start_date, end_date, reg_zone, reg_address = info[8], info[9], info[10], info[11]
			scope, del_date = info[12], info[13]
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			row_count = cursor.execute(update_string, (
			gs_basic_id, name, ccode, status, types, legal_person, reg_date, appr_date, reg_amount, start_date,
			end_date, reg_zone, reg_address, scope, del_date, updated_time, gs_basic_id))
			connect.commit()
		except Exception, e:
			cursor.close()
			connect.close()
			logging.error("basic error:%s" % e)
			remark = 100000006
		finally:
			if remark < 100000001:
				remark = row_count
				logging.info("update basic:%s" % remark)
			# print remark
			return remark
		
def main(org,id,seq_id,gs_basic_id):
	tmp = random.randint(0, 100)
	url = config.basic_url.format(org, id, seq_id, tmp)
	headers = config.headers
	object = Basic(url, headers)
	info, flag, encryed_code = object.name()
	if flag ==1:
		flag = object.update_to_db(info, gs_basic_id)
	print "basic_flag:%s" % flag
	
	return encryed_code
# if __name__ == '__main__':
# 	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# 	start = time.time()
# 	main()
# 	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
