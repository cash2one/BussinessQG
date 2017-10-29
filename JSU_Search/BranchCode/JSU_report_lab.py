#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_report_lab.py
# @Author: Lmm
# @Date  : 2017-09-23
# @Desc  : 用于获得年报中的社保信息
from PublicCode.Public_Code import config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Judge
from PublicCode import deal_html_code
import logging
import time

import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

lab_string = 'insert into gs_report_lab(gs_basic_id,gs_report_id,uuid,province,if_owe, if_basenum, if_periodamount,birth_owe, birth_num, birth, birth_base' \
			 ',old_num, old_owe, old, old_base,unemploy, unemploy_base, unemploy_owe, unemploy_num,medical, medical_base, medical_owe, medical_num, ' \
			 'injury, injury_owe, injury_num,created,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Report_Lab:
	def __init__(self, url, headers):
		self.url = url
		self.headers = headers
	def get_info(self):
		result, status_code = Send_Request(self.url,self.headers).send_request()
		info = {}
		if status_code == 200:
			flag = 1
			data = json.loads(result.content)
			if len(data) >0:
				uuid = data["ID"]
				birth_owe = data["PAYMENT_SY"]
				birth_num = data["MATERNITY_NUM"]
				birth = data["SOCIALINS_SY"]
				birth_base = data["WAGES_SY"]
				if u"不公示" in birth_owe:
					if_owe = 0
				else:
					if_owe = 1
				if u"不公示" in birth_base:
					 if_basenum = 0
				else:
					if_basenum = 0
				if u"不公示" in birth:
					if_periodamount = 0
				else:
					if_periodamount = 1
				
				birth_owe = deal_html_code.match_float(birth_owe)
				birth_num =deal_html_code.match_float(birth_num)
				birth =deal_html_code.match_float(birth)
				birth_base = deal_html_code.match_float(birth_base)
				old_num = deal_html_code.match_float(data["ENDOWMENT_NUM"])
				old_owe = deal_html_code.match_float(data["PAYMENT_JBYL"])
				old = deal_html_code.match_float(data["SOCIALINS_JBYL"])
				old_base = deal_html_code.match_float(data["WAGES_JBYL"])
				unemploy = deal_html_code.match_float(data["SOCIALINS_SYBX"])
				unemploy_base = deal_html_code.match_float(data["WAGES_SYBX"])
				unemploy_owe = deal_html_code.match_float(data["PAYMENT_SYBX"])
				unemploy_num = deal_html_code.match_float(data["UNEMPLOYED_NUM"])
				medical = deal_html_code.match_float(data["SOCIALINS_YLBX"])
				medical_base = deal_html_code.match_float(data["WAGES_YLBX"])
				medical_owe = deal_html_code.match_float(data["PAYMENT_YLBX"])
				medical_num = deal_html_code.match_float(data["MEDICARE_NUM"])
				injury = deal_html_code.match_float(data["SOCIALINS_GSBX"])
				injury_owe = deal_html_code.match_float(data["PAYMENT_GSBX"])
				injury_num = deal_html_code.match_float(data["EMPLOYMENT_INJURY_NUM"])
				info[0] = [uuid, if_owe, if_basenum, if_periodamount, birth_owe, birth_num, birth, birth_base, old_num,
						   old_owe, old, old_base, \
						   unemploy, unemploy_base, unemploy_owe, unemploy_num, medical, medical_base, medical_owe,
						   medical_num, injury, injury_owe, injury_num]
			else:
				logging.info("无社保信息")
		else:
			flag = 100000004
			logging.info("打开社保链接失败！")
		
	
		return info,flag
	
	def update_to_db(self, gs_report_id, gs_basic_id, cursor, connect, info):
		remark = 0
		try:
			uuid, if_owe, if_basenum, if_periodamount = info[0][0], info[0][1], info[0][2], info[0][3]
			birth_owe, birth_num, birth, birth_base = info[0][4], info[0][5], info[0][6], info[0][7]
			old_num, old_owe, old, old_base = info[0][8], info[0][9], info[0][10], info[0][11]
			unemploy, unemploy_base, unemploy_owe, unemploy_num = info[0][12], info[0][13], info[0][14], info[0][15]
			medical, medical_base, medical_owe, medical_num = info[0][16], info[0][17], info[0][18], info[0][19]
			injury, injury_owe, injury_num = info[0][20], info[0][21], info[0][22]
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			row_count = cursor.execute(lab_string, (
			gs_basic_id, gs_report_id, uuid, config.province, if_owe, if_basenum, if_periodamount, birth_owe, birth_num, birth,
			birth_base, old_num, old_owe, old, old_base, unemploy, unemploy_base, unemploy_owe,
			unemploy_num, medical, medical_base, medical_owe, medical_num, injury, injury_owe, injury_num, updated_time,
			updated_time))
			connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error("lab error %s" % e)
		finally:
			if remark < 100000001:
				remark = row_count
			return remark
def main(report_id,gs_report_id,cursor,connect,gs_basic_id):
	url = config.main_branch_url
	headers = config.headers
	types = config.key_params["report_lab"]
	url = url + config.report_params1.format(types,report_id)
	object = Report_Lab(url,headers)
	info,flag = object.get_info()
	if len(info)>0:
		remark = object.update_to_db(gs_report_id, gs_basic_id, cursor, connect, info)
		