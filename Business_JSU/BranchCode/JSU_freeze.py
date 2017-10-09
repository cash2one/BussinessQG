#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_freeze.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获得司法协助信息
import sys
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Log
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Judge
import json
import logging
import time
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?querySfxzGqdjDetail=true&org={0}&id={1}'


freeze_string = 'insert into gs_freeze(gs_basic_id,executor, stock_amount, court, notice_no,status,items, rule_no, enforce_no,cert_cate,cert_code, start_date, end_date,period, pub_date,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_freeze = 'select gs_freeze_id from gs_freeze where gs_basic_id = %s and rule_no = %s and executor = %s'
update_freeze_py = 'update gs_py set gs_py_id = %s ,gs_freeze = %s ,updated = %s where gs_py_id = %s'
headers = config.headers
class Freeze:
	def deal_single_info(self,data,info):
		for i,singledata in enumerate(data):
			org = singledata["ORG"]
			id = singledata["ID"]
			RN = singledata["RN"]
			status = singledata["FREEZE_STATUS"]
			detail_url = url.format(org,id)
			self.get_detail_info(info,RN,detail_url,status)
					
	#用于获得一条详情信息	
	def get_detail_info(self,info,RN,detail_url,status):
		result, status_code = Send_Request(detail_url, headers).send_request()
		if status_code == 200:
			
			data = json.loads(result.content)["djInfo"][0]
			executor = data["ASSIST_NAME"]
			if executor ==None:
				executor = ''
			stock_amount = data["FREEZE_AMOUNT"]
			court = data["EXECUTE_COURT"]
			notice_no = data["NOTICE_NO"]
			items = data["ASSIST_ITEM"]
			rule_no = data["ADJUDICATE_NO"]
			enforce_no = data["NOTICE_NO"]
			cert_cate = data["ASSIST_IDENT_TYPE"]
			cert_code = data["ASSIST_IDENT_NO"]
			start_date = data["FREEZE_START_DATE"]
			end_date = data["FREEZE_END_DATE"]
			period = data["FREEZE_YEAR_MONTH"]
			pub_date = data["PUBLIC_DATE"]
			info[RN] = [executor, stock_amount, court, notice_no, status, items, rule_no, enforce_no, cert_cate,
						  cert_code, start_date, end_date, period, pub_date]
	
	def update_to_db(self, info,gs_basic_id):
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(info)
		try:
			for key in info.keys():
				executor, stock_amount, court, notice_no = info[key][0], info[key][1], info[key][2], info[key][3]
				status, items, rule_no, enforce_no = info[key][4], info[key][5], info[key][6], info[key][7]
				cert_cate, cert_code, start_date, end_date = info[key][8], info[key][9], info[key][10],info[key][11]
				period, pub_date = info[key][12], info[key][13]
				count = cursor.execute(select_freeze, (gs_basic_id, rule_no,executor))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(freeze_string, (
						gs_basic_id, executor, stock_amount, court, notice_no, status, items, rule_no, enforce_no,
						cert_cate, cert_code, start_date, end_date, period, pub_date, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			logging.error("freeze error: %s" % e)
			flag = 100000006
		finally:
			cursor.close()
			connect.close()
			if flag < 100000001:
				flag = insert_flag
			return flag,total, insert_flag, update_flag
def main(org, id, seqid, regno, gs_basic_id, gs_py_id):
	pattern = "freeze"
	flag = Judge().update_info2(pattern, org, id, seqid, regno, Freeze, gs_basic_id)
	Judge().update_py(gs_py_id, update_freeze_py, flag)



if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main(org, id, seqid, regno)
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
