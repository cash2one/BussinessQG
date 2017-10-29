#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_report_assure.py
# @Author: Lmm
# @Date  : 2017-09-25
# @Desc  : 用于获取年报中的对外担保信息
from PublicCode import config

from PublicCode.Public_Code import GetBranchInfo
from PublicCode.Public_Code import Judge
import logging
import time
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

assure_string = 'insert into gs_report_assure(gs_basic_id,gs_report_id, uuid, province, creditor, debtor, cates, amount, deadline, period, ways,if_fwarnnt,created,updated) \
values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

assure_py = 'update gs_py set gs_py_id = %s ,report_assure = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s '
class Report_Assure:
	def deal_single_info(self, data, info):
		for i, singledata in enumerate(data):
			uuid = singledata["ID"]
			creditor = singledata["CRED_NAME"]
			debtor = singledata["DEBT_NAME"]
			cates = singledata["CRED_TYPE"]
			amount = singledata["CRED_AMOUNT"]
			deadline = singledata["GUAR_DATE"]
			period = singledata["GUAR_PERIOD"]
			ways = singledata["GUAR_TYPE"]
			if_fwarnnt = 1
			info[i] = [uuid, creditor, debtor, cates, amount, deadline, period, ways, if_fwarnnt]
		
	def update_to_db(self, gs_report_id, gs_basic_id, cursor, connect, info):
		remark = 0
		insert_flag, update_flag = 0, 0
		total = len(info)
		try:
			for key in info.keys():
				uuid, creditor, debtor, cates = info[key][0], info[key][1], info[key][2], info[key][3]
				amount, deadline, period, ways = info[key][4], info[key][5], info[key][6], info[key][7]
				if_fwarnnt = info[key][8]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(gs_report_id)+str(uuid))
				uuid = m.hexdigest()
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(assure_string, (
				gs_basic_id, gs_report_id, uuid, config.province, creditor, debtor, cates, amount, deadline, period, ways,
				if_fwarnnt, updated_time, updated_time))
				insert_flag += flag
				connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error("report assure error:%s" % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
def main(report_id,gs_report_id,cursor,connect,gs_basic_id,gs_py_id):
	pattern = "report_assure"
	types = config.key_params["report_assure"]
	url = config.main_branch_url
	headers = config.headers
	object = Report_Assure()
	info, flag = GetBranchInfo(url, headers, object, types).get_report_info(report_id)
	flag = Judge().update_report_info(flag,info,gs_report_id,gs_basic_id,cursor,connect,pattern)
	Judge().update_py(gs_py_id,assure_py,flag)